#!/usr/bin/env python3
"""사이트(site/)의 분석기 화면이 읽을 데이터를 만든다: site/data.json

라이브러리마다 하네스별 1회차 갭 분석(gap.json), 5회 반복의 커버리지 중앙값, 제안 검증 결과(samples/verify/*.md)를 모은다.
사용법: python3 scripts/export_site.py              (전부 다시 만들기, out/ 필요)
       python3 scripts/export_site.py --team-only  (팀 장시간 실험 results/만 다시 넣기)
"""
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = Path(os.environ.get("GAPFUZZ_RESULTS", ROOT / "results"))
CATS = ["NOT_CALLED", "BLOCKED", "PARTIAL", "FULL"]

LIBS = [
    {"id": "tinyxml2", "name": "TinyXML2", "lang": "C++", "kind": "XML 파서", "repo": "github.com/leethomason/tinyxml2",
     "dir": "third_party/tinyxml2", "runs": "out/repeat",
     "harnesses": [("official", "OSS-Fuzz 하네스", "harnesses/tinyxml2/official.cpp"),
                   ("official_v3", "OSS-Fuzz 하네스 + gapfuzz 수정", "harnesses/tinyxml2/official_v3.cpp")],
     "verify": [("official", "official_v3", ["official_to_v2.md", "official_v2_to_v3.md"])]},
    {"id": "pugixml", "name": "pugixml", "lang": "C++", "kind": "XML 파서", "repo": "github.com/zeux/pugixml",
     "dir": "third_party/pugixml", "runs": "out/targets/pugixml",
     "harnesses": [("official", "OSS-Fuzz 하네스", "harnesses/pugixml/official.cpp"),
                   ("official_v2", "OSS-Fuzz 하네스 + gapfuzz 수정", "harnesses/pugixml/official_v2.cpp")],
     "verify": [("official", "official_v2", ["pugixml_official_to_v2.md"])]},
    {"id": "cjson", "name": "cJSON", "lang": "C", "kind": "JSON 파서", "repo": "github.com/DaveGamble/cJSON",
     "dir": "third_party/cjson", "runs": "out/targets/cjson",
     "harnesses": [("official", "OSS-Fuzz 하네스", "harnesses/cjson/official.c"),
                   ("official_v2", "OSS-Fuzz 하네스 + gapfuzz 수정", "harnesses/cjson/official_v2.c")],
     "verify": [("official", "official_v2", ["cjson_official_to_v2.md"])]},
    {"id": "jsoncpp", "name": "jsoncpp", "lang": "C++", "kind": "JSON 파서", "repo": "github.com/open-source-parsers/jsoncpp",
     "dir": "third_party/jsoncpp", "runs": "out/targets/jsoncpp",
     "harnesses": [("official", "OSS-Fuzz 하네스", "harnesses/jsoncpp/official.cpp"),
                   ("official_v2", "OSS-Fuzz 하네스 + gapfuzz 수정", "harnesses/jsoncpp/official_v2.cpp")],
     "verify": [("official", "official_v2", ["jsoncpp_official_to_v2.md"])]},
    {"id": "zlib", "name": "zlib", "lang": "C", "kind": "압축", "repo": "github.com/madler/zlib",
     "dir": "third_party/zlib", "runs": "out/targets/zlib",
     "harnesses": [("official", "OSS-Fuzz 하네스 (uncompress)", "harnesses/zlib/official.cc"),
                   ("official_v2", "OSS-Fuzz 하네스 + gapfuzz 수정", "harnesses/zlib/official_v2.cc")],
     "verify": [("official", "official_v2", ["zlib_official_to_v2.md"])]},
    {"id": "expat", "name": "expat", "lang": "C", "kind": "XML 파서", "repo": "github.com/libexpat/libexpat",
     "dir": "third_party/libexpat", "runs": "out/targets/expat",
     "harnesses": [("official", "OSS-Fuzz 하네스", "harnesses/expat/official.c"),
                   ("official_v2", "OSS-Fuzz 하네스 + gapfuzz 수정", "harnesses/expat/official_v2.c")],
     "verify": [("official", "official_v2", ["expat_official_to_v2.md"])]},
    {"id": "json-c", "name": "json-c", "lang": "C", "kind": "JSON 파서", "repo": "github.com/json-c/json-c",
     "dir": "third_party/json-c", "runs": "out/targets/json-c",
     "harnesses": [("official", "OSS-Fuzz 하네스", "harnesses/json-c/official.cc"),
                   ("official_v2", "OSS-Fuzz 하네스 + gapfuzz 수정", "harnesses/json-c/official_v2.cc")],
     "verify": [("official", "official_v2", ["json-c_official_to_v2.md"])]},
    {"id": "libyaml", "name": "libyaml", "lang": "C", "kind": "YAML 파서", "repo": "github.com/yaml/libyaml",
     "dir": "third_party/libyaml", "runs": "out/targets/libyaml",
     "harnesses": [("official", "OSS-Fuzz 하네스 (parser)", "harnesses/libyaml/official.c")],
     "verify": []},
]


def rel(p: str) -> str:
    return os.path.relpath(p, ROOT) if p and os.path.isabs(p) else (p or "")


def context(path: str, line: int, n: int = 2) -> list:
    try:
        src = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return []
    lo, hi = max(1, line - n), min(len(src), line + n)
    return [[i, src[i - 1].replace("\t", "    ").rstrip()[:140]] for i in range(lo, hi + 1)]


def coverage(runs_dir: Path, h: str) -> dict:
    vals = {"lines": [], "branches": []}
    for r in range(1, 6):
        p = runs_dir / h / f"r{r}" / "coverage.json"
        if not p.exists():
            continue
        t = json.load(open(p))["data"][0]["totals"]
        vals["lines"].append(t["lines"]["percent"])
        vals["branches"].append(t["branches"]["percent"])
    return {k: round(statistics.median(v), 2) if v else None for k, v in vals.items()} | {"n": len(vals["lines"])}


def harness_data(gap: dict) -> dict:
    res = gap["results"]
    apis = [{"a": r["api"], "c": r["category"], "h": r.get("region_hit", 0), "t": r.get("region_total", 0)} for r in res]
    branches = []
    for r in res:
        for b in r.get("stuck_branches", []):
            causes = b.get("causes") or []
            # 확장 분석의 후보(ext)는 사이트에 올리지 않는다: 기존 판정 중 첫 번째를 대표로 쓴다
            c0 = next((c for c in causes if not c.get("ext")), causes[0]) if causes else {"verdict": "UNKNOWN", "suggestion": ""}
            sites = [{"l": s["line"], "s": (s.get("source") or "").strip()[:160]} for s in c0.get("sites", [])][:3]
            branches.append({"api": r["api"], "f": rel(b["file"]), "l": b["line"], "col": b.get("col", 0), "src": (b.get("source") or "").strip(),
                             "never": b.get("never", ""), "v": c0["verdict"], "s": c0.get("suggestion", ""),
                             "sites": sites, "ctx": context(b["file"], b["line"])})
    fixes = [{"v": f["verdict"], "s": f.get("suggestion", ""), "hl": f.get("harness_lines", []),
              "hs": [x.strip() for x in f.get("harness_source", [])][:3], "n": len(f.get("blocked", []))}
             for f in gap.get("harness_fixes", [])]
    counts = {c: sum(1 for r in res if r["category"] == c) for c in CATS}
    return {"apis": apis, "branches": branches, "fixes": fixes, "counts": counts}


ROW_RE = re.compile(r"^\| (\d+) \| (.+?) \| (적용|미적용) \| (\d+) \| (\d+) \|$")
SUG_RE = re.compile(r"^## (\d+)\. (.+)$")


def parse_verify(md: Path) -> list:
    rows, sugs = {}, {}
    for line in md.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if m:
            rows[int(m.group(1))] = {"what": m.group(2), "applied": m.group(3) == "적용",
                                     "total": int(m.group(4)), "opened": int(m.group(5))}
        m = SUG_RE.match(line)
        if m:
            sugs[int(m.group(1))] = m.group(2)
    return [dict(rows[i], s=sugs.get(i, "")) for i in sorted(rows)]


TEAM_IDS = {"official": "base", "official_llm": "llm"}


def team(lib_id: str, results: Path) -> dict | None:
    """팀 장시간 실험(results/<라이브러리>/1h, 24h): OSS-Fuzz 하네스 vs Claude 수정 하네스."""
    d = results / lib_id
    if not (d / "1h" / "official_llm").is_dir():
        return None
    t = {"h1": {}, "h24": {}}
    owner = d / "OWNER.txt"
    t["by"] = owner.read_text(encoding="utf-8").strip().splitlines()[0] if owner.exists() else ""
    llm = sorted((ROOT / "harnesses" / lib_id).glob("official_llm.*"))
    t["file"] = str(llm[0].relative_to(ROOT)) if llm else ""
    for h, k in TEAM_IDS.items():
        runs = [json.load(open(f)) for f in sorted((d / "1h" / h).glob("r*.json"))]
        if not runs:
            continue
        app = lambda r: [x for x in r["targets"] if x["applied"]]
        ctl = lambda r: [x for x in r["targets"] if not x["applied"]]
        t["h1"][k] = {"n": len(runs),
                      "br": [round(r["coverage"]["branches"]["pct"], 2) for r in runs],
                      "ln": [round(r["coverage"]["lines"]["pct"], 2) for r in runs],
                      "open": [sum(x["opened"] for x in app(r)) for r in runs], "tot": len(app(runs[0])),
                      "copen": [sum(x["opened"] for x in ctl(r)) for r in runs], "ctot": len(ctl(runs[0])),
                      "crash": sum(len(r.get("crashes") or []) for r in runs)}
        f24 = d / "24h" / f"{h}.json"
        if f24.exists():
            day = json.load(open(f24))
            mins, acc = [], 0
            for m in day["schedule_min"][:len(day["points"])]:
                acc += m
                mins.append(acc)
            pts = day["points"]
            t["h24"][k] = {"min": mins, "br": [round(x["coverage"]["branches"]["pct"], 2) for x in pts],
                           "open": sum(x["opened"] for x in pts[-1]["targets"] if x["applied"]),
                           "tot": sum(1 for x in pts[-1]["targets"] if x["applied"])}
    return t


def team_only() -> None:
    """이미 있는 site/data.json에 팀 장시간 실험 결과만 다시 넣는다 (out/ 없이도 됨)."""
    p = ROOT / "site" / "data.json"
    out = json.load(open(p))
    for lib in out["libs"]:
        tm = team(lib["id"], RESULTS)
        if tm:
            lib["team"] = tm
            print(f"  {lib['name']}: 팀 실험 {tm['h1'].get('llm', {}).get('n', 0)}회, 24시간 {'있음' if tm['h24'] else '없음'}")
        else:
            lib.pop("team", None)
    json.dump(out, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"[site] {p} {p.stat().st_size / 1024:.0f}KB")


def main():
    if "--team-only" in sys.argv:
        return team_only()
    out = {"libs": []}
    for L in LIBS:
        lib = {k: L[k] for k in ("id", "name", "lang", "kind", "repo")}
        try:
            lib["commit"] = subprocess.run(["git", "-C", str(ROOT / L["dir"]), "log", "-1", "--format=%h %cs"],
                                           capture_output=True, text=True).stdout.strip()
        except OSError:
            lib["commit"] = ""
        runs = ROOT / L["runs"]
        lib["harnesses"] = []
        for hid, label, path in L["harnesses"]:
            gap = json.load(open(runs / hid / "r1" / "gap" / "gap.json"))
            d = harness_data(gap)
            d.update({"id": hid, "label": label, "file": path, "cov": coverage(runs, hid)})
            lib["harnesses"].append(d)
        lib["verify"] = []
        for a, b, mds in L["verify"]:
            groups = []
            for md in mds:
                groups += parse_verify(ROOT / "samples" / "verify" / md)
            app = [g for g in groups if g["applied"]]
            ctl = [g for g in groups if not g["applied"]]
            lib["verify"].append({"from": a, "to": b, "groups": groups,
                                  "opened": sum(g["opened"] for g in app), "total": sum(g["total"] for g in app),
                                  "c_opened": sum(g["opened"] for g in ctl), "c_total": sum(g["total"] for g in ctl)})
        tm = team(lib["id"], RESULTS)
        if tm:
            lib["team"] = tm
        out["libs"].append(lib)
    p = ROOT / "site" / "data.json"
    json.dump(out, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"[site] {p} {p.stat().st_size / 1024:.0f}KB")
    for lib in out["libs"]:
        print(f"  {lib['name']}: " + ", ".join(f"{h['id']} 분기 {len(h['branches'])}, 고칠 곳 {len(h['fixes'])}" for h in lib["harnesses"])
              + " | " + ", ".join(f"검증 {v['opened']}/{v['total']} 대조 {v['c_opened']}/{v['c_total']}" for v in lib["verify"]))


if __name__ == "__main__":
    main()
