#!/usr/bin/env bash
# 분석기 회귀 테스트: 빌드 → 짧은 퍼징 → 분석 → 기대 분류 확인
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
B=out/test_blocked
LIB=third_party/tinyxml2

scripts/build.sh tests/blocked_harness.cpp "$B" > /dev/null
scripts/run.sh "$B" "${SECS:-15}" > /dev/null
python3 -m gapfuzz analyze --name test_blocked --header $LIB/tinyxml2.h --source $LIB/tinyxml2.cpp \
    --harness tests/blocked_harness.cpp --include harnesses/include \
    --coverage "$B/coverage.json" --out "$B/gap" > /dev/null

python3 - "$B/gap/gap.json" <<'EOF'
import json, sys
res = {r["api"]: r for r in json.load(open(sys.argv[1]))["results"]}
src = open("tests/blocked_harness.cpp").read().splitlines()
site = next(i + 1 for i, l in enumerate(src) if "BLOCKED_SITE" in l)
fails = 0

def check(cond, msg):
    global fails
    print(("PASS " if cond else "FAIL ") + msg)
    fails += 0 if cond else 1

p = res["XMLDocument::Print(XMLPrinter *) const"]
check(p["category"] == "BLOCKED", f"XMLDocument::Print 는 BLOCKED (실제: {p['category']})")
check(any(b["line"] == site and b["file"].endswith("blocked_harness.cpp") for b in p["blocks"]),
      f"막힌 지점이 하네스 {site}행을 가리킴")

o = res["XMLPrinter::OpenElement(const char *, bool)"]
check(o["category"] == "BLOCKED", f"XMLPrinter::OpenElement 는 간접 경로로 BLOCKED (실제: {o['category']})")
check(any(len(b["chain"]) > 2 for b in o["blocks"]), "OpenElement 는 여러 단계 경로(가상 함수 경유)로 연결됨")

q = res["XMLDocument::Parse(const char *, size_t)"]
check(q["category"] in ("FULL", "PARTIAL"), f"XMLDocument::Parse 는 도달 (실제: {q['category']})")

s = res["XMLDocument::SaveFile(const char *, bool)"]
check(s["category"] == "NOT_CALLED", f"XMLDocument::SaveFile 은 NOT_CALLED (실제: {s['category']})")

sys.exit(1 if fails else 0)
EOF
