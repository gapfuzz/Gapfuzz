#!/usr/bin/env bash
# 사용법: scripts/run.sh <빌드 디렉터리> <퍼징 초> [딕셔너리] [시드 디렉터리]
#   1) fuzz 바이너리로 정해진 시간 퍼징 → <빌드>/corpus
#   2) cov 바이너리로 코퍼스 재생 → coverage.json (라이브러리 소스만 집계)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
B="$(realpath "$1")"
SECS="${2:-60}"
DICT="${3:-}"
SEEDS="${4:-}"
LIB="${TINYXML2_DIR:-$ROOT/third_party/tinyxml2}"

mkdir -p "$B/corpus"
[ -n "$SEEDS" ] && cp -n "$SEEDS"/* "$B/corpus/" 2>/dev/null || true

ARGS=(-max_total_time="$SECS" -rss_limit_mb=2048 -timeout=10 -print_final_stats=1
      -artifact_prefix="$B/")                       # 크래시 파일을 실행 위치가 아니라 빌드 디렉터리에 저장
[ -n "$DICT" ] && ARGS+=(-dict="$DICT")
[ -n "${FUZZ_SEED:-}" ] && ARGS+=(-seed="$FUZZ_SEED")   # 반복 실험 재현용 난수 시드

echo "[run] fuzzing ${SECS}s ..."
"$B/fuzz" "${ARGS[@]}" "$B/corpus" > "$B/fuzz.log" 2>&1 || echo "[run] fuzzer exited non-zero (see fuzz.log)"
echo "[run] corpus size: $(ls "$B/corpus" | wc -l)"

# 크래시가 나왔으면 원인 귀속(하네스 탓/라이브러리 탓)을 바로 돌린다. HARNESS_SRC에 하네스 소스 경로를 주면 동작.
if ls "$B" | grep -qE '^(crash|leak|timeout|oom)-' && [ -n "${HARNESS_SRC:-}" ]; then
    echo "[run] crash found -> triage"
    (cd "$ROOT" && python3 -m gapfuzz triage "$B" --binary "$B/fuzz" --harness "$HARNESS_SRC" \
        --harness-dir "$ROOT/harnesses" --lib-dir "$LIB" --out "$B/triage.md") || echo "[run] triage failed"
fi

echo "[run] replaying corpus for coverage ..."
rm -f "$B"/cov-*.profraw
LLVM_PROFILE_FILE="$B/cov-%p.profraw" "$B/cov" -runs=0 "$B/corpus" > "$B/cov.log" 2>&1 || true
llvm-profdata merge -sparse "$B"/cov-*.profraw -o "$B/cov.profdata"

# 분모 고정: 라이브러리 소스(tinyxml2.cpp, tinyxml2.h)만 집계
llvm-cov export -format=text -instr-profile="$B/cov.profdata" "$B/cov" \
    "$LIB/tinyxml2.cpp" "$LIB/tinyxml2.h" > "$B/coverage.json"
llvm-cov report -instr-profile="$B/cov.profdata" "$B/cov" \
    "$LIB/tinyxml2.cpp" "$LIB/tinyxml2.h" | tee "$B/coverage_summary.txt" | tail -3
echo "[run] -> $B/coverage.json"
