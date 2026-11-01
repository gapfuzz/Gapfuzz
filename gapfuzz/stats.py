"""반복 실행 결과 요약: 커버리지 분포, 두 하네스 간 검정, API 분류 안정성.

입력 구조: <root>/<하네스>/r<회차>/{coverage.json, gap/gap.json, crash-* ...}
"""
from __future__ import annotations

import json
import os
import statistics
from collections import Counter, defaultdict

try:
    from scipy.stats import mannwhitneyu
except ImportError:          # scipy가 없으면 검정만 생략
    mannwhitneyu = None

METRICS = [("lines", "라인"), ("functions", "함수"), ("regions", "영역"), ("branches", "분기")]
CATS = ["NOT_CALLED", "BLOCKED", "PARTIAL", "FULL"]
CAT_KO = {"NOT_CALLED": "호출 안 함", "BLOCKED": "조건에 막힘", "PARTIAL": "일부 분기 미실행", "FULL": "완전 도달"}


def _p(p: float) -> str:
    return f"{p:.4f}" if p >= 1e-4 else f"{p:.1e}"


def load_runs(root: str, harness: str) -> list[dict]:
    runs = []
    base = os.path.join(root, harness)
    for d in sorted(os.listdir(base), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
        p = os.path.join(base, d)
        cov_p, gap_p = os.path.join(p, "coverage.json"), os.path.join(p, "gap", "gap.json")
        if not (os.path.exists(cov_p) and os.path.exists(gap_p)):
            continue
        totals = json.load(open(cov_p))["data"][0]["totals"]
        gap = json.load(open(gap_p))["results"]
        crashes = [f for f in os.listdir(p) if f.split("-")[0] in ("crash", "leak", "timeout", "oom")]
        runs.append({
            "run": d,
            "cov": {k: totals[k]["percent"] for k, _ in METRICS},
            "cats": Counter(r["category"] for r in gap),
            "api_cat": {r["mangled"]: (r["api"], r["category"]) for r in gap},
            "crashes": crashes,
        })
    return runs


def _fmt(vals: list[float], pct: bool = True) -> str:
    med = statistics.median(vals)
    suf = "%" if pct else ""
    if pct:
        return f"{med:.2f}{suf} [{min(vals):.2f}–{max(vals):.2f}]"
    return f"{med:g} [{min(vals):g}–{max(vals):g}]"


def a12(x: list[float], y: list[float]) -> float:
    """Vargha–Delaney A12: y가 x보다 클 확률 (0.5=차이 없음, 1.0=항상 큼)."""
    gt = sum(1 for a in x for b in y if b > a)
    eq = sum(1 for a in x for b in y if b == a)
    return (gt + 0.5 * eq) / (len(x) * len(y))


def stability(runs: list[dict]) -> dict:
    """회차마다 분류가 같은 API 비율, 그리고 매번 바뀐 API 목록."""
    per_api = defaultdict(list)
    for r in runs:
        for m, (name, cat) in r["api_cat"].items():
            per_api[m].append((name, cat))
    stable = [m for m, v in per_api.items() if len({c for _, c in v}) == 1]
    unstable = sorted({v[0][0]: sorted({c for _, c in v}) for m, v in per_api.items()
                       if len({c for _, c in v}) > 1}.items())
    reached_any = {m for m, v in per_api.items() if any(c in ("FULL", "PARTIAL") for _, c in v)}
    reached_all = {m for m, v in per_api.items() if all(c in ("FULL", "PARTIAL") for _, c in v)}
    return {"total": len(per_api), "stable": len(stable), "unstable": unstable,
            "reached_any": reached_any, "reached_all": reached_all}


def summarize(root: str, base: str, target: str, out_md: str, secs: int | None = None) -> dict:
    A, B = load_runs(root, base), load_runs(root, target)
    lines = [f"# 반복 측정 결과 — {base} vs {target}", ""]
    cond = f"각 {len(A)}회/{len(B)}회"
    if secs:
        cond += f", 회당 {secs}초"
    lines += [f"조건: {cond}, 같은 회차는 같은 퍼저 시드, 같은 딕셔너리, ASan+UBSan.",
              "값은 **중앙값 [최솟값–최댓값]**. 커버리지는 라이브러리 소스만 집계 (하네스 코드 제외).", ""]

    lines += ["## 커버리지", "", f"| 지표 | {base} | {target} | A12 | p (Mann-Whitney U, 양측) |",
              "|---|---|---|---:|---:|"]
    result = {"coverage": {}}
    for key, ko in METRICS:
        xa = [r["cov"][key] for r in A]
        xb = [r["cov"][key] for r in B]
        eff = a12(xa, xb)
        p = mannwhitneyu(xa, xb, alternative="two-sided", method="exact").pvalue if mannwhitneyu else float("nan")
        result["coverage"][key] = {"base": xa, "target": xb, "a12": eff, "p": p}
        lines.append(f"| {ko} | {_fmt(xa)} | {_fmt(xb)} | {eff:.2f} | {_p(p)} |")
    lines += ["", "A12는 무작위로 하나씩 뽑았을 때 오른쪽 하네스가 더 높을 확률(0.5면 차이 없음, 1.0이면 항상 높음).",
              f"표본이 {len(A)}개씩일 때 양측 정확검정으로 나올 수 있는 가장 작은 p는 "
              f"{_p(2 / _comb(len(A) + len(B), len(A)))}입니다.", ""]

    lines += ["## 공개 API 분류 (gapfuzz)", "", f"| 분류 | {base} | {target} |", "|---|---|---|"]
    for c in CATS:
        lines.append(f"| {CAT_KO[c]} | {_fmt([r['cats'][c] for r in A], False)} | {_fmt([r['cats'][c] for r in B], False)} |")
    lines.append("")

    sa, sb = stability(A), stability(B)
    lines += ["## 분류 안정성", "",
              "같은 하네스를 반복했을 때 API 분류가 얼마나 일관된지 봅니다.", "",
              f"| | {base} | {target} |", "|---|---:|---:|",
              f"| 모든 회차에서 분류가 같은 API | {sa['stable']}/{sa['total']} | {sb['stable']}/{sb['total']} |",
              f"| 한 번이라도 도달한 API | {len(sa['reached_any'])} | {len(sb['reached_any'])} |",
              f"| 매 회차 도달한 API | {len(sa['reached_all'])} | {len(sb['reached_all'])} |", ""]
    for name, s in ((base, sa), (target, sb)):
        if s["unstable"]:
            lines.append(f"{name}에서 회차마다 분류가 바뀐 API:")
            for api, cats in s["unstable"]:
                lines.append(f"- `{api}`: " + " / ".join(CAT_KO[c] for c in cats))
            lines.append("")

    only_t = sb["reached_all"] - sa["reached_any"]
    lines += [f"{target}에서 매번 도달했지만 {base}에서는 한 번도 도달하지 못한 API: **{len(only_t)}개**", ""]

    lines += ["## 크래시", "", f"| | {base} | {target} |", "|---|---:|---:|",
              f"| 크래시가 난 회차 | {sum(1 for r in A if r['crashes'])}/{len(A)} | {sum(1 for r in B if r['crashes'])}/{len(B)} |", ""]
    for name, runs in ((base, A), (target, B)):
        for r in runs:
            for c in r["crashes"]:
                lines.append(f"- {name} {r['run']}: `{c}`")
    open(out_md, "w").write("\n".join(lines) + "\n")
    result.update({"A": A, "B": B, "stab": (sa, sb)})
    return result


def plot(result: dict, base: str, target: str, out_png: str) -> None:
    """회차별 라인·함수 커버리지를 점으로 찍고 중앙값을 가로선으로 표시한다 (발표용 PNG)."""
    import logging
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)   # 없는 대체 글꼴 경고 숨김

    plt.rcParams["font.family"] = ["Noto Sans CJK KR", "NanumGothic", "Malgun Gothic",
                                   "AppleGothic", "DejaVu Sans"]
    ink, ink2, grid, surface = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
    colors = {base: "#2a78d6", target: "#eb6834"}     # 검증된 범주색 1·2번 (색각이상 대비 통과)

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), dpi=200, facecolor=surface)
    for ax, (key, ko) in zip(axes, [("lines", "라인 커버리지"), ("functions", "함수 커버리지")]):
        ax.set_facecolor(surface)
        for i, name in enumerate((base, target)):
            vals = result["coverage"][key]["base" if name == base else "target"]
            xs = [i + (j - (len(vals) - 1) / 2) * 0.06 for j in range(len(vals))]
            ax.scatter(xs, vals, s=46, color=colors[name], edgecolor=surface, linewidth=1.5, zorder=3)
            med = statistics.median(vals)
            ax.hlines(med, i - 0.22, i + 0.22, color=ink, linewidth=2, zorder=2)
            ax.text(i + 0.26, med, f"중앙값 {med:.1f}%", va="center", ha="left", fontsize=9, color=ink)
        ax.set_xticks([0, 1], [base, target], fontsize=10, color=ink)
        ax.set_xlim(-0.5, 1.9)
        ax.set_ylim(0, 100)
        ax.set_title(ko, fontsize=11, color=ink, loc="left")
        ax.yaxis.grid(True, color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", colors=ink2, labelsize=9, length=0)
        ax.tick_params(axis="x", length=0)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(grid)
        ax.set_ylabel("%", color=ink2, fontsize=9)
    n = len(result["coverage"]["lines"]["base"])
    fig.text(0.01, 0.01, f"점 하나 = 퍼징 1회 (n={n}씩). 라이브러리 소스만 집계.", fontsize=8, color=ink2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out_png, facecolor=surface)
    plt.close(fig)


def _comb(n: int, k: int) -> int:
    from math import comb
    return comb(n, k)
