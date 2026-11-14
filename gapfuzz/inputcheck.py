"""'입력 탓'으로 판정한 분기를 실제로 확인한다 (inputcheck).

원인 추적은 하네스에서 원인을 못 찾은 분기를 "입력 내용·라이브러리 내부 때문"이라고 적는다. 이것은 추정이다.
inputcheck는 그 분기들의 조건식에서 딕셔너리를 만들고(dictgen), 기준 실행의 코퍼스에서 이어서 두 가지로 다시 퍼징한다.

  A. 기존 딕셔너리만        B. 기존 + gapfuzz가 만든 딕셔너리        (같은 시드, 같은 시간)

그리고 기준 실행에서 막혀 있던 분기가 열렸는지 분기별로 센다.
  - B에서만 열림        → 딕셔너리 토큰이 있어야 열리는 분기. 입력 탓으로 확인.
  - A·B 모두에서 열림   → 시간만 더 주면 열리는 분기. 입력 탓(퍼징 시간 문제)으로 확인.
  - 어디서도 안 열림    → 미확인. 입력 탓이 아닐 수도 있다(호출 순서, 빌드 설정, 도달 불가 등).

  python3 -m gapfuzz inputcheck zlib official                  # 기본 10분 × 3회 (A, B 각각)
  python3 -m gapfuzz inputcheck zlib official --secs 3600      # 근거로 쓸 때는 1시간

퍼징 시간: 하네스를 고친 효과는 몇 초 안에 나타나지만, 입력 탓 분기는 퍼저가 맞는 입력을 찾아야 열리므로 시간이 걸린다.
그래서 기본값을 제안 검증(1~2분)보다 길게 둔다. 짧게 돌리면 '안 열림(미확인)'만 늘어난다.

결과: out/targets/<이름>/<하네스>/inputcheck/{gapfuzz.dict, result.json, report.md}

한계: 짧은 재실행에서 안 열렸다고 "입력 탓이 아니다"가 증명되지는 않는다. 열린 쪽만 확정이다.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import shutil
import subprocess
from pathlib import Path

from .causes import FIX_VERDICTS
from .dictgen import generate, write_dict
from .llmfix import ROOT, _tgt
from .report import VERDICT_KO, primary_cause


def suspects(gap: dict) -> list[dict]:
    """기준 실행에서 막힌 분기 중, 기존 분석이 하네스에서 원인을 찾지 못한 것."""
    out, seen = [], set()
    for r in gap["results"]:
        for b in r.get("stuck_branches", []):
            if not b.get("causes"):
                continue
            pc = primary_cause(b)
            key = (b["file"], b["line"], b["col"], b["never"])
            if pc["verdict"] in FIX_VERDICTS or key in seen:
                continue
            seen.add(key)
            out.append({"api": r["api"], "file": b["file"], "line": b["line"], "col": b["col"], "never": b["never"],
                        "expr": b.get("expr") or b["source"], "verdict": pc["verdict"]})
    return out


def branch_counts(coverage_json: Path) -> dict:
    """coverage.json → {(파일, 줄, 열): [참 횟수, 거짓 횟수]} (템플릿 등으로 여러 번 나오면 합친다)."""
    out: dict = {}
    for f in json.load(open(coverage_json))["data"][0]["files"]:
        name = os.path.abspath(f["filename"])
        for b in f.get("branches", []):
            c = out.setdefault((name, b[0], b[1]), [0, 0])
            c[0] += b[4]
            c[1] += b[5]
    return out


def _one(tg, t: dict, base: Path, d: Path, seed_corpus: Path | None, secs: int, seed: int, dct: str | None) -> Path:
    shutil.rmtree(d, ignore_errors=True)
    (d / "corpus").mkdir(parents=True)
    if seed_corpus:
        for p in seed_corpus.iterdir():
            shutil.copy(p, d / "corpus" / p.name)
    args = ["nice", "-n", "10", str(base / "fuzz"), f"-max_total_time={secs}", f"-seed={seed}", "-rss_limit_mb=2048",
            "-timeout=10", f"-artifact_prefix={d}/"]
    if dct:
        args.append(f"-dict={dct}")
    with open(d / "fuzz.log", "w") as log:
        subprocess.run([*args, str(d / "corpus")], stdout=log, stderr=subprocess.STDOUT)
    env = dict(os.environ, LLVM_PROFILE_FILE=str(d / "cov-%p.profraw"))
    subprocess.run([str(base / "cov"), "-runs=0", str(d / "corpus")], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    raws = [str(p) for p in d.glob("cov-*.profraw")]
    subprocess.run(["llvm-profdata", "merge", "-sparse", *raws, "-o", str(d / "cov.profdata")], check=True)
    files = [str(s) for s in t["srcs"]] + [str(x) for x in t["headers"]]
    with open(d / "coverage.json", "w") as f:
        subprocess.run(["llvm-cov", "export", "-format=text", f"-instr-profile={d / 'cov.profdata'}", str(base / "cov"), *files],
                       stdout=f, check=True)
    return d / "coverage.json"


def run(target: str, harness: str, before: str | None, secs: int, trials: int, fresh: bool = False) -> dict:
    tg = _tgt()
    t = tg.load(target)
    base = ROOT / "out" / "targets" / t["name"] / harness
    bd = Path(before) if before else base / "r1"
    if not (bd / "gap" / "gap.json").exists() or not (base / "fuzz").exists():
        raise SystemExit(f"기준 실행 없음: {bd}  (먼저 `python3 scripts/tgt.py build {target} {harness}` 와 "
                         f"`python3 scripts/tgt.py repeat {target} {harness} --trials 1`)")
    gap = json.load(open(bd / "gap" / "gap.json"))
    sus = suspects(gap)
    work = base / "inputcheck"
    work.mkdir(parents=True, exist_ok=True)
    base_dict = str(ROOT / t["dict"]) if t.get("dict") else None
    entries = generate([gap], [str(s) for s in t["srcs"]] + [str(h) for h in t["headers"]], existing=base_dict)
    gen = work / "gapfuzz.dict"
    write_dict(entries, str(gen), base=base_dict)
    print(f"[inputcheck] {target}/{harness}: 하네스에서 원인을 못 찾은 막힌 분기 {len(sus)}개, 딕셔너리 토큰 {len(entries)}개 생성")
    if not sus:
        return {"suspects": 0}

    seed_corpus = None if fresh else bd / "corpus"
    jobs = [(arm, k, work / arm / f"r{k}", base_dict if arm == "A" else str(gen)) for k in range(1, trials + 1) for arm in ("A", "B")]
    with cf.ThreadPoolExecutor(max_workers=max(1, min(os.cpu_count() or 1, 4))) as ex:
        futs = {ex.submit(_one, tg, t, base, d, seed_corpus, secs, 7000 + k, dct): (arm, k) for arm, k, d, dct in jobs}
        covs = {futs[f]: f.result() for f in cf.as_completed(futs)}

    opened = {"A": [0] * len(sus), "B": [0] * len(sus)}
    for (arm, k), path in covs.items():
        bc = branch_counts(path)
        for i, s in enumerate(sus):
            c = bc.get((os.path.abspath(s["file"]), s["line"], s["col"]))
            if c and c[0 if s["never"] == "참" else 1] > 0:
                opened[arm][i] += 1
    for i, s in enumerate(sus):
        a, b = opened["A"][i], opened["B"][i]
        s["opened_A"], s["opened_B"] = a, b
        s["result"] = "dict" if b and not a else "time" if a and b else "time_only_A" if a else "unconfirmed"
    n = lambda r: sum(1 for s in sus if s["result"] == r)
    res = {"target": target, "harness": harness, "before": str(bd), "secs": secs, "trials": trials, "fresh": fresh,
           "tokens": len(entries), "suspects": len(sus), "confirmed_by_dict": n("dict"), "confirmed_by_time": n("time") + n("time_only_A"),
           "unconfirmed": n("unconfirmed"), "branches": sus}
    json.dump(res, open(work / "result.json", "w"), ensure_ascii=False, indent=1)

    KO = {"dict": "딕셔너리로 열림 (입력 탓 확인)", "time": "시간만 더 줘도 열림 (입력 탓 확인)",
          "time_only_A": "딕셔너리 없이만 열림 (입력 탓 확인, 운에 따라 다름)", "unconfirmed": "안 열림 (미확인)"}
    md = [f"# 입력 탓 판정 확인 — {target}/{harness}", "",
          f"- 기준 실행: `{bd.relative_to(ROOT) if bd.is_relative_to(ROOT) else bd}`, 재실행: {secs}초 × {trials}회, "
          f"{'빈 코퍼스에서 시작' if fresh else '기준 코퍼스에서 이어서'}",
          f"- 하네스에서 원인을 못 찾은 막힌 분기: **{len(sus)}개**, 그 조건식에서 만든 딕셔너리 토큰: {len(entries)}개", "",
          "| 결과 | 분기 수 |", "|---|---:|"]
    for r in ("dict", "time", "time_only_A", "unconfirmed"):
        if n(r):
            md.append(f"| {KO[r]} | {n(r)} |")
    md += ["", "A = 기존 딕셔너리만, B = 기존 + gapfuzz 딕셔너리. 숫자는 그 분기가 열린 회차 수입니다.", "",
           "| 분기 | 조건 | 기존 판정 | A | B | 결과 |", "|---|---|---|---:|---:|---|"]
    order = {"dict": 0, "time": 1, "time_only_A": 2, "unconfirmed": 3}
    for s in sorted(sus, key=lambda s: (order[s["result"]], s["file"], s["line"])):
        expr = s["expr"].strip().replace("|", "\\|")[:60]
        md.append(f"| `{os.path.basename(s['file'])}:{s['line']}` | `{expr}` ({s['never']} 쪽) | {VERDICT_KO[s['verdict']].split(' (')[0]} "
                  f"| {s['opened_A']}/{trials} | {s['opened_B']}/{trials} | {KO[s['result']].split(' (')[0]} |")
    md += ["", "안 열린 분기는 '입력 탓이 아니다'가 아니라 '이 시간 안에는 확인하지 못했다'는 뜻입니다."]
    (work / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[inputcheck] 딕셔너리로 열림 {res['confirmed_by_dict']}개, 시간만 더 줘도 열림 {res['confirmed_by_time']}개, 안 열림 {res['unconfirmed']}개")
    print(f"[inputcheck] -> {work}/report.md, result.json, gapfuzz.dict")
    return res
