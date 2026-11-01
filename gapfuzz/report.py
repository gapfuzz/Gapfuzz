"""분석 결과를 Markdown / HTML 리포트로 쓴다."""
from __future__ import annotations

import html
import os
from collections import Counter, defaultdict

CAT_ORDER = ["NOT_CALLED", "BLOCKED", "PARTIAL", "FULL"]
CAT_KO = {
    "NOT_CALLED": "호출 안 함",
    "BLOCKED": "호출 경로 있음 · 조건에 막힘",
    "PARTIAL": "도달 · 일부 분기 미실행",
    "FULL": "완전 도달",
}
CAT_FIX = {
    "NOT_CALLED": "하네스에 이 API(또는 상위 API) 호출을 추가",
    "BLOCKED": "막힌 조건을 만족시키는 입력·상태를 만들어 줌",
    "PARTIAL": "입력·옵션 다양화(분기 조건 확인)",
    "FULL": "조치 불필요",
}


def _rel(path: str, root: str) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


def _short_lines(lines: list[int], n: int = 8) -> str:
    s = ", ".join(str(x) for x in lines[:n])
    return s + (f" 외 {len(lines) - n}개" if len(lines) > n else "")


def summary(results: list[dict]) -> Counter:
    return Counter(r["category"] for r in results)


VERDICT_KO = {
    "FIXED": "하네스가 인자를 고정",
    "SETTER_NOT_CALLED": "값을 정하는 API를 하네스가 안 부름",
    "NARROW": "하네스가 값의 범위를 좁힘",
    "DIRECT_CALL": "공개 API를 하네스가 직접 안 부름",
    "VARIES": "인자는 바뀌지만 맞는 값이 안 나옴",
    "ALLOC_FAIL": "할당 실패·크기 넘침 처리 (하네스로 못 엶)",
    "INTERNAL": "라이브러리 내부에서 정해짐",
    "UNKNOWN": "출처 추적 실패",
}
ARG_KO = {"default": "기본값", "literal": "상수", "same_object": "같은 객체", "fuzzer": "퍼저 입력", "variable": "변수"}


def _fix_counts(res: list[dict]) -> Counter:
    """막힌 분기마다 가장 앞선 원인 판정으로 센다."""
    return Counter(b["causes"][0]["verdict"] for r in res for b in r.get("stuck_branches", []) if b.get("causes"))


def _fixes_markdown(data: dict) -> list[str]:
    fixes = data.get("harness_fixes", [])
    res = data["results"]
    vc = _fix_counts(res)
    total = sum(vc.values())
    out = ["## 하네스에서 고칠 곳", "",
           "도달한 API 안에서 한쪽으로만 간 조건을 거슬러 올라가, 그 값이 **하네스의 어떤 호출·인자에서 정해지는지** 찾은 결과입니다.", ""]
    if total:
        out += ["| 막힌 분기의 원인 | 개수 |", "|---|---:|"]
        for v in ("FIXED", "SETTER_NOT_CALLED", "NARROW", "DIRECT_CALL", "VARIES", "ALLOC_FAIL", "INTERNAL", "UNKNOWN"):
            if vc[v]:
                out.append(f"| {VERDICT_KO[v]} | {vc[v]} |")
        out.append(f"| 합계 | {total} |")
        out.append("")
    if not fixes:
        out += ["하네스가 고정한 인자나 빠진 설정 API는 없었습니다.", ""]
        return out
    for i, g in enumerate(fixes, 1):
        where = ", ".join(f"{l}행" for l in g["harness_lines"]) or "하네스에 호출 없음"
        out.append(f"### {i}. [{VERDICT_KO[g['verdict']]}] {where}")
        out.append(f"- {g['suggestion']}")
        for s in g.get("harness_source", [])[:2]:
            out.append(f"- 하네스 코드: `{s}`")
        out.append(f"- 이 때문에 막힌 분기 {len(g['blocked'])}개:")
        for b in g["blocked"][:5]:
            out.append(f"  - `{b['api']}` {b['line']}행 조건 `{b.get('expr') or b['source']}` 한 번도 {b['never']} 아님")
        if len(g["blocked"]) > 5:
            out.append(f"  - … 외 {len(g['blocked']) - 5}개")
        out.append("")
    return out


def write_markdown(data: dict, path: str) -> None:
    meta, res = data["meta"], data["results"]
    root = meta.get("root", "")
    cnt = summary(res)
    total = len(res)
    out = [f"# 커버리지 갭 리포트 — {meta.get('name', '')}", ""]
    out += [f"- 하네스: `{meta.get('harness', '')}`",
            f"- 대상 헤더: `{meta.get('header', '')}`",
            f"- 공개 API 수: **{total}**", ""]
    out += ["## 요약", "", "| 분류 | 개수 | 비율 | 조치 |", "|---|---:|---:|---|"]
    for c in CAT_ORDER:
        out.append(f"| {CAT_KO[c]} | {cnt[c]} | {cnt[c] / total:.0%} | {CAT_FIX[c]} |")
    out.append("")

    by_cls = defaultdict(Counter)
    for r in res:
        by_cls[r["cls"] or "(자유 함수)"][r["category"]] += 1
    out += ["## 클래스별", "", "| 클래스 | " + " | ".join(CAT_KO[c] for c in CAT_ORDER) + " |",
            "|---|" + "---:|" * len(CAT_ORDER)]
    for k in sorted(by_cls):
        out.append(f"| {k} | " + " | ".join(str(by_cls[k][c]) for c in CAT_ORDER) + " |")
    out.append("")

    out += _fixes_markdown(data)

    out += ["## 호출 안 함", "", "하네스의 실행 경로에서 이 함수로 가는 호출 자체가 없습니다. 퍼징을 오래 돌려도 열리지 않으므로 하네스를 바꿔야 합니다.", ""]
    for r in [r for r in res if r["category"] == "NOT_CALLED"]:
        line = f"- `{r['api']}` (헤더 {r['decl_line']}행) — {r['note']}"
        if r["entry_apis"]:
            line += "  \n  경로를 여는 상위 API: " + ", ".join(f"`{a}`" for a in r["entry_apis"])
        out.append(line)
    out.append("")

    out += ["## 호출 경로 있음 · 조건에 막힘", "", "이미 실행된 함수 안에 이 API로 가는 호출이 있지만, 그 줄까지 실행이 도달하지 못했습니다. 아래 조건을 만족시키는 입력·상태가 필요합니다.", ""]
    for r in [r for r in res if r["category"] == "BLOCKED"]:
        out.append(f"### `{r['api']}`")
        for b in r["blocks"]:
            out.append(f"- 막힌 지점: `{b['caller']}` @ {_rel(b['file'], root)}:{b['line']}")
            out.append(f"  - 소스: `{b['source']}`")
            if len(b["chain"]) > 2:
                out.append("  - 경로: " + " → ".join(f"`{c}`" for c in b["chain"]))
        out.append("")

    out += ["## 도달 · 일부 분기 미실행", "",
            "API는 실행됐지만 안쪽 조건문 일부가 한 방향으로만 갔습니다. '한 번도 참/거짓 아님'인 조건을 만족시키는 입력·상태·옵션을 만들면 열립니다.", ""]
    for r in sorted([r for r in res if r["category"] == "PARTIAL"],
                    key=lambda r: r["region_hit"] / max(r["region_total"], 1)):
        out.append(f"### `{r['api']}` — 영역 {r['region_hit']}/{r['region_total']} 실행")
        for b in r["stuck_branches"][:6]:
            out.append(f"- {_rel(b['file'], root)}:{b['line']} 조건 `{b.get('expr') or b['source']}` 한 번도 **{b['never']}** 아님 — `{b['source']}`")
            for c in b.get("causes", [])[:2]:
                out.append(f"  - 원인({VERDICT_KO[c['verdict']]}): {c['suggestion']}")
        if len(r["stuck_branches"]) > 6:
            out.append(f"- … 외 {len(r['stuck_branches']) - 6}개 조건")
        if not r["stuck_branches"] and r["missed_lines"]:
            out.append(f"- 미실행 줄: {_short_lines(r['missed_lines'])}")
        out.append("")

    full = [r for r in res if r["category"] == "FULL"]
    out += ["## 완전 도달", "", ", ".join(f"`{r['api']}`" for r in full) or "(없음)", ""]
    open(path, "w").write("\n".join(out))


def write_html(data: dict, path: str) -> None:
    meta, res = data["meta"], data["results"]
    root = meta.get("root", "")
    cnt = summary(res)
    total = len(res) or 1
    e = html.escape

    cards = "".join(
        f'<div class="card c-{c.lower()}"><div class="n">{cnt[c]}</div>'
        f'<div class="l">{CAT_KO[c]}</div><div class="f">{CAT_FIX[c]}</div></div>'
        for c in CAT_ORDER)
    bar = "".join(
        f'<span class="seg c-{c.lower()}" style="width:{cnt[c] / total * 100:.2f}%" title="{CAT_KO[c]} {cnt[c]}"></span>'
        for c in CAT_ORDER)

    rows = []
    for r in res:
        detail = ""
        if r["category"] == "NOT_CALLED":
            detail = e(r["note"])
            if r["entry_apis"]:
                detail += "<br><span class='muted'>상위 API:</span> " + ", ".join(f"<code>{e(a)}</code>" for a in r["entry_apis"])
        elif r["category"] == "BLOCKED":
            parts = []
            for b in r["blocks"]:
                p = (f"<code>{e(b['caller'])}</code> @ {e(_rel(b['file'], root))}:{b['line']}"
                     f"<pre>{e(b['source'])}</pre>")
                if len(b["chain"]) > 2:
                    p += "<span class='muted'>경로: " + " → ".join(e(c) for c in b["chain"]) + "</span>"
                parts.append(f"<div class='blk'>{p}</div>")
            detail = "".join(parts)
        elif r["category"] == "PARTIAL":
            detail = f"영역 {r['region_hit']}/{r['region_total']} 실행"
            for b in r["stuck_branches"][:4]:
                cz = b.get("causes") or []
                why = (f"<div class='why v-{cz[0]['verdict'].lower()}'><b>{VERDICT_KO[cz[0]['verdict']]}</b> · "
                       f"{e(cz[0]['suggestion'])}</div>") if cz else ""
                detail += (f"<div class='blk'><span class='muted'>{e(_rel(b['file'], root))}:{b['line']} · "
                           f"조건 <code>{e(b.get('expr') or '')}</code> 한 번도 <b>{b['never']}</b> 아님</span>"
                           f"<pre>{e(b['source'])}</pre>{why}</div>")
            if len(r["stuck_branches"]) > 4:
                detail += f"<span class='muted'>… 외 {len(r['stuck_branches']) - 4}개 조건</span>"
            if not r["stuck_branches"] and r["missed_lines"]:
                detail += f" · 미실행 줄: {e(_short_lines(r['missed_lines']))}"
        rows.append(
            f"<tr data-cat='{r['category']}'><td><span class='tag c-{r['category'].lower()}'>{CAT_KO[r['category']]}</span></td>"
            f"<td>{e(r['cls'] or '—')}</td><td><code>{e(r['api'])}</code></td>"
            f"<td class='num'>{r['decl_line'] or ''}</td><td>{detail}</td></tr>")

    filters = "".join(
        f"<label><input type='checkbox' value='{c}' checked> {CAT_KO[c]} ({cnt[c]})</label>"
        for c in CAT_ORDER)

    # ---- 하네스에서 고칠 곳 (차별점 A) ----
    vc = _fix_counts(res)
    fix_items = []
    for i, g in enumerate(data.get("harness_fixes", []), 1):
        where = ", ".join(f"{l}행" for l in g["harness_lines"]) or "하네스에 호출 없음"
        src = "".join(f"<pre>{e(s)}</pre>" for s in g.get("harness_source", [])[:2])
        blocked = "".join(f"<li><code>{e(b['api'])}</code> {b['line']}행 조건 <code>{e(b.get('expr') or b['source'])}</code>"
                          f" 한 번도 {b['never']} 아님</li>" for b in g["blocked"][:5])
        more = f"<li class='muted'>… 외 {len(g['blocked']) - 5}개</li>" if len(g["blocked"]) > 5 else ""
        fix_items.append(
            f"<div class='fix v-{g['verdict'].lower()}'><div class='fh'><span class='num'>{i}</span>"
            f"<span class='vt'>{VERDICT_KO[g['verdict']]}</span><span class='muted'>{e(where)}</span>"
            f"<span class='cnt'>막힌 분기 {len(g['blocked'])}</span></div>"
            f"<p>{e(g['suggestion'])}</p>{src}<ul>{blocked}{more}</ul></div>")
    vrow = "".join(f"<span class='chip v-{v.lower()}'>{VERDICT_KO[v]} <b>{vc[v]}</b></span>"
                   for v in ("FIXED", "SETTER_NOT_CALLED", "NARROW", "DIRECT_CALL", "VARIES", "ALLOC_FAIL", "INTERNAL", "UNKNOWN") if vc[v])
    fixes_html = (
        "<section class='fixes'><h2>하네스에서 고칠 곳</h2>"
        "<p class='muted'>도달한 API 안에서 한쪽으로만 간 조건을 거슬러 올라가, 그 값이 하네스의 어떤 호출·인자에서 정해지는지 찾았습니다.</p>"
        f"<div class='chips'>{vrow}</div>"
        + ("".join(fix_items) or "<p>하네스가 고정한 인자나 빠진 설정 API는 없었습니다.</p>")
        + "</section>") if vc else ""

    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Coverage Gap Report</title>
<style>
:root{{--bg:#fbfbfa;--fg:#1d1d1b;--muted:#6b6b66;--line:#e4e3de;--card:#fff;
--nc:#c2410c;--bl:#a16207;--pa:#2563eb;--fu:#15803d;--code:#f2f1ed}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#161615;--fg:#ecebe6;--muted:#9a9993;--line:#2e2e2b;--card:#1f1f1d;
--nc:#fb923c;--bl:#facc15;--pa:#60a5fa;--fu:#4ade80;--code:#2a2a27}}}}
:root[data-theme="dark"]{{--bg:#161615;--fg:#ecebe6;--muted:#9a9993;--line:#2e2e2b;--card:#1f1f1d;
--nc:#fb923c;--bl:#facc15;--pa:#60a5fa;--fu:#4ade80;--code:#2a2a27}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.55 -apple-system,"Pretendard","Apple SD Gothic Neo","Noto Sans KR",sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:28px 16px 60px}}
h1{{font-size:22px;margin:0 0 4px}} .meta{{color:var(--muted);font-size:13px;margin-bottom:20px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-bottom:12px}}
.card{{background:var(--card);border:1px solid var(--line);border-left:4px solid;border-radius:8px;padding:12px 14px}}
.card .n{{font-size:26px;font-weight:700;font-variant-numeric:tabular-nums}} .card .l{{font-weight:600}} .card .f{{color:var(--muted);font-size:12px}}
.c-not_called{{border-color:var(--nc)}} .c-blocked{{border-color:var(--bl)}} .c-partial{{border-color:var(--pa)}} .c-full{{border-color:var(--fu)}}
.bar{{display:flex;height:10px;border-radius:5px;overflow:hidden;margin:6px 0 22px;background:var(--line)}}
.seg.c-not_called{{background:var(--nc)}} .seg.c-blocked{{background:var(--bl)}} .seg.c-partial{{background:var(--pa)}} .seg.c-full{{background:var(--fu)}}
.filters{{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:10px;font-size:13px}}
.wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}}
table{{border-collapse:collapse;width:100%;min-width:760px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;color:var(--muted);font-weight:600;position:sticky;top:0;background:var(--card)}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}}
code{{background:var(--code);padding:1px 5px;border-radius:4px;font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace}}
pre{{margin:4px 0;background:var(--code);padding:6px 8px;border-radius:6px;font:12px ui-monospace,Menlo,monospace;white-space:pre-wrap}}
.tag{{display:inline-block;border:1px solid;border-radius:999px;padding:1px 8px;font-size:12px;white-space:nowrap}}
.tag.c-not_called{{color:var(--nc)}} .tag.c-blocked{{color:var(--bl)}} .tag.c-partial{{color:var(--pa)}} .tag.c-full{{color:var(--fu)}}
.muted{{color:var(--muted);font-size:12px}} .blk+.blk{{margin-top:8px;padding-top:8px;border-top:1px dashed var(--line)}}
h2{{font-size:17px;margin:26px 0 4px}}
.fixes{{margin:0 0 26px}} .chips{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 14px}}
.chip{{border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:12px;background:var(--card)}}
.fix{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--muted);border-radius:8px;padding:12px 14px;margin-bottom:10px}}
.fix.v-fixed{{border-left-color:var(--nc)}} .fix.v-setter_not_called{{border-left-color:var(--bl)}} .fix.v-narrow{{border-left-color:var(--pa)}}
.fh{{display:flex;flex-wrap:wrap;align-items:center;gap:10px}} .fh .num{{font-weight:700;font-variant-numeric:tabular-nums}}
.fh .vt{{font-weight:600}} .fh .cnt{{margin-left:auto;font-size:12px;color:var(--muted)}}
.fix p{{margin:6px 0}} .fix ul{{margin:6px 0 0;padding-left:18px;font-size:13px}}
.why{{font-size:12.5px;margin-top:4px;padding-left:8px;border-left:3px solid var(--line)}}
.why.v-fixed{{border-left-color:var(--nc)}} .why.v-setter_not_called{{border-left-color:var(--bl)}} .why.v-narrow{{border-left-color:var(--pa)}}
</style></head><body><main>
<h1>커버리지 갭 리포트 — {e(meta.get('name', ''))}</h1>
<div class="meta">하네스 <code>{e(meta.get('harness', ''))}</code> · 공개 API {len(res)}개 · 대상 <code>{e(meta.get('header', ''))}</code></div>
<div class="cards">{cards}</div>
<div class="bar">{bar}</div>
{fixes_html}
<h2>공개 API 전체</h2>
<div class="filters">{filters}</div>
<div class="wrap"><table><thead><tr><th>분류</th><th>클래스</th><th>API</th><th>헤더 행</th><th>근거 / 다음 조치</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
</main>
<script>
document.querySelectorAll('.filters input').forEach(cb=>cb.addEventListener('change',()=>{{
  const on=new Set([...document.querySelectorAll('.filters input:checked')].map(x=>x.value));
  document.querySelectorAll('tbody tr').forEach(tr=>tr.style.display=on.has(tr.dataset.cat)?'':'none');
}}));
</script></body></html>"""
    open(path, "w").write(doc)


def write_diff(a: dict, b: dict, path: str) -> None:
    """두 하네스의 분석 결과를 비교한다 (a: 기준, b: 비교 대상)."""
    ra = {r["mangled"]: r for r in a["results"]}
    rb = {r["mangled"]: r for r in b["results"]}
    reached = {"FULL", "PARTIAL"}
    newly, lost, moved = [], [], []
    for m, r in rb.items():
        old = ra.get(m)
        if not old:
            continue
        if r["category"] in reached and old["category"] not in reached:
            newly.append((old, r))
        elif old["category"] in reached and r["category"] not in reached:
            lost.append((old, r))
        elif old["category"] != r["category"]:
            moved.append((old, r))
    ca, cb = summary(a["results"]), summary(b["results"])
    na, nb = a["meta"].get("name", "A"), b["meta"].get("name", "B")
    out = [f"# 하네스 비교 — {na} → {nb}", "",
           f"| 분류 | {na} | {nb} | 변화 |", "|---|---:|---:|---:|"]
    for c in CAT_ORDER:
        out.append(f"| {CAT_KO[c]} | {ca[c]} | {cb[c]} | {cb[c] - ca[c]:+d} |")
    out += ["", f"## {nb}에서 새로 도달한 API ({len(newly)}개)", ""]
    out += [f"- `{r['api']}` ({CAT_KO[o['category']]} → {CAT_KO[r['category']]})" for o, r in newly] or ["(없음)"]
    out += ["", f"## {nb}에서 도달하지 못하게 된 API ({len(lost)}개)", ""]
    out += [f"- `{r['api']}` ({CAT_KO[o['category']]} → {CAT_KO[r['category']]})" for o, r in lost] or ["(없음)"]
    out += ["", f"## 분류만 바뀐 API ({len(moved)}개)", ""]
    out += [f"- `{r['api']}` ({CAT_KO[o['category']]} → {CAT_KO[r['category']]})" for o, r in moved] or ["(없음)"]
    open(path, "w").write("\n".join(out) + "\n")
