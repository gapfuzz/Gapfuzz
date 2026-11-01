#!/usr/bin/env bash
# 모든 테스트 실행
#   run_tests.sh   : 호출 경로 분류(BLOCKED/NOT_CALLED) — TinyXML2로 짧게 퍼징
#   test_causes.sh : 차별점 A, 하네스가 고정한 인자 탐지 — 가짜 라이브러리, 결정적
#   test_triage.sh : 차별점 C, 크래시 원인 귀속 — 가짜 라이브러리, 결정적
#   triage_real    : 크래시 원인 귀속 — 실제 TinyXML2 크래시 9건 (scripts/setup.sh --extra 필요, 없으면 건너뜀)
set -uo pipefail
cd "$(dirname "$0")"
fail=0
for t in run_tests.sh test_causes.sh test_triage.sh; do
    echo "== $t"
    if ./"$t"; then :; else fail=1; fi
done
echo "== triage_real/run.py"
if [ -d ../third_party/tx_del ] && [ -d ../third_party/tx_cve ] && [ -d ../third_party/tx_stack ] && [ -d ../third_party/tx_assert21 ]; then
    (cd .. && python3 tests/triage_real/run.py) || fail=1
else
    echo "SKIP: TinyXML2 옛 버전이 없음 (scripts/setup.sh --extra)"
fi
echo
[ "$fail" = 0 ] && echo "모든 테스트 통과" || { echo "실패한 테스트 있음"; exit 1; }
