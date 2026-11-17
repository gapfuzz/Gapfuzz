"""LLM(Claude API)으로 '하네스에서 고칠 곳'을 실제 하네스 코드에 적용하고, gapfuzz가 그 결과를 검사한다.

흐름 (제안 하나마다, 또는 --fix 1,3,4처럼 여러 제안을 한 하네스에 한꺼번에)
  1. 수정 전 gap.json의 harness_fixes에서 제안 하나를 고른다.
  2. 하네스 코드(줄 번호 포함), 제안 문장, 막힌 라이브러리 분기의 코드, 지킬 규칙을 Claude에게 주고 고친 하네스 전체를 받는다.
  3. gapfuzz가 검사한다: 컴파일 → 짧은 퍼징(기본 60초 × 2회) → 그 제안이 겨냥한 분기가 열렸는지(verify) → 크래시가 나면 귀속(triage).
  4. 실패하면 이유(컴파일 오류, 여전히 막힌 분기, 하네스 탓 크래시의 근거)를 같은 대화에 이어 보내고 다시 받는다(기본 최대 3번).
  5. 결과: out/llm/<라이브러리>/<하네스>_fix<번호>/ 에 시도별 하네스, 최종 diff, report.md, log.json

LLM이 틀린 코드를 내도 검증과 크래시 귀속이 걸러 내는 것이 핵심이다. 통과한 수정안도 사람이 읽고 넣는다.
API 키는 환경 변수 ANTHROPIC_API_KEY에서 읽는다(파일이나 로그에 남기지 않음). --mock으로 미리 준비한 응답 파일을 쓰면 키 없이 흐름을 시험할 수 있다.
"""
from __future__ import annotations

import concurrent.futures as cf
import difflib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from .triage import triage
from .verify import verify

ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://api.anthropic.com/v1/messages"
# 기본 모델. 환경 변수 GAPFUZZ_MODEL이나 --model로 바꿀 수 있다. 어떤 모델로 만들었는지는 report.md와 log.json에 남는다.
# official_llm과 gapfuzz_ops를 같은 모델로 만들기 위해 기본값을 바꾸지 않는다 (기존 official_llm: claude-sonnet-5-5).
DEFAULT_MODEL = os.environ.get("GAPFUZZ_MODEL", "claude-sonnet-5-5")

SYSTEM = """당신은 libFuzzer 퍼징 하네스를 고치는 보안 엔지니어입니다.
커버리지 분석 도구 gapfuzz가 하네스 때문에 막힌 라이브러리 분기와 그 원인을 찾았습니다. 주어진 제안만 하네스에 적용하세요.

규칙
- 제안이 말하는 부분만 바꾸고 나머지 코드는 그대로 둡니다. LLVMFuzzerTestOneInput의 시그니처는 바꾸지 않습니다.
- 새 값은 상수가 아니라 퍼저 입력에서 고르게 합니다(입력 앞쪽 바이트나 FuzzedDataProvider). 원래 값도 계속 나올 수 있게 둡니다.
- 하네스가 스스로 잘못 써서 생기는 크래시를 만들지 않습니다: 라이브러리 문서상 금지된 인자(예: null 금지 인자에 null)를 넘기지 말고,
  C++ 라이브러리가 예외를 던질 수 있는 호출은 try/catch로 감싸고, 할당한 것은 해제합니다.
- 제안이 여러 개면 모두 한 하네스에 적용합니다. 여러 수정이 퍼저 입력 바이트를 쓸 때는 서로 겹치지 않게 나눠 씁니다
  (예: 앞쪽 바이트를 순서대로 배분하거나 FuzzedDataProvider 하나로 차례로 꺼냄). 원래 하네스가 쓰던 입력 부분도 계속 쓰이게 둡니다.
- 바꾼 줄 끝에 `// [gapfuzz-llm] 이유` 주석을 한국어로 답니다.
- 답은 고친 하네스 파일 전체를 코드 블록 하나(```cpp 또는 ```c)로만 주고, 그 뒤에 무엇을 바꿨는지 한두 문장으로 씁니다."""


def _tgt():
    spec = importlib.util.spec_from_file_location("gapfuzz_tgt", ROOT / "scripts" / "tgt.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def numbered(text: str) -> str:
    return "\n".join(f"{i:4d}  {l}" for i, l in enumerate(text.splitlines(), 1))


def context(path: str, line: int, n: int = 4) -> str:
    try:
        src = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return ""
    lo, hi = max(1, line - n), min(len(src), line + n)
    return "\n".join(f"{i:5d}{'>' if i == line else ' '} {src[i - 1]}" for i in range(lo, hi + 1))


def build_request(harness_src: str, harness_name: str, fix, before: dict, lib_name: str,
                  nos: list[int] | None = None, hints: dict[int, str] | None = None) -> str:
    """fix: 제안 하나(dict) 또는 여러 개(list). nos: 제안 번호, hints: 번호 → 그 제안만 따로 적용해 검증을 통과한 diff."""
    fixes = fix if isinstance(fix, list) else [fix]
    nos = nos or list(range(1, len(fixes) + 1))
    files = {}
    for r in before["results"]:
        for b in r.get("stuck_branches", []):
            files[(r["api"], b["line"], b.get("col", 0))] = b["file"]
    parts = [f"라이브러리: {lib_name}", f"하네스 파일: {harness_name}", ""]
    multi = len(fixes) > 1
    if multi:
        parts += [f"아래 제안 {len(fixes)}개를 **모두 한 하네스에** 적용하세요.", ""]
    for no, fx in zip(nos, fixes):
        head = f"## 제안 {no}" if multi else "## gapfuzz의 제안"
        parts += [head, fx.get("suggestion", ""), "", f"### 이 제안 때문에 막혀 있던 라이브러리 분기 ({len(fx['blocked'])}개)"]
        for b in fx["blocked"][:8]:
            f = files.get((b["api"], b["line"], b.get("col", 0)))
            parts += [f"- `{b['api']}` {b['line']}행, 조건 `{b.get('expr') or b.get('source')}`가 퍼징 중 한 번도 '{b['never']}'이 되지 않음"]
            if f:
                parts += ["```", context(f, b["line"]), "```"]
        if hints and hints.get(no):
            parts += ["", "### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)",
                      "```diff", hints[no].rstrip(), "```"]
        parts.append("")
    parts += ["## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)", "```", numbered(harness_src), "```"]
    return "\n".join(parts)


MAX_TOKENS = int(os.environ.get("GAPFUZZ_MAX_TOKENS", "64000"))
EFFORT = os.environ.get("GAPFUZZ_EFFORT", "medium")


def call_claude(messages: list, model: str, key: str, max_tokens: int | None = None, system: str | None = None) -> tuple[str, dict]:
    """Claude API 호출. (본문 글자, usage)를 돌려준다. usage["stop_reason"]에 응답이 끝난 이유를 넣는다.

    최근 모델은 답을 쓰기 전에 '생각'을 하고, 그 생각 토큰도 max_tokens에 포함된다. 상한이 작으면 생각만 하다
    코드를 쓰기 전에 잘린다. 그래서 상한을 넉넉히 주고(기본 64000, GAPFUZZ_MAX_TOKENS로 조절),
    생각 분량은 effort로 줄인다(기본 medium, GAPFUZZ_EFFORT로 조절. 빈 값이면 보내지 않음).
    effort를 모르는 모델이면 그 항목을 빼고 한 번 더 보낸다."""
    payload = {"model": model, "max_tokens": max_tokens or MAX_TOKENS, "system": system or SYSTEM, "messages": messages}
    if EFFORT:
        payload["output_config"] = {"effort": EFFORT}
    for attempt in range(6):
        req = urllib.request.Request(API_URL, data=json.dumps(payload).encode(), headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                data = json.load(r)
            text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
            usage = dict(data.get("usage", {}), stop_reason=data.get("stop_reason"))
            return text, usage
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code == 400 and "output_config" in payload and re.search(r"output_config|effort", detail):
                payload.pop("output_config")           # 이 모델은 effort를 받지 않는다
                continue
            if e.code == 400 and re.search(r"max_tokens", detail) and payload["max_tokens"] > 8000:
                m = re.search(r"(\d{4,})", detail)            # 모델의 출력 상한이 더 작다: 메시지에 적힌 값(없으면 절반)으로 낮춰 다시 보낸다
                lim = int(m.group(1)) if m else 0
                payload["max_tokens"] = lim if 8000 <= lim < payload["max_tokens"] else payload["max_tokens"] // 2
                continue
            if e.code in (429, 500, 502, 503, 529) and attempt < 5:
                time.sleep(10 * (attempt + 1))
                continue
            raise SystemExit(f"[llmfix] Claude API 오류 {e.code}: {detail}")
    raise SystemExit("[llmfix] Claude API가 계속 응답하지 않음")


def no_code_reason(text: str, usage: dict) -> str:
    """응답에서 코드를 못 꺼냈을 때의 이유. 상한에 걸려 잘린 경우를 따로 알려 준다."""
    if usage.get("stop_reason") == "max_tokens":
        think = (usage.get("output_tokens_details") or {}).get("thinking_tokens")
        return (f"응답이 토큰 상한에서 잘렸습니다 (출력 {usage.get('output_tokens')}토큰"
                + (f", 그중 생각 {think}토큰" if think is not None else "")
                + "). GAPFUZZ_MAX_TOKENS를 올리거나 GAPFUZZ_EFFORT=low로 생각 분량을 줄이거나 --top을 줄이세요.")
    return "응답에 코드 블록이 없습니다."


def extract_code(text: str) -> str | None:
    blocks = re.findall(r"```(?:cpp|c\+\+|cc|c)?\s*\n(.*?)```", text, re.S)
    return max(blocks, key=len) if blocks else None


def _compile(tg, t: dict, src: Path, out: Path) -> str | None:
    out.mkdir(parents=True, exist_ok=True)
    for mode in ("fuzz", "cov"):
        for c in tg.compile_cmds(t, src, out, mode):
            p = subprocess.run(c, capture_output=True, text=True)
            if p.returncode != 0:
                err = [l for l in (p.stderr or p.stdout).splitlines() if "error" in l or "^" in l]
                return "\n".join(err[:30]) or (p.stderr or p.stdout)[-2000:]
    return None


def check(tg, t: dict, name: str, src: Path, before: dict, fix_idx, secs: int, trials: int) -> dict:
    out = ROOT / "out" / "targets" / t["name"] / name
    err = _compile(tg, t, src, out)
    if err:
        return {"ok": False, "stage": "compile", "detail": err}
    with cf.ThreadPoolExecutor(max_workers=min(2, trials)) as ex:
        list(ex.map(lambda r: tg.run_one(t, name, r, secs, 1000, 10, None), range(1, trials + 1)))
    afters, crashes = [], []
    for r in range(1, trials + 1):
        d = out / f"r{r}"
        g = d / "gap" / "gap.json"
        if g.exists():
            afters.append(json.load(open(g)))
        crashes += [str(d / f) for f in os.listdir(d) if f.split("-")[0] in ("crash", "leak", "timeout", "oom")]
    idxs = fix_idx if isinstance(fix_idx, list) else [fix_idx]
    vs = verify(before, afters) if afters else []
    per = [vs[i] if vs else {"opened": 0, "total": 0, "checks": []} for i in idxs]
    res = {"stage": "fuzz", "opened": sum(v["opened"] for v in per), "total": sum(v["total"] for v in per),
           "per_fix": {str(i + 1): [v["opened"], v["total"]] for i, v in zip(idxs, per)},
           "still": [f"{'제안 ' + str(i + 1) + ': ' if len(idxs) > 1 else ''}`{c['api']}` {c['line']}행 `{c.get('expr') or c.get('source')}`"
                     for i, v in zip(idxs, per) for c in v["checks"] if c["state"] != "OPENED"],
           "crashes": []}
    if crashes:
        tri = triage(str(out / "fuzz"), crashes[:5], [str(src)], [str(t["lib"])], [str(src.parent), str(ROOT / "harnesses")],
                     2, 10, root=str(ROOT))
        res["crashes"] = [{"cls": c.verdict.cls, "conf": c.verdict.confidence, "reason": c.verdict.reason,
                           "evidence": c.verdict.evidence[:8], "kind": c.kind} for c in tri]
    # 검사 퍼징에서 크래시가 난 하네스는 귀속과 상관없이 채택하지 않는다. 60초 안에 죽는 하네스는 1시간 실험에서도
    # 시작하자마자 멈추기 때문이다. (2026-11-16 이전에는 LIBRARY·ASSERT 크래시를 통과시켰고, Claude에게 알리지도 않았다.)
    res["ok"] = res["opened"] > 0 and not res["crashes"]
    res["complete"] = res["ok"] and res["opened"] == res["total"]
    return res


CRASH_NOTE = ("실험용 하네스는 검사 퍼징에서 크래시가 없어야 합니다(크래시가 나면 그 실행의 퍼징이 거기서 멈춥니다). 귀속이 라이브러리 쪽이어도 이 크래시로 이어지는 호출·인자·호출 순서를 하네스에서 피하세요: 라이브러리 문서의 소유권·해제 규칙을 다시 확인하고, 구조체의 내부 필드를 직접 바꾸지 말고, 안전하게 부를 수 없으면 그 호출을 빼고 이유를 적으세요.")


def feedback(res: dict) -> str:
    if res["stage"] == "compile":
        return "고친 하네스가 컴파일되지 않습니다. 오류:\n```\n" + res["detail"] + "\n```\n오류를 고친 하네스 전체를 다시 주세요."
    lines = [f"고친 하네스로 다시 퍼징했더니 겨냥한 분기 {res['total']}개 중 {res['opened']}개가 열렸습니다."]
    if res["still"]:
        lines += ["아직 막힌 분기:"] + [f"- {s}" for s in res["still"]]
    for c in res["crashes"]:
        lines += [f"크래시가 났고 gapfuzz 크래시 귀속은 '{c['cls']}'(확신 {c['conf']})로 판정했습니다: {c['reason']}"] + [f"  - {e}" for e in c["evidence"]]
    if res["crashes"]:
        lines.append(CRASH_NOTE)
    lines.append("제안의 의도는 유지하면서 위 문제를 고친 하네스 전체를 다시 주세요.")
    return "\n".join(lines)


def run(target: str, harness: str, fix_no, before_path: str | None, secs: int, trials: int, tries: int,
        model: str, mock: list[str] | None, out_name: str | None = None, hints: bool = False) -> dict:
    """fix_no: 번호 하나 또는 목록. 목록이면 모든 제안을 한 하네스에 적용한다(out_name: 결과 폴더 이름)."""
    tg = _tgt()
    t = tg.load(target)
    hp = tg.harness_path(t, harness)
    bp = Path(before_path) if before_path else ROOT / "out" / "targets" / target / harness / "r1" / "gap" / "gap.json"
    before = json.load(open(bp))
    fixes = before.get("harness_fixes", [])
    nos = fix_no if isinstance(fix_no, list) else [fix_no]
    if not nos or not all(1 <= n <= len(fixes) for n in nos):
        raise SystemExit(f"[llmfix] 제안 번호는 1~{len(fixes)} (--list로 확인)")
    fix = fixes[nos[0] - 1] if len(nos) == 1 else [fixes[n - 1] for n in nos]
    tag = out_name or (f"{harness}_fix{nos[0]}" if len(nos) == 1 else f"{harness}_fix{'_'.join(map(str, nos))}")
    hint = {}
    if hints:
        for n in nos:
            for d in (ROOT / "out" / "llm" / target / f"{harness}_fix{n}",
                      ROOT / "evaluation" / "artifacts" / "llm" / "runs" / target / f"{harness}_fix{n}"):
                if (d / "best.diff").exists():
                    hint[n] = (d / "best.diff").read_text(encoding="utf-8")
                    break
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not mock and not key:
        raise SystemExit("[llmfix] ANTHROPIC_API_KEY 환경 변수가 없습니다 (키 없이 시험하려면 --mock 응답파일)")

    base = ROOT / t.get("harness_dir", f"harnesses/{t['name']}")
    rel_dir = Path("llm") / tag
    work = ROOT / "out" / "llm" / target / tag
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (base / rel_dir).mkdir(parents=True, exist_ok=True)
    orig = hp.read_text(encoding="utf-8")
    messages = [{"role": "user", "content": build_request(orig, hp.name, fix, before, target, nos, hint)}]
    (work / "request.md").write_text(messages[0]["content"], encoding="utf-8")
    log, best = [], None
    for k in range(1, tries + 1):
        t0 = time.time()
        if mock:
            text, usage = Path(mock[min(k, len(mock)) - 1]).read_text(encoding="utf-8"), {}
            if "```" not in text:
                text = "```cpp\n" + text + "\n```"
        else:
            text, usage = call_claude(messages, model, key)
        (work / f"try{k}_response.md").write_text(text, encoding="utf-8")
        code = extract_code(text)
        entry = {"try": k, "llm_seconds": round(time.time() - t0, 1), "usage": usage}
        if not code:
            res = {"ok": False, "stage": "compile", "detail": no_code_reason(text, usage)}
        else:
            name = str(rel_dir / f"try{k}")
            src = base / rel_dir / f"try{k}{hp.suffix}"
            src.write_text(code if code.endswith("\n") else code + "\n", encoding="utf-8")
            shutil.copy(src, work / src.name)
            res = check(tg, t, name, src, before, [n - 1 for n in nos] if len(nos) > 1 else nos[0] - 1, secs, trials)
            entry["harness"] = str(src.relative_to(ROOT))
        entry.update(res)
        log.append(entry)
        print(f"[llmfix] {target}/{harness} 제안 {','.join(map(str, nos))} 시도 {k}: "
              + (f"컴파일 실패" if res["stage"] == "compile" else
                 f"열림 {res['opened']}/{res['total']}, 크래시 {[c['cls'] for c in res['crashes']]}"), flush=True)
        if res.get("ok") and (best is None or res["opened"] > best["opened"]):
            best = entry
        if res.get("complete"):
            break
        prev = log[-2] if len(log) > 1 else None
        if res.get("ok") and prev and prev.get("ok") and prev.get("opened") == res.get("opened"):
            break                                   # 두 번 연속 같은 결과로 통과: 남은 분기는 하네스로 안 열릴 가능성이 큼
        fb = feedback(res)
        (work / f"try{k}_feedback.md").write_text(fb, encoding="utf-8")
        messages += [{"role": "assistant", "content": text}, {"role": "user", "content": fb}]
    report = write_report(work, target, harness, ",".join(map(str, nos)), fix, orig, log, best, model if not mock else "mock")
    json.dump({"target": target, "harness": harness, "fix": nos[0] if len(nos) == 1 else nos, "model": model if not mock else "mock",
               "tries": log, "best": best and best["try"]}, open(work / "log.json", "w"), ensure_ascii=False, indent=1)
    print(f"[llmfix] -> {report}")
    return {"best": best, "log": log}


def write_report(work: Path, target: str, harness: str, fix_no, fix, orig: str, log: list, best: dict | None,
                 model: str) -> Path:
    fx = fix if isinstance(fix, list) else [fix]
    L = [f"# LLM 하네스 수정 — {target}/{harness}, 제안 {fix_no}", "", f"- 모델: `{model}`"]
    L += [f"- 제안: {f.get('suggestion', '')}" for f in fx]
    L += [f"- 겨냥한 분기: {sum(len(f['blocked']) for f in fx)}개", "",
          "| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |", "|---:|---|---:|---|---|---|"]
    for e in log:
        st = "컴파일 실패" if e["stage"] == "compile" else ("통과" if e.get("ok") else "실패")
        cr = ", ".join(f"{c['cls']}({c['conf']})" for c in e.get("crashes", [])) or "-"
        u = e.get("usage") or {}
        pf = ", ".join(f"{k}: {v[0]}/{v[1]}" for k, v in (e.get("per_fix") or {}).items()) or "-"
        L.append(f"| {e['try']} | {st} | {e.get('opened', '-')}/{e.get('total', '-')} | {pf} | {cr} | "
                 f"{u.get('input_tokens', '-')}/{u.get('output_tokens', '-')} |")
    L.append("")
    if best:
        new = (ROOT / best["harness"]).read_text(encoding="utf-8")
        diff = "".join(difflib.unified_diff(orig.splitlines(True), new.splitlines(True), "수정 전", f"시도 {best['try']}"))
        (work / "best.diff").write_text(diff, encoding="utf-8")
        L += [f"**채택 후보: 시도 {best['try']}** (`{best['harness']}`). 사람이 읽고 넣으세요.", "", "```diff", diff.rstrip(), "```"]
    else:
        L.append("**통과한 수정안이 없습니다.** 마지막 실패 이유는 log.json을 보세요.")
    p = work / "report.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p


def list_fixes(target: str, harness: str, before_path: str | None) -> None:
    tg = _tgt()
    t = tg.load(target)
    bp = Path(before_path) if before_path else ROOT / "out" / "targets" / target / harness / "r1" / "gap" / "gap.json"
    before = json.load(open(bp))
    for i, f in enumerate(before.get("harness_fixes", []), 1):
        print(f"{i:2d}. [{f['verdict']}] 막힌 분기 {len(f['blocked'])}개 — {f.get('suggestion', '')[:150]}")
