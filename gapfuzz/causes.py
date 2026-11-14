"""막힌 조건의 원인을 하네스 코드에서 찾는다 (차별점 A: 하네스가 고정한 인자 탐지).

흐름
  1. 한 방향으로만 간 분기(stuck branch)의 위치로 AST의 조건식을 찾는다.
  2. 조건식이 읽는 값의 출처를 거슬러 올라간다.
       - 함수 매개변수            → (그 함수, 매개변수 번호)
       - 필드 / 필드를 돌려주는 게터 → 그 필드를 쓰는 곳들
            · 생성자 초기화·대입에서 매개변수로 설정 → (그 함수, 매개변수 번호)
            · 매개변수 없이 내부에서 설정        → 라이브러리 내부 상태·입력 내용
  3. (함수, 매개변수 번호)마다 하네스의 호출 지점에서 넘긴 인자를 본다.
       - 기본값 / 상수 / 항상 같은 객체         → FIXED (하네스가 고정함 → 하네스를 고치면 열림)
       - 몇 개 값 중에서만 고름(cond ? A : B)    → NARROW (하네스가 값의 범위를 좁힘)
       - null 검사가 한 번도 null 쪽으로 안 감   → NARROW (하네스가 null을 넘긴 적 없음)
       - 하네스가 그 함수를 부르지 않음          → SETTER_NOT_CALLED
       - 공개 API인데 라이브러리 내부에서만 불리고, 내부 호출이 그 인자를 항상 같은 값으로 넘기거나
         인자가 라이브러리 객체(노드 등)라 하네스가 다른 상태의 객체를 넘길 수 있음 → DIRECT_CALL
       - 조건이 this의 실제 타입(this->ToDocument() 등)이고 공개 API → DIRECT_CALL (그 타입 객체에서 부르기)
       - 퍼저 입력·변수로 바뀜                  → VARIES (인자는 바뀌지만 조건을 만족하는 값이 안 나옴)
     매개변수 출처가 없으면 INTERNAL (라이브러리 내부 상태나 입력 내용으로 정해짐)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .ast_index import AstIndex, CallSite, Cond

VERDICT_ORDER = ["FIXED", "SETTER_NOT_CALLED", "NARROW", "DIRECT_CALL", "CALLBACK", "STATE", "VARIES", "STATE_ORDER",
                 "ALLOC_FAIL", "ASSERT", "INTERNAL", "UNKNOWN"]
FIX_VERDICTS = ("FIXED", "SETTER_NOT_CALLED", "NARROW", "DIRECT_CALL", "CALLBACK", "STATE")
# 확장 분석(Cause.ext가 채워진 것)은 검증이 덜 된 판정이라 '고칠 곳'이 아니라 '고칠 곳 후보'로 따로 모은다.
#   c_field  : C 구조체 필드를 거쳐 추적한 원인        state : 다른 공개 API가 바꾸는 상태(호출 순서·조합)
#   callback : 등록되지 않은 콜백(함수 포인터 필드)     runtime : 실행 중 관찰한 인자 값(argtrace)    env : 어서션 등 빌드·환경
VERDICT_KO = {
    "FIXED": "하네스가 인자를 고정",
    "SETTER_NOT_CALLED": "값을 정하는 API를 하네스가 안 부름",
    "NARROW": "하네스가 값의 범위를 좁힘",
    "DIRECT_CALL": "라이브러리만 부르는 공개 API를 하네스가 직접 안 부름",
    "CALLBACK": "콜백(함수 포인터)을 하네스가 등록하지 않음",
    "STATE": "조건이 읽는 상태를 바꾸는 공개 API를 하네스가 안 부름",
    "STATE_ORDER": "다른 API가 바꾸는 상태에 달림 (호출 순서·조합을 바꿔야 함)",
    "ASSERT": "어서션 (실패 쪽은 버그가 있어야 열림, 하네스로 열 대상 아님)",
    "VARIES": "인자는 바뀌지만 조건을 만족하는 값이 안 나옴",
    "ALLOC_FAIL": "메모리 할당 실패·크기 넘침을 처리하는 분기 (하네스로는 열 수 없음)",
    "INTERNAL": "라이브러리 내부 상태·입력 내용으로 정해짐",
    "UNKNOWN": "출처를 추적하지 못함",
}
ARG_KO = {"default": "기본값", "literal": "상수", "same_object": "항상 같은 객체", "choice": "몇 개 값 중 선택",
          "fuzzer": "퍼저 입력", "variable": "변수"}
FIXED_KINDS = {"default", "literal", "same_object"}
NARROW_KINDS = FIXED_KINDS | {"choice"}


def null_side(expr: str, names: set[str]) -> str | None:
    """조건식이 이름 하나에 대한 null 검사이면, null일 때의 분기 방향("참"/"거짓")을 돌려준다."""
    e = expr.strip()
    while e.startswith("(") and e.endswith(")"):
        e = e[1:-1].strip()
    ident = r"(?:this->)?([A-Za-z_]\w*)"
    m = re.fullmatch(ident, e)
    if m and m.group(1) in names:
        return "거짓"                           # if (p) — null이면 거짓
    m = re.fullmatch(r"!\s*" + ident, e)
    if m and m.group(1) in names:
        return "참"                             # if (!p) — null이면 참
    m = re.fullmatch(ident + r"\s*(==|!=)\s*(?:0|nullptr|NULL)", e)
    if m and m.group(1) in names:
        return "참" if m.group(2) == "==" else "거짓"
    m = re.fullmatch(r"(?:0|nullptr|NULL)\s*(==|!=)\s*" + ident, e)
    if m and m.group(2) in names:
        return "참" if m.group(1) == "==" else "거짓"
    return None


@dataclass
class HarnessArg:
    file: str
    line: int
    kind: str              # default | literal | same_object | fuzzer | variable
    value: str | None
    source: str
    seen: dict | None = None   # 실행 중 관찰(argtrace): {"count": 호출 수, "values": [값 키…], "overflow": 값 종류가 한도를 넘음}


@dataclass
class Cause:
    verdict: str
    api: str | None = None          # 값을 정하는 함수(보기 좋은 이름)
    api_mangled: str | None = None
    param_index: int | None = None
    param_name: str | None = None
    via_field: str | None = None    # 필드를 거쳐 왔으면 그 필드 이름
    sites: list[HarnessArg] = field(default_factory=list)
    internal_writers: list[str] = field(default_factory=list)
    suggestion: str = ""
    param_type: str = ""
    narrow_kind: str = ""           # NARROW일 때: choice(몇 개 값 중 선택) | never_null(null을 넘긴 적 없음)
    chain: list[str] = field(default_factory=list)   # 라이브러리 내부 호출을 거쳐 왔으면 그 경로 (하네스 쪽 → 조건 쪽)
    ext: str = ""                   # 확장 분석에서 나온 판정이면 그 종류 (c_field | state | callback | runtime | env). 비어 있으면 기존 분석
    evidence: str = ""              # 실행 중 관찰 등 판정을 뒷받침하는 근거


class CauseFinder:
    def __init__(self, idx: AstIndex, harness_files: set[str], pretty, src_line, is_public_api,
                 executed=None, virtual_bases=None, runtime: dict | None = None, public_headers: set[str] | None = None):
        self.runtime = runtime or {}                 # (하네스 줄, 열, 인자 번호) -> 실행 중 관찰 (argtrace)
        self.public_headers = public_headers or set()
        self._entry_cache: dict[str, set[str]] = {}
        self._reach_cache: dict[str, set[str]] = {}
        self.idx = idx
        self.harness_files = harness_files
        self.pretty = pretty
        self.src_line = src_line
        self.is_public_api = is_public_api
        self.executed = executed or (lambda m: False)
        self.virtual_bases = virtual_bases or {}     # 파생 메서드 -> 가상 호출로 이어지는 부모 메서드들
        self.calls_into: dict[str, list[CallSite]] = {}
        for cs in idx.calls:
            for m in cs.callees:
                self.calls_into.setdefault(m, []).append(cs)

    def _sites_into(self, api: str) -> list[CallSite]:
        """api로 이어지는 호출 지점: 직접 호출 + 부모 클래스 메서드를 통한 가상 호출."""
        out = list(self.calls_into.get(api, []))
        for base in self.virtual_bases.get(api, []):
            out += self.calls_into.get(base, [])
        return out

    def _is_copy(self, m: str) -> bool:
        """복사 생성자·대입 연산자: 같은 타입의 다른 객체에서 값을 복사할 뿐 독립된 출처가 아님."""
        fd = self.idx.funcs.get(m)
        if not fd or not fd.record:
            return False
        short = fd.record.split("::")[-1]
        if fd.name == "operator=":
            return True
        return fd.kind == "CXXConstructorDecl" and f"const {short} &" in fd.sig.replace("tinyxml2::", "")

    # ---------------------------------------------------------- 조건식 찾기
    def find_cond(self, func: str, file: str, line: int, col: int) -> Cond | None:
        conds = [c for c in self.idx.conds.get(func, []) if c.file == file]
        exact = [c for c in conds if (c.line, c.col) == (line, col)]
        pool = exact or [c for c in conds if (c.line, c.col) <= (line, col) <= (c.end_line, c.end_col)]
        if not pool:
            return None
        # 같은 시작 위치면 범위가 가장 작은 것(&&의 피연산자)이 실제 분기
        return min(pool, key=lambda c: (c.end_line - c.line, c.end_col - c.col))

    # ---------------------------------------------------------- 출처 추적
    def _origins(self, func: str, cond: Cond):
        """(함수, 매개변수 번호, 경유 필드) 목록과 내부 설정 함수 목록."""
        origins: list[tuple] = [(func, p, None, None) for p in sorted(cond.params)]
        internal: dict[str, list[str]] = {}
        fields = set(cond.fields)
        for callee in cond.calls:
            if callee in self.idx.getters:
                fields.add(self.idx.getters[callee])
        for fk in sorted(fields):
            short = fk.split("::")[-1]
            for w in self.idx.field_writes.get(fk, []):
                if w.file in self.harness_files:
                    continue                         # 하네스가 공개 구조체 필드에 직접 쓴 것 (콜백 판정에서 따로 봄)
                if w.params:
                    origins += [(w.writer, p, short, fk) for p in sorted(w.params)]
                else:
                    internal.setdefault(short, []).append(w.writer)
        return origins, internal

    def _cond_fields(self, cond: Cond) -> list[str]:
        fields = set(cond.fields)
        for callee in cond.calls:
            if callee in self.idx.getters:
                fields.add(self.idx.getters[callee])
        return sorted(fields)

    def _state_fields(self, cond: Cond) -> list[str]:
        """상태·콜백 분석에 쓸 필드. 조건이 `_list.Size()`처럼 필드 객체의 게터를 부르면, 게터가 읽는 컨테이너 내부 필드
        (모든 컨테이너 인스턴스가 공유하는 이름)가 아니라 조건이 직접 가리키는 필드(`_list`)를 본다."""
        direct = set(cond.fields)
        own = {f.rsplit("::", 1)[0] for f in direct}
        via_getter = {self.idx.getters[c] for c in cond.calls if c in self.idx.getters}
        return sorted(direct | {f for f in via_getter if not direct or f.rsplit("::", 1)[0] in own})

    def _is_c_field(self, fk: str | None) -> bool:
        return bool(fk) and fk.rsplit("::", 1)[0] in self.idx.c_records

    def _ptype(self, func: str, q: int) -> str:
        fd = self.idx.funcs.get(func)
        return fd.param_types[q] if fd and q < len(fd.param_types) else ""

    def _polymorphic(self, ptype: str) -> bool:
        """매개변수 타입이 가상 함수를 가진 클래스(다른 구현 객체를 넘기면 동작이 바뀜)인가."""
        base = ptype.replace("const", "").replace("*", "").replace("&", "").strip().split("::")[-1]
        if not base:
            return False
        return any(fd.virtual and fd.record and fd.record.split("::")[-1] == base for fd in self.idx.funcs.values())

    def _harness_args(self, api: str, p: int) -> list[HarnessArg]:
        out = []
        for cs in self._sites_into(api):
            if cs.file not in self.harness_files:
                continue
            if cs.via_ctor and len(cs.callees) > 1:
                continue                         # 어느 생성자인지 확정 못 하면 인자 위치를 믿을 수 없음
            if p >= len(cs.args):
                continue
            a = cs.args[p]
            out.append(HarnessArg(cs.file, cs.line, a.kind, a.value, self.src_line(cs.file, cs.line),
                                  self.runtime.get((cs.line, cs.col, p))))
        return out

    ALLOCATORS = {"malloc", "calloc", "realloc", "strdup", "strndup", "aligned_alloc", "posix_memalign"}

    def _is_allocator(self, f: str) -> bool:
        """malloc 등 표준 할당 함수이거나, 라이브러리의 할당 래퍼(yaml_malloc, expat_realloc처럼 이름이 …alloc으로 끝남)."""
        name = self.idx.funcs[f].name if f in self.idx.funcs else f
        return name in self.ALLOCATORS or bool(re.search(r"_(malloc|calloc|realloc)$", name))

    def _reaches_alloc(self, funcs: set[str], depth: int = 6) -> bool:
        """이 함수들이 (라이브러리 안에서 최대 depth단계 호출을 따라) 메모리 할당 함수를 부르는가."""
        if not hasattr(self, "_callgraph"):
            g: dict[str, set[str]] = {}
            for cs in self.idx.calls:
                g.setdefault(cs.caller, set()).update(cs.callees)
            self._callgraph = g
        seen, frontier = set(), set(funcs)
        for _ in range(depth + 1):
            if any(self._is_allocator(f) for f in frontier):
                return True
            seen |= frontier
            frontier = {c for f in frontier for c in self._callgraph.get(f, ())} - seen
            if not frontier:
                break
        return False

    def alloc_failure(self, func: str, file: str, line: int, col: int, expr: str, never: str) -> bool:
        """할당 실패·크기 넘침을 처리하는 방어 분기인가: 실패 쪽(보통 '참')이 한 번도 안 갔고,
        - 조건이 SIZE_MAX·INT_MAX 같은 상한과 비교하는 넘침 검사이거나
        - 조건이 부르는(또는 읽는 지역 변수를 만든) 함수가 결국 malloc·realloc 등을 부르고, 식이 실패 검사 모양(!x, == NULL, < 0)일 때."""
        if never != "참" or not expr:
            return False
        if re.search(r"\b(SIZE_MAX|INT_MAX|UINT_MAX|LONG_MAX|SSIZE_MAX|PTRDIFF_MAX)\b", expr):
            return True
        cond = self.find_cond(func, file, line, col)
        if cond is None:
            return False
        e = expr.replace(" ", "")
        failure_shape = e.startswith("!") or "==NULL" in e or "==0" in e or "<0" in e or e.endswith("==NULL)")
        if not failure_shape:
            return False
        # 할당 래퍼 함수 안의 실패 검사(expat_malloc 안의 `mallocedPtr == NULL` 등: 함수 포인터로 할당해 호출이 안 보임)
        if self._is_allocator(func):
            return True
        return bool(cond.calls) and self._reaches_alloc(set(cond.calls))

    def explain(self, func: str, file: str, line: int, col: int, expr: str = "", never: str = "") -> list[Cause]:
        if self.alloc_failure(func, file, line, col, expr, never):
            return [Cause("ALLOC_FAIL", suggestion="메모리 할당 실패나 크기 넘침을 처리하는 분기입니다 → 하네스 인자로는 열 수 없고, "
                                                   "할당 실패를 주입하는 별도 시험이 필요합니다")]
        causes = self._explain(func, file, line, col, expr, never)
        if ASSERT_LINE.search(self.src_line(file, line) or ""):
            # 기존 판정은 그대로 두고 덧붙인다 (정렬 순서상 INTERNAL·UNKNOWN보다 앞, 고칠 곳 판정보다 뒤)
            causes = [c for c in causes if c.verdict != "UNKNOWN"] + [
                Cause("ASSERT", ext="env", suggestion="어서션 안의 검사입니다. 실패 쪽은 라이브러리에 버그가 있어야 열리므로 하네스로 열 대상이 아닙니다 "
                                                     "(어서션을 끈 빌드에서는 이 검사 자체가 없어집니다)")]
            causes.sort(key=lambda c: VERDICT_ORDER.index(c.verdict))
        if expr and causes and all(c.verdict in ("INTERNAL", "UNKNOWN") for c in causes):
            rc = self.receiver_type_cause(func, expr, never)
            if rc:
                causes = [rc] + causes
        # null 검사인데 null 쪽으로 한 번도 안 갔고, 그 포인터를 하네스가 넘긴다면 → 하네스가 null을 넘긴 적 없음
        if expr and never:
            for c in causes:
                if c.verdict != "VARIES" or "*" not in c.param_type:
                    continue
                names = {n for n in (c.param_name, c.via_field) if n}
                if null_side(expr, names) == never:
                    c.verdict = "NARROW"
                    c.narrow_kind = "never_null"
                    lines = ", ".join(f"{s.line}행" for s in c.sites)
                    c.suggestion = (f"`{c.api}`의 {c.param_index + 1}번째 인자 `{c.param_name}`에 하네스가 null을 넘긴 적이 없습니다"
                                    f"({lines}){' (필드 `' + c.via_field + '`를 거쳐 조건에 쓰임)' if c.via_field else ''}"
                                    f" → nullptr도 넘겨 보세요")
            causes.sort(key=lambda c: VERDICT_ORDER.index(c.verdict))
        return causes

    def _explain(self, func: str, file: str, line: int, col: int, expr: str = "", never: str = "") -> list[Cause]:
        cond = self.find_cond(func, file, line, col)
        if cond is None:
            return [Cause("UNKNOWN", suggestion="이 분기의 조건식을 AST에서 찾지 못했습니다(매크로로 만든 조건일 수 있음)")]
        origins, internal = self._origins(func, cond)
        direct: list[Cause] = []
        by_field: dict[str, list[Cause]] = {}
        seen = set()
        for api, p, via, fk in origins:
            if (api, p) in seen or (via and self._is_copy(api)):
                continue
            seen.add((api, p))
            c = self._judge(api, p, via)
            if self._is_c_field(fk) and not c.ext:
                c.ext = "c_field"
            if (via is None and api == func and p in cond.member_only and c.verdict in ("FIXED", "NARROW")
                    and c.sites and all(s.kind == "same_object" for s in c.sites)
                    and not self._polymorphic(c.param_type)):
                # 조건은 객체 안의 필드만 읽는다: 하네스가 '같은 객체'를 넘기는 건 원인이 아니고, 필드는 라이브러리가 채움
                c.verdict = "INTERNAL"
                c.suggestion = (f"`{c.api}`의 `{c.param_name}`는 라이브러리가 상태를 쌓는 객체이고, 조건은 그 안의 필드를 읽습니다"
                                f" → 하네스가 다른 객체를 넘겨도 열리지 않습니다")
            (by_field.setdefault(via, []) if via else direct).append(c)

        causes: list[Cause] = list(direct)
        for via, group in by_field.items():
            causes += self._merge_field(group)
        for short, writers in internal.items():
            names = sorted({self.pretty(w) for w in writers})
            causes.append(Cause("INTERNAL", via_field=short, internal_writers=names,
                                suggestion=f"`{short}`는 {', '.join(f'`{n}`' for n in names[:3])}에서 내부적으로 정해집니다 "
                                           f"(입력 내용이나 이전 상태에 따라 달라짐)"))
        if not causes:
            causes.append(Cause("INTERNAL", suggestion="조건이 매개변수·필드가 아니라 지역 변수나 입력 데이터에 달려 있습니다 "
                                                       "(입력 내용·딕셔너리로 열어야 함)"))
        # ---- 확장 분석: 콜백 미등록, 다른 공개 API가 바꾸는 상태 ----
        for fk in self._state_fields(cond):
            cb = self.callback_cause(fk, expr, never)
            if cb:
                short = fk.split("::")[-1]
                causes = [c for c in causes if not (c.via_field == short and c.verdict in ("SETTER_NOT_CALLED", "INTERNAL"))]
                causes.append(cb)
                continue
            st = self.state_cause(func, fk)
            if st:
                causes.append(st)
        causes.sort(key=lambda c: VERDICT_ORDER.index(c.verdict))
        return causes

    # ---------------------------------------------------------- 확장: 상태·콜백
    MAX_ENTRY_DEPTH = 6

    def _entries(self, f: str) -> set[str]:
        """f가 실행되게 만드는 공개 API들: f가 공개 API면 f 자신, 아니면 f를 (거슬러 올라가) 부르는 가장 가까운 공개 API."""
        if f in self._entry_cache:
            return self._entry_cache[f]
        out, seen, frontier = set(), {f}, {f}
        for _ in range(self.MAX_ENTRY_DEPTH + 1):
            nxt = set()
            for cur in frontier:
                fd = self.idx.funcs.get(cur)
                if fd and self.is_public_api(fd):
                    out.add(cur)
                    continue
                for cs in self._sites_into(cur):
                    if cs.file not in self.harness_files and cs.caller not in seen:
                        seen.add(cs.caller)
                        nxt.add(cs.caller)
            frontier = nxt
            if not frontier:
                break
        self._entry_cache[f] = out
        return out

    def _reach(self, f: str) -> set[str]:
        """f에서 호출 그래프를 따라 닿는 함수들."""
        if f in self._reach_cache:
            return self._reach_cache[f]
        if not hasattr(self, "_callgraph"):
            g: dict[str, set[str]] = {}
            for cs in self.idx.calls:
                g.setdefault(cs.caller, set()).update(cs.callees)
            self._callgraph = g
        seen, stack = {f}, [f]
        while stack:
            for c in self._callgraph.get(stack.pop(), ()):
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
        self._reach_cache[f] = seen
        return seen

    def _file_io(self, api: str) -> bool:
        fd = self.idx.funcs.get(api)
        return bool(fd) and (bool(re.search(r"file|fopen|(^|_)fd(_|$)", fd.name, re.I))
                             or any(re.search(r"\bFILE\b", t or "") for t in fd.param_types))

    def _harness_calls(self, api: str) -> bool:
        return any(cs.file in self.harness_files for cs in self._sites_into(api))

    def state_cause(self, func: str, fk: str) -> Cause | None:
        """조건이 읽는 필드를, 이 조건을 실행하는 API와는 '다른' 공개 API가 바꾸는가.
        같은 API 호출 안에서만 바뀌는 필드(파서 상태 등)는 입력에 달린 것이므로 제외한다.
        - 그런 API를 하네스가 한 번도 부르지 않음       → STATE (호출을 추가하면 열릴 수 있음)
        - 하네스가 부르긴 하지만 조건이 한쪽으로만 감   → STATE_ORDER (호출 순서·조합 문제, 조언만)"""
        short = fk.split("::")[-1]
        readers = self._entries(func)
        if not readers:
            return None
        inside = set().union(*(self._reach(r) for r in readers))
        ok = lambda e: (e not in readers and e not in inside and not self._is_copy(e) and not self._file_io(e)
                        and self.idx.funcs[e].kind not in ("CXXConstructorDecl", "CXXDestructorDecl"))
        never_ran: set[str] = set()                  # 한 번도 실행되지 않은 '상태를 바꾸는 코드'로 이어지는 공개 API
        ran: set[str] = set()                        # 이미 실행되는 '상태를 바꾸는 코드'로 이어지는 공개 API
        for w in self.idx.field_writes.get(fk, []):
            if w.file in self.harness_files or w.kind == "init":
                continue                             # 생성자 초기화는 처음 상태일 뿐
            if w.kind == "mutate" and self.idx.field_types.get(fk, "").rstrip().endswith("*"):
                continue                             # 포인터 필드로 메서드를 부른 것은 가리키는 객체를 바꿀 뿐, 포인터 값은 그대로
            fd = self.idx.funcs.get(w.writer)
            if fd and fd.kind in ("CXXConstructorDecl", "CXXDestructorDecl"):
                continue
            es = {e for e in self._entries(w.writer) if ok(e)}
            if self.executed(w.writer):
                ran |= es
            else:
                never_ran |= {e for e in es if not self.executed(e)}
        if not never_ran and not ran:
            return None
        rd = ", ".join(f"`{self.pretty(r).split('(')[0]}`" for r in sorted(readers)[:2])
        uncalled = sorted(never_ran)
        others = ran
        if uncalled:
            names = [self.pretty(e) for e in uncalled]
            c = Cause("STATE", names[0], uncalled[0], via_field=short, internal_writers=names[:6], ext="state")
            c.suggestion = (f"조건이 읽는 상태 `{short}`를 바꾸는 공개 API {', '.join(f'`{n.split(chr(40))[0]}`' for n in names[:4])}"
                            f"{' 등 ' + str(len(names)) + '개' if len(names) > 4 else ''}를 하네스가 부르지 않습니다 "
                            f"→ {rd}를 부르기 전에 이 호출을 추가해 보세요")
            return c
        direct = sorted(e for e in others if self._harness_calls(e))
        if direct:                                   # 조건이 실행됐으니 읽는 쪽은 (직접이든 다른 API를 거쳐서든) 이미 불리고 있다
            names = [self.pretty(e) for e in direct]
            c = Cause("STATE_ORDER", names[0], direct[0], via_field=short, internal_writers=names[:6], ext="state")
            c.suggestion = (f"조건이 읽는 상태 `{short}`는 하네스가 부르는 {', '.join(f'`{n.split(chr(40))[0]}`' for n in names[:4])}"
                            f"{' 등' if len(names) > 4 else ''}가 바꿉니다. {rd}를 부르는 시점에 이 상태가 조건과 맞은 적이 없습니다 "
                            f"→ 호출 순서·조합을 바꿔 보세요 (예: 이 API를 부른 직후에, 또는 부르지 않은 채로 {rd} 호출)")
            return c
        return None

    def callback_cause(self, fk: str, expr: str, never: str) -> Cause | None:
        """조건이 함수 포인터 필드의 null 검사이고 '등록된 쪽'으로 한 번도 안 갔으면: 콜백을 등록한 적이 없음."""
        short = fk.split("::")[-1]
        if "(*)" not in self.idx.field_types.get(fk, "") or not expr or not never:
            return None
        e = expr.replace(" ", "")
        if not re.search(r"\b" + re.escape(short) + r"\b", e):
            return None
        neg = e.lstrip("(").startswith("!") or bool(re.search(
            re.escape(short) + r"\)?==(\(\w+\))?(0|NULL|nullptr|Z_NULL)\b|\b(0|NULL|nullptr|Z_NULL)==\(?[\w>.\-]*" + re.escape(short), e))
        if never != ("거짓" if neg else "참"):
            return None
        writes = self.idx.field_writes.get(fk, [])
        if any(w.file in self.harness_files for w in writes):
            return None                              # 하네스가 직접 설정하고 있음
        setters = sorted({e2 for w in writes if w.params for e2 in self._entries(w.writer) if not self.executed(e2)})
        rec = fk.rsplit("::", 1)[0]
        direct = self.idx.record_file.get(rec) in self.public_headers
        if not setters and not direct:
            return None
        names = [self.pretty(x) for x in setters]
        c = Cause("CALLBACK", names[0] if names else None, setters[0] if setters else None, via_field=short,
                  internal_writers=names[:6], ext="callback")
        how = []
        if names:
            how.append(", ".join(f"`{n.split('(')[0]}`" for n in names[:3]) + "로 콜백을 등록")
        if direct:
            how.append(f"공개 구조체 `{rec.split('::')[-1]}`의 필드 `{short}`에 함수를 직접 넣기")
        c.suggestion = (f"콜백 `{short}`가 한 번도 등록되지 않아 콜백을 부르는 쪽 코드가 실행되지 않습니다 → " + " 또는 ".join(how)
                        + " (콜백 안에서도 라이브러리 API를 부르면 더 많은 코드가 열립니다)")
        return c

    MAX_UP = 8

    def _upstream(self, api: str, p: int, depth: int = 0, seen=None) -> list[tuple[str, int, list[str]]]:
        """하네스가 직접 넘기지 않는 (함수, 매개변수)를, 실행된 라이브러리 내부 호출 지점을 따라 거슬러 올라가
        하네스가 값을 넘기는 (함수, 매개변수)까지 찾는다. 반환: [(그 함수, 매개변수 번호, 거친 함수들)]."""
        seen = seen if seen is not None else {(api, p)}
        out = []
        for cs in self._sites_into(api):
            if cs.file in self.harness_files or not self.executed(cs.caller) or p >= len(cs.args):
                continue
            for q in sorted(cs.args[p].params):
                if q in cs.args[p].member_only and not self._polymorphic(self._ptype(cs.caller, q)):
                    continue                     # 값이 객체 안 필드(라이브러리가 채움)에서 옴: 하네스가 넘긴 객체 탓이 아님
                key = (cs.caller, q)
                if key in seen or depth >= self.MAX_UP:
                    continue
                seen.add(key)
                if self._harness_args(cs.caller, q):
                    out.append((cs.caller, q, [api]))
                else:
                    out += [(f, i, ch + [api]) for f, i, ch in self._upstream(cs.caller, q, depth + 1, seen)]
        return out

    def _judge(self, api: str, p: int, via: str | None, _up: bool = True) -> Cause:
        fd = self.idx.funcs.get(api)
        pname = fd.params[p] if fd and p < len(fd.params) else ""
        ptype = fd.param_types[p] if fd and p < len(fd.param_types) else ""
        if not pname:   # 이름 없는 매개변수는 타입으로 보여 준다
            pname = ptype.replace("tinyxml2::", "") or f"#{p + 1}"
        sites = self._harness_args(api, p)
        c = Cause("", self.pretty(api), api, p, pname, via, sites)
        c.param_type = ptype
        distinct = {(s.kind, s.value) for s in sites}
        if sites and all(s.kind in FIXED_KINDS for s in sites) and len(distinct) == 1:
            c.verdict = "FIXED"
        elif sites and all(s.kind in FIXED_KINDS for s in sites):
            c.verdict = "NARROW"                  # 호출 지점마다 다른 상수 → 정해진 몇 개 값 중에서만 고름
            c.narrow_kind = "choice"
        elif sites and all(s.kind in NARROW_KINDS for s in sites):
            c.verdict = "NARROW"                  # cond ? A : B 처럼 몇 개 값 중에서만 고름
            c.narrow_kind = "choice"
        elif sites:
            c.verdict = "VARIES"
            self._apply_runtime(c)
        elif self.executed(api) and _up and (ups := self._upstream(api, p)):
            # 라이브러리 내부 호출을 거쳐 하네스가 넘긴 인자에서 온 값: 가장 가까운 출처로 판정
            f, q, chain = min(ups, key=lambda u: len(u[2]))
            top = self._judge(f, q, via, _up=False)
            top.chain = [self.pretty(x) for x in chain]
            top.suggestion = self._suggest(top)
            return top
        elif self.executed(api) and self._direct_callable(api, p):
            # 공개 API인데 라이브러리만 부름: 라이브러리는 이 인자를 한 가지 방식으로만 넘기므로 하네스가 직접 불러야 열림
            c.verdict = "DIRECT_CALL"
            c.internal_writers = sorted({self.pretty(cs.caller) for cs in self._sites_into(api)
                                         if cs.file not in self.harness_files and self.executed(cs.caller)})[:4]
        elif self.executed(api):
            # 하네스가 직접 넘기진 않지만 라이브러리 내부 호출로 실행되고 있음
            c.verdict = "INTERNAL"
            callers = sorted({self.pretty(cs.caller) for cs in self._sites_into(api)
                              if cs.file not in self.harness_files and self.executed(cs.caller)})
            c.internal_writers = callers[:4]
        elif fd and self.is_public_api(fd):
            c.verdict = "SETTER_NOT_CALLED"
        else:
            c.verdict = "INTERNAL"
        if c.ext != "runtime":
            c.suggestion = self._suggest(c)
        return c

    MIN_RUNTIME_CALLS = 50

    def _apply_runtime(self, c: Cause) -> None:
        """코드로는 '변수'라 바뀌는 것처럼 보이지만 실행 중 관찰한 값이 한 가지뿐이면 고정으로 판정한다."""
        if not c.sites or not all(s.seen for s in c.sites):
            return
        total = sum(s.seen["count"] for s in c.sites)
        vals = sorted({v for s in c.sites for v in s.seen["values"]})
        over = any(s.seen.get("overflow") for s in c.sites)
        if total < self.MIN_RUNTIME_CALLS or not vals:
            return
        show = lambda v: {"p:null": "null", "p:nonnull": "null이 아닌 포인터"}.get(v, v.split(":", 1)[1] if ":" in v else v)
        lines = ", ".join(f"{s.line}행" for s in c.sites)
        nth = f"{c.param_index + 1}번째 인자 `{c.param_name}`"
        if over or all(v == "o" for v in vals):
            return
        c.evidence = f"실행 중 관찰: {total}번 호출에서 값 {len(vals)}가지 ({', '.join(show(v) for v in vals[:6])})"
        if len(vals) == 1 and vals[0] != "p:nonnull":
            c.verdict, c.ext = "FIXED", "runtime"
            c.suggestion = (f"`{c.api}`의 {nth}는 코드로는 변수지만, 실행 중 {total}번 호출에서 항상 `{show(vals[0])}`였습니다({lines})"
                            f" → 퍼저 입력에 따라 바뀌게 하세요")

    def _direct_callable(self, api: str, p: int) -> bool:
        """하네스가 이 공개 API를 직접 불러서 조건을 바꿀 수 있는가.
        - 하네스가 이 API를 한 번도 직접 부르지 않고 (어느 인자로도)
        - 라이브러리 내부 호출 지점이 이 인자를 모두 상수·기본값으로 넘기거나,
          인자가 라이브러리 객체 포인터·참조(노드 등)라서 하네스가 다른 상태의 객체를 넘길 수 있을 때.
        문자열·바이트 포인터처럼 입력 내용을 담는 인자는 입력으로 열어야 하므로 제외한다."""
        fd = self.idx.funcs.get(api)
        if not fd or not self.is_public_api(fd) or p >= len(fd.param_types):
            return False
        if any(cs.file in self.harness_files for cs in self._sites_into(api)):
            return False
        inner = [cs for cs in self._sites_into(api)
                 if cs.file not in self.harness_files and self.executed(cs.caller) and p < len(cs.args)]
        if not inner:
            return False
        if all(cs.args[p].kind in ("default", "literal") for cs in inner):
            return True                      # (같은 지역 변수 주소를 넘기는 출력 인자 &len 등은 제외)
        return self._is_record_ptr(fd.param_types[p])

    def _is_record_ptr(self, t: str) -> bool:
        """라이브러리 클래스(노드 등)를 가리키는 포인터·참조 타입인가 (문자열·바이트·정수 포인터는 아님)."""
        if "*" not in t and "&" not in t:
            return False
        base = re.sub(r"\b(const|struct|class)\b|[*&]", "", t).strip()
        return base in self.idx.records or any(r.endswith("::" + base) for r in self.idx.records)

    def _cls(self, short: str) -> str:
        """ToDocument → XMLDocument처럼, To 뒤의 이름으로 끝나는 실제 클래스 이름."""
        for r in self.idx.records:
            n = r.split("::")[-1]
            if n == short or n.endswith(short) and n[: -len(short)].isupper():
                return n
        return short

    def receiver_type_cause(self, func: str, expr: str, never: str) -> Cause | None:
        """조건이 this의 실제 타입 검사(this->ToDocument() 등)이고 공개 API이면: 그 타입 객체에서 부르면 열림."""
        m = re.fullmatch(r"\(?\s*!?\s*(?:this->)?To(\w+)\(\)\s*\)?", expr.strip())
        fd = self.idx.funcs.get(func)
        if not m or not fd or not self.is_public_api(fd):
            return None
        want = m.group(1)
        c = Cause("DIRECT_CALL", self.pretty(func), func)
        c.suggestion = (f"`{self.pretty(func)}`를 `{self._cls(want)}` 객체에서 부른 적이 없습니다(조건 `{expr}`가 한쪽으로만 감) "
                        f"→ 하네스가 `{self._cls(want)}` 객체에서 이 API를 불러 보세요")
        return c

    def _merge_field(self, group: list[Cause]) -> list[Cause]:
        """같은 필드를 정하는 출처가 여럿이면 필드 단위로 판정을 하나로 모은다."""
        has = {c.verdict for c in group}
        unused = [c for c in group if c.verdict == "SETTER_NOT_CALLED"]
        alt = ", ".join(f"`{c.api}`" for c in unused[:3])
        if "VARIES" in has:
            return [c for c in group if c.verdict == "VARIES"]        # 하네스가 이미 값을 바꾸고 있음
        if "FIXED" in has or "NARROW" in has:
            keep = [c for c in group if c.verdict in ("FIXED", "NARROW")]
            if alt:
                for c in keep:
                    c.suggestion += f" (또는 {alt}로도 이 값을 바꿀 수 있음)"
            return keep
        return sorted(group, key=lambda c: VERDICT_ORDER.index(c.verdict))[:4]

    def _suggest(self, c: Cause) -> str:
        nth = f"{c.param_index + 1}번째 인자 `{c.param_name}`"
        via = f" (필드 `{c.via_field}`를 거쳐 조건에 쓰임)" if c.via_field else ""
        if c.chain:
            via += " (라이브러리 내부 " + " → ".join(f"`{x.split('(')[0]}`" for x in c.chain) + "를 거쳐 조건에 쓰임)"
        if c.verdict == "FIXED":
            parts = []
            for s in c.sites:
                what = "기본값" if s.kind == "default" else (
                    f"항상 `{s.value}`" if s.kind == "literal" else f"항상 같은 객체 `{s.value}`")
                parts.append(f"{s.line}행에서 {what}")
            return f"`{c.api}`의 {nth}를 하네스가 고정합니다({', '.join(parts)}){via} → 퍼저 입력으로 바꾸세요"
        if c.verdict == "SETTER_NOT_CALLED":
            return f"하네스가 `{c.api}`를 부르지 않아 {nth} 값이 들어가지 않습니다{via} → 호출을 추가하세요"
        if c.verdict == "DIRECT_CALL":
            who = ", ".join(f"`{w.split('(')[0]}`" for w in c.internal_writers[:3])
            return (f"`{c.api}`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부({who})에서만 불립니다. "
                    f"내부 호출은 {nth}를 한 가지 방식으로만 넘기므로{via} → 하네스가 직접 불러 "
                    f"{'다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를' if self._is_record_ptr(c.param_type) else ('다른 값(null 포함)을' if '*' in c.param_type else '다른 값을')} 넘겨 보세요")
        if c.verdict == "NARROW":
            vals = []
            for s in c.sites:
                for v in (s.value or ("기본값" if s.kind == "default" else "")).split("|"):
                    if v and v not in vals:
                        vals.append(v)
            lines = ", ".join(f"{s.line}행" for s in c.sites)
            return (f"`{c.api}`의 {nth}를 하네스가 {', '.join(f'`{v}`' for v in vals)} 중에서만 고릅니다({lines}){via}"
                    f" → 나머지 값도 나오게 하세요")
        if c.verdict == "VARIES":
            lines = ", ".join(f"{s.line}행({ARG_KO[s.kind]})" for s in c.sites)
            if "*" in c.param_type or "&" in c.param_type:
                hint = ("포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 "
                        "→ null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요")
            else:
                hint = "→ 값의 범위·특수값(0, 음수, 큰 값, 빈 문자열 등)을 확인하세요"
            return f"`{c.api}`의 {nth}는 하네스에서 바뀌지만({lines}) 조건을 만족하는 값이 나오지 않았습니다{via}. {hint}"
        who = f" ({', '.join(f'`{w}`' for w in c.internal_writers[:3])}에서 호출)" if c.internal_writers else ""
        tail = " → 그 상위 API의 입력·상태를 바꿔야 합니다"
        fd = self.idx.funcs.get(c.api_mangled or "")
        if fd and self.is_public_api(fd) and not self._harness_args(c.api_mangled, c.param_index):
            tail += f". `{c.api.split('(')[0]}`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다"
        return f"`{c.api}`의 {nth}는 하네스가 아니라 라이브러리 내부 호출로 정해집니다{who}{via}{tail}"


ASSERT_LINE = re.compile(r"\b\w*assert\w*\s*\(", re.I)


def summarize_fixes(results, ext: bool = False) -> list[dict]:
    """여러 API에 흩어진 원인을 '하네스에서 고칠 곳' 단위로 묶는다.
    ext=False: 기존 분석의 판정만(harness_fixes). ext=True: 확장 분석의 판정만(harness_fix_candidates, 검증이 덜 된 후보).

    FIXED는 하네스의 같은 줄·같은 인자 위치가 원인이면 하나로 묶는다
    (가상 함수라 구현 클래스가 여러 개여도 하네스에서 고칠 곳은 한 군데).
    """
    groups: dict[tuple, dict] = {}
    for r in results:
        for b in r.stuck_branches:
            for c in b.causes:
                if c.verdict not in FIX_VERDICTS or bool(c.ext) != ext:
                    continue
                lines = tuple(sorted({s.line for s in c.sites}))
                key = (c.verdict, lines, c.param_index) if c.verdict in ("FIXED", "NARROW") \
                    else (c.verdict, c.api_mangled, c.param_index)
                if ext:
                    key += (c.via_field if c.verdict in ("STATE", "CALLBACK") else None,)
                g = groups.setdefault(key, {
                    "verdict": c.verdict, "apis": [], "param_index": c.param_index,
                    "param_name": c.param_name, "suggestions": [],
                    "harness_lines": list(lines), "harness_source": [s.source for s in c.sites[:2]],
                    "arg": [{"line": s.line, "kind": s.kind, "value": s.value} for s in c.sites],
                    "blocked": [],
                })
                if ext:
                    g.setdefault("ext", c.ext)
                    g.setdefault("evidence", c.evidence)
                if c.api not in g["apis"]:
                    g["apis"].append(c.api)
                    g["suggestions"].append(c.suggestion)
                g["blocked"].append({"api": r.api, "line": b.line, "col": b.col, "expr": b.expr,
                                     "never": b.never, "source": b.source})
    out = list(groups.values())
    for g in out:
        uniq = {(x["api"], x["line"], x["col"], x["never"]): x for x in g["blocked"]}
        g["blocked"] = sorted(uniq.values(), key=lambda x: (x["line"], x["col"]))
        g["suggestion"] = g["suggestions"][0] if len(g["apis"]) == 1 else (
            g["suggestions"][0] + f" (같은 호출이 {len(g['apis'])}개 구현 클래스에 영향: "
            + ", ".join(f"`{a.split('(')[0]}`" for a in g["apis"]) + ")")
    out.sort(key=lambda g: (VERDICT_ORDER.index(g["verdict"]), -len(g["blocked"])))
    return out
