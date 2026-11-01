"""LLM 하네스 수정 슬라이드(llm_slide.tpl.html)의 숫자를 samples/llm/summary.json으로 채워 midterm.src.html에 넣는다.

사용법: python3 fill_llm.py   (그 뒤 build_deck.py로 다시 빌드)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = json.load(open(HERE.parent / "samples" / "llm" / "summary.json"))
n = len(rows)
ok = sum(r["llm_ok"] for r in rows)
first = sum(r["first_try_ok"] for r in rows)
tgt = sum(r["targets"] for r in rows)
opened = sum(r["llm_opened"] for r in rows)
both = [r for r in rows if r["human"]]
h_open, h_tot = sum(r["human"][0] for r in both), sum(r["human"][1] for r in both)
l_open, l_tot = sum(r["llm_opened"] for r in both), sum(r["targets"] for r in both)
filt = sum(r["harness_crashes"] for r in rows)
comp = sum(r["compile_fail"] for r in rows)
libs = len({r["lib"] for r in rows})
vals = {
    "@@PASS@@": f"{ok}<small>/{n}</small>",
    "@@FIRST@@": f"{first}개",
    "@@OPEN@@": f"{opened}<small>/{tgt}</small>",
    "@@HUMAN@@": (f"사람도 적용했던 제안 {len(both)}개만 보면 사람 {h_open}/{h_tot}, Claude {l_open}/{l_tot}. "
                  f"라이브러리 {libs}개, 검사는 60초 × 2회 퍼징 (사람 결과는 120초 × 5회)."),
    "@@FILTER@@": ((f"이번 실험에서 컴파일 실패 {comp}번" + (f", 하네스 탓 크래시 {filt}번" if filt else "") + "을 걸러 다시 고치게 했습니다. ")
                   + "아직 막힌 분기를 알려 주자 두 번째 시도에 연 경우도 있었습니다(cJSON: 앞의 null 검사를 피해 안쪽 함수를 직접 부름)."),
    "@@SCRIPT@@": (f"라이브러리 {libs}개의 고칠 곳 {n}개를 모두 맡겨 보니 {ok}개가 통과했고, 겨냥한 분기 {tgt}개 중 {opened}개가 열렸습니다. "
                   f"사람이 고쳤던 제안끼리 비교하면 {h_tot}개 중 사람이 {h_open}개, Claude가 {l_open}개를 열었습니다."),
}
tpl = (HERE / "llm_slide.tpl.html").read_text(encoding="utf-8")
for k, v in vals.items():
    tpl = tpl.replace(k, v)
src = (HERE / "midterm.src.html").read_text(encoding="utf-8")
start = src.find("<!-- LLM 하네스 수정 슬라이드")
if start >= 0:
    end = src.index("</section>", start) + len("</section>\n\n")
    src = src[:start] + tpl + src[end:]
else:
    at = src.index("<!-- 최종 발표까지 -->")
    src = src[:at] + tpl + src[at:]
(HERE / "midterm.src.html").write_text(src, encoding="utf-8")
print(f"[fill_llm] 통과 {ok}/{n}, 첫 시도 {first}, 열림 {opened}/{tgt}, 사람 {h_open}/{h_tot} vs Claude {l_open}/{l_tot}")
