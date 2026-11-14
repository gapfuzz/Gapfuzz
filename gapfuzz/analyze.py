"""커버리지(llvm-cov JSON)와 AST 호출 그래프를 대조해 공개 API를 분류한다.

분류
  FULL       : 실행됐고, 함수 안의 코드 영역도 모두 실행됨
  PARTIAL    : 실행됐지만 함수 안에 실행되지 않은 분기/영역이 남음
  BLOCKED    : 실행되지 않음. 이 함수로 이어지는 호출 지점이 '이미 실행된 함수 안'에 있지만
               그 지점까지 실행이 도달하지 못함 → 조건(입력·상태)에 막힌 것
  NOT_CALLED : 실행되지 않음. 실행된 코드에서 이 함수로 이어지는 호출 경로 자체가 없음
               → 하네스가 이 API(또는 이 API를 부르는 상위 API)를 호출해야 열림
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict

from .ast_index import AstIndex, CallSite, FuncDecl
from .causes import Cause, CauseFinder, summarize_fixes

# 공개 헤더에 선언돼 있지만 공개 API로 세지 않을 내부 클래스. 라이브러리마다 다르므로 기본값은 비워 두고
# targets/<이름>.json의 internal_classes(또는 analyze --internal-class)로 준다.
DEFAULT_INTERNAL_CLASSES: tuple = ()
MAX_DEPTH = 8


# ---------------------------------------------------------------- coverage

@dataclass
class FuncCov:
    count: int
    regions: list          # [ls, cs, le, ce, count, fileid, expfileid, kind]
    filenames: list[str]
    branches: list = field(default_factory=list)   # [ls, cs, le, ce, true, false, fileid, expfileid, kind]


def load_coverage(path: str) -> dict[str, FuncCov]:
    data = json.load(open(path))["data"][0]
    out: dict[str, FuncCov] = {}
    for f in data["functions"]:
        name = f["name"]
        if ":" in name and not name.startswith("_Z"):
            name = name.split(":", 1)[1]           # 정적 함수는 "파일:이름" 형태
        fc = FuncCov(f["count"], f["regions"], [os.path.abspath(p) for p in f["filenames"]],
                     f.get("branches", []))
        # 생성자/소멸자는 C1(완전 객체)/C2(기반 객체), D1/D2 두 심볼이 같은 몸체를 공유한다.
        # AST는 C1, 커버리지는 C2로 기록하는 일이 많아서 양쪽 이름을 모두 등록한다.
        for key in {name, *_ctor_dtor_aliases(name)}:
            prev = out.get(key)
            if prev is None or fc.count > prev.count:
                out[key] = fc
    return out


ASSERT_USE = re.compile(r"\b\w*assert\w*\s*\(", re.I)


def assert_branches(path: str) -> list[dict]:
    """어서션 매크로 안에서 한쪽으로만 간 검사. llvm-cov는 매크로 안의 분기를 '전개(expansion)'로 따로 기록하므로
    일반 막힌 분기 목록에는 나오지 않는다. 매크로를 쓴 줄에 assert가 있고, 그 안의 분기가 한쪽으로만 갔으면 모은다.
    (정적 어서션처럼 실행 시점 분기가 없는 것은 llvm-cov가 분기를 만들지 않아 자연히 빠진다.)"""
    out, seen, lines = [], set(), {}
    for f in json.load(open(path))["data"][0].get("files", []):
        for ex in f.get("expansions", []):
            sr = ex.get("source_region") or []
            names = ex.get("filenames") or [f["filename"]]
            if len(sr) < 5 or not sr[4]:
                continue                                   # 그 줄이 실행된 적 없으면 '막힌' 것이 아니라 '안 간' 것
            file = os.path.abspath(names[0])
            if file not in lines:
                try:
                    lines[file] = open(file, encoding="utf-8", errors="replace").read().splitlines()
                except OSError:
                    lines[file] = []
            src = lines[file][sr[0] - 1].strip() if 0 < sr[0] <= len(lines[file]) else ""
            if not ASSERT_USE.search(src) or re.search(r"static_assert", src, re.I):
                continue
            one_sided = [b for b in ex.get("branches", []) if (b[4] == 0) != (b[5] == 0)]
            key = (file, sr[0], sr[1])
            if one_sided and key not in seen:
                seen.add(key)
                out.append({"file": file, "line": sr[0], "col": sr[1], "source": src[:160], "count": sr[4]})
    return sorted(out, key=lambda a: (a["file"], a["line"], a["col"]))


_CD_RE = re.compile(r"(?<=[A-Za-z0-9_])([CD])([0-2])E")


def _ctor_dtor_aliases(name: str) -> list[str]:
    if not name.startswith("_ZN"):
        return []
    m = _CD_RE.search(name)
    if not m:
        return []
    alts = {"C": "12", "D": "012"}[m.group(1)]
    return [name[:m.start(2)] + d + name[m.end(2):] for d in alts if d != m.group(2)]


def _code_regions(fc: FuncCov):
    return [r for r in fc.regions if r[7] == 0]


def site_executed(fc: FuncCov, site: CallSite) -> bool:
    """호출 지점(파일, 줄, 열)을 감싸는 가장 작은 코드 영역이 실행됐는지."""
    best = None
    for r in _code_regions(fc):
        ls, cs, le, ce, cnt, fid = r[0], r[1], r[2], r[3], r[4], r[5]
        if fc.filenames[fid] != site.file:
            continue
        if (ls, cs) <= (site.line, site.col) <= (le, ce):
            size = (le - ls, ce - cs)
            if best is None or size < best[0]:
                best = (size, cnt)
    if best is None:
        return fc.count > 0
    return best[1] > 0


# ---------------------------------------------------------------- result

@dataclass
class BlockPoint:
    caller: str            # 실행된 함수(막힌 지점이 있는 곳)
    file: str
    line: int
    source: str            # 그 줄의 소스 코드
    chain: list[str]       # 막힌 지점 → ... → 대상 API


@dataclass
class StuckBranch:
    file: str
    line: int
    source: str
    never: str             # "참" 또는 "거짓": 한 번도 그쪽으로 가지 않은 방향
    col: int = 0
    causes: list[Cause] = field(default_factory=list)   # 하네스 쪽 원인 (차별점 A)
    expr: str = ""         # 그 분기의 조건식 조각 (예: "nBytes == 0")
    in_func: str = ""      # 공개 API가 아니라 그 API가 부르는 내부 함수 안의 분기이면 그 함수 이름


@dataclass
class ApiResult:
    api: str               # 보기 좋은 이름
    mangled: str
    cls: str | None
    sig: str
    decl_line: int | None
    category: str
    region_total: int = 0
    region_hit: int = 0
    missed_lines: list[int] = field(default_factory=list)
    stuck_branches: list[StuckBranch] = field(default_factory=list)   # 도달한 API 안에서 한쪽으로만 간 조건
    blocks: list[BlockPoint] = field(default_factory=list)
    entry_apis: list[str] = field(default_factory=list)   # NOT_CALLED: 하네스에서 부르면 경로가 생기는 공개 API
    note: str = ""


# ---------------------------------------------------------------- analysis

class Analyzer:
    def __init__(self, idx: AstIndex, cov: dict[str, FuncCov], header: str,
                 namespace: str = "", internal_classes=DEFAULT_INTERNAL_CLASSES,
                 harness_files: list[str] | None = None, internal_branches: bool = False, runtime: dict | None = None):
        self.idx = idx
        self.internal_branches = internal_branches   # 내부 함수의 막힌 분기도 가장 가까운 공개 API 아래에 모은다
        self.harness_files = {os.path.abspath(h) for h in (harness_files or [])}
        self.cov = cov
        # 공개 API 헤더: 하나 또는 여러 개 (jsoncpp처럼 공개 API가 헤더 여러 개에 나뉜 라이브러리)
        hs = [header] if isinstance(header, str) else list(header)
        self.headers = {os.path.abspath(h) for h in hs}
        self.header = os.path.abspath(hs[0])
        self.ns = namespace
        self.internal = {f"{namespace}::{c}" for c in internal_classes}
        self.callers: dict[str, list[CallSite]] = defaultdict(list)
        for cs in idx.calls:
            for callee in cs.callees:
                self.callers[callee].append(cs)
        self._src_cache: dict[str, list[str]] = {}
        self._virtual_alias = self._build_virtual_alias()
        self.causes = CauseFinder(idx, self.harness_files, self.pretty, self._src, self.is_public_api,
                                  executed=self._executed, virtual_bases=self._virtual_alias,
                                  runtime=runtime, public_headers=self.headers)

    # 가상 함수: Base::f 를 부르는 지점은 Derived::f 로도 이어질 수 있다
    def _resolve_record(self, name: str, ctx: str) -> str:
        """부모 클래스 이름이 'XMLVisitor'처럼 짧게 적힌 경우 네임스페이스를 붙여 찾는다."""
        if name in self.idx.records:
            return name
        parts = ctx.split("::")[:-1]
        while parts:
            cand = "::".join(parts + [name])
            if cand in self.idx.records:
                return cand
            parts.pop()
        return name

    def _ancestors(self, rec: str, seen=None) -> list[str]:
        seen = seen or set()
        out = []
        for raw in self.idx.records.get(rec, []):
            b = self._resolve_record(raw, rec)
            if b in seen:
                continue
            seen.add(b)
            out.append(b)
            out += self._ancestors(b, seen)
        return out

    def _build_virtual_alias(self) -> dict[str, list[str]]:
        by_key = defaultdict(list)
        for m, fd in self.idx.funcs.items():
            if fd.record and fd.kind == "CXXMethodDecl":
                by_key[(fd.record, fd.name, fd.sig)].append(m)
        alias = defaultdict(list)
        for m, fd in self.idx.funcs.items():
            if not (fd.record and fd.kind == "CXXMethodDecl"):
                continue
            for anc in self._ancestors(fd.record):
                for bm in by_key.get((anc, fd.name, fd.sig), []):
                    if self.idx.funcs[bm].virtual or fd.virtual:
                        alias[m].append(bm)
        return alias

    def _call_sites_into(self, m: str) -> list[CallSite]:
        sites = list(self.callers.get(m, []))
        for base in self._virtual_alias.get(m, []):
            sites += self.callers.get(base, [])
        return sites

    def _expr(self, path: str, ls: int, cs: int, le: int, ce: int) -> str:
        """분기 영역(줄·열 범위)에 해당하는 조건식 조각."""
        self._src(path, ls)
        lines = self._src_cache.get(path, [])
        if not (0 < ls <= len(lines)):
            return ""
        if le == ls:
            return lines[ls - 1][cs - 1:ce - 1].strip()
        return (lines[ls - 1][cs - 1:] + " …").strip()

    def _src(self, path: str, line: int) -> str:
        if path not in self._src_cache:
            try:
                self._src_cache[path] = open(path, errors="replace").read().splitlines()
            except OSError:
                self._src_cache[path] = []
        lines = self._src_cache[path]
        return lines[line - 1].strip() if 0 < line <= len(lines) else ""

    def pretty(self, m: str) -> str:
        fd = self.idx.funcs.get(m)
        if not fd:
            return m
        q = fd.qualname
        if self.ns and q.startswith(self.ns + "::"):
            q = q[len(self.ns) + 2:]
        params = fd.sig[fd.sig.find("("):] if "(" in fd.sig else "()"
        params = params.replace(self.ns + "::", "") if self.ns else params
        return f"{q}{params}".replace("::::", "::{익명}::")

    def is_public_api(self, fd: FuncDecl) -> bool:
        if fd.file not in self.headers or fd.implicit or fd.deleted or fd.pure:
            return False
        if self.ns and not fd.qualname.startswith(self.ns + "::"):   # C 라이브러리는 네임스페이스 없음
            return False
        if fd.kind == "CXXDestructorDecl":
            return False
        if fd.record in self.internal:
            return False
        if fd.record and fd.access not in (None, "public"):
            return False
        # 바깥 클래스의 private/protected 영역에 선언된 중첩 클래스는 공개 API가 아님
        rec = fd.record
        while rec:
            if self.idx.record_access.get(rec, "public") not in (None, "public"):
                return False
            rec = rec.rsplit("::", 1)[0] if rec.count("::") > 1 else None
        return True

    def _executed(self, m: str) -> bool:
        c = self.cov.get(m)
        return bool(c and c.count > 0)

    def classify(self, m: str) -> ApiResult:
        fd = self.idx.funcs[m]
        cls = fd.record[len(self.ns) + 2:] if fd.record and fd.record.startswith(self.ns + "::") else fd.record
        res = ApiResult(api=self.pretty(m), mangled=m, cls=cls, sig=fd.sig,
                        decl_line=fd.line, category="")
        c = self.cov.get(m)
        if c:
            regs = _code_regions(c)
            res.region_total = len(regs)
            res.region_hit = sum(1 for r in regs if r[4] > 0)
            res.missed_lines = sorted({r[0] for r in regs if r[4] == 0})
        if c and c.count > 0:
            res.stuck_branches = self._stuck(m)
            full = res.region_hit == res.region_total and not res.stuck_branches
            res.category = "FULL" if full else "PARTIAL"
            return res

        # 실행 안 됨: 호출 그래프를 거꾸로 올라가며 '실행된 함수 안의 막힌 지점'을 찾는다
        blocks: list[BlockPoint] = []
        dispatch_only = False
        roots: set[str] = set()
        seen = {m}
        q = deque([(m, [m])])
        while q:
            cur, chain = q.popleft()
            sites = self._call_sites_into(cur)
            if not sites and cur != m:
                roots.add(cur)
            for s in sites:
                if self._executed(s.caller):
                    if site_executed(self.cov[s.caller], s):
                        dispatch_only = True       # 지점은 실행됐는데 이 구현으로는 안 감(가상 함수/생성자)
                        continue
                    blocks.append(BlockPoint(
                        caller=self.pretty(s.caller), file=s.file, line=s.line,
                        source=self._src(s.file, s.line),
                        chain=[self.pretty(x) for x in [s.caller] + chain[::-1]],
                    ))
                elif s.caller not in seen and len(chain) < MAX_DEPTH:
                    seen.add(s.caller)
                    q.append((s.caller, chain + [s.caller]))

        if blocks:
            # 같은 줄 중복 제거, 가까운(체인이 짧은) 순으로
            uniq = {}
            for b in sorted(blocks, key=lambda b: len(b.chain)):
                uniq.setdefault((b.file, b.line), b)
            res.blocks = list(uniq.values())[:5]
            res.category = "BLOCKED"
            return res

        res.category = "NOT_CALLED"
        entry = sorted({self.pretty(x) for x in seen - {m}
                        if x in self.idx.funcs and self.is_public_api(self.idx.funcs[x])})
        res.entry_apis = entry[:6]
        if dispatch_only:
            res.note = "호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)"
        elif not self._call_sites_into(m):
            res.note = "라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함"
        else:
            res.note = "이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함"
        return res

    def _stuck(self, m: str) -> list[StuckBranch]:
        """함수 m 몸통 안에서 한 방향으로만 간 분기들과 그 원인."""
        c = self.cov.get(m)
        out, seen = [], set()
        for b in (c.branches if c else []):
            ls, cs, le, ce, t, f, fid = b[0], b[1], b[2], b[3], b[4], b[5], b[6]
            if (t > 0) == (f > 0):
                continue                       # 양쪽 다 갔거나(정상) 둘 다 0(상위 영역 미실행)
            path = c.filenames[fid]
            # 한 줄에 조건이 여러 개(a || b || c)일 수 있으므로 줄+열로 구분한다
            if (path, ls, cs) in seen:
                continue
            seen.add((path, ls, cs))
            sb = StuckBranch(path, ls, self._src(path, ls), "참" if t == 0 else "거짓", cs)
            sb.expr = self._expr(path, ls, cs, le, ce)
            sb.causes = self.causes.explain(m, path, ls, cs, sb.expr, sb.never)
            out.append(sb)
        return out

    def _nearest_public(self, f: str, public: set[str]) -> str | None:
        """실행된 호출 경로를 거꾸로 올라가 처음 만나는 실행된 공개 API."""
        seen, q = {f}, deque([(f, 0)])
        while q:
            cur, d = q.popleft()
            for s in self._call_sites_into(cur):
                if s.caller in seen or not self._executed(s.caller):
                    continue
                if s.caller in public:
                    return s.caller
                if d < MAX_DEPTH:
                    seen.add(s.caller)
                    q.append((s.caller, d + 1))
        return None

    def _attach_internal(self, results: list[ApiResult]) -> None:
        by_api = {r.mangled: r for r in results}
        public = set(by_api)
        for f, fd in self.idx.funcs.items():
            if f in public or not fd.file or fd.file in self.harness_files or not self._executed(f):
                continue
            stuck = self._stuck(f)
            if not stuck:
                continue
            owner = self._nearest_public(f, public)
            if owner is None:
                continue
            r = by_api[owner]
            name = self.pretty(f)
            for sb in stuck:
                sb.in_func = name
            r.stuck_branches += stuck
            if r.category == "FULL":
                r.category = "PARTIAL"

    def run(self) -> list[ApiResult]:
        apis = [m for m, fd in self.idx.funcs.items() if m and self.is_public_api(fd)]
        results = [self.classify(m) for m in apis]
        if self.internal_branches:
            self._attach_internal(results)
        results.sort(key=lambda r: (r.cls or "", r.decl_line or 0))
        return results


def results_to_json(results: list[ApiResult], meta: dict) -> dict:
    return {"meta": meta, "results": [asdict(r) for r in results],
            "harness_fixes": summarize_fixes(results),
            # 확장 분석(C 구조체 필드, 상태·콜백, 실행 중 관찰)에서 나온 후보. 검증이 덜 됐으므로 harness_fixes와 섞지 않는다
            "harness_fix_candidates": summarize_fixes(results, ext=True)}
