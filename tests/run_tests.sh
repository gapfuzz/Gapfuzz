#!/usr/bin/env bash
# 분석기 회귀 테스트: 빌드 → 짧은 퍼징 → 분석 → 기대 분류 확인 (BLOCKED / NOT_CALLED)
# 다른 라이브러리와 같은 범용 실행기(scripts/tgt.py)를 쓴다. 설정: targets/_blockedtest.json (TinyXML2 + tests/blocked_harness.cpp)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
D=out/targets/_blockedtest/blocked_harness
rm -rf "$D"
python3 scripts/tgt.py build _blockedtest blocked_harness > /dev/null
python3 scripts/tgt.py repeat _blockedtest blocked_harness --trials 1 --secs "${SECS:-15}" > /dev/null

python3 - "$D/r1/gap/gap.json" <<'EOF2'
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
EOF2
