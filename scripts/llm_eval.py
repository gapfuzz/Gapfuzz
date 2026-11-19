#!/usr/bin/env python3
"""LLM 하네스 수정 평가: 라이브러리의 '하네스에서 고칠 곳'을 Claude에게 하나씩 맡기고(gapfuzz llmfix),
사람이 같은 제안을 적용했을 때(evaluation/artifacts/verify/*.md)와 비교한다.

사용법: ANTHROPIC_API_KEY=... python3 scripts/llm_eval.py [--secs 60] [--trials 2] [--tries 3] [--only zlib]
  - 이미 끝난 제안(out/llm/<라이브러리>/<하네스>_fix<번호>/log.json)은 건너뛴다 (끊겨도 다시 실행하면 이어서)
  - 결과: evaluation/artifacts/llm/summary.md, evaluation/artifacts/llm/summary.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gapfuzz.llmfix import DEFAULT_MODEL, run  # noqa: E402

# (라이브러리, 수정 전 하네스, 수정 전 gap.json, 사람이 적용한 결과 md들)
CASES = [
    ("tinyxml2", "official", "out/repeat/official/r1/gap/gap.json", ["official_to_v2.md", "official_v2_to_v3.md"]),
    ("pugixml", "official", None, ["pugixml_official_to_v2.md"]),
    ("cjson", "official", None, ["cjson_official_to_v2.md"]),
    ("jsoncpp", "official", None, ["jsoncpp_official_to_v2.md"]),
    ("zlib", "official", None, ["zlib_official_to_v2.md"]),
    ("expat", "official", None, ["expat_official_to_v2.md"]),
    ("json-c", "official", None, ["json-c_official_to_v2.md"]),
]
ROW_RE = re.compile(r"^\| (\d+) \| (.+?) \| (적용|미적용) \| (\d+) \| (\d+) \|$")


def human_rows(mds):
    rows = {}
    for md in mds:
        for line in (ROOT / "evaluation" / "artifacts" / "verify" / md).read_text(encoding="utf-8").splitlines():
            m = ROW_RE.match(line)
            if m and m.group(3) == "적용":
                rows[m.group(2).strip()] = (int(m.group(5)), int(m.group(4)))
    return rows


def key(fix):
    title = fix["apis"][0].split("(")[0] if fix.get("apis") else "?"
    return f"{title} · {fix['param_name']}" if fix.get("param_name") else title


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--secs", type=int, default=60)
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--tries", type=int, default=3)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--only")
    a = ap.parse_args()
    rows = []
    for lib, h, before, mds in CASES:
        if a.only and lib != a.only:
            continue
        bp = ROOT / (before or f"out/targets/{lib}/{h}/r1/gap/gap.json")
        fixes = json.load(open(bp)).get("harness_fixes", [])
        human = human_rows(mds)
        for i, f in enumerate(fixes, 1):
            logp = ROOT / "out" / "llm" / lib / f"{h}_fix{i}" / "log.json"
            if not logp.exists():
                try:
                    run(lib, h, i, str(bp), a.secs, a.trials, a.tries, a.model, None)
                except SystemExit as e:
                    print(f"[eval] {lib}/{h} 제안 {i} 실패: {e}", flush=True)
                    continue
            log = json.load(open(logp))
            best = next((t for t in log["tries"] if t["try"] == log["best"]), None)
            last = log["tries"][-1]
            hk = key(f)
            rows.append({"lib": lib, "harness": h, "fix": i, "verdict": f["verdict"], "what": hk, "targets": len(f["blocked"]),
                         "llm_opened": best["opened"] if best else 0, "llm_ok": bool(best), "tries": len(log["tries"]),
                         "first_try_ok": bool(log["tries"][0].get("ok")),
                         "harness_crashes": sum(1 for t in log["tries"] for c in t.get("crashes", []) if c["cls"] != "LIBRARY"),
                         "library_crashes": sum(1 for t in log["tries"] for c in t.get("crashes", []) if c["cls"] == "LIBRARY"),
                         "compile_fail": sum(1 for t in log["tries"] if t["stage"] == "compile"),
                         "tokens_in": sum((t.get("usage") or {}).get("input_tokens", 0) for t in log["tries"]),
                         "tokens_out": sum((t.get("usage") or {}).get("output_tokens", 0) for t in log["tries"]),
                         "human": human.get(hk)})
            write(rows, a.model)


def write(rows, model):
    out = ROOT / "evaluation" / "artifacts" / "llm"
    out.mkdir(parents=True, exist_ok=True)
    json.dump(rows, open(out / "summary.json", "w"), ensure_ascii=False, indent=1)
    both = [r for r in rows if r["human"]]
    L = ["# LLM(Claude) 하네스 수정 평가", "",
         f"모델 `{model}`. 제안 하나마다 Claude가 하네스를 고치고, gapfuzz가 컴파일 → 60초 × 2회 퍼징 → 겨냥한 분기가 열렸는지 → 크래시 귀속으로 검사.",
         "실패하면 이유를 같은 대화로 돌려주고 최대 3번까지 다시 받음. 사람 결과는 evaluation/artifacts/verify/*.md(같은 제안을 사람이 적용, 120초 × 5회).", "",
         f"- 제안 {len(rows)}개 중 통과 {sum(r['llm_ok'] for r in rows)}개 (첫 시도에 통과 {sum(r['first_try_ok'] for r in rows)}개)",
         f"- 겨냥한 분기 {sum(r['targets'] for r in rows)}개 중 열림 {sum(r['llm_opened'] for r in rows)}개",
         f"- 사람도 적용한 제안 {len(both)}개: 사람 {sum(r['human'][0] for r in both)}/{sum(r['human'][1] for r in both)}, "
         f"LLM {sum(r['llm_opened'] for r in both)}/{sum(r['targets'] for r in both)}",
         f"- 하네스 탓 크래시(걸러 냄) {sum(r['harness_crashes'] for r in rows)}번, 컴파일 실패 {sum(r['compile_fail'] for r in rows)}번, "
         f"라이브러리 결함 의심 {sum(r['library_crashes'] for r in rows)}번",
         f"- 토큰: 입력 {sum(r['tokens_in'] for r in rows):,}, 출력 {sum(r['tokens_out'] for r in rows):,}", "",
         "| 라이브러리 | 제안 | 판정 | 겨냥 | LLM 열림 | 시도 | 걸러 낸 크래시 | 사람 열림 |", "|---|---|---|---:|---:|---:|---:|---:|"]
    for r in rows:
        hm = f"{r['human'][0]}/{r['human'][1]}" if r["human"] else "–"
        L.append(f"| {r['lib']}/{r['harness']} | {r['fix']}. {r['what']} | {r['verdict']} | {r['targets']} | "
                 f"{r['llm_opened']}{'' if r['llm_ok'] else ' (실패)'} | {r['tries']} | {r['harness_crashes']} | {hm} |")
    (out / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
