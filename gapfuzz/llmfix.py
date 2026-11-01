"""LLM(Claude API)으로 '하네스에서 고칠 곳'을 실제 하네스 코드에 적용하고, gapfuzz가 그 결과를 검사한다.

흐름 (제안 하나마다)
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
DEFAULT_MODEL = "claude-sonnet-5-5"

SYSTEM = """당신은 libFuzzer 퍼징 하네스를 고치는 보안 엔지니어입니다.
커버리지 분석 도구 gapfuzz가 하네스 때문에 막힌 라이브러리 분기와 그 원인을 찾았습니다. 그 제안 하나만 하네스에 적용하세요.

규칙
- 제안이 말하는 부분만 바꾸고 나머지 코드는 그대로 둡니다. LLVMFuzzerTestOneInput의 시그니처는 바꾸지 않습니다.
- 새 값은 상수가 아니라 퍼저 입력에서 고르게 합니다(입력 앞쪽 바이트나 FuzzedDataProvider). 원래 값도 계속 나올 수 있게 둡니다.
- 하네스가 스스로 잘못 써서 생기는 크래시를 만들지 않습니다: 라이브러리 문서상 금지된 인자(예: null 금지 인자에 null)를 넘기지 말고,
  C++ 라이브러리가 예외를 던질 수 있는 호출은 try/catch로 감싸고, 할당한 것은 해제합니다.
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


def build_request(harness_src: str, harness_name: str, fix: dict, before: dict, lib_name: str) -> str:
    files = {}
    for r in before["results"]:
        for b in r.get("stuck_branches", []):
            files[(r["api"], b["line"], b.get("col", 0))] = b["file"]
    parts = [f"라이브러리: {lib_name}", f"하네스 파일: {harness_name}", "",
             "## gapfuzz의 제안", fix.get("suggestion", ""), "",
             f"## 이 제안 때문에 막혀 있던 라이브러리 분기 ({len(fix['blocked'])}개)"]
    for b in fix["blocked"][:8]:
        f = files.get((b["api"], b["line"], b.get("col", 0)))
        parts += [f"- `{b['api']}` {b['line']}행, 조건 `{b.get('expr') or b.get('source')}`가 퍼징 중 한 번도 '{b['never']}'이 되지 않음"]
        if f:
            parts += ["```", context(f, b["line"]), "```"]
    parts += ["", "## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)", "```", numbered(harness_src), "```"]
    return "\n".join(parts)


def call_claude(messages: list, model: str, key: str, max_tokens: int = 8000) -> tuple[str, dict]:
    body = json.dumps({"model": model, "max_tokens": max_tokens, "system": SYSTEM, "messages": messages}).encode()
    for attempt in range(5):
        req = urllib.request.Request(API_URL, data=body, headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                data = json.load(r)
            text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
            return text, data.get("usage", {})
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 529) and attempt < 4:
                time.sleep(10 * (attempt + 1))
                continue
            raise SystemExit(f"[llmfix] Claude API 오류 {e.code}: {detail}")
    raise SystemExit("[llmfix] Claude API가 계속 응답하지 않음")


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


def check(tg, t: dict, name: str, src: Path, before: dict, fix_idx: int, secs: int, trials: int) -> dict:
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
    v = verify(before, afters)[fix_idx] if afters else {"opened": 0, "total": 0, "checks": []}
    res = {"stage": "fuzz", "opened": v["opened"], "total": v["total"],
           "still": [f"`{c['api']}` {c['line']}행 `{c.get('expr') or c.get('source')}`" for c in v["checks"] if c["state"] != "OPENED"],
           "crashes": []}
    if crashes:
        tri = triage(str(out / "fuzz"), crashes[:5], [str(src)], [str(t["lib"])], [str(src.parent), str(ROOT / "harnesses")],
                     2, 10, root=str(ROOT))
        res["crashes"] = [{"cls": c.verdict.cls, "conf": c.verdict.confidence, "reason": c.verdict.reason,
                           "evidence": c.verdict.evidence[:4], "kind": c.kind} for c in tri]
    harness_bug = [c for c in res["crashes"] if c["cls"] in ("HARNESS", "UNCLEAR", "RESOURCE")]
    res["ok"] = res["opened"] > 0 and not harness_bug
    res["complete"] = res["ok"] and res["opened"] == res["total"]
    return res


def feedback(res: dict) -> str:
    if res["stage"] == "compile":
        return "고친 하네스가 컴파일되지 않습니다. 오류:\n```\n" + res["detail"] + "\n```\n오류를 고친 하네스 전체를 다시 주세요."
    lines = [f"고친 하네스로 다시 퍼징했더니 겨냥한 분기 {res['total']}개 중 {res['opened']}개가 열렸습니다."]
    if res["still"]:
        lines += ["아직 막힌 분기:"] + [f"- {s}" for s in res["still"]]
    for c in res["crashes"]:
        if c["cls"] in ("HARNESS", "UNCLEAR", "RESOURCE"):
            lines += [f"크래시가 났고 gapfuzz 크래시 귀속은 '{c['cls']}'(확신 {c['conf']})로 판정했습니다: {c['reason']}"] + [f"  - {e}" for e in c["evidence"]]
    lines.append("제안의 의도는 유지하면서 위 문제를 고친 하네스 전체를 다시 주세요.")
    return "\n".join(lines)


def run(target: str, harness: str, fix_no: int, before_path: str | None, secs: int, trials: int, tries: int,
        model: str, mock: list[str] | None) -> dict:
    tg = _tgt()
    t = tg.load(target)
    hp = tg.harness_path(t, harness)
    bp = Path(before_path) if before_path else ROOT / "out" / "targets" / target / harness / "r1" / "gap" / "gap.json"
    before = json.load(open(bp))
    fixes = before.get("harness_fixes", [])
    if not 1 <= fix_no <= len(fixes):
        raise SystemExit(f"[llmfix] 제안 번호는 1~{len(fixes)} (--list로 확인)")
    fix = fixes[fix_no - 1]
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not mock and not key:
        raise SystemExit("[llmfix] ANTHROPIC_API_KEY 환경 변수가 없습니다 (키 없이 시험하려면 --mock 응답파일)")

    base = ROOT / t.get("harness_dir", f"harnesses/{t['name']}")
    rel_dir = Path("llm") / f"{harness}_fix{fix_no}"
    work = ROOT / "out" / "llm" / target / f"{harness}_fix{fix_no}"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (base / rel_dir).mkdir(parents=True, exist_ok=True)
    orig = hp.read_text(encoding="utf-8")
    messages = [{"role": "user", "content": build_request(orig, hp.name, fix, before, target)}]
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
            res = {"ok": False, "stage": "compile", "detail": "응답에 코드 블록이 없습니다."}
        else:
            name = str(rel_dir / f"try{k}")
            src = base / rel_dir / f"try{k}{hp.suffix}"
            src.write_text(code if code.endswith("\n") else code + "\n", encoding="utf-8")
            shutil.copy(src, work / src.name)
            res = check(tg, t, name, src, before, fix_no - 1, secs, trials)
            entry["harness"] = str(src.relative_to(ROOT))
        entry.update(res)
        log.append(entry)
        print(f"[llmfix] {target}/{harness} 제안 {fix_no} 시도 {k}: "
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
    report = write_report(work, target, harness, fix_no, fix, orig, log, best, model if not mock else "mock")
    json.dump({"target": target, "harness": harness, "fix": fix_no, "model": model if not mock else "mock",
               "tries": log, "best": best and best["try"]}, open(work / "log.json", "w"), ensure_ascii=False, indent=1)
    print(f"[llmfix] -> {report}")
    return {"best": best, "log": log}


def write_report(work: Path, target: str, harness: str, fix_no: int, fix: dict, orig: str, log: list, best: dict | None,
                 model: str) -> Path:
    L = [f"# LLM 하네스 수정 — {target}/{harness}, 제안 {fix_no}", "",
         f"- 모델: `{model}`", f"- 제안: {fix.get('suggestion', '')}", f"- 겨냥한 분기: {len(fix['blocked'])}개", "",
         "| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |", "|---:|---|---:|---|---|"]
    for e in log:
        st = "컴파일 실패" if e["stage"] == "compile" else ("통과" if e.get("ok") else "실패")
        cr = ", ".join(f"{c['cls']}({c['conf']})" for c in e.get("crashes", [])) or "-"
        u = e.get("usage") or {}
        L.append(f"| {e['try']} | {st} | {e.get('opened', '-')}/{e.get('total', '-')} | {cr} | "
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
