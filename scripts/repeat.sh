#!/usr/bin/env bash
# 같은 조건으로 여러 하네스를 N번씩 반복 퍼징하고, 회차마다 갭 분석까지 한다.
#
# 사용법: scripts/repeat.sh <회차 수> <퍼징 초> <하네스 이름...>
#   예) scripts/repeat.sh 5 120 official stateful
#
#   - 하네스는 out/asan_<이름>/ 에 미리 빌드되어 있어야 한다 (scripts/build.sh 로 빌드)
#   - 회차 r의 퍼저 시드는 1000+r 로 고정 (모든 하네스가 같은 시드 사용)
#   - 같은 회차의 하네스들은 동시에 실행한다 (코어 수 이상으로 띄우지 않도록 주의)
#   - 결과: out/repeat/<이름>/r<회차>/{coverage.json, coverage_summary.txt, gap/gap.json, fuzz.log}
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
N="$1"; SECS="$2"; shift 2
HARNESSES=("$@")
LIB="${TINYXML2_DIR:-$ROOT/third_party/tinyxml2}"
DICT="${DICT:-$ROOT/dicts/xml.dict}"

for r in $(seq 1 "$N"); do
    pids=()
    for h in "${HARNESSES[@]}"; do
        D="$ROOT/out/repeat/$h/r$r"
        rm -rf "$D"; mkdir -p "$D"
        ln -s "$ROOT/out/asan_$h/fuzz" "$D/fuzz"
        ln -s "$ROOT/out/asan_$h/cov" "$D/cov"
        FUZZ_SEED=$((1000 + r)) HARNESS_SRC="$ROOT/harnesses/$h.cpp" \
            "$ROOT/scripts/run.sh" "$D" "$SECS" "$DICT" > "$D/run.log" 2>&1 &
        pids+=($!)
    done
    for p in "${pids[@]}"; do wait "$p" || echo "[repeat] run failed (pid $p)"; done
    for h in "${HARNESSES[@]}"; do
        D="$ROOT/out/repeat/$h/r$r"
        python3 -m gapfuzz analyze --name "$h-r$r" \
            --header "$LIB/tinyxml2.h" --source "$LIB/tinyxml2.cpp" \
            --harness "$ROOT/harnesses/$h.cpp" --include "$ROOT/harnesses/include" \
            --coverage "$D/coverage.json" --out "$D/gap" > /dev/null
        crashes=$(ls "$D" | grep -cE '^(crash|leak|timeout|oom)-' || true)
        echo "[repeat] r$r $h: $(tail -1 "$D/coverage_summary.txt" | awk '{print "lines " $10}') crashes=$crashes"
    done
done
echo "[repeat] done -> out/repeat/"
