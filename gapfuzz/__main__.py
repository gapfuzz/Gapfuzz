"""gapfuzz — 커버리지 갭 분석기

보통은 라이브러리 설정 파일(targets/<이름>.json)을 읽는 실행기로 돌린다.
  python3 scripts/tgt.py build  zlib official
  python3 scripts/tgt.py repeat zlib official --trials 1 --secs 120     # 퍼징 → 커버리지 → analyze
  python3 -m gapfuzz llmfix zlib --list                                 # 하네스에서 고칠 곳
  python3 -m gapfuzz llmops zlib --list                                 # 호출 안 함 API 우선순위

직접 부를 때
  python3 -m gapfuzz analyze --name zlib-official \\
      --header third_party/zlib/zlib.h --source third_party/zlib/inflate.c ... \\
      --harness harnesses/zlib/official.cc --namespace "" \\
      --coverage out/targets/zlib/official/r1/coverage.json --out out/targets/zlib/official/r1/gap
  python3 -m gapfuzz diff <수정 전 gap.json> <수정 후 gap.json> --out diff.md
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
    from .argtrace import load_runtime
    results = Analyzer(idx, cov, a.header, a.namespace, internal, harness_files=[a.harness],
                       internal_branches=a.internal_branches, runtime=load_runtime(a.args)).run()

    os.makedirs(a.out, exist_ok=True)
    meta = {"name": a.name, "harness": a.harness, "header": ", ".join(a.header),
            "root": os.path.abspath(a.root or os.getcwd())}
    data = results_to_json(results, meta)
    from .analyze import assert_branches
    data["assert_branches"] = assert_branches(a.coverage)
    json.dump(data, open(os.path.join(a.out, "gap.json"), "w"), ensure_ascii=False, indent=1)
    write_markdown(data, os.path.join(a.out, "gap_report.md"))
    write_html(data, os.path.join(a.out, "gap_report.html"))

    cnt = summary(data["results"])
    print(f"[gapfuzz] {a.name}: 공개 API {len(results)}개")
    for c in CAT_ORDER:
        print(f"  {CAT_KO[c]:<22} {cnt[c]:>4}")
    if data["harness_fix_candidates"] or data["assert_branches"]:
        print(f"  확장 분석 후보 {len(data['harness_fix_candidates'])}곳, 어서션 안의 분기 {len(data['assert_branches'])}개 (gap_report.md 참고)")
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


def cmd_argtrace(a) -> int:
    from .argtrace import run
    run(a.target, a.harness, a.corpus, a.out)
    return 0


def cmd_inputcheck(a) -> int:
    from .inputcheck import run
    run(a.target, a.harness, a.before, a.secs, a.trials, a.fresh)
    return 0


def cmd_llmops(a) -> int:
    from .llmfix import DEFAULT_MODEL
    from .llmops import choose, ranking, ranking_md, run
    apis = a.api.split(",") if a.api else None
    if a.list:
        _, _, _, _, rows = ranking(a.target, a.harness, a.before, union=a.union)
        print(ranking_md(a.target, "_union (OSS-Fuzz 하네스 전체)" if a.union else a.harness, rows, choose(rows, a.top, apis)))
        return 0
    res = run(a.target, a.harness, a.top, a.before, a.secs, a.trials, a.tries, a.model or DEFAULT_MODEL,
              a.mock.split(",") if a.mock else None, apis=apis, save=a.save, union=a.union)
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
    an.add_argument("--args", help="argtrace가 만든 args.json (실행 중 관찰한 인자 값을 판정 근거로 사용)")
    an.add_argument("--out", required=True)
    an.add_argument("--namespace", default="", help="공개 API의 네임스페이스 (C 라이브러리는 비워 둠)")
    an.add_argument("--include", action="append", help="추가 include 디렉터리")
    an.add_argument("--define", action="append", help="빌드와 같은 전처리 정의 (NAME 또는 NAME=값)")
    an.add_argument("--internal-class", action="append",
                    help="공개 API에서 제외할 내부 클래스 (여러 번 지정 가능, 기본 없음)")
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

    st = sub.add_parser("stats", help="반복 실행 결과 요약 (scripts/tgt.py repeat 출력)")
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
    lf.add_argument("--model", help="Claude 모델 (기본 claude-sonnet-5-5, 환경 변수 GAPFUZZ_MODEL로도 지정)")
    lf.add_argument("--mock", help="API 대신 쓸 응답 파일들 (쉼표로 구분, 시도 순서대로)")
    lf.set_defaults(func=cmd_llmfix)

    lo = sub.add_parser("llmops", help="'호출 안 함' 공개 API의 호출을 Claude API로 하네스에 추가하고 퍼징·크래시 귀속으로 검사 (모든 라이브러리)")
    lo.add_argument("target", help="targets/<이름>.json의 이름 (예: zlib, expat, tinyxml2)")
    lo.add_argument("harness", nargs="?", default="official", help="넓힐 하네스 이름 (기본 official)")
    lo.add_argument("--top", type=int, default=10, help="우선순위 상위 몇 개를 추가할지 (기본 10)")
    lo.add_argument("--api", help="우선순위 대신 직접 고를 API 이름 (쉼표로 구분, 이름 일부만 써도 됨)")
    lo.add_argument("--list", action="store_true", help="우선순위 표만 출력 (API 호출 없음)")
    lo.add_argument("--union", action="store_true",
                    help="OSS-Fuzz 하네스 전체의 커버리지를 합친 기준으로, 어느 하네스도 안 부르는 API를 부르는 '새 하네스'를 만든다 "
                         "(기존 하네스는 고치지 않음, 저장 이름 gapfuzz_ops)")
    lo.add_argument("--before", help="수정 전 gap.json (기본 out/targets/<이름>/<하네스>/r1/gap/gap.json, 없으면 120초 진단부터)")
    lo.add_argument("--secs", type=int, default=60, help="검사용 퍼징 시간(초, 회당)")
    lo.add_argument("--trials", type=int, default=2, help="검사용 퍼징 횟수")
    lo.add_argument("--tries", type=int, default=3, help="Claude에게 다시 묻는 최대 횟수")
    lo.add_argument("--model", help="Claude 모델 (기본 claude-sonnet-5-5, 환경 변수 GAPFUZZ_MODEL로도 지정)")
    lo.add_argument("--save", help="통과한 하네스를 저장할 이름 (기본 <하네스>_ops)")
    lo.add_argument("--mock", help="API 대신 쓸 응답 파일들 (쉼표로 구분, 시도 순서대로)")
    lo.set_defaults(func=cmd_llmops)

    at = sub.add_parser("argtrace", help="하네스가 라이브러리를 부르는 지점의 실제 인자 값을 코퍼스 재실행으로 기록 (analyze --args로 반영)")
    at.add_argument("target"); at.add_argument("harness", nargs="?", default="official")
    at.add_argument("--corpus", action="append", help="재실행할 코퍼스 디렉터리 (여러 번 지정 가능, 기본 out/targets/<이름>/<하네스>/r1/corpus)")
    at.add_argument("--out", help="결과 파일 (기본 <코퍼스 상위>/args.json)")
    at.set_defaults(func=cmd_argtrace)

    ic = sub.add_parser("inputcheck", help="'입력 탓'으로 판정한 분기를 확인: 조건식에서 딕셔너리를 만들어 다시 퍼징하고 열린 분기를 센다")
    ic.add_argument("target"); ic.add_argument("harness", nargs="?", default="official")
    ic.add_argument("--before", help="기준 실행 폴더 (기본 out/targets/<이름>/<하네스>/r1)")
    ic.add_argument("--secs", type=int, default=600, help="확인용 퍼징 시간(초, 회당). 입력 탓 분기는 열리는 데 시간이 걸리므로 기본 10분")
    ic.add_argument("--trials", type=int, default=3, help="딕셔너리 없이/넣고 각각 몇 번 돌릴지 (기본 3)")
    ic.add_argument("--fresh", action="store_true", help="빈 코퍼스에서 시작 (기본: 기준 실행의 코퍼스에서 이어서 퍼징)")
    ic.set_defaults(func=cmd_inputcheck)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
