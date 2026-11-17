# Claude가 고친 추가 하네스 (<하네스 이름>_llm)

대표 하네스가 아닌 OSS-Fuzz 하네스에서, 하네스 전체를 합친 커버리지로도 막혀 있는 분기를 겨냥한 제안만 골라 Claude API에 맡긴 결과입니다.
같은 분기는 한 하네스에만 맡겼습니다(scripts/make_llm_harness_extra.py의 규칙 1, 2).

| 라이브러리 | 하네스 | 모델 | 맡긴 제안 | 결과 | 겨냥 분기 열림 | 시도 | 토큰(입력/출력) |
|---|---|---|---|---|---:|---:|---|
| expat | official_parsebuffer | claude-sonnet-5-5 | 3 | 통과 | 1/1 | 1 | 3,406/2,263 |
| http-parser | official | claude-sonnet-5-5 | 1,2 | 통과 | 44/59 | 3 | 19,347/7,502 |
| json-c | official_json_array | claude-sonnet-5-5 | 2,3,4,7 | 통과 | 48/67 | 3 | 30,963/14,248 |
| json-c | official_json_object | claude-sonnet-5-5 | 1,2,3,4 | 통과 | 60/81 | 3 | 36,757/15,076 |
| json-c | official_json_pointer | claude-sonnet-5-5 | 1,2,3,4,5,8,9 | 통과 | 10/11 | 3 | 21,999/15,139 |
| libucl | official | claude-sonnet-5-5 | 1,2,3,4,5,6,7,8,9 | 통과 | 14/15 | 3 | 27,011/12,202 |
| libucl | official_msgpack | claude-sonnet-5-5 | 1,3,10 | 통과 | 9/9 | 2 | 9,790/4,836 |
| libyaml | official_deconstructor | claude-sonnet-5-5 | 2,3,4,5,6,10 | 통과 | 10/11 | 3 | 125,016/58,362 |
| libyaml | official_deconstructor_alt | claude-sonnet-5-5 | 1,2,3,4,5,6,8,9 | 통과 | 11/17 | 3 | 106,188/54,124 |
| pugixml | official_xpath | claude-sonnet-5-5 | 3,5,6,9 | 통과 | 30/40 | 3 | 37,103/23,775 |
| tinyxml2 | official_xmltest2 | claude-sonnet-5-5 | 2,3 | 통과 | 1/2 | 2 | 6,225/5,902 |
| yyjson | official | claude-sonnet-5-5 | 1,2,3,4,5,9 | 통과 | 7/7 | 2 | 12,967/7,339 |
| yyjson | official_patch | claude-sonnet-5-5 | 1,4,5,6,8,9,10,12,13,14 | 통과 | 12/12 | 2 | 20,320/11,420 |
| zlib | official_compress | claude-sonnet-5-5 | 1,2,3,4,8,9,10,11 | 통과 | 18/18 | 3 | 34,927/12,591 |
| zlib | official_example_dict | claude-sonnet-5-5 | 1,3,4,5,6,8,9,10 | 통과 | 23/24 | 3 | 45,866/24,113 |
| zlib | official_example_flush | claude-sonnet-5-5 | 2,8 | 통과 | 8/13 | 3 | 30,409/13,688 |
| zlib | official_example_large | claude-sonnet-5-5 | 2,10,11,12 | 통과 | 24/26 | 3 | 36,818/21,749 |
| zlib | official_example_small | claude-sonnet-5-5 | 9 | 통과 | 5/8 | 3 | 24,389/13,393 |
