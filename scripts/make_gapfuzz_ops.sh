#!/usr/bin/env bash
# 라이브러리마다 새 하네스 gapfuzz_ops를 만든다 (evaluation/README.md 2부 A2).
#
#   bash scripts/make_gapfuzz_ops.sh                 # 11개 전부, 하네스가 적은 것부터
#   bash scripts/make_gapfuzz_ops.sh cjson zlib      # 고른 것만
#   FORCE=1 bash scripts/make_gapfuzz_ops.sh cjson   # 이미 있어도 다시 만든다 (실험을 시작한 뒤에는 쓰지 말 것)
#
# 필요: 컨테이너 안, 환경 변수 ANTHROPIC_API_KEY. 모델은 기본 claude-sonnet-5-5 (GAPFUZZ_MODEL로 바꿈).
# 하나가 실패해도 다음 라이브러리로 넘어간다. 로그: out/ops_logs/<라이브러리>.log
set -u
cd "$(dirname "$0")/.."

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "ANTHROPIC_API_KEY가 없습니다. evaluation/README.md 2부의 A1을 보세요." >&2
    exit 1
fi

LIBS=("$@")
if [ ${#LIBS[@]} -eq 0 ]; then
    LIBS=(cjson jsoncpp http-parser expat pugixml tinyxml2 libucl yyjson json-c zlib libyaml)
fi

mkdir -p out/ops_logs
echo "모델: ${GAPFUZZ_MODEL:-claude-sonnet-5-5}   도구 커밋: $(git rev-parse --short HEAD 2>/dev/null || echo '?')   시작: $(date '+%Y-%m-%d %H:%M')"

for lib in "${LIBS[@]}"; do
    log="out/ops_logs/$lib.log"
    if ls "harnesses/$lib"/gapfuzz_ops.* >/dev/null 2>&1 && [ -z "${FORCE:-}" ]; then
        echo "=== $lib: 이미 있음, 건너뜀 ($(ls "harnesses/$lib"/gapfuzz_ops.*))"
        continue
    fi
    echo "=== $lib 시작 $(date +%H:%M)"
    python3 scripts/exp.py fetch "$lib" > "$log" 2>&1
    python3 -m gapfuzz llmops "$lib" --union >> "$log" 2>&1
    tail -2 "$log"
done

echo
echo "=== 요약 $(date '+%Y-%m-%d %H:%M')"
for lib in "${LIBS[@]}"; do
    f=$(ls "harnesses/$lib"/gapfuzz_ops.* 2>/dev/null | head -1)
    if [ -n "$f" ]; then
        echo "  만들어짐  $lib  $f"
    else
        echo "  없음      $lib  (이유: out/ops_logs/$lib.log, out/llm/$lib/union_ops/report.md)"
    fi
done
