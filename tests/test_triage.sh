#!/usr/bin/env bash
# 크래시 원인 귀속(C) 테스트: 일부러 만든 11가지 크래시가 기대한 분류로 나오는지 확인
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
F=tests/fixtures/fakelib
B=out/test_triage
rm -rf "$B"; mkdir -p "$B/crashes"

if ! clang++ -g -O1 -fno-optimize-sibling-calls -std=c++17 -fsanitize=fuzzer,address,undefined -I"$F" \
        "$F/triage_harness.cpp" "$F/fakelib.cpp" -o "$B/fuzz" 2>"$B/build.log"; then
    echo "SKIP: ASan/libFuzzer 런타임이 없어 빌드할 수 없음 (build.log 참고)"; exit 0
fi

# 첫 바이트가 크래시 종류를 고른다
printf 'Oabcdefgh'     > "$B/crashes/crash-lib-overflow"
printf 'Ax'            > "$B/crashes/crash-assert"
printf 'Uhello world, this string is long enough for the heap' > "$B/crashes/crash-harness-uaf"
printf 'Uhi'           > "$B/crashes/crash-harness-scope"     # 짧은 문자열은 std::string 안(스택)에 저장됨
printf 'Habcdefghijkl' > "$B/crashes/crash-harness-stack"
printf 'T\x00'         > "$B/crashes/timeout-loop"
printf 'Mx'            > "$B/crashes/oom-alloc"
printf 'Zzz'           > "$B/crashes/crash-not-a-crash"
printf 'Dx'            > "$B/crashes/crash-harness-destroy-use"
printf 'Fx'            > "$B/crashes/crash-harness-double-destroy"
printf 'Ix'            > "$B/crashes/crash-lib-internal-uaf"

python3 -m gapfuzz triage "$B/crashes" --binary "$B/fuzz" \
    --harness "$F/triage_harness.cpp" --lib-dir "$F" --repeat 2 --timeout 2 \
    --name test_triage --out "$B/triage.md" > "$B/triage.out"

python3 - "$B/triage.json" <<'EOF'
import json, os, sys
crashes = json.load(open(sys.argv[1]))["crashes"]
by_file = {os.path.basename(f): c for c in crashes for f in c["files"]}
expect = {
    "crash-lib-overflow":  "LIBRARY",
    "crash-assert":        "ASSERT",
    "crash-harness-uaf":   "HARNESS",
    "crash-harness-scope": "HARNESS",
    "crash-harness-stack": "HARNESS",
    "timeout-loop":        "RESOURCE",
    "oom-alloc":           "RESOURCE",
    "crash-not-a-crash":   "UNCLEAR",
    "crash-harness-destroy-use":    "HARNESS",
    "crash-harness-double-destroy": "HARNESS",
    "crash-lib-internal-uaf":       "LIBRARY",
}
fails = 0
for f, want in expect.items():
    got = by_file.get(f, {}).get("verdict", {}).get("cls")
    ok = got == want
    fails += not ok
    print(("PASS " if ok else "FAIL ") + f"{f}: 기대 {want}, 실제 {got}")
uaf = by_file["crash-harness-uaf"]["verdict"]["evidence"]
ok = any("해제 위치" in e and "triage_harness.cpp" in e for e in uaf)
fails += not ok
print(("PASS " if ok else "FAIL ") + "하네스 UAF의 근거가 하네스의 해제 위치를 가리킴")
ok = by_file["crash-lib-overflow"]["reproduced"] == "2/2"
fails += not ok
print(("PASS " if ok else "FAIL ") + "라이브러리 결함이 매번 재현됨")
sys.exit(1 if fails else 0)
EOF
