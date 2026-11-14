#!/usr/bin/env python3
"""짧은 진단과 긴 진단이 같은 '하네스에서 고칠 곳'을 내는지 비교한다.

질문: 진단용 퍼징을 2분만 돌려도 되는가? 더 오래 돌리면 고칠 곳이 더 나오는가?
방법: 같은 하네스의 짧은 실행(기본 r1, 2분)과 긴 실행(기본 long3600/r1, 1시간)의 커버리지를
      지금 코드로 각각 다시 분석해서, 고칠 곳 목록과 그 때문에 막힌 분기를 비교한다. 새로 퍼징하지 않는다.

  python3 scripts/diag_compare.py zlib jsoncpp                 # OSS-Fuzz 하네스(official) 기준
  python3 scripts/diag_compare.py zlib --harness official --long out/targets/zlib/official/long3600/r3

짧은 실행이 없으면 --secs(기본 120)초로 한 번 돌려서 만든다(빌드된 바이너리가 있어야 함).
결과: 화면 출력 + out/diag_compare/<라이브러리>_<하네스>.md
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("gapfuzz_tgt", ROOT / "scripts" / "tgt.py")
tg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tg)


def analyze(t, h, d: Path) -> dict:
    if not (d / "coverage.json").exists():
        raise SystemExit(f"커버리지 파일 없음: {d / 'coverage.json'}")
    tg.analyze(t, h, d)
    return json.load(open(d / "gap" / "gap.json"))


def fix_key(g: dict) -> tuple:
    return (g["verdict"], tuple(g["harness_lines"]), g["param_index"], tuple(sorted(a.split("(")[0] for a in g["apis"])))


def blocked(gap: dict) -> set:
    return {(b["line"], b["col"], b["never"]) for g in gap["harness_fixes"] for b in g["blocked"]}


def stuck(gap: dict) -> set:
    return {(b["line"], b["col"], b["never"]) for r in gap["results"] for b in r["stuck_branches"]}


def cats(gap: dict) -> dict:
    out = {}
    for r in gap["results"]:
        out[r["category"]] = out.get(r["category"], 0) + 1
    return out


def one(lib: str, h: str, short: Path | None, long: Path | None, secs: int) -> str:
    t = tg.load(lib)
    base = ROOT / "out" / "targets" / lib / h
    sd = short or base / "r1"
    ld = long or base / "long3600" / "r1"
    if not (sd / "coverage.json").exists():
        if not (base / "fuzz").exists():
            raise SystemExit(f"빌드된 바이너리 없음: {base}/fuzz  (python3 scripts/tgt.py build {lib} {h})")
        print(f"[diag] {lib}/{h}: 짧은 실행이 없어 {secs}초 진단을 한 번 돌립니다 …", flush=True)
        tg.run_one(t, h, 1, secs, 1000, 0, None)
    s, l = analyze(t, h, sd), analyze(t, h, ld)
    sf = {fix_key(g): g for g in s["harness_fixes"]}
    lf = {fix_key(g): g for g in l["harness_fixes"]}
    both, only_s, only_l = sf.keys() & lf.keys(), sf.keys() - lf.keys(), lf.keys() - sf.keys()
    sb, lb = blocked(s), blocked(l)
    ss, ls = stuck(s), stuck(l)
    opened = sb - ls                       # 짧은 진단이 하네스 탓이라 한 분기 중, 긴 실행에서는 막힌 목록에 없는 것
    rel = lambda p: p.relative_to(ROOT) if p.is_relative_to(ROOT) else p
    cs, cl = cats(s), cats(l)
    md = [f"# 짧은 진단 vs 긴 진단 — {lib}/{h}", "",
          f"- 짧은 실행: `{rel(sd)}`", f"- 긴 실행: `{rel(ld)}`", "",
          "| | 짧은 진단 | 긴 진단 |", "|---|---:|---:|",
          f"| 호출 안 함 API | {cs.get('NOT_CALLED', 0)} | {cl.get('NOT_CALLED', 0)} |",
          f"| 막힌 분기 (전체) | {len(ss)} | {len(ls)} |",
          f"| 하네스에서 고칠 곳 | {len(sf)} | {len(lf)} |",
          f"| 그 때문에 막힌 분기 | {len(sb)} | {len(lb)} |", "",
          f"- 두 진단에 모두 나온 고칠 곳: **{len(both)}**",
          f"- 짧은 진단에만 나온 고칠 곳: **{len(only_s)}**",
          f"- 긴 진단에만 나온 고칠 곳: **{len(only_l)}** (짧은 진단이 놓친 것)",
          f"- 하네스 탓으로 막힌 분기: 공통 {len(sb & lb)}, 짧은 쪽에만 {len(sb - lb)}, 긴 쪽에만 {len(lb - sb)}",
          f"- 짧은 진단이 하네스 탓이라 한 분기 중 긴 실행에서 막힌 목록에 없는 것: **{len(opened)}** "
          "(0이 아니면: 시간이 지나 열렸거나, 그 API가 긴 실행에서 다르게 분류된 것. 아래 목록을 확인)", ""]
    def show(title, keys, src):
        if not keys:
            return
        md.append(f"## {title}")
        md.append("")
        for k in sorted(keys, key=str):
            g = src[k]
            where = ", ".join(f"{x}행" for x in g["harness_lines"]) or "하네스에 호출 없음"
            md.append(f"- [{g['verdict']}] {where}: {g['suggestion'][:160]} (막힌 분기 {len(g['blocked'])}개)")
        md.append("")
    show("긴 진단에만 나온 고칠 곳", only_l, lf)
    show("짧은 진단에만 나온 고칠 곳", only_s, sf)
    if opened:
        md += ["## 짧은 진단이 짚었지만 긴 실행에서는 막힌 목록에 없는 분기", ""]
        md += [f"- {ln}행 {col}열 ({nv} 쪽)" for ln, col, nv in sorted(opened)] + [""]
    text = "\n".join(md)
    out = ROOT / "out" / "diag_compare"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{lib}_{h}.md").write_text(text + "\n", encoding="utf-8")
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("libs", nargs="+")
    ap.add_argument("--harness", default="official")
    ap.add_argument("--short", help="짧은 실행 폴더 (라이브러리를 하나만 줄 때)")
    ap.add_argument("--long", help="긴 실행 폴더 (라이브러리를 하나만 줄 때)")
    ap.add_argument("--secs", type=int, default=120, help="짧은 실행이 없을 때 돌릴 진단 시간(초)")
    a = ap.parse_args()
    if (a.short or a.long) and len(a.libs) > 1:
        raise SystemExit("--short/--long은 라이브러리를 하나만 줄 때 쓸 수 있습니다")
    for lib in a.libs:
        print(one(lib, a.harness, Path(a.short).resolve() if a.short else None, Path(a.long).resolve() if a.long else None, a.secs))
        print(f"[diag] -> out/diag_compare/{lib}_{a.harness}.md\n")


if __name__ == "__main__":
    sys.exit(main())
