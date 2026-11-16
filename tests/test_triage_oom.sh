#!/usr/bin/env bash
# libFuzzer out-of-memory 리포트의 스택을 읽는지 확인 (빌드 없이, 저장해 둔 로그로).
# 2026-11-16: jsoncpp에서 Json::Path::makePath가 2.5GB를 한 번에 요청해 죽었는데, 오류 줄과 스택 사이의 안내 줄 때문에
# 스택을 놓쳐 "가장 가까운 코드: ?"로만 나왔다. 그래서 Claude에게 어느 API가 문제인지 전달되지 않았다.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
from gapfuzz import triage as T
txt = open("tests/fixtures/triage_logs/jsoncpp_path_oom.log", errors="replace").read()
own = T.Owner(["/work/harnesses/jsoncpp/llm/union_ops/try1.cpp"], ["/work/harnesses"], ["/work/third_party/jsoncpp"])
rep = T.parse_report(txt, own)
v = T.classify(rep, "/work")
ev = "\n".join(v.evidence)
assert rep.kind == "out-of-memory" and rep.access, "스택을 읽지 못함"
assert rep.request == 2684354560, rep.request
assert v.cls == "RESOURCE" and "library" in v.reason, v.reason
assert "Json::Path::makePath" in ev and "Json::Path::Path" in ev and "RunOps" in ev and "try1.cpp" in ev, ev
print("[test_triage_oom] 통과: out-of-memory 스택에서 라이브러리 위치와 하네스가 부른 API를 읽음")
PY
