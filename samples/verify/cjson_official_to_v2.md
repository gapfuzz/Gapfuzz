# 제안 검증 — cjson-official-r1 → cjson-official_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | cJSON_ParseWithOpts · return_parse_end | 적용 | 2 | 2 |
| 2 | cJSON_PrintBuffered · prebuffer | 적용 | 1 | 1 |
| 3 | cJSON_ParseWithOpts · value | 적용 | 3 | 1 |
| 4 | cJSON_PrintBuffered · item | 적용 | 1 | 1 |
| 5 | cJSON_Minify · json | 미적용 | 1 | 0 |

**적용한 제안 기준: 막혀 있던 분기 7개 중 5개가 열림**

## 1. `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 2번째 인자 `return_parse_end`를 하네스가 고정합니다(34행에서 항상 `0`) (라이브러리 내부 `cJSON_ParseWithLengthOpts`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1187행 조건 `return_parse_end` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1215행 조건 `return_parse_end != NULL` (수정 전: 한 번도 참 아님)

## 2. `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 2번째 인자 `prebuffer`를 하네스가 고정합니다(40행에서 항상 `1`) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)` 1321행 조건 `prebuffer < 0` (수정 전: 한 번도 참 아님)

## 3. `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 1번째 인자 `value`에 하네스가 null을 넘긴 적이 없습니다(34행) → nullptr도 넘겨 보세요
- 열림 (5/5) — `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)` 1135행 조건 `NULL == value` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1156행 조건 `value == NULL` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1200행 조건 `value != NULL` (수정 전: 한 번도 거짓 아님)

## 4. `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 1번째 인자 `item`에 하네스가 null을 넘긴 적이 없습니다(40행) → nullptr도 넘겨 보세요
- 열림 (5/5) — `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)` 1427행 조건 `(item == NULL)` (수정 전: 한 번도 참 아님)

## 5. `cJSON_Minify(char *)`의 1번째 인자 `json`에 하네스가 null을 넘긴 적이 없습니다(64행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `cJSON_Minify(char *)` 2928행 조건 `json == NULL` (수정 전: 한 번도 참 아님)

