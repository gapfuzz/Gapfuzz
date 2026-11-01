#!/usr/bin/env python3
"""제안 검증의 안정성 점검 (새 퍼징 없이 기존 결과로).

1) 수정 전: 겨냥한 분기가 r1만이 아니라 수정 전 5회 모두에서 막혀 있었나
2) 수정 후: 열린 분기가 5회 중 몇 회에서 열렸나 (samples/verify/*.json의 opened_runs)
결과: samples/verify/stability.md
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = [  # (이름, verify json, 수정 전 5회 디렉터리 패턴)
    ("TinyXML2 (공식 하네스, v2→v3)", "official_v2_to_v3.json", "out/repeat/official_v2/r{}"),
    ("pugixml", "pugixml_official_to_v2.json", "out/targets/pugixml/official/r{}"),
    ("cJSON", "cjson_official_to_v2.json", "out/targets/cjson/official/r{}"),
    ("jsoncpp", "jsoncpp_official_to_v2.json", "out/targets/jsoncpp/official/r{}"),
    ("zlib", "zlib_official_to_v2.json", "out/targets/zlib/official/r{}"),
    ("expat", "expat_official_to_v2.json", "out/targets/expat/official/r{}"),
    ("json-c", "json-c_official_to_v2.json", "out/targets/json-c/official/r{}"),
]


def branch_map(cov):
    m = {}
    for f in json.load(open(cov))["data"][0]["files"]:
        for b in f["branches"]:
            key = (b[0], b[1])
            t, fl = m.get(key, (0, 0))
            m[key] = (t + b[4], fl + b[5])
    return m


def main():
    L = ["# 제안 검증의 안정성", "",
         "새로 퍼징하지 않고 기존 결과만으로 본 것. 수정 전·후 모두 120초 × 5회, 같은 시드.", "",
         "| 라이브러리 | 겨냥한 분기 | 수정 전 5회 모두 막힘 | 수정 후 열린 분기 | 그중 5회 모두 열림 | 대조군 5회 모두 막힘 |",
         "|---|---:|---:|---:|---:|---:|"]
    tot = [0] * 6
    notes = []
    for name, vj, pat in CASES:
        fixes = json.load(open(ROOT / "samples" / "verify" / vj))
        md = (ROOT / "samples" / "verify" / vj.replace(".json", ".md")).read_text(encoding="utf-8")
        applied_set = {int(m.group(1)) for m in re.finditer(r"^\| (\d+) \| .+? \| 적용 \|", md, re.M)}
        runs = [branch_map(ROOT / pat.format(i) / "coverage.json") for i in range(1, 6)]
        targets = blocked5 = opened = opened5 = 0
        ctrl = ctrl5 = 0
        for k, fx in enumerate(fixes, 1):
            for ch in fx["checks"]:
                side = 0 if ch["never"] == "참" else 1
                seen = [r.get((ch["line"], ch["col"])) for r in runs]
                still = all(s is not None and s[side] == 0 for s in seen)
                if k not in applied_set:
                    ctrl += 1
                    ctrl5 += ch["opened_runs"] == "0/5"
                    continue
                targets += 1
                blocked5 += still
                if not still:
                    notes.append(f"{name}: {ch['line']}행 `{ch['expr']}` — 수정 전 일부 회차에서 이미 열림 "
                                 f"({sum(1 for s in seen if s and s[side] > 0)}/5)")
                if ch["state"] == "OPENED":
                    opened += 1
                    opened5 += ch["opened_runs"] == "5/5"
        L.append(f"| {name} | {targets} | {blocked5}/{targets} | {opened} | {opened5}/{opened} | {ctrl5}/{ctrl} |")
        for i, v in enumerate([targets, blocked5, opened, opened5, ctrl5]):
            tot[i] += v
        tot[5] += ctrl
    L.append(f"| **합계** | {tot[0]} | {tot[1]}/{tot[0]} | {tot[2]} | {tot[3]}/{tot[2]} | {tot[4]}/{tot[5]} |")
    L += [""] + [f"- {n}" for n in notes]
    out = ROOT / "samples" / "verify" / "stability.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
