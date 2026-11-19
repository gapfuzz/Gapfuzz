# gapfuzz_ops 상태

기존 기록(`evaluation/artifacts/llm/ops/<라이브러리>/_union/log.json`)에서 계산했습니다. 하네스는 다시 만들지 않았습니다.

- 생성 상태: `COMPLETE` 요청한 API 전부 실행 · `PARTIAL` 일부 실행 · `REJECTED` 채택된 시도 없음
- 실험 포함: 채택된 시도가 검사 퍼징(60초 × 2회)에서 크래시 없이 통과했을 때만 "예"

| 라이브러리 | 기록 | 생성 상태 | API 달성도 | 실험 포함 | 채택한 시도 | 크래시 | 실행되지 않은 API | 탈락한 시도 |
|---|---|---|---:|---|---:|---:|---|---|
| `cjson` | 현재 | COMPLETE | 10/10 (100%) | 예 | 1/1 | 0 | - | - |
| `expat` | 현재 | COMPLETE | 10/10 (100%) | 예 | 1/1 | 0 | - | - |
| `http-parser` | 현재 | COMPLETE | 10/10 (100%) | 예 | 2/2 | 0 | - | - |
| `json-c` | 현재 | PARTIAL | 9/10 (90%) | 예 | 2/3 | 0 | `json_c_set_serialization_double_format` | 1: 컴파일 실패 |
| `jsoncpp` | 현재 | COMPLETE | 10/10 (100%) | 예 | 2/2 | 0 | - | 1: RESOURCE |
| `libucl` | 현재 | COMPLETE | 10/10 (100%) | 예 | 2/2 | 0 | - | 1: LIBRARY |
| `libyaml` | 현재 | PARTIAL | 9/10 (90%) | 예 | 1/2 | 0 | `yaml_set_max_nest_level` | - |
| `pugixml` | 현재 | COMPLETE | 10/10 (100%) | 예 | 1/1 | 0 | - | - |
| `tinyxml2` | 현재 | COMPLETE | 10/10 (100%) | 예 | 1/1 | 0 | - | - |
| `yyjson` | 현재 | COMPLETE | 10/10 (100%) | 예 | 1/1 | 0 | - | - |
| `zlib` | 현재 | COMPLETE | 10/10 (100%) | 예 | 2/2 | 0 | - | 1: 컴파일 실패 |

현재 기록 11개: COMPLETE 9, PARTIAL 2, REJECTED 0, 실험 포함 11
