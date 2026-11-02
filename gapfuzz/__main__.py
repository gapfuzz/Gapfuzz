"""gapfuzz — 커버리지 갭 분석기

사용법
  python3 -m gapfuzz analyze --name official \\
      --header third_party/tinyxml2/tinyxml2.h \\
      --source third_party/tinyxml2/tinyxml2.cpp \\
      --harness harnesses/official.cpp \\
      --coverage out/official/coverage.json \\
      --out out/official/gap

  python3 -m gapfuzz diff out/official/gap/gap.json out/stateful/gap/gap.json --out diff.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .analyze import Analyzer, DEFAULT_INTERNAL_CLASSES, load_coverage, results_to_json
from .ast_index import build_index
from .report import summary, write_diff, write_html, write_markdown, CAT_ORDER, CAT_KO


def cmd_analyze(a) -> int:
    inc = [os.path.dirname(os.path.abspath(h)) for h in a.header] + (a.include or [])
    idx = build_index(a.source + [a.harness], inc, [f"-D{d}" for d in (a.define or [])])
    cov = load_coverage(a.coverage)
    internal = a.internal_class if a.internal_class is not None else list(DEFAULT_INTERNAL_CLASSES)
    results = Analyzer(idx, cov, a.header, a.namespace, internal, harness_files=[a.harness],
                       internal_branches=a.internal_branches).run()

    os.makedirs(a.out, exist_ok=True)
    meta = {"name": a.name, "harness": a.harness, "header": ", ".join(a.header),
            "root": os.path.abspath(a.root or os.getcwd())}
    data = results_to_json(results, meta)
    json.dump(data, open(os.path.join(a.out, "gap.json"), "w"), ensure_ascii=False, indent=1)
    write_markdown(data, os.path.join(a.out, "gap_report.md"))
    write_html(data, os.path.join(a.out, "gap_report.html"))

    cnt = summary(data["results"])
    print(f"[gapfuzz] {a.name}: 공개 API {len(results)}개")
    for c in CAT_ORDER:
        print(f"  {CAT_KO[c]:<22} {cnt[c]:>4}")
    print(f"[gapfuzz] -> {a.out}/gap_report.html, gap_report.md, gap.json")
    return 0


def cmd_diff(a) -> int:
    write_diff(json.load(open(a.base)), json.load(open(a.target)), a.out)
    print(f"[gapfuzz] -> {a.out}")
    return 0


def cmd_stats(a) -> int:
    from .stats import plot, summarize
    res = summarize(a.root, a.base, a.target, a.out, a.secs)
    print(f"[gapfuzz] -> {a.out}")
    if a.plot:
        plot(res, a.base, a.target, a.plot)
        print(f"[gapfuzz] -> {a.plot}")
    return 0


def cmd_triage(a) -> int:
    import glob
    from .triage import CLASS_KO, triage, write_reports
    files = []
    for c in a.crashes:
        if os.path.isdir(c):
            files += sorted(f for f in glob.glob(os.path.join(c, "*"))
                            if os.path.basename(f).split("-")[0] in ("crash", "leak", "timeout", "oom"))
        else:
            files.append(c)
    res = triage(a.binary, files, a.harness, a.lib_dir, a.harness_dir, a.repeat, a.timeout, root=a.root)
    write_reports(res, a.out, {"name": a.name or os.path.basename(a.binary), "binary": a.binary, "repeat": a.repeat})
    print(f"[gapfuzz] 크래시 입력 {len(files)}개 → 서로 다른 크래시 {len(res)}개")
    for r in res:
        print(f"  {CLASS_KO[r.verdict.cls]:<16} (확신 {r.verdict.confidence}) {r.kind}  재현 {r.reproduced}  입력 {len(r.files)}개")
    print(f"[gapfuzz] -> {a.out}")
    return 0


def cmd_verify(a) -> int:
    from .verify import write_verify
    before = json.load(open(a.before))
    afters = [json.load(open(p)) for p in a.after]
    applied = [int(x) for x in a.applied.split(",")] if a.applied else None
    res = write_verify(before, afters, a.out, applied)
    for i, g in enumerate(res, 1):
        mark = "" if applied is None or i in applied else " (미적용)"
        print(f"  제안 {i}{mark}: 막혀 있던 분기 {g['total']}개 중 {g['opened']}개 열림")
    print(f"[gapfuzz] -> {a.out}")
    return 0


def cmd_ops(a) -> int:
    import re
    from .opgen import OpGen
    inc = [os.path.dirname(os.path.abspath(h)) for h in a.header] + (a.include or [])
    idx = build_index(a.source + [a.harness], inc, [f"-D{d}" for d in (a.define or [])])
    an = Analyzer(idx, load_coverage(a.coverage), a.header, a.namespace, list(DEFAULT_INTERNAL_CLASSES),
                  harness_files=[a.harness])
    results = [__import__("dataclasses").asdict(r) for r in an.run()]
    src = open(a.harness, encoding="utf-8").read()
    sw = max(re.finditer(r"switch \(fdp\.ConsumeIntegralInRange<int>\(0, (\d+)\)\)", src), key=lambda m: int(m.group(1)))
    nmax = int(sw.group(1))
    code, rows = OpGen(an, a.namespace).generate(results, nmax + 1, a.top)
    n_new = code.count("[자동 생성]")
    out = src[:sw.start()] + f"switch (fdp.ConsumeIntegralInRange<int>(0, {nmax + n_new}))" + src[sw.end():]
    d = out.rfind("        default:")
    out = out[:d] + code + "\n" + out[d:]
    head = (f"// [gapfuzz ops] {os.path.basename(a.harness)}에 '호출 안 함' API {n_new}개의 연산을 자동으로 추가한 버전.\n"
            f"// 우선순위: 그 API로 새로 실행될 수 있는 코드 영역 수. 생성 규칙은 gapfuzz/opgen.py 참고.\n")
    open(a.out, "w", encoding="utf-8").write(head + out)
    lines = ["# 호출 안 함 API 우선순위와 연산 초안", "",
             f"하네스: `{a.harness}`. 상위 {n_new}개를 `{a.out}`에 넣음.", "",
             "| 순위 | API | 새로 실행될 수 있는 함수 | 코드 영역 | 생성 |", "|---|---|---|---|---|"]
    for i, x in enumerate(rows, 1):
        lines.append(f"| {i} | `{x['api']}` | {x['functions']} | {x['regions']} | {'✓' if x['code'] else x['skip']} |")
    if a.report:
        open(a.report, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"[gapfuzz] 호출 안 함 API {len(rows)}개 중 자동 생성 가능 {sum(1 for x in rows if x['code'])}개, 상위 {n_new}개 추가 -> {a.out}")
    return 0


def cmd_dict(a) -> int:
    from .dictgen import generate, write_dict
    gaps = [json.load(open(p)) for p in a.gap]
    entries = generate(gaps, a.source, existing=a.base)
    write_dict(entries, a.out, base=a.base if a.merge else None)
    print(f"[gapfuzz] 딕셔너리 후보 {len(entries)}개")
    for e in entries[:20]:
        print(f"  {e['kind']:<6} {e['token']!r:<12} ← {e['evidence'][0]}")
    print(f"[gapfuzz] -> {a.out}")
    return 0


def cmd_llmfix(a) -> int:
    from .llmfix import DEFAULT_MODEL, list_fixes, run
    if a.list:
        list_fixes(a.target, a.harness, a.before)
        return 0
    if not a.fix:
        raise SystemExit("--fix 번호가 필요합니다 (--list로 확인)")
    nos = [int(x) for x in str(a.fix).split(",")]
    res = run(a.target, a.harness, nos[0] if len(nos) == 1 else nos, a.before, a.secs, a.trials, a.tries,
              a.model or DEFAULT_MODEL, a.mock.split(",") if a.mock else None, hints=a.hints)
    return 0 if res["best"] else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="gapfuzz", description="커버리지 갭 분석기")
    sub = p.add_subparsers(dest="cmd", required=True)

    an = sub.add_parser("analyze", help="하네스 하나의 커버리지를 공개 API 단위로 분류")
    an.add_argument("--name", required=True)
    an.add_argument("--header", required=True, action="append", help="공개 API가 선언된 헤더 (여러 번 가능)")
    an.add_argument("--source", required=True, action="append", help="라이브러리 구현 소스 (여러 번 가능)")
    an.add_argument("--harness", required=True)
    an.add_argument("--coverage", required=True, help="llvm-cov export JSON")
    an.add_argument("--out", required=True)
    an.add_argument("--namespace", default="tinyxml2")
    an.add_argument("--include", action="append", help="추가 include 디렉터리")
    an.add_argument("--define", action="append", help="빌드와 같은 전처리 정의 (NAME 또는 NAME=값)")
    an.add_argument("--internal-class", action="append",
                    help="공개 API에서 제외할 내부 클래스 (기본: %s)" % ", ".join(DEFAULT_INTERNAL_CLASSES))
    an.add_argument("--root", help="리포트에 상대 경로로 표시할 기준 디렉터리")
    an.add_argument("--internal-branches", action="store_true",
                    help="공개 API가 부르는 내부 함수의 막힌 분기도 가장 가까운 공개 API 아래에 모은다 "
                         "(실제 처리가 내부 함수에 있는 라이브러리용, 예: pugixml)")
    an.set_defaults(func=cmd_analyze)

    df = sub.add_parser("diff", help="두 하네스 분석 결과 비교")
    df.add_argument("base")
    df.add_argument("target")
    df.add_argument("--out", required=True)
    df.set_defaults(func=cmd_diff)

    st = sub.add_parser("stats", help="반복 실행 결과 요약 (scripts/repeat.sh 출력)")
    st.add_argument("--root", default="out/repeat")
    st.add_argument("--base", required=True)
    st.add_argument("--target", required=True)
    st.add_argument("--secs", type=int, help="회당 퍼징 시간(리포트 표기용)")
    st.add_argument("--out", required=True)
    st.add_argument("--plot", help="회차별 커버리지 그래프 PNG 경로 (matplotlib 필요)")
    st.set_defaults(func=cmd_stats)

    tr = sub.add_parser("triage", help="크래시가 하네스 탓인지 라이브러리 탓인지 분류")
    tr.add_argument("crashes", nargs="+", help="크래시 입력 파일 또는 그 파일들이 있는 디렉터리")
    tr.add_argument("--binary", required=True, help="퍼징용 바이너리 (sanitizer 포함)")
    tr.add_argument("--harness", action="append", required=True, help="하네스 소스 (여러 번 가능)")
    tr.add_argument("--lib-dir", action="append", required=True, help="라이브러리 소스 디렉터리 (여러 번 가능)")
    tr.add_argument("--harness-dir", action="append",
                    help="하네스 쪽으로 볼 디렉터리 (기본: 하네스 파일이 있는 디렉터리)")
    tr.add_argument("--repeat", type=int, default=3, help="재현 확인 횟수")
    tr.add_argument("--timeout", type=int, default=10)
    tr.add_argument("--name")
    tr.add_argument("--root", help="리포트에 상대 경로로 표시할 기준 디렉터리")
    tr.add_argument("--out", required=True)
    tr.set_defaults(func=cmd_triage)

    vf = sub.add_parser("verify", help="'하네스에서 고칠 곳' 제안을 적용한 뒤 막힌 분기가 열렸는지 확인")
    vf.add_argument("before", help="수정 전 gap.json")
    vf.add_argument("after", nargs="+", help="수정 후 gap.json (여러 회차 가능)")
    vf.add_argument("--applied", help="실제로 적용한 제안 번호 (예: 1,2,3). 생략하면 전부 적용한 것으로 봄")
    vf.add_argument("--out", required=True)
    vf.set_defaults(func=cmd_verify)

    op = sub.add_parser("ops", help="'호출 안 함' API 우선순위를 매기고 스테이트풀 하네스에 연산 초안을 넣은 사본을 만든다")
    op.add_argument("--header", required=True, action="append"); op.add_argument("--source", required=True, action="append")
    op.add_argument("--harness", required=True, help="연산을 추가할 스테이트풀 하네스")
    op.add_argument("--coverage", required=True); op.add_argument("--include", action="append")
    op.add_argument("--define", action="append")
    op.add_argument("--namespace", default="tinyxml2")
    op.add_argument("--top", type=int, default=15)
    op.add_argument("--out", required=True, help="새 하네스 파일"); op.add_argument("--report")
    op.set_defaults(func=cmd_ops)

    dc = sub.add_parser("dict", help="입력 내용에 막힌 분기의 조건식에서 딕셔너리 후보 생성")
    dc.add_argument("gap", nargs="+", help="gap.json (여러 회차 가능)")
    dc.add_argument("--source", action="append", required=True, help="상수 정의를 찾을 라이브러리 소스·헤더")
    dc.add_argument("--base", help="기존 딕셔너리 (이미 있는 토큰은 제외)")
    dc.add_argument("--merge", action="store_true", help="기존 딕셔너리 내용까지 합쳐서 출력")
    dc.add_argument("--out", required=True)
    dc.set_defaults(func=cmd_dict)

    lf = sub.add_parser("llmfix", help="'하네스에서 고칠 곳'을 Claude API로 하네스에 적용하고 검증·크래시 귀속으로 검사")
    lf.add_argument("target", help="targets/<이름>.json의 이름 (예: zlib, tinyxml2)")
    lf.add_argument("harness", help="수정할 하네스 이름 (예: official)")
    lf.add_argument("--fix", help="적용할 제안 번호 (--list로 확인). 1,3,4처럼 여러 개면 한 하네스에 모두 적용")
    lf.add_argument("--hints", action="store_true", help="제안별로 따로 검증을 통과한 수정(best.diff)을 참고로 함께 보냄")
    lf.add_argument("--list", action="store_true", help="제안 목록만 출력")
    lf.add_argument("--before", help="수정 전 gap.json (기본 out/targets/<이름>/<하네스>/r1/gap/gap.json)")
    lf.add_argument("--secs", type=int, default=60, help="검사용 퍼징 시간(초, 회당)")
    lf.add_argument("--trials", type=int, default=2, help="검사용 퍼징 횟수")
    lf.add_argument("--tries", type=int, default=3, help="LLM에게 다시 묻는 최대 횟수")
    lf.add_argument("--model", help="Claude 모델 (기본 claude-sonnet-5-5)")
    lf.add_argument("--mock", help="API 대신 쓸 응답 파일들 (쉼표로 구분, 시도 순서대로)")
    lf.set_defaults(func=cmd_llmfix)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
