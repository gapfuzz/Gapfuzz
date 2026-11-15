#!/usr/bin/env python3
"""대표 하네스(official)가 아닌 OSS-Fuzz 하네스도 Claude API로 고쳐서 <하네스 이름>_llm 으로 저장한다.

  python3 scripts/make_llm_harness_extra.py zlib --list        # 어떤 하네스의 어떤 제안을 맡길지만 본다 (키 없이)
  ANTHROPIC_API_KEY=... python3 scripts/make_llm_harness_extra.py zlib
  ANTHROPIC_API_KEY=... python3 scripts/make_llm_harness_extra.py --all
  ANTHROPIC_API_KEY=... python3 scripts/make_llm_harness_extra.py libyaml --primary   # official_llm이 없는 라이브러리는 대표 하네스도

scripts/make_llm_harness.py(대표 하네스 → official_llm)와 같은 흐름이다: 제안을 한 하네스에 한꺼번에 맡기고,
gapfuzz가 검사(컴파일 → 퍼징 → 겨냥 분기가 열렸나 → 크래시 귀속)한 뒤 통과한 것만 저장한다.
다른 점은 맡길 제안을 사람이 고르지 않고 아래 두 규칙으로 고른다는 것이다.

  규칙 1 (하네스 전체 기준). 그 하네스의 '고칠 곳' 제안 중, 겨냥한 분기가 OSS-Fuzz 하네스 전체를 합친 커버리지
         (python3 scripts/tgt.py union <라이브러리>)에서도 여전히 막혀 있는 것만 맡긴다.
         다른 하네스가 이미 여는 분기는 고칠 이유가 없다.
  규칙 2 (한 번만). 같은 분기를 여러 하네스가 겨냥하면 목록에서 앞선 하네스 하나에만 맡긴다.
         대표 하네스가 먼저다: official_llm이 이미 맡은 분기(experiments/targets/<라이브러리>.json의 applied=true)는 빼고 시작한다.
         같은 분기를 여러 하네스에서 고쳐도 합친 커버리지는 늘지 않고, 고친 하네스마다 실험 시간(1시간 × 10회)만 늘기 때문이다.
         (--no-dedup 으로 끄면 규칙 1만 쓴다.)

맡길 제안이 없는 하네스는 고친 버전을 만들지 않는다. 팀 실험(exp.py run --plan union)은 그 하네스를 원본 그대로 쓴다.
이미 <하네스 이름>_llm 이 있으면 건너뛴다(--force 로 다시 만듦. 실험을 시작한 뒤에는 쓰지 말 것).

기록: samples/llm/combined/<라이브러리>/<하네스>/{report.md, best.diff, log.json, request.md, summary.json}
요약: samples/llm/combined/EXTRA.md
API 키는 환경 변수로만 받는다. 파일이나 로그에 남기지 않는다.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gapfuzz.llmfix import DEFAULT_MODEL, _tgt, run  # noqa: E402
from gapfuzz.verify import verify  # noqa: E402

LIBS = ["cjson", "jsoncpp", "http-parser", "expat", "pugixml", "tinyxml2", "libucl", "yyjson", "json-c", "zlib", "libyaml"]
OUT = ROOT / "samples" / "llm" / "combined"
EXTS = (".c", ".cc", ".cpp")


def fixed_name(h: str) -> str:
    return "official_llm" if h == "official" else f"{h}_llm"


def has(base: Path, name: str) -> bool:
    return any((base / f"{name}{x}").exists() for x in EXTS)


def gap_of(lib: str, h: str) -> Path:
    return ROOT / "out" / "targets" / lib / h / "r1" / "gap" / "gap.json"


def key_of(r: dict) -> tuple:
    return (r["api"], r["line"], r.get("col", 0), r["never"])


def primary_claims(lib: str, checked: list[dict]) -> set:
    """official_llm이 이미 맡은 분기. 사람이 고른 목록(experiments/targets)이 있으면 applied=true인 제안만, 없으면 전부."""
    p = ROOT / "experiments" / "targets" / f"{lib}.json"
    on = None
    if p.exists():
        on = {b["fix"] for b in json.load(open(p))["branches"] if b["applied"]}
    return {key_of(r) for i, g in enumerate(checked, 1) if on is None or i in on
            for r in g["checks"] if r["state"] == "STILL"}


def plan(lib: str, a) -> tuple[dict, list[dict]]:
    """하네스마다 맡길 제안 번호를 고른다. [(하네스, 제안 번호들, 설명 줄들)]"""
    tg = _tgt()
    t = tg.load(lib)
    hs = tg.ossfuzz_harnesses(t)
    ugap = ROOT / "out" / "targets" / lib / "_union" / "r1" / "gap" / "gap.json"
    if not ugap.exists() or any(not gap_of(lib, h).exists() for h in hs):
        print(f"[extra] {lib}: 합친 커버리지가 없어 먼저 만듭니다 (python3 scripts/tgt.py union {lib})", flush=True)
        tg.union(t)
    union = json.load(open(ugap))
    base = ROOT / t.get("harness_dir", f"harnesses/{t['name']}")
    claimed, rows = set(), []
    for h in hs:
        checked = verify(json.load(open(gap_of(lib, h))), [union])
        primary = h == hs[0]
        if primary and has(base, "official_llm"):
            claimed |= primary_claims(lib, checked)              # 이미 있는 official_llm이 맡은 분기
            rows.append({"harness": h, "fixes": [], "note": "official_llm이 이미 있음", "detail": []})
            continue
        if primary and not a.primary:
            rows.append({"harness": h, "fixes": [], "note": "대표 하네스 (--primary 를 주면 official_llm을 만듦)", "detail": []})
            continue
        sel, detail = [], []
        for i, g in enumerate(checked, 1):
            still = {key_of(r) for r in g["checks"] if r["state"] == "STILL"}
            new = still if a.no_dedup else still - claimed
            title = g["apis"][0].split("(")[0] if g.get("apis") else "?"
            what = f"{title} · {g['param_name']}" if g.get("param_name") else title
            if not still:
                why = "다른 하네스가 이미 엶"
            elif not new:
                why = "앞선 하네스가 맡음"
            else:
                why = f"맡김 (합쳐도 막힌 분기 {len(still)}개 중 새로 맡는 것 {len(new)}개)"
                sel.append(i)
                claimed |= still
            detail.append(f"{i}. [{g['verdict']}] {what}: {why}")
        note = "" if sel else ("고칠 곳 없음" if not checked else "맡길 제안 없음")
        if sel and has(base, fixed_name(h)) and not a.force:
            note = f"{fixed_name(h)}이 이미 있음, 건너뜀"
        rows.append({"harness": h, "fixes": sel, "note": note, "detail": detail})
    return t, rows


def make(lib: str, h: str, fixes: list[int], t: dict, a) -> dict:
    tag = f"{h}_combined"
    res = run(lib, h, fixes if len(fixes) > 1 else fixes[0], str(gap_of(lib, h)), a.secs, a.trials, a.tries, a.model,
              a.mock.split(",") if a.mock else None, out_name=tag, hints=False)
    work = ROOT / "out" / "llm" / lib / tag
    dst = OUT / lib / h
    dst.mkdir(parents=True, exist_ok=True)
    for f in ("report.md", "best.diff", "log.json", "request.md"):
        if (work / f).exists():
            shutil.copy(work / f, dst / f)
    best = res["best"]
    row = {"lib": lib, "harness": h, "fixes": fixes, "ok": bool(best), "tries": len(res["log"]),
           "model": "mock" if a.mock else a.model, "dedup": not a.no_dedup}
    if best:
        src = ROOT / best["harness"]
        out = ROOT / t.get("harness_dir", f"harnesses/{t['name']}") / f"{fixed_name(h)}{src.suffix}"
        head = (f"// [gapfuzz-llm] 이 파일은 Claude({row['model']})가 gapfuzz 제안 {','.join(map(str, fixes))}를 OSS-Fuzz 하네스 {h}에 적용하고\n"
                f"// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: samples/llm/combined/{lib}/{h}/).\n")
        out.write_text(head + src.read_text(encoding="utf-8"), encoding="utf-8")
        row.update({"opened": best["opened"], "total": best["total"], "per_fix": best.get("per_fix", {}),
                    "crashes": [c["cls"] for c in best.get("crashes", [])], "saved": str(out.relative_to(ROOT))})
        print(f"[extra] {lib}/{h}: 통과 → {row['saved']} (겨냥 분기 {best['opened']}/{best['total']})", flush=True)
    else:
        print(f"[extra] {lib}/{h}: 통과한 하네스가 없습니다. {dst / 'report.md'}를 보세요", flush=True)
    usage = [e.get("usage") or {} for e in res["log"]]
    row["tokens"] = [sum(u.get("input_tokens", 0) for u in usage), sum(u.get("output_tokens", 0) for u in usage)]
    json.dump(row, open(dst / "summary.json", "w"), ensure_ascii=False, indent=1)
    return row


def summary() -> None:
    rows = [json.load(open(p)) for p in sorted(OUT.glob("*/*/summary.json"))]
    if not rows:
        return
    L = ["# Claude가 고친 추가 하네스 (<하네스 이름>_llm)", "",
         "대표 하네스가 아닌 OSS-Fuzz 하네스에서, 하네스 전체를 합친 커버리지로도 막혀 있는 분기를 겨냥한 제안만 골라 Claude API에 맡긴 결과입니다.",
         "같은 분기는 한 하네스에만 맡겼습니다(scripts/make_llm_harness_extra.py의 규칙 1, 2).", "",
         "| 라이브러리 | 하네스 | 모델 | 맡긴 제안 | 결과 | 겨냥 분기 열림 | 시도 | 토큰(입력/출력) |", "|---|---|---|---|---|---:|---:|---|"]
    for r in rows:
        L.append(f"| {r['lib']} | {r['harness']} | {r.get('model', '?')} | {','.join(map(str, r['fixes']))} | {'통과' if r['ok'] else '실패'} | "
                 f"{r.get('opened', '–')}/{r.get('total', '–')} | {r['tries']} | {r['tokens'][0]:,}/{r['tokens'][1]:,} |")
    (OUT / "EXTRA.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[extra] 요약 → {OUT / 'EXTRA.md'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("libs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true", help="무엇을 맡길지만 보여 준다 (API 키 없이)")
    ap.add_argument("--harness", help="이 하네스만 (쉼표로 여러 개)")
    ap.add_argument("--primary", action="store_true", help="official_llm이 없는 라이브러리는 대표 하네스도 같은 규칙으로 고친다")
    ap.add_argument("--no-dedup", action="store_true", help="같은 분기를 여러 하네스에서 고치는 것을 허용 (규칙 2를 끔)")
    ap.add_argument("--force", action="store_true", help="이미 있어도 다시 만든다")
    ap.add_argument("--secs", type=int, default=60, help="검사용 퍼징 시간(초, 회당)")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--tries", type=int, default=3, help="실패하면 이유를 돌려주고 다시 받는 최대 횟수")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mock", help=argparse.SUPPRESS)          # 시험용: API 대신 쓸 응답 파일
    a = ap.parse_args()
    libs = LIBS if a.all else a.libs
    if not libs:
        ap.error("라이브러리 이름이나 --all")
    only = set(a.harness.split(",")) if a.harness else None
    todo_total = 0
    for lib in libs:
        t, rows = plan(lib, a)
        todo = [r for r in rows if r["fixes"] and not r["note"] and (only is None or r["harness"] in only)]
        todo_total += len(todo)
        print(f"\n== {lib}: OSS-Fuzz 하네스 {len(rows)}개 중 고칠 하네스 {len(todo)}개"
              f" (고친 하네스 하나마다 팀 실험 1시간 × 10회가 늘어납니다)")
        for r in rows:
            mark = f"제안 {','.join(map(str, r['fixes']))}" if r["fixes"] else "–"
            print(f"  {r['harness']}: {mark}" + (f"  [{r['note']}]" if r["note"] else ""))
            if a.list:
                for d in r["detail"]:
                    print(f"      {d}")
        if a.list:
            continue
        for r in todo:
            make(lib, r["harness"], r["fixes"], t, a)
    if a.list:
        print(f"\n고칠 하네스 합계 {todo_total}개 → 팀 실험 {todo_total * 10} CPU시간 추가")
        return 0
    summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
