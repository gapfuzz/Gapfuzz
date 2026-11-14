#!/usr/bin/env python3
"""판정 정확도 점검: gap.json의 원인 판정을 사람이 단 정답(audit_labels.json)과 비교한다.

사용법: python3 scripts/audit.py <gap.json> <audit_labels.json> [--out audit.md] [--with-candidates]

기본은 기존 분석의 판정만 본다(예전 수치와 그대로 비교됨).
--with-candidates 를 주면 확장 분석의 후보(STATE, CALLBACK, C 구조체 필드, 실행 중 관찰)가 붙은 분기도
'고칠 곳으로 낸 것'으로 쳐서 정밀도·재현율이 어떻게 달라지는지 본다.

정답(actual)
  H : 하네스를 고치면 열림
  I : 입력 내용(딕셔너리·시드)으로 열어야 함
  D : 하네스로 열 수 없는 방어 분기

도구 판정과의 대응
  FIXED / SETTER_NOT_CALLED / NARROW / DIRECT_CALL → '하네스에서 고칠 곳' (H라고 말한 것)
  VARIES                              → 하네스가 값을 바꾸지만 맞는 값이 안 나옴 (H의 한 형태로 봄)
  INTERNAL / UNKNOWN                  → 라이브러리 내부·입력 내용 (I 또는 D라고 말한 것)
  확장: STATE / CALLBACK → 고칠 곳 후보,  STATE_ORDER → 조언(VARIES와 같은 취급),  ASSERT → 방어 분기(D)

지표
  판정 정확도      : 도구의 판정이 정답 범주(H ↔ 고칠 곳·VARIES, I·D ↔ INTERNAL)와 맞는 비율
  고칠 곳 정밀도   : 고칠 곳으로 낸 분기 중 정답이 H인 비율
  고칠 곳 재현율   : 정답이 H인 분기 중 고칠 곳으로 나온 비율 (VARIES는 조언만 있고 목록엔 없으므로 제외)
"""
import argparse
import json
from collections import Counter

FIX = {"FIXED", "SETTER_NOT_CALLED", "NARROW", "DIRECT_CALL", "CALLBACK", "STATE"}
ADVICE = {"VARIES", "STATE_ORDER"}
NOT_HARNESS = {"ALLOC_FAIL", "ASSERT", "INTERNAL", "UNKNOWN"}


def verdict_of(b: dict, with_candidates: bool) -> str:
    cs = b.get("causes") or []
    if not cs:
        return "UNKNOWN"
    legacy = next((c for c in cs if not c.get("ext")), None)
    if not with_candidates:
        return legacy["verdict"] if legacy else "UNKNOWN"
    if legacy and legacy["verdict"] in FIX:
        return legacy["verdict"]
    cand = next((c for c in cs if c.get("ext") and c["verdict"] in FIX), None)
    return cand["verdict"] if cand else (legacy["verdict"] if legacy else cs[0]["verdict"])


def key(api: str, line: int, col: int) -> str:
    return f"{api.split('(')[0]}|{line}|{col}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gap")
    ap.add_argument("labels")
    ap.add_argument("--out")
    ap.add_argument("--with-candidates", action="store_true", help="확장 분석의 후보도 '고칠 곳'으로 쳐서 계산")
    a = ap.parse_args()
    gap = json.load(open(a.gap))
    labels = json.load(open(a.labels))["labels"]

    rows, unlabeled = [], []
    for r in gap["results"]:
        for b in r.get("stuck_branches", []):
            k = key(r["api"], b["line"], b["col"])
            v = verdict_of(b, a.with_candidates)
            lab = labels.get(k)
            if not lab:
                unlabeled.append(k)
                continue
            act = lab["actual"]
            ok = (act == "H" and (v in FIX or v in ADVICE)) or (act in "ID" and v in NOT_HARNESS)
            rows.append({"key": k, "expr": b.get("expr", ""), "verdict": v, "actual": act, "ok": ok, "why": lab["why"]})

    n = len(rows)
    acc = sum(r["ok"] for r in rows)
    fix_rows = [r for r in rows if r["verdict"] in FIX]
    h_rows = [r for r in rows if r["actual"] == "H"]
    prec = sum(r["actual"] == "H" for r in fix_rows)
    rec = sum(r["verdict"] in FIX for r in h_rows)
    conf = Counter((r["verdict"], r["actual"]) for r in rows)

    out = [f"# 판정 정확도 점검 — {gap['meta'].get('name', '')}", "",
           f"막힌 분기 {n}개를 사람이 소스와 대조해 단 정답과 비교했습니다."
           + (" (확장 분석의 후보 포함)" if a.with_candidates else ""), "",
           "| 지표 | 값 |", "|---|---:|",
           f"| 판정 정확도 | {acc}/{n} ({acc / n:.0%}) |",
           f"| 고칠 곳 정밀도 | {prec}/{len(fix_rows)} ({prec / max(len(fix_rows), 1):.0%}) |",
           f"| 고칠 곳 재현율 | {rec}/{len(h_rows)} ({rec / max(len(h_rows), 1):.0%}) |", "",
           "| 도구 판정 \\ 정답 | H (하네스) | I (입력) | D (방어) |", "|---|---:|---:|---:|"]
    for v in ("FIXED", "SETTER_NOT_CALLED", "NARROW", "DIRECT_CALL", "CALLBACK", "STATE", "VARIES", "STATE_ORDER", "ALLOC_FAIL", "ASSERT", "INTERNAL", "UNKNOWN"):
        if any(conf[(v, x)] for x in "HID"):
            out.append(f"| {v} | {conf[(v, 'H')]} | {conf[(v, 'I')]} | {conf[(v, 'D')]} |")
    out += ["", "## 틀린 판정", ""]
    for r in rows:
        if not r["ok"]:
            out.append(f"- `{r['key']}` 조건 `{r['expr']}` — 도구 {r['verdict']}, 정답 {r['actual']}: {r['why']}")
    if unlabeled:
        out += ["", f"## 정답이 없는 분기 {len(unlabeled)}개", ""] + [f"- `{k}`" for k in unlabeled]
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
