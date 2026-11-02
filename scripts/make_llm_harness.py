#!/usr/bin/env python3
"""팀 실험용 Claude 하네스 만들기: 라이브러리마다 gapfuzz의 '하네스에서 고칠 곳'을 Claude API에 한꺼번에 맡겨
공식 하네스를 고치게 하고, gapfuzz가 검사(컴파일 → 퍼징 → 겨냥 분기가 열렸나 → 크래시 귀속)한 뒤 통과한 것을
harnesses/<라이브러리>/official_llm.* 로 저장한다.

  ANTHROPIC_API_KEY=... python3 scripts/make_llm_harness.py --all
  ANTHROPIC_API_KEY=... python3 scripts/make_llm_harness.py zlib expat

- 맡기는 제안: experiments/targets/<라이브러리>.json에서 applied=true인 것(사람 수정본 official_v2와 같은 집합).
  applied=false인 제안은 대조군이라 맡기지 않는다. 그래서 대조군 분기가 열리지 않는지도 함께 볼 수 있다.
- 제안별로 따로 검증을 통과했던 Claude 수정(samples/llm/runs/.../best.diff)을 참고로 함께 보낸다(--no-hints로 끔).
- 수정 전 분석(out/targets/<라이브러리>/official/r1/gap/gap.json)이 있어야 한다. 없으면
  python3 scripts/tgt.py repeat <라이브러리> official --trials 1 --secs 120 으로 만든다(2분 실험과 같은 조건).
- 기록: samples/llm/combined/<라이브러리>/{report.md, best.diff, log.json, request.md}, 요약 samples/llm/combined/SUMMARY.md
- API 키는 환경 변수로만 받는다. 파일이나 로그에 남기지 않는다.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gapfuzz.llmfix import DEFAULT_MODEL, run  # noqa: E402

LIBS = ["pugixml", "cjson", "jsoncpp", "zlib", "expat", "json-c"]
TAG = "official_combined"
OUT = ROOT / "samples" / "llm" / "combined"


def applied_fixes(lib: str) -> tuple[list[int], list[int]]:
    d = json.load(open(ROOT / "experiments" / "targets" / f"{lib}.json"))
    on = sorted({b["fix"] for b in d["branches"] if b["applied"]})
    off = sorted({b["fix"] for b in d["branches"] if not b["applied"]})
    return on, off


def make(lib: str, a) -> dict:
    on, off = applied_fixes(lib)
    before = ROOT / "out" / "targets" / lib / "official" / "r1" / "gap" / "gap.json"
    if not before.exists():
        raise SystemExit(f"[make_llm] {lib}: 수정 전 분석이 없습니다 → python3 scripts/tgt.py repeat {lib} official --trials 1 --secs 120")
    print(f"[make_llm] {lib}: 제안 {on}를 한 하네스에 (대조군 {off}는 맡기지 않음)", flush=True)
    res = run(lib, "official", on if len(on) > 1 else on[0], str(before), a.secs, a.trials, a.tries, a.model,
              a.mock.split(",") if a.mock else None, out_name=TAG, hints=not a.no_hints)
    work = ROOT / "out" / "llm" / lib / TAG
    dst = OUT / lib
    dst.mkdir(parents=True, exist_ok=True)
    for f in ("report.md", "best.diff", "log.json", "request.md"):
        if (work / f).exists():
            shutil.copy(work / f, dst / f)
    best = res["best"]
    row = {"lib": lib, "fixes": on, "controls": off, "ok": bool(best), "tries": len(res["log"])}
    if best:
        src = ROOT / best["harness"]
        out = ROOT / "harnesses" / lib / f"official_llm{src.suffix}"
        model = "mock" if a.mock else a.model
        head = (f"// [gapfuzz-llm] 이 파일은 Claude({model})가 gapfuzz 제안 {','.join(map(str, on))}를 공식 하네스에 적용하고\n"
                f"// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness.py, 기록: samples/llm/combined/{lib}/).\n")
        out.write_text(head + src.read_text(encoding="utf-8"), encoding="utf-8")
        row.update({"opened": best["opened"], "total": best["total"], "per_fix": best.get("per_fix", {}),
                    "crashes": [c["cls"] for c in best.get("crashes", [])], "harness": str(out.relative_to(ROOT))})
        print(f"[make_llm] {lib}: 통과 → {row['harness']} (겨냥 분기 {best['opened']}/{best['total']})", flush=True)
    else:
        print(f"[make_llm] {lib}: 통과한 하네스가 없습니다. {dst / 'report.md'}를 보세요", flush=True)
    usage = [e.get("usage") or {} for e in res["log"]]
    row["tokens"] = [sum(u.get("input_tokens", 0) for u in usage), sum(u.get("output_tokens", 0) for u in usage)]
    json.dump(row, open(dst / "summary.json", "w"), ensure_ascii=False, indent=1)
    return row


def summary() -> None:
    rows = [json.load(open(p)) for p in sorted(OUT.glob("*/summary.json"))]
    L = ["# Claude가 만든 팀 실험용 하네스 (official_llm)", "",
         "라이브러리마다 gapfuzz의 '하네스에서 고칠 곳'(대조군 제외)을 Claude API에 한꺼번에 맡겨 공식 하네스를 고치게 하고,",
         "gapfuzz가 컴파일 → 퍼징 → 겨냥 분기 확인 → 크래시 귀속으로 검사해 통과한 하네스입니다. 팀 실험은 이 하네스를 공식 하네스와 비교합니다.", "",
         "| 라이브러리 | 맡긴 제안 | 대조군 | 결과 | 겨냥 분기 열림 | 제안별 | 시도 | 토큰(입력/출력) |", "|---|---|---|---|---:|---|---:|---|"]
    for r in rows:
        pf = ", ".join(f"{k}: {v[0]}/{v[1]}" for k, v in r.get("per_fix", {}).items()) or "–"
        L.append(f"| {r['lib']} | {','.join(map(str, r['fixes']))} | {','.join(map(str, r['controls'])) or '–'} | "
                 f"{'통과' if r['ok'] else '실패'} | {r.get('opened', '–')}/{r.get('total', '–')} | {pf} | {r['tries']} | "
                 f"{r['tokens'][0]:,}/{r['tokens'][1]:,} |")
    (OUT / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[make_llm] 요약 → {OUT / 'SUMMARY.md'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("libs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--secs", type=int, default=60, help="검사용 퍼징 시간(초, 회당)")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--tries", type=int, default=3, help="실패하면 이유를 돌려주고 다시 받는 최대 횟수")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--no-hints", action="store_true", help="제안별 수정(best.diff)을 참고로 보내지 않음")
    ap.add_argument("--mock", help=argparse.SUPPRESS)          # 시험용: API 대신 쓸 응답 파일
    a = ap.parse_args()
    libs = LIBS if a.all else a.libs
    if not libs:
        ap.error("라이브러리 이름이나 --all")
    for lib in libs:
        make(lib, a)
    summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
