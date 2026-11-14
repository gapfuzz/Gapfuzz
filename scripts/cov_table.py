#!/usr/bin/env python3
"""하네스 여러 개의 반복 실행 결과를 한 표로 요약한다 (중앙값 [최솟값–최댓값]).

  python3 scripts/tgt.py repeat tinyxml2 official official_llm official_llm_ops --trials 3 --secs 600
  python3 scripts/cov_table.py tinyxml2 official official_llm official_llm_ops

읽는 곳: out/targets/<라이브러리>/<하네스>/r*/{coverage.json, gap/gap.json}   (--sub long3600 이면 그 아래)
결과: 화면 출력 + out/cov_table/<라이브러리>.md
"""
import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def med(xs, fmt="{:.2f}"):
    if not xs:
        return "–"
    m = fmt.format(statistics.median(xs))
    return m if len(xs) == 1 else f"{m} [{fmt.format(min(xs))}–{fmt.format(max(xs))}]"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lib")
    ap.add_argument("harnesses", nargs="+")
    ap.add_argument("--sub", default="", help="결과 하위 폴더 (예: long3600)")
    a = ap.parse_args()
    rows = []
    for h in a.harnesses:
        base = ROOT / "out" / "targets" / a.lib / h
        base = base / a.sub if a.sub else base
        runs = sorted(p for p in base.glob("r*") if (p / "coverage.json").exists())
        ln, br, nc, crashes = [], [], [], 0
        for r in runs:
            t = json.load(open(r / "coverage.json"))["data"][0]["totals"]
            ln.append(t["lines"]["percent"]); br.append(t["branches"]["percent"])
            g = r / "gap" / "gap.json"
            if g.exists():
                res = json.load(open(g))["results"]
                nc.append(sum(1 for x in res if x["category"] == "NOT_CALLED"))
                total = len(res)
            crashes += sum(1 for f in r.iterdir() if f.name.split("-")[0] in ("crash", "leak", "timeout", "oom"))
        rows.append((h, len(runs), med(ln), med(br), (med(nc, "{:.0f}") + (f" / {total}" if nc else "")), crashes))
    md = [f"# 하네스 비교 — {a.lib}" + (f" ({a.sub})" if a.sub else ""), "",
          "| 하네스 | 회차 | 라인 % | 분기 % | 호출 안 함 API | 크래시 파일 |", "|---|---:|---:|---:|---:|---:|"]
    md += [f"| {h} | {n} | {l} | {b} | {c} | {k} |" for h, n, l, b, c, k in rows]
    md += ["", "값은 중앙값 [최솟값–최댓값]. 커버리지는 라이브러리 소스만 집계. 같은 회차는 같은 시드."]
    text = "\n".join(md)
    out = ROOT / "out" / "cov_table"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.lib}.md").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
