#!/usr/bin/env python3
"""실제 TinyXML2 크래시로 크래시 귀속 정확도를 잰다 (새 규칙 vs 예전 규칙).

사례마다 정답은 실제로 누가 고쳤는지로 정했다: 라이브러리 커밋으로 고쳐진 버그 → 라이브러리(또는 assert·리소스),
TinyXML2 문서의 사용 규칙(문서가 노드를 소유, Clear·delete 뒤 사용 금지)을 어긴 하네스 → 하네스.
사용법: python3 tests/triage_real/run.py   (결과: tests/triage_real/results.md, 정답과 다르면 종료 코드 1)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "out" / "triage_real"


def build(case: dict) -> Path:
    lib = ROOT / "third_party" / case["lib"]
    harness = (HERE / "harnesses" / case["harness"]).resolve()
    d = OUT / case["name"]
    d.mkdir(parents=True, exist_ok=True)
    binary = d / "fuzz"
    if not binary.exists():
        flags = ["-g", "-O1", "-fno-omit-frame-pointer", "-fno-optimize-sibling-calls", "-std=c++17", f"-I{lib}", f"-I{ROOT / 'harnesses' / 'include'}",
                 "-fsanitize=fuzzer,address,undefined"] + (["-DTINYXML2_DEBUG"] if case.get("debug") else [])
        subprocess.run(["clang++", *flags, str(harness), str(lib / "tinyxml2.cpp"), "-o", str(binary)], check=True)
    return binary


def triage(case: dict, binary: Path, legacy: bool) -> str:
    d = OUT / case["name"] / ("legacy" if legacy else "new")
    d.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, GAPFUZZ_TRIAGE_LEGACY="1" if legacy else "0")
    harness = (HERE / "harnesses" / case["harness"]).resolve()
    subprocess.run([sys.executable, "-m", "gapfuzz", "triage", str(HERE / "inputs" / case["name"]),
                    "--binary", str(binary), "--harness", str(harness), "--harness-dir", str(harness.parent),
                    "--harness-dir", str(ROOT / "harnesses" / "include"),
                    "--lib-dir", str(ROOT / "third_party" / case["lib"]), "--repeat", "2", "--out", str(d / "triage.md")],
                   cwd=ROOT, env=env, stdout=subprocess.DEVNULL, check=True)
    t = json.load(open(d / "triage.json"))
    v = t["crashes"][0]["verdict"]
    return v["cls"], v["confidence"], v["reason"], t["crashes"][0]["kind"]


def main():
    cases = json.load(open(HERE / "cases.json"))
    rows, ok_new, ok_old = [], 0, 0
    for c in cases:
        b = build(c)
        new = triage(c, b, legacy=False)
        old = triage(c, b, legacy=True)
        ok_new += new[0] == c["expect"]
        ok_old += old[0] == c["expect"]
        mark = lambda v: ("✓ " if v[0] == c["expect"] else "✗ ") + v[0]
        rows.append(f"| {c['name']} | {new[3]} | {c['expect']} | {mark(old)} | {mark(new)} ({new[1]}) | {c['why']} |")
        print(f"{c['name']:<24} 정답 {c['expect']:<9} 예전 {old[0]:<9} 새 규칙 {new[0]:<9} {new[2][:60]}")
    md = ["# 실제 크래시로 본 크래시 귀속 정확도", "",
          f"사례 {len(cases)}개. 예전 규칙 {ok_old}/{len(cases)}, 새 규칙 {ok_new}/{len(cases)}.", "",
          "| 사례 | 크래시 종류 | 정답 | 예전 규칙 | 새 규칙 (확신) | 정답 근거 |", "|---|---|---|---|---|---|", *rows]
    (HERE / "results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"예전 규칙 {ok_old}/{len(cases)}, 새 규칙 {ok_new}/{len(cases)} -> {HERE / 'results.md'}")
    sys.exit(0 if ok_new == len(cases) else 1)


if __name__ == "__main__":
    main()
