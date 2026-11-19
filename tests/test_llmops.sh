#!/usr/bin/env bash
# llmops 흐름 시험 (API 키 없이): 준비해 둔 응답 두 개를 Claude 대신 넣는다.
#   1번 응답은 일부러 컴파일 오류가 있고, 2번 응답은 고친 것이다.
#   기대: 시도 1 컴파일 실패 → 오류를 돌려줌 → 시도 2에서 요청한 API 8개가 모두 실행되고 크래시 없음.
# 필요: third_party/zlib (python3 scripts/exp.py fetch zlib), clang 18. 약 1~3분.
set -euo pipefail
cd "$(dirname "$0")/.."
F=tests/fixtures/llmops
python3 -m gapfuzz llmops zlib --top 8 --secs 30 --trials 2 --tries 2 --save _test_ops \
    --mock "$F/zlib_try1_compile_error.md,$F/zlib_try2_ok.md"
python3 - <<'PY'
import json
d = json.load(open("out/llm/zlib/official_ops/log.json"))
t1, t2 = d["tries"]
assert t1["stage"] == "compile" and not t1["ok"], t1
assert t2["ok"] and t2["called"] == 8 and t2["total"] == 8 and not t2["crashes"] and not t2["lost"], t2
print("[test_llmops] 통과: 시도 1 컴파일 실패 → 시도 2에서 8/8 실행, 크래시 0")
PY
rm -f harnesses/zlib/_test_ops.cc
rm -rf evaluation/artifacts/llm/ops/zlib/official harnesses/zlib/llm/official_ops
