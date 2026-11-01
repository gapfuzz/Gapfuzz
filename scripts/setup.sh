#!/usr/bin/env bash
# 처음 한 번 실행: TinyXML2 소스와 OSS-Fuzz 딕셔너리를 받아온다.
# 시스템 clang에 libFuzzer 런타임이 없으면 LLVM 소스에서 직접 빌드한다(대개 WSL에서는 불필요).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TP="$ROOT/third_party"
mkdir -p "$TP" "$ROOT/dicts"

# 1) TinyXML2 (재현성을 위해 커밋 고정)
TINYXML2_COMMIT="${TINYXML2_COMMIT:-8224e42}"
if [ ! -d "$TP/tinyxml2" ]; then
    git clone -q https://github.com/leethomason/tinyxml2.git "$TP/tinyxml2"
    git -C "$TP/tinyxml2" checkout -q "$TINYXML2_COMMIT" || echo "[setup] 커밋 $TINYXML2_COMMIT 없음, 최신 버전 사용"
fi
echo "[setup] tinyxml2 @ $(git -C "$TP/tinyxml2" log -1 --format=%h)"

# 2) OSS-Fuzz 공식 딕셔너리
if [ ! -f "$ROOT/dicts/xml.dict" ]; then
    rm -rf "$TP/oss-fuzz"
    git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/oss-fuzz.git "$TP/oss-fuzz"
    git -C "$TP/oss-fuzz" sparse-checkout set projects/tinyxml2
    cp "$TP/oss-fuzz/projects/tinyxml2/xml.dict" "$ROOT/dicts/"
fi
echo "[setup] dict: dicts/xml.dict"

# 3) libFuzzer 런타임 확인
probe="$(mktemp -d)"
echo 'extern "C" int LLVMFuzzerTestOneInput(const char*,unsigned long){return 0;}' > "$probe/p.cpp"
if clang++ -fsanitize=fuzzer,address "$probe/p.cpp" -o "$probe/p" 2>/dev/null; then
    echo "[setup] 시스템 clang의 libFuzzer/ASan 사용 가능"
else
    echo "[setup] 시스템 런타임 없음 → LLVM 소스에서 libFuzzer/profile 런타임 빌드"
    ver="$(clang --version | sed -n 's/.*clang version \([0-9.]*\).*/\1/p' | head -1)"
    git clone -q --depth 1 --filter=blob:none --sparse --branch "llvmorg-$ver" \
        https://github.com/llvm/llvm-project.git "$TP/llvm-project"
    git -C "$TP/llvm-project" sparse-checkout set compiler-rt/lib/fuzzer compiler-rt/lib/profile compiler-rt/include
    SRC="$TP/llvm-project/compiler-rt"; RT="$TP/rt"; mkdir -p "$RT/fz" "$RT/pf"
    (cd "$RT/fz" && for f in "$SRC"/lib/fuzzer/Fuzzer*.cpp; do clang++ -c -O2 -std=c++17 -fPIC -w "$f"; done && ar rcs "$RT/libFuzzer.a" ./*.o)
    (cd "$RT/pf" && for f in "$SRC"/lib/profile/*.c "$SRC"/lib/profile/*.cpp; do
        case $f in *Windows*|*Darwin*|*AIX*|*Fuchsia*|*Baremetal*|*Mingw*) continue;; esac
        clang -c -O2 -fPIC -w -I"$SRC/include" -I"$SRC/lib/profile" \
            -DCOMPILER_RT_HAS_UNAME=1 -DCOMPILER_RT_HAS_ATOMICS=1 -DCOMPILER_RT_HAS_FCNTL_LCK=1 "$f"
    done && ar rcs "$RT/libprofile.a" ./*.o)
    echo "[setup] -> $RT/libFuzzer.a, $RT/libprofile.a (이 경우 ASan은 생략됨)"
fi
rm -rf "$probe"

# 4) (선택) 추가 실험 재료: scripts/setup.sh --extra
#    - TinyXML2 옛 버전 4개: 버그 재발견·크래시 귀속 실험용 (각 버그를 고친 커밋의 바로 앞)
#    - pugixml, cJSON: 다른 라이브러리 일반화 실험용
if [ "${1:-}" = "--extra" ]; then
    [ -d "$TP/tinyxml2_hist" ] || git clone -q https://github.com/leethomason/tinyxml2.git "$TP/tinyxml2_hist"
    for spec in "tx_cve:494735d^" "tx_del:aba13c5^" "tx_stack:d946dda^" "tx_assert21:9efb6b0^"; do
        d="${spec%%:*}"; c="${spec#*:}"
        [ -d "$TP/$d" ] || git -C "$TP/tinyxml2_hist" worktree add -q "$TP/$d" "$c"
        echo "[setup] $d @ $(git -C "$TP/$d" log -1 --format=%h)"
    done
    [ -d "$TP/pugixml" ] || git clone -q --depth 1 https://github.com/zeux/pugixml "$TP/pugixml"
    [ -d "$TP/cjson" ] || git clone -q --depth 1 https://github.com/DaveGamble/cJSON.git "$TP/cjson"
    echo "[setup] pugixml @ $(git -C "$TP/pugixml" log -1 --format=%h), cjson @ $(git -C "$TP/cjson" log -1 --format=%h)"
fi
