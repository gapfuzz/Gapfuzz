#!/usr/bin/env bash
# 최신 버전 새 버그 찾기: 1시간씩, 2개 동시
set -u
cd /home/claude/gapfuzz

H=out/hunt; mkdir -p $H
run() { # name binary dict
  d=$H/$1; rm -rf $d; mkdir -p $d/corpus
  $2 -max_total_time=3600 -seed=4242 -dict=$3 -rss_limit_mb=2048 -timeout=10 -artifact_prefix=$d/ -print_final_stats=1 $d/corpus > $d/fuzz.log 2>&1
  echo "[hunt] $1 done: $(ls $d | grep -cE '^(crash|leak|timeout|oom)-') artifacts"
}
run tinyxml2_auto out/asan_stateful_auto/fuzz dicts/xml.dict &
run pugixml_v2 out/targets/pugixml/official_v2/fuzz third_party/pugixml/tests/fuzz_parse.dict &
run cjson_v2 out/targets/cjson/official_v2/fuzz third_party/cjson/fuzzing/json.dict &
wait
echo "[hunt] all done"
