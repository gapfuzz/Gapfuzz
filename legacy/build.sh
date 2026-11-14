#!/usr/bin/env bash
# 사용법: scripts/build.sh <하네스.cpp> [출력 디렉터리]
#   <출력>/fuzz : libFuzzer 퍼징용 바이너리 (가능하면 ASan+UBSan 포함)
#   <출력>/cov  : 커버리지 측정용 바이너리 (-fprofile-instr-generate -fcoverage-mapping)
#
# 시스템 clang에 compiler-rt(libFuzzer/ASan/profile 런타임)가 없으면
# GAPFUZZ_RT 디렉터리의 libFuzzer.a / libprofile.a를 대신 사용한다(ASan은 생략).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HARNESS="$(realpath "$1")"
NAME="$(basename "${HARNESS%.*}")"
OUT="${2:-$ROOT/out/$NAME}"
LIB="${TINYXML2_DIR:-$ROOT/third_party/tinyxml2}"
RT="${GAPFUZZ_RT:-$ROOT/third_party/rt}"
CXX="${CXX:-clang++}"
mkdir -p "$OUT"

COMMON=(-g -O1 -fno-omit-frame-pointer -fno-optimize-sibling-calls -std=c++17 -I"$LIB" -I"$ROOT/harnesses/include" ${EXTRA_CXXFLAGS:-})  # EXTRA_CXXFLAGS 예: -DTINYXML2_DEBUG (assert 켜기)

# 시스템 런타임 사용 가능 여부 확인
probe="$(mktemp -d)"
echo 'extern "C" int LLVMFuzzerTestOneInput(const char*,unsigned long){return 0;}' > "$probe/p.cpp"
if "$CXX" -fsanitize=fuzzer,address,undefined "$probe/p.cpp" -o "$probe/p" 2>/dev/null; then
    MODE=system
else
    MODE=bundled
fi
rm -rf "$probe"
echo "[build] $NAME (runtime: $MODE)"

# 1) 퍼징 바이너리
if [ "$MODE" = system ]; then
    "$CXX" "${COMMON[@]}" -fsanitize=fuzzer,address,undefined \
        "$HARNESS" "$LIB/tinyxml2.cpp" -o "$OUT/fuzz"
else
    # 계측은 컴파일 단계에서만 넣고, 링크는 sanitizer 플래그 없이 직접 한다
    "$CXX" "${COMMON[@]}" -fsanitize=fuzzer-no-link -c "$HARNESS" -o "$OUT/h_fuzz.o"
    "$CXX" "${COMMON[@]}" -fsanitize=fuzzer-no-link -c "$LIB/tinyxml2.cpp" -o "$OUT/lib_fuzz.o"
    "$CXX" "$OUT/h_fuzz.o" "$OUT/lib_fuzz.o" "$RT/libFuzzer.a" -lpthread -o "$OUT/fuzz"
fi

# 2) 커버리지 바이너리 (같은 하네스 + 라이브러리, 소스 기반 커버리지)
CF=(-fprofile-instr-generate -fcoverage-mapping)
if [ "$MODE" = system ]; then
    "$CXX" "${COMMON[@]}" "${CF[@]}" -fsanitize=fuzzer \
        "$HARNESS" "$LIB/tinyxml2.cpp" -o "$OUT/cov"
else
    "$CXX" "${COMMON[@]}" "${CF[@]}" -c "$HARNESS" -o "$OUT/h_cov.o"
    "$CXX" "${COMMON[@]}" "${CF[@]}" -c "$LIB/tinyxml2.cpp" -o "$OUT/lib_cov.o"
    "$CXX" "$OUT/h_cov.o" "$OUT/lib_cov.o" "$RT/libFuzzer.a" \
        -Wl,--whole-archive "$RT/libprofile.a" -Wl,--no-whole-archive \
        -Wl,-u,__llvm_profile_runtime -lpthread -o "$OUT/cov"
fi
echo "[build] -> $OUT/fuzz, $OUT/cov"
