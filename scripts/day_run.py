#!/usr/bin/env python3
"""24시간 실험: 하네스 두 개를 같은 조건으로 오래 퍼징하고, 구간마다 커버리지를 재서 시간에 따른 곡선을 남긴다.

이 환경은 작업 하나를 2시간까지만 돌릴 수 있어서 구간(기본 110분)으로 나눠 이어 붙인다.
같은 코퍼스 디렉터리에서 다시 시작하므로 모은 입력은 이어지지만, libFuzzer 내부 상태(추천 딕셔너리 등)는 구간마다 초기화된다.
크래시로 퍼저가 멈추면 기록을 남기고 남은 시간만큼 바로 다시 돌린다.

사용법: python3 scripts/day_run.py [--hours 24] [--chunk-min 110] stateful stateful_v3
  한 번 실행하면 한 구간만 돌리고 끝난다. 다 끝날 때까지 같은 명령을 다시 실행한다(진행 상황은 out/day/state.json).
결과: out/day/<하네스>/{corpus, timeline.json, crash-*}, 끝나면 samples/day/timeline.md
"""
import argparse
import concurrent.futures as cf
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "day"
spec = importlib.util.spec_from_file_location("tgt", ROOT / "scripts" / "tgt.py")
tg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tg)
T = tg.load("tinyxml2")


def build(h: str) -> Path:
    b = OUT / h / "bin"
    if not (b / "fuzz").exists() or not (b / "cov").exists():
        b.mkdir(parents=True, exist_ok=True)
        for mode in ("fuzz", "cov"):
            for c in tg.compile_cmds(T, tg.harness_path(T, h), b, mode):
                subprocess.run(c, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return b


def fuzz_chunk(h: str, secs: int, seed: int) -> dict:
    d, b = OUT / h, OUT / h / "bin"
    (d / "corpus").mkdir(parents=True, exist_ok=True)
    left, runs, t0 = secs, 0, time.time()
    with open(d / "fuzz.log", "a") as log:
        while left > 30:
            runs += 1
            log.write(f"\n=== {time.strftime('%m-%d %H:%M')} 시작 seed={seed + runs} 남은 {left}초 ===\n")
            log.flush()
            subprocess.run(["nice", "-n", "5", str(b / "fuzz"), f"-max_total_time={left}", f"-seed={seed + runs}",
                            f"-dict={ROOT / 'dicts' / 'xml.dict'}", "-rss_limit_mb=2048", "-timeout=10",
                            f"-artifact_prefix={d}/", str(d / "corpus")], stdout=log, stderr=subprocess.STDOUT)
            left = secs - int(time.time() - t0)
    return {"wall": int(time.time() - t0), "restarts": runs - 1}


def measure(h: str) -> dict:
    d, b = OUT / h, OUT / h / "bin"
    for f in d.glob("cov-*.profraw"):
        f.unlink()
    env = dict(os.environ, LLVM_PROFILE_FILE=str(d / "cov-%p.profraw"))
    subprocess.run([str(b / "cov"), "-runs=0", str(d / "corpus")], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    raws = [str(p) for p in d.glob("cov-*.profraw")]
    subprocess.run(["llvm-profdata", "merge", "-sparse", *raws, "-o", str(d / "cov.profdata")], check=True)
    files = [str(s) for s in T["srcs"]] + [str(x) for x in T["headers"]]
    with open(d / "coverage.json", "w") as f:
        subprocess.run(["llvm-cov", "export", "-format=text", f"-instr-profile={d / 'cov.profdata'}", str(b / "cov"), *files],
                       stdout=f, check=True)
    t = json.load(open(d / "coverage.json"))["data"][0]["totals"]
    crashes = sorted(x.name for x in d.iterdir() if x.name.split("-")[0] in ("crash", "leak", "timeout", "oom"))
    return {"lines": round(t["lines"]["percent"], 2), "branches": round(t["branches"]["percent"], 2),
            "corpus": len(os.listdir(d / "corpus")), "crashes": crashes}


def report(state: dict) -> None:
    out = ROOT / "samples" / "day"
    out.mkdir(parents=True, exist_ok=True)
    L = [f"# 24시간 실험 — {' vs '.join(state['harnesses'])}", "",
         f"TinyXML2, 하네스마다 CPU 1개, {state['chunk_min']}분 구간으로 이어 붙임(구간마다 libFuzzer 재시작). "
         "커버리지는 구간이 끝날 때 코퍼스 전체를 다시 실행해 라이브러리 소스만 집계.", "",
         "| 경과 시간 | " + " | ".join(f"{h} 라인 | {h} 분기" for h in state["harnesses"]) + " |",
         "|---:|" + "---:|---:|" * len(state["harnesses"])]
    n = max(len(state["timeline"][h]) for h in state["harnesses"])
    for i in range(n):
        row = []
        for h in state["harnesses"]:
            p = state["timeline"][h][i] if i < len(state["timeline"][h]) else None
            row += [f"{p['lines']:.2f}%" if p else "", f"{p['branches']:.2f}%" if p else ""]
        hours = state["timeline"][state["harnesses"][0]][i]["hours"] if i < len(state["timeline"][state["harnesses"][0]]) else ""
        L.append(f"| {hours}시간 | " + " | ".join(row) + " |")
    L.append("")
    for h in state["harnesses"]:
        last = state["timeline"][h][-1] if state["timeline"][h] else {}
        L.append(f"- {h}: 크래시·타임아웃 {len(last.get('crashes', []))}개, 코퍼스 {last.get('corpus', 0)}개")
    (out / "timeline.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    json.dump(state, open(out / "timeline.json", "w"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("harnesses", nargs="+")
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--chunk-min", type=int, default=110)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    sp = OUT / "state.json"
    state = json.load(open(sp)) if sp.exists() else {"harnesses": a.harnesses, "hours": a.hours, "chunk_min": a.chunk_min,
                                                     "done_secs": 0, "chunks": 0, "timeline": {h: [] for h in a.harnesses}}
    total = int(state["hours"] * 3600)
    if state["done_secs"] >= total:
        print(f"[day] 이미 끝남 ({state['done_secs'] / 3600:.1f}시간)")
        report(state)
        return
    for h in state["harnesses"]:
        build(h)
    if state["chunks"] == 0:                       # 0시간 지점(빈 코퍼스)은 측정하지 않고 바로 시작
        print(f"[day] 시작: {', '.join(state['harnesses'])}, 총 {state['hours']}시간", flush=True)
    # 앞쪽은 짧게 끊어 초반 곡선을 촘촘히 본다: 10분, 20분, 30분, 그 뒤로 chunk_min분
    early = [10, 20, 30]
    mins = early[state["chunks"]] if state["chunks"] < len(early) else state["chunk_min"]
    secs = min(mins * 60, total - state["done_secs"])
    seed = 5000 + state["chunks"] * 100
    print(f"[day] {time.strftime('%m-%d %H:%M')} 구간 {state['chunks'] + 1}: {secs // 60}분", flush=True)
    with cf.ThreadPoolExecutor(max_workers=len(state["harnesses"])) as ex:
        res = dict(zip(state["harnesses"], ex.map(lambda h: fuzz_chunk(h, secs, seed), state["harnesses"])))
    state["done_secs"] += secs
    state["chunks"] += 1
    with cf.ThreadPoolExecutor(max_workers=len(state["harnesses"])) as ex:
        ms = dict(zip(state["harnesses"], ex.map(measure, state["harnesses"])))
    for h in state["harnesses"]:
        m = ms[h] | {"hours": round(state["done_secs"] / 3600, 2), "restarts": res[h]["restarts"]}
        state["timeline"][h].append(m)
        print(f"[day] {h} {m['hours']}시간: 라인 {m['lines']}% 분기 {m['branches']}% 코퍼스 {m['corpus']} 크래시 {len(m['crashes'])}", flush=True)
    json.dump(state, open(sp, "w"), ensure_ascii=False, indent=1)
    report(state)
    print(f"[day] 진행 {state['done_secs'] / 3600:.1f}/{state['hours']}시간", flush=True)


if __name__ == "__main__":
    main()
