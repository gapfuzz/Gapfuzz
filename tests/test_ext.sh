#!/usr/bin/env bash
# 확장 판정 시험: 콜백 미등록(CALLBACK), 상태를 바꾸는 API 미호출(STATE), 어서션(ASSERT), 실행 중 관찰한 고정 인자(argtrace).
# 가짜 C 라이브러리(tests/fixtures/extlib)에 정해진 입력 60개만 넣으므로 결과가 항상 같다. 퍼징 없음, 약 10초.
set -euo pipefail
cd "$(dirname "$0")/.."
D=out/targets/_exttest/ext_harness
rm -rf "$D"
if ! python3 scripts/tgt.py build _exttest ext_harness > /dev/null 2>"out/test_ext_build.log"; then
    echo "SKIP: libFuzzer/커버리지 런타임이 없어 빌드할 수 없음 (out/test_ext_build.log 참고)"; exit 0
fi
R="$D/r1"; mkdir -p "$R/corpus"
for i in $(seq 1 60); do head -c "$i" /dev/zero | tr '\0' 'a' > "$R/corpus/in$i"; done
LLVM_PROFILE_FILE="$R/cov-%p.profraw" "$D/cov" -runs=0 "$R/corpus" > "$R/cov.log" 2>&1
llvm-profdata merge -sparse "$R"/cov-*.profraw -o "$R/cov.profdata"
llvm-cov export -format=text -instr-profile="$R/cov.profdata" "$D/cov" \
    tests/fixtures/extlib/extlib.c tests/fixtures/extlib/extlib.h > "$R/coverage.json"

python3 scripts/tgt.py analyze _exttest ext_harness "$R"          # 1) 실행 기록 없이
cp "$R/gap/gap.json" "$R/gap_static.json"
python3 -m gapfuzz argtrace _exttest ext_harness > "$R/argtrace.log"
python3 scripts/tgt.py analyze _exttest ext_harness "$R"          # 2) args.json 반영

python3 - "$R" <<'PY'
import json, sys
R = sys.argv[1]
fails = 0
def check(cond, msg):
    global fails
    fails += not cond
    print(("PASS " if cond else "FAIL ") + msg)

def branches(path):
    d = json.load(open(path))
    feed = next(r for r in d["results"] if r["api"].startswith("ext_feed"))
    return d, {b["source"].strip(): b for b in feed["stuck_branches"]}

def has(b, verdict, **kw):
    return any(c["verdict"] == verdict and all(str(kw[k]) in str(c.get(k)) for k in kw) for c in (b["causes"] if b else []))

def find(bs, part):
    return next((b for s, b in bs.items() if part in s), None)

s, sb = branches(f"{R}/gap_static.json")
d, db = branches(f"{R}/gap/gap.json")

b = find(db, "if (c->on_item)")
check(has(b, "CALLBACK", api="ext_set_handler"), "on_item 조건 → 콜백 등록 API ext_set_handler를 하네스가 안 부름 (CALLBACK)")
b = find(db, "if (c->dirty)")
check(has(b, "STATE", api="ext_mark_dirty"), "dirty 조건 → 상태를 바꾸는 ext_mark_dirty를 하네스가 안 부름 (STATE)")
ab = d.get("assert_branches", [])
check(len(ab) == 1 and "EXT_ASSERT(size < 100000)" in ab[0]["source"], f"어서션 매크로 안의 분기 → assert_branches에 따로 분류 ({len(ab)}개)")

b0, b1 = find(sb, "if (level > 5)"), find(db, "if (level > 5)")
c0 = b0["causes"][0] if b0 and b0["causes"] else None
check(c0 and c0["verdict"] == "VARIES", f"level 조건, 실행 기록 없이 → 변수라서 '값은 바뀜' (실제 {c0 and c0['verdict']})")
check(has(b1, "FIXED", ext="runtime") and any("값 1가지" in (c.get("evidence") or "") for c in b1["causes"]),
      "level 조건, argtrace 반영 → 모든 호출에서 값이 한 가지 → 고정(FIXED, 근거: 실행 중 관찰)")

legacy = lambda g: [f for f in g["harness_fixes"]]
check(legacy(s) == [] or all(not f.get("ext") for f in legacy(s)), "기존 '하네스에서 고칠 곳' 목록에는 확장 판정이 섞이지 않음")
cands = d.get("harness_fix_candidates", [])
check(len(cands) >= 3, f"확장 판정은 harness_fix_candidates에 따로 들어감 ({len(cands)}개)")
print("\n[test_ext] 통과" if not fails else f"\n[test_ext] 실패 {fails}건")
sys.exit(1 if fails else 0)
PY
