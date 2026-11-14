#!/usr/bin/env python3
"""장시간 반복 실험 실행기.

사용법: python3 scripts/long_runs.py --trials 10 --secs 3600 --jobs 2 --budget-min 115 official stateful stateful_v3

- 회차 r의 퍼저 시드는 1000+r (모든 하네스가 같은 시드)
- 회차 순서를 하네스끼리 섞어서(r1의 하네스들 → r2의 하네스들 …) 기계 상태 차이가 한쪽에 몰리지 않게 한다
- 이미 끝난 회차(coverage.json + gap.json 있음)는 건너뛰므로, 중간에 끊겨도 다시 실행하면 이어서 돈다
- --budget-min: 이번 실행에서 쓸 수 있는 시간(분). 남은 시간이 한 회차보다 짧으면 새 회차를 시작하지 않는다
결과: out/long/<하네스>/r<회차>/{coverage.json, coverage_summary.txt, gap/gap.json, fuzz.log}
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def done(d: Path) -> bool:
    return (d / "coverage.json").exists() and (d / "gap" / "gap.json").exists()


def start(h: str, r: int, secs: int, out: Path, lib: Path, dict_path: Path, seed_base: int):
    d = out / h / f"r{r}"
    if d.exists():
        subprocess.run(["rm", "-rf", str(d)], check=True)
    d.mkdir(parents=True)
    os.symlink(ROOT / "out" / f"asan_{h}" / "fuzz", d / "fuzz")
    os.symlink(ROOT / "out" / f"asan_{h}" / "cov", d / "cov")
    env = dict(os.environ, FUZZ_SEED=str(seed_base + r), HARNESS_SRC=str(ROOT / "harnesses" / f"{h}.cpp"),
               TINYXML2_DIR=str(lib))
    log = open(d / "run.log", "w")
    p = subprocess.Popen([str(ROOT / "scripts" / "run.sh"), str(d), str(secs), str(dict_path)],
                         env=env, stdout=log, stderr=subprocess.STDOUT)
    return p, d, h, r


def finish(d: Path, h: str, r: int, lib: Path):
    subprocess.run([sys.executable, "-m", "gapfuzz", "analyze", "--name", f"{h}-r{r}",
                    "--header", str(lib / "tinyxml2.h"), "--source", str(lib / "tinyxml2.cpp"),
                    "--harness", str(ROOT / "harnesses" / f"{h}.cpp"),
                    "--include", str(ROOT / "harnesses" / "include"),
                    "--coverage", str(d / "coverage.json"), "--out", str(d / "gap")],
                   cwd=ROOT, stdout=subprocess.DEVNULL, check=True)
    summ = (d / "coverage_summary.txt").read_text().strip().splitlines()[-1].split()
    crashes = sum(1 for f in os.listdir(d) if f.split("-")[0] in ("crash", "leak", "timeout", "oom"))
    print(f"[long] {time.strftime('%H:%M')} {h} r{r}: lines {summ[9]} branches {summ[12]} crashes={crashes}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("harnesses", nargs="+")
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--secs", type=int, default=3600)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--budget-min", type=float, default=115)
    ap.add_argument("--out", default=str(ROOT / "out" / "long"))
    ap.add_argument("--dict", default=str(ROOT / "dicts" / "xml.dict"))
    ap.add_argument("--seed-base", type=int, default=1000, help="회차 r의 시드 = seed-base + r")
    a = ap.parse_args()
    out = Path(a.out)
    lib = Path(os.environ.get("TINYXML2_DIR", ROOT / "third_party" / "tinyxml2"))
    dict_path = Path(a.dict)
    deadline = time.time() + a.budget_min * 60
    per_run = a.secs + 300  # 퍼징 + 코퍼스 재생·분석 여유

    queue = [(h, r) for r in range(1, a.trials + 1) for h in a.harnesses if not done(out / h / f"r{r}")]
    print(f"[long] 남은 회차 {len(queue)}개", flush=True)
    running = []
    while queue or running:
        while queue and len(running) < a.jobs and time.time() + per_run < deadline:
            h, r = queue.pop(0)
            running.append(start(h, r, a.secs, out, lib, dict_path, a.seed_base))
        if not running:
            break
        time.sleep(10)
        for item in list(running):
            p, d, h, r = item
            if p.poll() is not None:
                running.remove(item)
                finish(d, h, r, lib)
    print(f"[long] 이번 실행 종료, 남은 회차 {len(queue)}개", flush=True)


if __name__ == "__main__":
    main()
