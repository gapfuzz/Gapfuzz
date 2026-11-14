# legacy — 보관용

프로젝트 초기에 TinyXML2 하나만 대상으로 쓰던 스크립트입니다. 지금은 모든 라이브러리가
`scripts/tgt.py`(빌드·퍼징·분석), `scripts/exp.py`(팀 실험), `python3 -m gapfuzz llmops`(API 추가)를 씁니다.
예전 결과(`samples/`)가 어떻게 만들어졌는지 확인할 수 있도록 남겨 둔 것이고, 더 이상 유지하지 않습니다.
경로가 바뀌어 그대로는 실행되지 않을 수 있습니다.

| 파일 | 하던 일 | 지금 쓰는 것 |
|---|---|---|
| `build.sh`, `run.sh`, `repeat.sh` | TinyXML2 하네스 빌드, 퍼징, 반복 | `scripts/tgt.py build / repeat` |
| `long_runs.py`, `day_run.py`, `day_loop.sh` | TinyXML2 1시간 × 10회, 24시간 실험 | `scripts/exp.py run` |
| `opgen.py` (`gapfuzz ops` 명령) | TinyXML2 전용 규칙으로 연산 초안 생성 | `python3 -m gapfuzz llmops` |
| `bug_bench.py`, `hunt.sh` | TinyXML2 옛 버전 버그 재발견, 새 버그 찾기 | - |
| `stability.py` | TinyXML2 제안 검증의 안정성 점검 | `scripts/diag_compare.py` |
| `run_fi.sh` | Fuzz Introspector를 TinyXML2에 실행 | - |

## tinyxml2_stateful/

사람이 새로 설계한 TinyXML2 스테이트풀 하네스(`stateful`, `stateful_v2`, `stateful_v3`, `stateful_auto`)로 낸 결과입니다.
다른 라이브러리는 "OSS-Fuzz 하네스 → gapfuzz 적용"으로 비교하는데 TinyXML2만 기준이 달라서, 2026-11-12에 하네스를 저장소에서 내리고
결과를 여기로 옮겼습니다. 요약은 `tinyxml2_stateful/RESULTS.md`. 하네스 소스는 git 기록에서 볼 수 있습니다.
