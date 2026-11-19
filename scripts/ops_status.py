#!/usr/bin/env python3
"""이미 만든 gapfuzz_ops의 상태 표를 기존 기록에서 계산한다. 하네스를 다시 만들지 않는다.

  python3 scripts/ops_status.py            # 표를 찍고 evaluation/artifacts/llm/ops/STATUS.md에 저장
  python3 scripts/ops_status.py --all      # 다시 만들기 전 기록(_union_run1 등)도 함께

읽는 것: evaluation/artifacts/llm/ops/<라이브러리>/_union*/log.json (llmops가 남긴 기록)
  생성 상태   COMPLETE = 요청한 API 전부 실행, PARTIAL = 일부 실행, REJECTED = 채택된 시도 없음
  실험 포함   채택된 시도가 검사 퍼징에서 크래시 없이 통과했을 때만 "예"
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def name(api: str) -> str:
    return api.split("(")[0]


def status(log: dict) -> dict:
    tries = log.get("tries", [])
    best = next((t for t in tries if t.get("try") == log.get("best")), None)
    rejected = [f"{t.get('try')}: " + ("컴파일 실패" if t.get("stage") == "compile" else
                                       ", ".join(c.get("cls", "?") for c in t.get("crashes", [])) or
                                       ("원래 API 사라짐" if t.get("regressed") else "실행된 API 없음"))
                for t in tries if t is not best and not (t.get("ok") and not t.get("crashes"))]
    if not best:
        return {"gen": "REJECTED", "called": 0, "total": len(log.get("chosen", [])), "missing": [], "crashes": 0,
                "eligible": False, "best": None, "tries": len(tries), "rejected": rejected}
    crashes = len(best.get("crashes", []))
    called, total = best.get("called", 0), best.get("total", 0)
    return {"gen": "COMPLETE" if called == total and total else "PARTIAL", "called": called, "total": total,
            "missing": [name(a) for a in best.get("missing", [])], "crashes": crashes,
            "eligible": bool(log.get("saved")) and crashes == 0 and not best.get("regressed"),
            "best": best.get("try"), "tries": len(tries), "rejected": rejected}


def main() -> int:
    ap = argparse.ArgumentParser(description="gapfuzz_ops 상태 표 (기존 기록에서 계산)")
    ap.add_argument("--all", action="store_true", help="다시 만들기 전 기록(_union_run1 등)도 포함")
    ap.add_argument("--root", default=str(ROOT / "evaluation" / "artifacts" / "llm" / "ops"))
    a = ap.parse_args()
    base = Path(a.root)
    rows = []
    for p in sorted(base.glob("*/_union*/log.json")):
        run = p.parent.name
        if run != "_union" and not a.all:
            continue
        s = status(json.loads(p.read_text(encoding="utf-8")))
        rows.append((p.parent.parent.name, "" if run == "_union" else run.replace("_union_", ""), s))
    if not rows:
        print(f"기록이 없습니다: {base}/<라이브러리>/_union/log.json")
        return 1
    L = ["# gapfuzz_ops 상태", "",
         "기존 기록(`evaluation/artifacts/llm/ops/<라이브러리>/_union/log.json`)에서 계산했습니다. 하네스는 다시 만들지 않았습니다.", "",
         "- 생성 상태: `COMPLETE` 요청한 API 전부 실행 · `PARTIAL` 일부 실행 · `REJECTED` 채택된 시도 없음",
         "- 실험 포함: 채택된 시도가 검사 퍼징(60초 × 2회)에서 크래시 없이 통과했을 때만 \"예\"", "",
         "| 라이브러리 | 기록 | 생성 상태 | API 달성도 | 실험 포함 | 채택한 시도 | 크래시 | 실행되지 않은 API | 탈락한 시도 |",
         "|---|---|---|---:|---|---:|---:|---|---|"]
    for lib, run, s in rows:
        pct = f" ({100 * s['called'] / s['total']:.0f}%)" if s["total"] else ""
        L.append(f"| `{lib}` | {run or '현재'} | {s['gen']} | {s['called']}/{s['total']}{pct} | {'예' if s['eligible'] else '아니오'} | "
                 f"{s['best'] or '-'}/{s['tries']} | {s['crashes']} | {', '.join('`' + m + '`' for m in s['missing']) or '-'} | "
                 f"{'; '.join(s['rejected']) or '-'} |")
    cur = [s for _, run, s in rows if not run]
    L += ["", f"현재 기록 {len(cur)}개: COMPLETE {sum(s['gen'] == 'COMPLETE' for s in cur)}, PARTIAL {sum(s['gen'] == 'PARTIAL' for s in cur)}, "
              f"REJECTED {sum(s['gen'] == 'REJECTED' for s in cur)}, 실험 포함 {sum(s['eligible'] for s in cur)}", ""]
    out = "\n".join(L)
    print(out)
    (base / "STATUS.md").write_text(out, encoding="utf-8")
    print(f"[ops_status] -> {base / 'STATUS.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
