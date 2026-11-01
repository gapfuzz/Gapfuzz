#!/usr/bin/env python3
"""독립 라벨링 키트: 도구의 판정을 가린 채 사람이 막힌 분기마다 정답을 달고, 사람끼리의 일치도를 잰다.

1) 시트 만들기 (도구 판정·원인·제안은 시트에 넣지 않는다)
   python3 scripts/label_kit.py make out/repeat/official/r1/gap/gap.json out/repeat/stateful/r1/gap/gap.json \
       --out labeling/ --seed 7
   → labeling/sheet.csv     : 번호, 키, 위치, 조건식, 안 간 방향, 정답(H/I/D), 이유  ← 이 두 칸만 채운다
     labeling/items.md      : 번호마다 함수 이름과 코드 앞뒤 8줄 (읽기용)
     labeling/GUIDE.md      : 정답 기준과 예시

2) 일치도 (두 사람의 시트 또는 기존 정답 파일)
   python3 scripts/label_kit.py agree labeling/sheet_kim.csv labeling/sheet_lee.csv
   → Cohen's kappa, 일치표, 서로 다른 항목 목록

3) 합치기: 두 사람이 같은 답을 단 항목만 정답 파일(audit_labels.json 형식)로 만든다. 다른 항목은 토론 목록으로.
   python3 scripts/label_kit.py merge labeling/sheet_kim.csv labeling/sheet_lee.csv --out labeling/consensus.json
   → 그 뒤 scripts/audit.py <gap.json> labeling/consensus.json 로 도구 정확도를 다시 잰다
"""
import argparse
import csv
import json
import os
import random
from collections import Counter

CLASSES = ("H", "I", "D")
GUIDE = """# 라벨링 기준

시트(sheet.csv)의 `정답` 칸에 H, I, D 중 하나를, `이유` 칸에 한 줄 근거를 적습니다.
items.md에서 각 번호의 코드와 조건식을 읽고, **하네스 코드를 고치면 이 분기의 안 간 방향이 열릴 수 있는가**로 판단하세요.
도구의 판정은 일부러 보여 주지 않습니다. 리포트(gap_report)는 라벨을 다 단 뒤에 보세요.

| 정답 | 뜻 | 예 |
|---|---|---|
| H | 하네스를 고치면 열림 (인자 값을 바꾸기, null 넘기기, 다른 API를 부르기, 호출 순서 바꾸기) | `ShallowClone(&doc)`만 불러서 `if (!doc)`가 안 열림 → nullptr도 넘기면 열림 |
| I | 하네스는 그대로 두고 입력 내용(시드·딕셔너리)을 바꿔야 열림 | `&#x10000;` 같은 큰 문자 참조가 있어야 4바이트 UTF-8 분기가 열림 |
| D | 어떤 입력·하네스로도 열 수 없음 (앞선 검사 때문에 도달 불가능한 방어 코드) | 바로 앞에서 0x10FFFF 초과를 걸렀는데 다시 `ucs > 0x10FFFF`를 검사 |

애매하면
- 하네스를 고쳐서 열 수 있고, 입력만 바꿔서도 열 수 있으면 → 더 쉬운 쪽 (대개 I)
- 판단이 안 서면 정답 칸을 비우고 이유에 "모름"이라고 적기 (일치도 계산에서 빠짐)
- 30분 안에 끝낼 필요 없습니다. 한 항목에 1~2분이면 충분합니다.
"""


def item_key(api: str, line: int, col: int) -> str:
    return f"{api.split('(')[0]}|{line}|{col}"


def excerpt(path: str, line: int, ctx: int = 8) -> str:
    try:
        lines = open(path, errors="replace").read().splitlines()
    except OSError:
        return "(소스를 읽지 못함)"
    lo, hi = max(1, line - ctx), min(len(lines), line + ctx)
    return "\n".join(f"{'>' if i == line else ' '} {i:5d}  {lines[i - 1]}" for i in range(lo, hi + 1))


def cmd_make(a):
    items, seen = [], set()
    for g in a.gap:
        gap = json.load(open(g))
        for r in gap["results"]:
            for b in r.get("stuck_branches", []):
                k = item_key(r["api"], b["line"], b["col"])
                if k in seen:
                    continue
                seen.add(k)
                items.append({"key": k, "api": r["api"], "func": b.get("in_func") or r["api"], "file": b["file"],
                              "line": b["line"], "expr": b.get("expr", ""), "never": b["never"]})
    random.Random(a.seed).shuffle(items)          # 도구 리포트의 순서(판정 순)를 따라가지 않도록 섞는다
    if a.sample and a.sample < len(items):
        items = items[:a.sample]
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "sheet.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["번호", "키", "위치", "조건식", "안 간 방향", "정답(H/I/D)", "이유"])
        for i, it in enumerate(items, 1):
            w.writerow([i, it["key"], f"{os.path.basename(it['file'])}:{it['line']}", it["expr"], it["never"], "", ""])
    md = ["# 라벨링 항목", "", f"{len(items)}개. 기준은 GUIDE.md. 정답은 sheet.csv에 적습니다.", ""]
    for i, it in enumerate(items, 1):
        md += [f"## {i}. `{it['expr']}` 가 한 번도 {it['never']}이 되지 않음", "",
               f"- 함수: `{it['func']}`", f"- 위치: {os.path.basename(it['file'])}:{it['line']}", "",
               "```cpp", excerpt(it["file"], it["line"]), "```", ""]
    open(os.path.join(a.out, "items.md"), "w", encoding="utf-8").write("\n".join(md))
    open(os.path.join(a.out, "GUIDE.md"), "w", encoding="utf-8").write(GUIDE)
    print(f"[label] 항목 {len(items)}개 -> {a.out}/sheet.csv, items.md, GUIDE.md")


def read_labels(path: str) -> dict[str, str]:
    """시트(CSV) 또는 정답 파일(audit_labels.json)에서 {키: H/I/D}를 읽는다."""
    if path.endswith(".json"):
        d = json.load(open(path))
        return {k: v["actual"] for k, v in d["labels"].items() if v.get("actual") in CLASSES}
    out = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            lab = (row.get("정답(H/I/D)") or "").strip().upper()
            if lab in CLASSES:
                out[row["키"]] = lab
    return out


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[c] * cb[c] for c in CLASSES) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def cmd_agree(a):
    A, B = read_labels(a.a), read_labels(a.b)
    common = sorted(set(A) & set(B))
    pairs = [(A[k], B[k]) for k in common]
    k = kappa(pairs)
    agree = sum(x == y for x, y in pairs)
    print(f"[label] 둘 다 단 항목 {len(common)}개, 일치 {agree}개 ({agree / max(len(common), 1):.0%}), Cohen's kappa = {k:.2f}")
    print("        (kappa 해석 관례: 0.61~0.80 상당한 일치, 0.81 이상 거의 완전한 일치)")
    print("        일치표 (행: 첫 번째, 열: 두 번째)")
    print("           " + "  ".join(f"{c:>3}" for c in CLASSES))
    for r in CLASSES:
        print(f"        {r:>3}" + "  ".join(f"{sum(1 for x, y in pairs if x == r and y == c):>3}" for c in CLASSES))
    diff = [(key, A[key], B[key]) for key in common if A[key] != B[key]]
    if diff:
        print("        서로 다른 항목:")
        for key, x, y in diff:
            print(f"          {key}: {x} vs {y}")


def cmd_merge(a):
    A, B = read_labels(a.a), read_labels(a.b)
    common = sorted(set(A) & set(B))
    labels = {k: {"actual": A[k], "why": "두 사람 독립 라벨 일치"} for k in common if A[k] == B[k]}
    json.dump({"labels": labels, "disagree": [k for k in common if A[k] != B[k]]},
              open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"[label] 합의 {len(labels)}개, 불일치 {len(common) - len(labels)}개 -> {a.out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("gap", nargs="+"); m.add_argument("--out", required=True)
    m.add_argument("--seed", type=int, default=7); m.add_argument("--sample", type=int)
    g = sub.add_parser("agree"); g.add_argument("a"); g.add_argument("b")
    mg = sub.add_parser("merge"); mg.add_argument("a"); mg.add_argument("b"); mg.add_argument("--out", required=True)
    a = ap.parse_args()
    {"make": cmd_make, "agree": cmd_agree, "merge": cmd_merge}[a.cmd](a)


if __name__ == "__main__":
    main()
