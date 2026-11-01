# 제안 검증 — zlib-official-r1 → zlib-official_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | uncompress · destLen | 적용 | 3 | 1 |
| 2 | uncompress · source | 미적용 | 1 | 0 |
| 3 | uncompress · dest | 적용 | 1 | 1 |
| 4 | inflate · flush | 적용 | 7 | 7 |

**적용한 제안 기준: 막혀 있던 분기 11개 중 9개가 열림**

## 1. `uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 2번째 인자 `destLen`를 하네스가 고정합니다(17행에서 항상 같은 객체 `&buffer_length`) (라이브러리 내부 `uncompress2` → `uncompress2_z`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 여전히 막힘 (0/5) — `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 36행 조건 `sourceLen == NULL` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 37행 조건 `destLen == NULL` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 37행 조건 `*destLen > 0` (수정 전: 한 번도 거짓 아님)

## 2. `uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 3번째 인자 `source`에 하네스가 null을 넘긴 적이 없습니다(17행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 36행 조건 `source == NULL` (수정 전: 한 번도 참 아님)

## 3. `uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 1번째 인자 `dest`에 하네스가 null을 넘긴 적이 없습니다(17행) → nullptr도 넘겨 보세요
- 열림 (5/5) — `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 37행 조건 `dest == NULL` (수정 전: 한 번도 참 아님)

## 4. `inflate(z_streamp, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`uncompress2_z`)에서만 불립니다. 내부 호출은 2번째 인자 `flush`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 열림 (5/5) — `inflate(z_streamp, int)` 717행 조건 `flush == Z_BLOCK` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `inflate(z_streamp, int)` 717행 조건 `flush == Z_TREES` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `inflate(z_streamp, int)` 739행 조건 `flush == Z_TREES` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `inflate(z_streamp, int)` 768행 조건 `flush == Z_TREES` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `inflate(z_streamp, int)` 917행 조건 `flush == Z_TREES` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `inflate(z_streamp, int)` 1142행 조건 `flush != Z_FINISH` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `inflate(z_streamp, int)` 1158행 조건 `flush == Z_FINISH` (수정 전: 한 번도 참 아님)

