#!/usr/bin/env bash
# day_run.py를 2시간 안에 끝나는 만큼 구간을 이어 돌린다 (작업 하나의 시간 제한 대응). 끝나면 다시 실행하면 이어서 간다.
cd "$(dirname "$0")/.."
START=$(date +%s)
while true; do
  NEXT=$(python3 - <<'PY'
import json, os
p = "out/day/state.json"
if not os.path.exists(p): print(10); raise SystemExit
s = json.load(open(p))
if s["done_secs"] >= s["hours"] * 3600: print(0); raise SystemExit
e = [10, 20, 30]
print(e[s["chunks"]] if s["chunks"] < len(e) else s["chunk_min"])
PY
)
  [ "$NEXT" = "0" ] && { echo "[day] 전부 끝남"; break; }
  ELAPSED=$(( ($(date +%s) - START) / 60 ))
  if [ $(( ELAPSED + NEXT + 8 )) -gt 118 ]; then echo "[day] 이번 실행 종료 (다음 구간 ${NEXT}분은 다음 실행에서)"; break; fi
  python3 scripts/day_run.py --hours 24 --chunk-min 105 stateful stateful_v3 || break
done
