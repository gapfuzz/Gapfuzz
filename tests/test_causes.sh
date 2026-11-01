#!/usr/bin/env bash
# 고정 인자 탐지(A) 테스트: 가짜 라이브러리 Widget::Run의 다섯 조건이 기대한 원인으로 판정되는지 확인
# 퍼징 없이 정해진 입력만 넣어 커버리지를 만들기 때문에 결과가 항상 같다.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
F=tests/fixtures/fakelib
B=out/test_causes
rm -rf "$B"; mkdir -p "$B/inputs"

if ! clang++ -g -O0 -std=c++17 -fprofile-instr-generate -fcoverage-mapping -fsanitize=fuzzer -I"$F" \
        "$F/causes_harness.cpp" "$F/fakelib.cpp" -o "$B/cov" 2>"$B/build.log"; then
    echo "SKIP: libFuzzer/커버리지 런타임이 없어 빌드할 수 없음 (build.log 참고)"; exit 0
fi

# 'x'로 시작하는 입력은 일부러 넣지 않는다 (s[0]=='x' 조건이 열리지 않게)
printf 'abc' > "$B/inputs/a"; printf 'de' > "$B/inputs/b"; printf 'q' > "$B/inputs/c"
LLVM_PROFILE_FILE="$B/cov-%p.profraw" "$B/cov" -runs=0 "$B/inputs" > "$B/cov.log" 2>&1 || true
llvm-profdata merge -sparse "$B"/cov-*.profraw -o "$B/cov.profdata"
llvm-cov export -format=text -instr-profile="$B/cov.profdata" "$B/cov" \
    "$F/fakelib.cpp" "$F/fakelib.h" > "$B/coverage.json"

python3 -m gapfuzz analyze --name test_causes --namespace fakelib \
    --header "$F/fakelib.h" --source "$F/fakelib.cpp" --harness "$F/causes_harness.cpp" \
    --coverage "$B/coverage.json" --out "$B/gap" > /dev/null

python3 - "$B/gap/gap.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
run = next(r for r in d["results"] if r["api"].startswith("Widget::Run"))
by_src = {b["source"]: b for b in run["stuck_branches"]}
fails = 0

def check(cond, msg):
    global fails
    fails += not cond
    print(("PASS " if cond else "FAIL ") + msg)

def first(src_part):
    b = next((b for s, b in by_src.items() if src_part in s), None)
    return b["causes"][0] if b and b["causes"] else None

check(run["category"] == "PARTIAL", f"Widget::Run은 PARTIAL (실제 {run['category']})")

c = first("if (verbose_)")
check(c and c["verdict"] == "FIXED" and c["param_name"] == "verbose" and c["via_field"] == "verbose_",
      f"verbose_ 조건 → 생성자 2번째 인자 verbose를 하네스가 고정 (실제 {c and (c['verdict'], c['param_name'], c['via_field'])})")
check(c and all(s["kind"] == "default" for s in c["sites"]) and len(c["sites"]) == 2,
      "verbose는 두 생성 지점 모두 기본값")

c = first("if (strict)")
check(c and c["verdict"] == "FIXED" and c["param_name"] == "strict" and all(s["kind"] == "default" for s in c["sites"]),
      f"strict 조건 → Run 2번째 인자를 하네스가 기본값으로 고정 (실제 {c and c['verdict']})")

c = first("if (HasLabel())")
check(c and c["verdict"] == "SETTER_NOT_CALLED" and "SetLabel" in (c["api"] or ""),
      f"HasLabel 조건 → 게터를 거쳐 label_ → SetLabel을 하네스가 안 부름 (실제 {c and (c['verdict'], c['api'])})")

c = first("if (mode_ == 2)")
kinds = sorted({s["kind"] for s in c["sites"]}) if c else []
check(c and c["verdict"] == "VARIES" and kinds == ["literal", "variable"],
      f"mode_ 조건 → w(1)은 상수, w2(data[0]%2)는 변수라 VARIES (실제 {c and c['verdict']}, {kinds})")

c = first("if (s[0] == 'x')")
check(c and c["verdict"] == "VARIES" and c["param_name"] == "s",
      f"s[0]=='x' 조건 → Run 1번째 인자 s는 입력에 따라 바뀜 (실제 {c and c['verdict']})")

c = first("if (q[0] == 'y')")
check(c and c["verdict"] == "VARIES" and c["param_name"] == "s",
      f"지역 변수 q를 거쳐도 Run 1번째 인자 s로 추적 (실제 {c and (c['verdict'], c['param_name'])})")

c = first("if (!s)")
check(c and c["verdict"] == "NARROW" and c["narrow_kind"] == "never_null",
      f"!s 조건 → 하네스가 null을 넘긴 적 없음 (실제 {c and (c['verdict'], c['narrow_kind'])})")

lvl = next(r for r in d["results"] if r["api"].startswith("Widget::Level"))
lb = next((b for b in lvl["stuck_branches"] if "lvl == 5" in b["source"]), None)
c = lb["causes"][0] if lb else None
check(c and c["verdict"] == "NARROW" and c["narrow_kind"] == "choice" and c["sites"][0]["value"] == "1|2",
      f"lvl == 5 조건 → 하네스가 1, 2 중에서만 고름 (실제 {c and (c['verdict'], c['narrow_kind'], c['sites'][0]['value'])})")

fixes = d["harness_fixes"]
check(any(g["verdict"] == "FIXED" and g["param_name"] == "verbose" for g in fixes) and
      any(g["verdict"] == "FIXED" and g["param_name"] == "strict" for g in fixes) and
      any(g["verdict"] == "SETTER_NOT_CALLED" and "SetLabel" in g["apis"][0] for g in fixes),
      "'하네스에서 고칠 곳'에 verbose, strict, SetLabel이 모두 나옴")
check(not any(g["param_name"] == "mode" for g in fixes),
      "입력에 따라 바뀌는 mode는 '고칠 곳'에 넣지 않음")
check(any(g["verdict"] == "NARROW" and g["param_name"] == "lvl" for g in fixes) and
      any(g["verdict"] == "NARROW" and g["param_name"] == "s" for g in fixes),
      "'고칠 곳'에 선택지 제한(lvl)과 null 미전달(s)이 나옴")
sys.exit(1 if fails else 0)
EOF
