#!/usr/bin/env bash
# llmops --union 흐름 시험 (API 키 없이): OSS-Fuzz 하네스 전체의 커버리지를 합치고,
# 어느 하네스도 안 부르는 API를 부르는 '새 하네스'를 만드는 흐름을 미리 써 둔 응답으로 돌려 본다.
#   기대: zlib에서 합친 기준 '호출 안 함'이 하네스 하나 기준보다 적고, 새 하네스가 요청한 10개를 모두 실행하며 크래시가 없다.
# 필요: third_party/zlib, harnesses/zlib/official_*.c(c) (OSS-Fuzz 하네스 전체), clang 18. 처음에는 하네스 9개를 각각 60초 돌려서 10분쯤 걸린다.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/tgt.py union zlib --secs 60 | tail -1
python3 -m gapfuzz llmops zlib --union --top 10 --secs 30 --trials 2 --tries 1 --save _test_union_ops \
    --mock tests/fixtures/llmops/zlib_union_ok.md | tail -3
python3 - <<'PY'
import json
u = json.load(open("out/targets/zlib/_union/r1/union.json"))
assert u["not_called_union"] < min(u["not_called_each"].values()), u
d = json.load(open("out/llm/zlib/union_ops/log.json"))
t = d["tries"][0]
assert t["ok"] and t["called"] == t["total"] == 10 and not t["crashes"] and not t["lost"], t
names = " ".join(d["chosen"])
assert "compress(" not in names and "deflateParams" not in names, "다른 하네스가 이미 부르는 API가 뽑혔다: " + names
print(f"[test_llmops_union] 통과: 하네스 하나 기준 {u['not_called_each']['official']}개 → 합친 기준 {u['not_called_union']}개 안 부름, "
      f"새 하네스가 {t['called']}/{t['total']} 실행, 크래시 0")
PY
rm -f harnesses/zlib/_test_union_ops.cc
rm -rf evaluation/artifacts/llm/ops/zlib/_union harnesses/zlib/llm/union_ops
