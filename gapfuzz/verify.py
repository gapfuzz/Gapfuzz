"""제안 검증: '하네스에서 고칠 곳'을 적용한 뒤, 그 때문에 막혀 있던 분기가 실제로 열렸는지 확인한다.

before : 수정 전 하네스의 gap.json (harness_fixes 포함)
after  : 수정 후 하네스의 gap.json (여러 회차를 주면 한 번이라도 열린 것을 '열림'으로 본다)

분기 판정
  열림        : 수정 후에는 그 분기가 양쪽으로 모두 실행됨
  여전히 막힘  : 수정 후에도 같은 방향으로만 감
  확인 불가    : 수정 후 그 API가 실행되지 않음
"""
from __future__ import annotations

import json
from collections import Counter

STATE_KO = {"OPENED": "열림", "STILL": "여전히 막힘", "UNKNOWN": "확인 불가"}


def _stuck_map(data: dict) -> tuple[dict, set]:
    stuck, reached = {}, set()
    for r in data["results"]:
        if r["category"] in ("FULL", "PARTIAL"):
            reached.add(r["api"])
        for b in r.get("stuck_branches", []):
            stuck[(r["api"], b["line"], b.get("col", 0))] = b["never"]
    return stuck, reached


def verify(before: dict, afters: list[dict]) -> list[dict]:
    maps = [_stuck_map(a) for a in afters]
    out = []
    for g in before.get("harness_fixes", []):
        rows = []
        for b in g["blocked"]:
            key = (b["api"], b["line"], b.get("col", 0))
            states = []
            for stuck, reached in maps:
                if b["api"] not in reached:
                    states.append("UNKNOWN")
                elif key in stuck and stuck[key] == b["never"]:
                    states.append("STILL")
                else:
                    states.append("OPENED")
            n_open = states.count("OPENED")
            state = "OPENED" if n_open else ("STILL" if "STILL" in states else "UNKNOWN")
            rows.append({**b, "state": state, "opened_runs": f"{n_open}/{len(states)}"})
        out.append({**g, "checks": rows,
                    "opened": sum(1 for r in rows if r["state"] == "OPENED"), "total": len(rows)})
    return out


def write_verify(before: dict, afters: list[dict], out_md: str, applied: list[int] | None = None) -> list[dict]:
    res = verify(before, afters)
    json.dump(res, open(out_md.rsplit(".", 1)[0] + ".json", "w"), ensure_ascii=False, indent=1)
    nb = before["meta"].get("name", "before")
    na = afters[0]["meta"].get("name", "after") if afters else "after"
    tot = Counter()
    lines = [f"# 제안 검증 — {nb} → {na}", "",
             f"수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후({len(afters)}회 실행)에 열렸는지 봅니다.",
             "한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.", "",
             "| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |", "|---:|---|---|---:|---:|"]
    for i, g in enumerate(res, 1):
        app = "적용" if (applied is None or i in applied) else "미적용"
        title = g["apis"][0].split("(")[0] if g.get("apis") else "?"
        what = f"{title} · {g['param_name']}" if g.get("param_name") else title
        lines.append(f"| {i} | {what} | {app} | {g['total']} | {g['opened']} |")
        if applied is None or i in applied:
            tot["total"] += g["total"]
            tot["opened"] += g["opened"]
    lines += ["", f"**적용한 제안 기준: 막혀 있던 분기 {tot['total']}개 중 {tot['opened']}개가 열림**", ""]
    for i, g in enumerate(res, 1):
        lines.append(f"## {i}. {g['suggestion']}")
        for r in g["checks"]:
            cond = f"`{r['expr']}`" if r.get("expr") else f"`{r['source']}`"
            lines.append(f"- {STATE_KO[r['state']]} ({r['opened_runs']}) — `{r['api']}` {r['line']}행 "
                         f"조건 {cond} (수정 전: 한 번도 {r['never']} 아님)")
        lines.append("")
    open(out_md, "w").write("\n".join(lines) + "\n")
    return res
