"""'호출 안 함' 공개 API를 Claude API로 하네스에 추가하고, gapfuzz가 그 결과를 검사한다 (모든 라이브러리 공용).

llmfix가 "이미 부르는 함수의 인자"를 고친다면, llmops는 "아예 부르지 않는 공개 API"의 호출을 하네스에 더한다.
라이브러리별 규칙이 없다. 코드는 Claude가 쓰고, 맞는지는 gapfuzz가 퍼징으로 확인한다.

흐름
  1. 우선순위(규칙, LLM 없음): 수정 전 커버리지와 호출 그래프로, '호출 안 함' API마다 "부르면 새로 실행될 수 있는 코드 영역 수"를 센다.
     서로 겹치는 API를 여러 개 고르지 않도록, 앞서 고른 API로 이미 닿는 코드는 빼고 다음 API를 고른다(탐욕 선택).
  2. Claude에게: 지금 하네스, 고른 API의 선언과 헤더 주석, 지킬 규칙 → 호출을 추가한 하네스 전체를 받는다.
  3. gapfuzz가 검사: 컴파일 → 짧은 퍼징(기본 60초 × 2회) → 고른 API가 실제로 실행됐나 → 원래 실행되던 API가 그대로 실행되나
     → 크래시가 나면 귀속(하네스 탓이면 탈락).
  4. 실패하면 이유를 같은 대화에 돌려주고 다시 받는다(기본 최대 3번).
  5. 통과하면 harnesses/<라이브러리>/<하네스>_ops.* 로 저장. 기록은 out/llm/<라이브러리>/<하네스>_ops/ 와 evaluation/artifacts/llm/ops/.

API 키는 환경 변수 ANTHROPIC_API_KEY에서만 읽는다(파일·로그에 남기지 않음). --mock 응답파일로 키 없이 흐름을 시험할 수 있다.
"""
from __future__ import annotations

import concurrent.futures as cf
import difflib
import json
import os
import re
import shutil
import statistics
import time
from collections import deque
from pathlib import Path

from .analyze import Analyzer, DEFAULT_INTERNAL_CLASSES, _code_regions, load_coverage
from .ast_index import build_index
from .llmfix import CRASH_NOTE, ROOT, _compile, _tgt, call_claude, extract_code, no_code_reason, numbered
from .triage import triage

EXECUTED = ("FULL", "PARTIAL")
FILE_IO = re.compile(r"\bFILE\b|gzFile|\bfd\b|filename|file_name|filepath|\bpath\b", re.I)
FILE_NAME = re.compile(r"file|fopen|fdopen|(^|_)fd(_|$)", re.I)

SYSTEM = """당신은 libFuzzer 퍼징 하네스를 넓히는 보안 엔지니어입니다.
커버리지 분석 도구 gapfuzz가 지금 하네스가 한 번도 부르지 않는 라이브러리 공개 API를 찾아 우선순위를 매겼습니다.
주어진 API들을 부르는 코드를 하네스에 추가하세요.

규칙
- 원래 하네스가 하던 호출은 그대로 둡니다(같은 입력이면 예전과 같은 라이브러리 코드가 계속 실행돼야 함). 추가만 합니다.
  LLVMFuzzerTestOneInput의 시그니처는 바꾸지 않습니다.
- 추가한 호출의 인자는 상수가 아니라 퍼저 입력에서 만듭니다. 원래 하네스가 쓰던 입력 바이트는 원래대로 쓰이게 두고,
  새 선택값은 입력 끝쪽 바이트에서 꺼내거나 같은 data/size를 다시 읽어 만듭니다.
- 라이브러리 헤더 주석에 적힌 사용 규칙을 지킵니다: 초기화 → 사용 → 해제 순서, null을 받지 않는 인자, 버퍼 크기 조건.
  주어진 API를 부르는 데 필요한 준비·정리 호출(예: Init/End, 객체 생성/해제)은 목록에 없어도 함께 넣습니다.
- 하네스가 스스로 잘못 써서 생기는 크래시를 만들지 않습니다: 반환값을 확인하고 실패하면 그 객체를 더 쓰지 않으며,
  할당한 것은 모두 해제하고, C++ 예외를 던질 수 있는 호출은 try/catch로 감쌉니다.
- 자원에 상한을 둡니다: 반복은 64회 이하, 출력 버퍼는 1MB 이하, 재귀·중첩 깊이 제한.
- 파일·네트워크·환경 변수·프로세스 전역 상태를 건드리지 않습니다. 그런 것이 꼭 필요한 API는 넣지 말고 이유를 적습니다.
- 안전하게 부를 방법이 없다고 판단한 API는 건너뛰고, 답 끝에 어떤 API를 왜 뺐는지 적습니다.
- 추가한 블록마다 `// [gapfuzz-ops] API 이름` 주석을 답니다. 설명 주석은 한국어로 씁니다.
- 답은 고친 하네스 파일 전체를 코드 블록 하나(```cpp 또는 ```c)로만 주고, 그 뒤에 무엇을 넣고 뺐는지 짧게 씁니다."""


SYSTEM_NEW = """당신은 libFuzzer 퍼징 하네스를 새로 쓰는 보안 엔지니어입니다.
이 라이브러리에는 OSS-Fuzz 하네스가 이미 여러 개 있습니다. 커버리지 분석 도구 gapfuzz가 그 하네스들의 커버리지를 모두 합쳐도
한 번도 불리지 않는 공개 API를 찾아 우선순위를 매겼습니다. 그 API들을 부르는 **새 하네스 파일 하나**를 처음부터 쓰세요.

규칙
- 기존 하네스를 고치지 않습니다. `LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)` 하나를 가진 독립된 파일을 씁니다.
  참고로 준 기존 하네스와 같은 언어(C 또는 C++)와 같은 include 방식을 씁니다.
- 기존 하네스들이 이미 하는 일(예: 입력 전체를 파싱만 하기)을 되풀이하는 것이 목적이 아닙니다. 주어진 API를 부르는 데 집중하되,
  그 API를 부르려면 필요한 준비·정리 호출(초기화, 객체 생성, 파싱, 해제)은 목록에 없어도 넣습니다.
- 호출의 인자는 상수가 아니라 퍼저 입력에서 만듭니다. 입력 앞쪽 몇 바이트를 선택값(옵션, 크기, 순서)으로 쓰고 나머지를 데이터로 씁니다.
  여러 API를 부를 때는 입력 바이트로 어떤 것을 어떤 순서로 부를지 고르게 해서, 호출 순서와 조합이 입력에 따라 달라지게 합니다.
- 라이브러리 헤더 주석에 적힌 사용 규칙을 지킵니다: 초기화 → 사용 → 해제 순서, null을 받지 않는 인자, 버퍼 크기 조건.
- 하네스가 스스로 잘못 써서 생기는 크래시를 만들지 않습니다: 반환값을 확인하고 실패하면 그 객체를 더 쓰지 않으며,
  할당한 것은 모두 해제하고, C++ 예외를 던질 수 있는 호출은 try/catch로 감쌉니다.
- 자원에 상한을 둡니다: 입력은 64KB까지만 쓰고, 반복은 64회 이하, 출력 버퍼는 1MB 이하, 재귀·중첩 깊이 제한.
- 파일·네트워크·환경 변수·프로세스 전역 상태를 건드리지 않습니다. 그런 것이 꼭 필요한 API는 넣지 말고 이유를 적습니다.
- 안전하게 부를 방법이 없다고 판단한 API는 건너뛰고, 답 끝에 어떤 API를 왜 뺐는지 적습니다.
- 호출 블록마다 `// [gapfuzz-ops] API 이름` 주석을 답니다. 설명 주석은 한국어로 씁니다.
- 답은 새 하네스 파일 전체를 코드 블록 하나(```cpp 또는 ```c)로만 주고, 그 뒤에 무엇을 넣고 뺐는지 짧게 씁니다."""


# ------------------------------------------------------------------ 우선순위
def make_analyzer(t: dict, harness: Path, coverage_json: Path) -> Analyzer:
    inc = [str(d) for d in t["incs"]] + [str(ROOT / "harnesses" / "include")]
    defs = [f for f in t.get("cflags", []) if f.startswith("-D")]
    idx = build_index([str(s) for s in t["srcs"]] + [str(harness)], inc, defs)
    internal = t["internal_classes"] if t.get("internal_classes") is not None else list(DEFAULT_INTERNAL_CLASSES)
    return Analyzer(idx, load_coverage(str(coverage_json)), [str(h) for h in t["headers"]], t["namespace"], internal,
                    harness_files=[str(harness)], internal_branches=bool(t.get("internal_branches")))


def _reach(an: Analyzer, fwd: dict, m: str) -> set[str]:
    """m을 부르면 새로 실행될 수 있는 함수들(m 포함): 호출 그래프를 따라가되 이미 실행된 함수에서 멈춘다."""
    seen, q = {m}, deque([m])
    while q:
        cur = q.popleft()
        for c in fwd.get(cur, ()):
            if c not in seen and c in an.idx.funcs and not an._executed(c):
                seen.add(c)
                q.append(c)
    return seen


def _skip_reason(an: Analyzer, r) -> str:
    fd = an.idx.funcs.get(r.mangled)
    if not r.region_total or r.mangled not in an.cov:
        return "구현이 빌드에 없음 (선언만 있거나 매크로·인라인)"
    if fd is None:
        return "선언을 찾지 못함"
    if fd.deleted or fd.pure:
        return "삭제됐거나 순수 가상 함수"
    if fd.name.startswith("operator") and fd.name not in ("operator[]", "operator()"):
        return ""                                   # 연산자는 Claude가 식으로 부를 수 있다
    if any(FILE_IO.search(x or "") for x in [*fd.param_types, fd.sig]) or FILE_NAME.search(fd.name):
        return "파일 입출력"
    return ""


def rank(an: Analyzer) -> list[dict]:
    """'호출 안 함' API를 '새로 실행될 수 있는 코드 영역 수'로 정렬. gain은 앞서 고른 API와 겹치지 않는 몫."""
    fwd: dict[str, set[str]] = {}
    for cs in an.idx.calls:
        for c in cs.callees:
            fwd.setdefault(cs.caller, set()).add(c)
            for base in an._virtual_alias.get(c, []):
                fwd[cs.caller].add(base)
    regs = lambda fs: sum(len(_code_regions(an.cov[f])) for f in fs if f in an.cov)
    rows = []
    for r in an.run():
        if r.category != "NOT_CALLED":
            continue
        reach = _reach(an, fwd, r.mangled)
        rows.append({"api": r.api, "mangled": r.mangled, "cls": r.cls, "sig": r.sig, "decl_line": r.decl_line,
                     "functions": len(reach), "regions": regs(reach), "skip": _skip_reason(an, r), "_reach": reach})
    todo = [x for x in rows if not x["skip"]]
    covered: set[str] = set()
    order = []
    while todo:
        best = max(todo, key=lambda x: (regs(x["_reach"] - covered), x["regions"], x["api"]))
        best["gain"] = regs(best["_reach"] - covered)
        covered |= best["_reach"]
        todo.remove(best)
        order.append(best)
    skipped = sorted((x for x in rows if x["skip"]), key=lambda x: (-x["regions"], x["api"]))
    for x in skipped:
        x["gain"] = 0
    out = order + skipped
    for i, x in enumerate(out, 1):
        x["rank"] = i
        del x["_reach"]
    return out


def choose(rows: list[dict], top: int, apis: list[str] | None = None) -> list[dict]:
    if apis:
        want = [a.strip() for a in apis if a.strip()]
        got = [x for x in rows if not x["skip"] and any(w == x["mangled"] or w in x["api"] for w in want)]
        if not got:
            raise SystemExit(f"[llmops] 이름이 맞는 '호출 안 함' API가 없습니다: {', '.join(want)}")
        return got
    return [x for x in rows if not x["skip"] and x["gain"] > 0][:top]


def declaration(t: dict, row: dict, max_comment: int = 30) -> str:
    """공개 헤더에서 선언과 그 위의 주석을 뽑는다(사용 규칙이 주석에 적혀 있는 라이브러리가 많다)."""
    name = re.sub(r"\(.*", "", row["api"]).split("::")[-1].strip()
    for h in t["headers"]:
        try:
            src = open(h, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        ln = row.get("decl_line")
        if not ln or ln > len(src) or name not in " ".join(src[max(0, ln - 2):ln + 2]):
            continue
        end = ln
        while end < len(src) and end - ln < 8 and ";" not in src[end - 1] and "{" not in src[end - 1]:
            end += 1
        nxt = end                                    # zlib처럼 설명 주석이 선언 '뒤'에 오는 헤더
        while nxt < len(src) and not src[nxt].strip():
            nxt += 1
        after = []
        if nxt < len(src) and src[nxt].lstrip().startswith("/*"):
            k = nxt
            while k < len(src) and len(after) < max_comment:
                after.append(src[k])
                if "*/" in src[k]:
                    break
                k += 1
        start = ln - 1                               # 선언 '앞'의 주석
        while start > 0 and ln - start < max_comment and (
                src[start - 1].lstrip().startswith(("//", "*", "/*")) or src[start - 1].rstrip().endswith("*/")):
            start -= 1
        return "\n".join(src[start:end] + after)
    return row["api"]


# ------------------------------------------------------------------ 요청·검사
def build_request(harness_src: str, harness_name: str, lib_name: str, t: dict, chosen: list[dict], counts: dict) -> str:
    parts = [f"라이브러리: {lib_name}", f"하네스 파일: {harness_name}",
             f"지금 하네스는 공개 API {counts['total']}개 중 {counts['not_called']}개를 한 번도 부르지 않습니다.", "",
             f"## 하네스에 추가할 API {len(chosen)}개 (새로 실행될 수 있는 코드가 많은 순서)", ""]
    for i, x in enumerate(chosen, 1):
        parts += [f"### {i}. `{x['api']}` — 새로 실행될 수 있는 코드 영역 {x['gain']}개", "```", declaration(t, x), "```", ""]
    parts += ["## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)", "```", numbered(harness_src), "```"]
    return "\n".join(parts)


def build_request_new(ref_src: str, ref_name: str, lib_name: str, t: dict, chosen: list[dict], counts: dict, harnesses: list[str]) -> str:
    """새 하네스를 쓰게 하는 요청문. 기존 하네스는 참고용으로만 보여 준다."""
    parts = [f"라이브러리: {lib_name}",
             f"OSS-Fuzz 하네스 {len(harnesses)}개({', '.join(harnesses)})의 커버리지를 모두 합쳐도, "
             f"공개 API {counts['total']}개 중 {counts['not_called']}개는 한 번도 불리지 않습니다.", "",
             f"## 새 하네스가 불러야 할 API {len(chosen)}개 (새로 실행될 수 있는 코드가 많은 순서)", ""]
    for i, x in enumerate(chosen, 1):
        parts += [f"### {i}. `{x['api']}` — 새로 실행될 수 있는 코드 영역 {x['gain']}개", "```", declaration(t, x), "```", ""]
    parts += [f"## 참고: 기존 하네스 {ref_name} (고치지 마세요. include와 작성 방식만 참고)", "```", ref_src, "```"]
    return "\n".join(parts)


def _cov_pct(d: Path) -> tuple[float, float] | None:
    try:
        tot = json.load(open(d / "coverage.json"))["data"][0]["totals"]
        return tot["lines"]["percent"], tot["branches"]["percent"]
    except (OSError, KeyError, IndexError, ValueError):
        return None


def check(tg, t: dict, name: str, src: Path, before: dict, chosen: list[dict], secs: int, trials: int,
          new_harness: bool = False) -> dict:
    out = ROOT / "out" / "targets" / t["name"] / name
    err = _compile(tg, t, src, out)
    if err:
        return {"ok": False, "stage": "compile", "detail": err}
    with cf.ThreadPoolExecutor(max_workers=min(2, trials)) as ex:
        list(ex.map(lambda r: tg.run_one(t, name, r, secs, 1000, 10, None), range(1, trials + 1)))
    afters, crashes, covs = [], [], []
    for r in range(1, trials + 1):
        d = out / f"r{r}"
        if (d / "gap" / "gap.json").exists():
            afters.append(json.load(open(d / "gap" / "gap.json")))
        c = _cov_pct(d)
        if c:
            covs.append(c)
        crashes += [str(d / f) for f in os.listdir(d) if f.split("-")[0] in ("crash", "leak", "timeout", "oom")]
    ran = {x["mangled"] for a in afters for x in a["results"] if x["category"] in EXECUTED}
    called = [x["api"] for x in chosen if x["mangled"] in ran]
    missing = [x["api"] for x in chosen if x["mangled"] not in ran]
    # 새 하네스는 기존 하네스를 대신하는 것이 아니라 옆에 추가되는 것이므로, '원래 실행되던 API가 사라졌나'는 보지 않는다
    was = [] if new_harness else [x for x in before["results"] if x["category"] in EXECUTED]
    lost = [x["api"] for x in was if x["mangled"] not in ran]
    res = {"stage": "fuzz", "called": len(called), "total": len(chosen), "missing": missing, "lost": lost,
           "not_called_after": min((sum(1 for x in a["results"] if x["category"] == "NOT_CALLED") for a in afters), default=None),
           "lines": round(statistics.median(c[0] for c in covs), 2) if covs else None,
           "branches": round(statistics.median(c[1] for c in covs), 2) if covs else None, "crashes": []}
    if crashes:
        tri = triage(str(out / "fuzz"), crashes[:5], [str(src)], [str(t["lib"])], [str(src.parent), str(ROOT / "harnesses")],
                     2, 10, root=str(ROOT))
        res["crashes"] = [{"cls": c.verdict.cls, "conf": c.verdict.confidence, "reason": c.verdict.reason,
                           "evidence": c.verdict.evidence[:8], "kind": c.kind} for c in tri]
    bad = res["crashes"]        # 검사 퍼징에서 크래시가 나면 귀속과 상관없이 채택하지 않는다 (llmfix.check와 같은 이유)
    res["regressed"] = len(lost) > max(1, len(was) // 10)      # 원래 실행되던 API가 눈에 띄게 사라짐: 원래 동작을 망가뜨린 것
    res["ok"] = bool(afters) and res["called"] > 0 and not bad and not res["regressed"]
    res["complete"] = res["ok"] and res["called"] == res["total"]
    return res


def feedback(res: dict) -> str:
    if res["stage"] == "compile":
        return "고친 하네스가 컴파일되지 않습니다. 오류:\n```\n" + res["detail"] + "\n```\n오류를 고친 하네스 전체를 다시 주세요."
    lines = [f"고친 하네스로 퍼징했더니 추가하려던 API {res['total']}개 중 {res['called']}개가 실행됐습니다."]
    if res["missing"]:
        lines += ["아직 한 번도 실행되지 않은 API (호출이 없거나, 앞의 조건 때문에 그 줄까지 가지 못함):"] + [f"- `{a}`" for a in res["missing"]]
    if res["regressed"]:
        lines += ["원래 하네스에서 실행되던 API가 실행되지 않게 됐습니다. 원래 호출이 예전과 같은 입력으로 계속 실행되게 고치세요:"] \
                 + [f"- `{a}`" for a in res["lost"][:15]]
    for c in res["crashes"]:
        lines += [f"크래시가 났고 gapfuzz 크래시 귀속은 '{c['cls']}'(확신 {c['conf']})로 판정했습니다: {c['reason']}"] + [f"  - {e}" for e in c["evidence"]]
    if res["crashes"]:
        lines.append(CRASH_NOTE)
    lines.append("이미 실행되는 호출은 유지하면서 위 문제를 고친 하네스 전체를 다시 주세요. 안전하게 부를 수 없는 API는 빼고 이유를 적어도 됩니다.")
    return "\n".join(lines)


# ------------------------------------------------------------------ 실행
def _before(tg, t: dict, target: str, harness: str, before_path: str | None, secs: int = 120) -> Path:
    bp = Path(before_path) if before_path else ROOT / "out" / "targets" / target / harness / "r1" / "gap" / "gap.json"
    if not bp.exists():
        if before_path:
            raise SystemExit(f"[llmops] 수정 전 분석이 없습니다: {bp}")
        print(f"[llmops] {target}/{harness}: 수정 전 분석이 없어 먼저 {secs}초 퍼징으로 진단합니다", flush=True)
        tg.build(t, harness)
        tg.run_one(t, harness, 1, secs, 1000, 10, None)
    return bp


def ranking(target: str, harness: str, before_path: str | None = None, union: bool = False):
    """union=True: OSS-Fuzz 하네스 전체의 커버리지를 합친 결과(tgt.py union)를 기준으로 삼는다.
    그러면 '호출 안 함'은 "어느 하네스도 부르지 않는 API"가 된다. 호출 지점은 대표 하네스(목록의 첫 번째)의 소스로 읽는다."""
    tg = _tgt()
    t = tg.load(target)
    if union:
        hs = tg.ossfuzz_harnesses(t)
        hp = tg.harness_path(t, hs[0])
        bp = Path(before_path) if before_path else ROOT / "out" / "targets" / target / "_union" / "r1" / "gap" / "gap.json"
        if not bp.exists():
            print(f"[llmops] {target}: 합친 커버리지가 없어 먼저 만듭니다 (python3 scripts/tgt.py union {target})", flush=True)
            tg.union(t)
        return tg, t, hp, bp, rank(make_analyzer(t, hp, bp.parent.parent / "coverage.json"))
    hp = tg.harness_path(t, harness)
    bp = _before(tg, t, target, harness, before_path)
    rows = rank(make_analyzer(t, hp, bp.parent.parent / "coverage.json"))
    return tg, t, hp, bp, rows


def ranking_md(target: str, harness: str, rows: list[dict], chosen: list[dict] | None = None) -> str:
    pick = {x["mangled"] for x in chosen or []}
    L = [f"# 호출 안 함 API 우선순위 — {target}/{harness}", "",
         f"'호출 안 함' API {len(rows)}개. 추가 가능 {sum(1 for x in rows if not x['skip'])}개, "
         f"제외 {sum(1 for x in rows if x['skip'])}개.", "",
         "'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.", "",
         "| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |", "|---:|---|---:|---:|---:|---|"]
    for x in rows:
        note = x["skip"] or ("이번에 추가" if x["mangled"] in pick else "")
        L.append(f"| {x['rank']} | `{x['api']}` | {x['functions']} | {x['regions']} | {x['gain']} | {note} |")
    return "\n".join(L) + "\n"


def run(target: str, harness: str, top: int, before_path: str | None, secs: int, trials: int, tries: int, model: str,
        mock: list[str] | None, apis: list[str] | None = None, save: str | None = None, union: bool = False) -> dict:
    """union=True: 기존 하네스를 고치지 않고, 어느 OSS-Fuzz 하네스도 부르지 않는 API를 부르는 새 하네스 파일을 만든다
    (기본 저장 이름 gapfuzz_ops). union=False: 하네스 하나에 호출을 끼워 넣는다(기본 저장 이름 <하네스>_ops)."""
    tg, t, hp, bp, rows = ranking(target, harness, before_path, union=union)
    if union:
        harness = "_union"
    before = json.load(open(bp))
    chosen = choose(rows, top, apis)
    if not chosen:
        raise SystemExit(f"[llmops] {target}/{harness}: 추가할 수 있는 '호출 안 함' API가 없습니다")
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not mock and not key:
        raise SystemExit("[llmops] ANTHROPIC_API_KEY 환경 변수가 없습니다 (키 없이 시험하려면 --mock 응답파일)")
    tag = "union_ops" if union else f"{harness}_ops"
    save = save or ("gapfuzz_ops" if union else tag)
    base = ROOT / t.get("harness_dir", f"harnesses/{t['name']}")
    rel_dir = Path("llm") / tag
    work = ROOT / "out" / "llm" / target / tag
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (base / rel_dir).mkdir(parents=True, exist_ok=True)
    (work / "ranking.md").write_text(ranking_md(target, harness, rows, chosen), encoding="utf-8")
    counts = {"total": len(before["results"]), "not_called": sum(1 for x in before["results"] if x["category"] == "NOT_CALLED")}
    base_cov = _cov_pct(bp.parent.parent)
    orig = hp.read_text(encoding="utf-8")
    if union:
        messages = [{"role": "user", "content": build_request_new(orig, hp.name, target, t, chosen, counts, tg.ossfuzz_harnesses(t))}]
    else:
        messages = [{"role": "user", "content": build_request(orig, hp.name, target, t, chosen, counts)}]
    (work / "request.md").write_text(messages[0]["content"], encoding="utf-8")
    print(f"[llmops] {target}/{harness}: {'어느 하네스도 안 부르는 API' if union else '호출 안 함'} {counts['not_called']}/{counts['total']}개 중 상위 {len(chosen)}개를 "
          f"{'부르는 새 하네스 요청' if union else '추가 요청'} "
          f"({', '.join(x['api'].split('(')[0] for x in chosen[:6])}{' …' if len(chosen) > 6 else ''})", flush=True)
    log, best = [], None
    for k in range(1, tries + 1):
        t0 = time.time()
        if mock:
            text, usage = Path(mock[min(k, len(mock)) - 1]).read_text(encoding="utf-8"), {}
            if "```" not in text:
                text = "```cpp\n" + text + "\n```"
        else:
            text, usage = call_claude(messages, model, key, system=SYSTEM_NEW if union else SYSTEM)
        (work / f"try{k}_response.md").write_text(text, encoding="utf-8")
        code = extract_code(text)
        entry = {"try": k, "llm_seconds": round(time.time() - t0, 1), "usage": usage}
        if not code:
            res = {"ok": False, "stage": "compile", "detail": no_code_reason(text, usage)}
        else:
            src = base / rel_dir / f"try{k}{hp.suffix}"
            src.write_text(code if code.endswith("\n") else code + "\n", encoding="utf-8")
            shutil.copy(src, work / src.name)
            res = check(tg, t, str(rel_dir / f"try{k}"), src, before, chosen, secs, trials, new_harness=union)
            entry["harness"] = str(src.relative_to(ROOT))
        entry.update(res)
        log.append(entry)
        print(f"[llmops] {target}/{harness} 시도 {k}: " + ("컴파일 실패" if res["stage"] == "compile" else
              f"실행된 API {res['called']}/{res['total']}, 사라진 API {len(res['lost'])}, 크래시 {[c['cls'] for c in res['crashes']]}"),
              flush=True)
        if res.get("ok") and (best is None or res["called"] > best["called"]):
            best = entry
        if res.get("complete"):
            break
        prev = log[-2] if len(log) > 1 else None
        if res.get("ok") and prev and prev.get("ok") and prev.get("called") == res.get("called"):
            break                                   # 두 번 연속 같은 결과: 남은 API는 이 방식으로 부르기 어려움
        if k < tries:
            fb = feedback(res)
            (work / f"try{k}_feedback.md").write_text(fb, encoding="utf-8")
            messages += [{"role": "assistant", "content": text}, {"role": "user", "content": fb}]
    saved = None
    mdl = model if not mock else "mock"
    if best:
        new = (ROOT / best["harness"]).read_text(encoding="utf-8")
        saved = base / f"{save}{hp.suffix}"
        if union:
            head = (f"// [gapfuzz-ops] 이 파일은 Claude({mdl})가 새로 쓴 하네스입니다. OSS-Fuzz 하네스 전체를 합쳐도 불리지 않던 API {best['called']}개를 부릅니다.\n"
                    f"// [gapfuzz-ops] gapfuzz가 검사해 통과했습니다 (python3 -m gapfuzz llmops {target} --union, 기록: evaluation/artifacts/llm/ops/{target}/_union/).\n")
        else:
            head = (f"// [gapfuzz-ops] 이 파일은 Claude({mdl})가 {hp.name}에 '호출 안 함' API {best['called']}개의 호출을 추가하고\n"
                    f"// [gapfuzz-ops] gapfuzz가 검사해 통과한 하네스입니다 (python3 -m gapfuzz llmops, 기록: evaluation/artifacts/llm/ops/{target}/{harness}/).\n")
        saved.write_text(head + new, encoding="utf-8")
    report = write_report(work, target, harness, chosen, counts, base_cov, "" if union else orig, log, best, mdl, saved)
    json.dump({"target": target, "harness": harness, "model": mdl, "chosen": [x["api"] for x in chosen],
               "before": {"not_called": counts["not_called"], "apis": counts["total"],
                          "lines": base_cov and round(base_cov[0], 2), "branches": base_cov and round(base_cov[1], 2)},
               "tries": log, "best": best and best["try"], "saved": saved and str(saved.relative_to(ROOT))},
              open(work / "log.json", "w"), ensure_ascii=False, indent=1)
    keep = ROOT / "evaluation" / "artifacts" / "llm" / "ops" / target / harness
    keep.mkdir(parents=True, exist_ok=True)
    for f in ("report.md", "ranking.md", "request.md", "best.diff", "log.json"):
        if (work / f).exists():
            shutil.copy(work / f, keep / f)
    print(f"[llmops] -> {report}" + (f"\n[llmops] 저장: {saved.relative_to(ROOT)} (사람이 읽고 쓰세요)" if saved else ""))
    return {"best": best, "log": log, "saved": saved}


def write_report(work: Path, target: str, harness: str, chosen: list[dict], counts: dict, base_cov, orig: str, log: list,
                 best: dict | None, model: str, saved: Path | None) -> Path:
    L = [f"# 호출 안 함 API 추가 — {target}/{harness}", "", f"- 모델: `{model}`",
         f"- 수정 전: 공개 API {counts['total']}개 중 호출 안 함 {counts['not_called']}개"
         + (f", 라인 {base_cov[0]:.2f}% · 분기 {base_cov[1]:.2f}%" if base_cov else ""),
         f"- 추가를 요청한 API {len(chosen)}개: " + ", ".join(f"`{x['api'].split('(')[0]}`" for x in chosen), "",
         "| 시도 | 결과 | 실행된 API | 호출 안 함 | 라인 | 분기 | 사라진 API | 크래시 귀속 | 토큰(입력/출력) |",
         "|---:|---|---:|---:|---:|---:|---:|---|---|"]
    for e in log:
        st = "컴파일 실패" if e["stage"] == "compile" else ("통과" if e.get("ok") else "실패")
        cr = ", ".join(f"{c['cls']}({c['conf']})" for c in e.get("crashes", [])) or "-"
        u = e.get("usage") or {}
        f = lambda v, p="": "-" if v is None else f"{v}{p}"
        L.append(f"| {e['try']} | {st} | {e.get('called', '-')}/{e.get('total', '-')} | {f(e.get('not_called_after'))} | "
                 f"{f(e.get('lines'), '%')} | {f(e.get('branches'), '%')} | {len(e.get('lost', []))} | {cr} | "
                 f"{u.get('input_tokens', '-')}/{u.get('output_tokens', '-')} |")
    L += ["", "수정 전 수치는 진단 때(기본 120초 × 1회), 시도별 수치는 검사 퍼징(짧음)의 중앙값이라 길이가 다릅니다. "
              "정식 비교는 같은 조건의 긴 실험으로 하세요.", ""]
    if best:
        if best["missing"]:
            L += ["실행되지 않은 API: " + ", ".join(f"`{a.split('(')[0]}`" for a in best["missing"]), ""]
        new = (ROOT / best["harness"]).read_text(encoding="utf-8")
        diff = "".join(difflib.unified_diff(orig.splitlines(True), new.splitlines(True), "수정 전", f"시도 {best['try']}"))
        (work / "best.diff").write_text(diff, encoding="utf-8")
        L += [f"**채택: 시도 {best['try']}**" + (f" → `{saved.relative_to(ROOT)}`" if saved else "") + ". 사람이 읽고 쓰세요.", "",
              "```diff", diff.rstrip(), "```"]
    else:
        L.append("**통과한 하네스가 없습니다.** 마지막 실패 이유는 log.json을 보세요.")
    p = work / "report.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p
