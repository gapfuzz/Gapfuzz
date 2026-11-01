#!/usr/bin/env python3
"""버그 재발견 실험: 이미 고쳐진 버그가 있는 옛 버전에서 하네스마다 그 버그를 찾는지, 몇 초 걸리는지 잰다.

사용법: python3 scripts/bug_bench.py --bug del --secs 600 --trials 5 official stateful stateful_v3
  - 바이너리: out/bugs/<bug>/<하네스>/fuzz (scripts/build.sh를 TINYXML2_DIR=옛 버전으로 빌드)
  - 회차 r의 시드 = 3000 + r, 딕셔너리 dicts/xml.dict
  - 첫 크래시에서 멈추고 걸린 시간(초)과 크래시 종류·맨 위 라이브러리 함수를 기록, 크래시는 귀속 분석까지
결과: out/bugs/<bug>/results.json, 회차별 디렉터리 out/bugs/<bug>/<하네스>/t<r>/
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUGS = {
    "cve": {"lib": "third_party/tx_cve", "title": "CVE-2024-50614/50615 (문자 참조 정수 경계 assert)",
            "match": r"GetCharacterRef"},   # 디버그 빌드라 다른 assert도 켜져 있으므로 이 함수의 assert만 센다
    "del": {"lib": "third_party/tx_del", "title": "#1048 DeleteNode(nullptr) 세그폴트",
            "match": r"DeleteNode"},
}


def run_one(bug: str, h: str, r: int, secs: int, nice: int) -> dict:
    b = ROOT / "out" / "bugs" / bug / h
    d = b / f"t{r}"
    subprocess.run(["rm", "-rf", str(d)], check=True)
    (d / "corpus").mkdir(parents=True)
    args = ["nice", "-n", str(nice), str(b / "fuzz"), f"-max_total_time={secs}", f"-seed={3000 + r}",
            f"-dict={ROOT / 'dicts' / 'xml.dict'}", "-rss_limit_mb=2048", "-timeout=10",
            f"-artifact_prefix={d}/", str(d / "corpus")]
    t0 = time.time()
    with open(d / "fuzz.log", "w") as log:
        subprocess.run(args, stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.time() - t0
    crashes = sorted(f for f in os.listdir(d) if f.split("-")[0] in ("crash", "leak", "timeout", "oom"))
    text = (d / "fuzz.log").read_text(errors="replace")
    kind = ""
    m = re.search(r"ERROR: (?:AddressSanitizer|libFuzzer|UndefinedBehaviorSanitizer): ([\w-]+)", text)
    if m:
        kind = m.group(1)
    elif "Assertion" in text:
        kind = "assertion"
    frames = re.findall(r"#\d+ 0x[0-9a-f]+ in (\S+)", text)
    top = next((f for f in frames if "tinyxml2::" in f), "")
    found = bool(crashes) and bool(re.search(BUGS[bug]["match"], text))
    res = {"bug": bug, "harness": h, "trial": r, "found": found, "crashed": bool(crashes),
           "seconds": round(elapsed, 1) if crashes else None, "kind": kind, "top_lib_frame": top,
           "crash_file": crashes[0] if crashes else None}
    if crashes:
        lib = ROOT / BUGS[bug]["lib"]
        subprocess.run([sys.executable, "-m", "gapfuzz", "triage", str(d / crashes[0]), "--binary", str(b / "fuzz"),
                        "--harness", str(ROOT / "harnesses" / f"{h}.cpp"), "--harness-dir", str(ROOT / "harnesses"),
                        "--lib-dir", str(lib), "--out", str(d / "triage.md")],
                       cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tj = d / "triage.json"
        if tj.exists():
            t = json.load(open(tj))
            if t.get("crashes"):
                res["triage"] = t["crashes"][0]["verdict"]["cls"]
    print(f"[bench] {bug} {h} t{r}: {'찾음' if found else ('다른 크래시' if crashes else '못 찾음')} "
          f"{res['seconds']}s {kind} {top}", flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("harnesses", nargs="+")
    ap.add_argument("--bug", required=True, choices=sorted(BUGS))
    ap.add_argument("--secs", type=int, default=600)
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--nice", type=int, default=19)
    a = ap.parse_args()
    out = ROOT / "out" / "bugs" / a.bug / "results.json"
    results = json.load(open(out)) if out.exists() else []
    have = {(x["harness"], x["trial"]) for x in results}
    for r in range(1, a.trials + 1):
        for h in a.harnesses:
            if (h, r) in have:
                continue
            results.append(run_one(a.bug, h, r, a.secs, a.nice))
            json.dump(results, open(out, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
