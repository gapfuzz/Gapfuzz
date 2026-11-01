# 제안 검증 — json-c-official-r1 → json-c-official_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | json_tokener_free · tok | 미적용 | 2 | 0 |
| 2 | json_object_object_add_ex · opts | 적용 | 2 | 2 |
| 3 | json_tokener_new_ex · depth | 적용 | 1 | 1 |
| 4 | json_object_to_json_string_length · length | 적용 | 1 | 1 |
| 5 | json_object_array_shrink · empty_slots | 적용 | 1 | 0 |

**적용한 제안 기준: 막혀 있던 분기 5개 중 4개가 열림**

## 1. `json_tokener_free(struct json_tokener *)`의 1번째 인자 `tok`에 하네스가 null을 넘긴 적이 없습니다(20행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `json_tokener_free(struct json_tokener *)` 188행 조건 `!tok` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `json_tokener_reset(struct json_tokener *)` 210행 조건 `!tok` (수정 전: 한 번도 참 아님)

## 2. `json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_object_object_add`)에서만 불립니다. 내부 호출은 4번째 인자 `opts`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 열림 (5/5) — `json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)` 755행 조건 `(opts & JSON_C_OBJECT_ADD_KEY_IS_NEW)` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)` 768행 조건 `!(opts & JSON_C_OBJECT_ADD_CONSTANT_KEY)` (수정 전: 한 번도 거짓 아님)

## 3. `json_tokener_new_ex(int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_new`)에서만 불립니다. 내부 호출은 1번째 인자 `depth`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 열림 (5/5) — `json_tokener_new_ex(int)` 157행 조건 `depth < 1` (수정 전: 한 번도 참 아님)

## 4. `json_object_to_json_string_length(struct json_object *, int, size_t *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_object_to_json_string_ext`)에서만 불립니다. 내부 호출은 3번째 인자 `length`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 열림 (5/5) — `json_object_to_json_string_length(struct json_object *, int, size_t *)` 612행 조건 `length` (수정 전: 한 번도 참 아님)

## 5. `json_object_array_shrink(struct json_object *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_parse_ex`)에서만 불립니다. 내부 호출은 2번째 인자 `empty_slots`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 여전히 막힘 (0/5) — `json_object_array_shrink(struct json_object *, int)` 1849행 조건 `empty_slots < 0` (수정 전: 한 번도 참 아님)

