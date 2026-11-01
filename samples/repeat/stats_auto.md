# 반복 측정 결과 — stateful_v3 vs stateful_auto

조건: 각 5회/5회, 회당 120초, 같은 회차는 같은 퍼저 시드, 같은 딕셔너리, ASan+UBSan.
값은 **중앙값 [최솟값–최댓값]**. 커버리지는 라이브러리 소스만 집계 (하네스 코드 제외).

## 커버리지

| 지표 | stateful_v3 | stateful_auto | A12 | p (Mann-Whitney U, 양측) |
|---|---|---|---:|---:|
| 라인 | 77.32% [76.59–77.91] | 80.60% [80.49–81.07] | 1.00 | 0.0079 |
| 함수 | 71.88% [71.88–71.88] | 75.78% [75.78–75.78] | 1.00 | 0.0079 |
| 영역 | 82.87% [82.14–83.44] | 86.37% [86.03–86.76] | 1.00 | 0.0079 |
| 분기 | 80.43% [79.08–81.79] | 84.51% [84.10–85.46] | 1.00 | 0.0079 |

A12는 무작위로 하나씩 뽑았을 때 오른쪽 하네스가 더 높을 확률(0.5면 차이 없음, 1.0이면 항상 높음).
표본이 5개씩일 때 양측 정확검정으로 나올 수 있는 가장 작은 p는 0.0079입니다.

## 공개 API 분류 (gapfuzz)

| 분류 | stateful_v3 | stateful_auto |
|---|---|---|
| 호출 안 함 | 102 [102–102] | 87 [87–87] |
| 조건에 막힘 | 0 [0–0] | 0 [0–0] |
| 일부 분기 미실행 | 23 [22–24] | 28 [26–28] |
| 완전 도달 | 178 [177–179] | 188 [188–190] |

## 분류 안정성

같은 하네스를 반복했을 때 API 분류가 얼마나 일관된지 봅니다.

| | stateful_v3 | stateful_auto |
|---|---:|---:|
| 모든 회차에서 분류가 같은 API | 301/303 | 298/303 |
| 한 번이라도 도달한 API | 201 | 216 |
| 매 회차 도달한 API | 201 | 216 |

stateful_v3에서 회차마다 분류가 바뀐 API:
- `XMLUtil::IsNameStartChar(unsigned char)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ToUnsigned(const char *, unsigned int *)`: 완전 도달 / 일부 분기 미실행

stateful_auto에서 회차마다 분류가 바뀐 API:
- `XMLDocument::Identify(char *, XMLNode **, bool)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::IsNameStartChar(unsigned char)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ToBool(const char *, bool *)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ToUnsigned(const char *, unsigned int *)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ToUnsigned64(const char *, uint64_t *)`: 완전 도달 / 일부 분기 미실행

stateful_auto에서 매번 도달했지만 stateful_v3에서는 한 번도 도달하지 못한 API: **15개**

## 크래시

| | stateful_v3 | stateful_auto |
|---|---:|---:|
| 크래시가 난 회차 | 0/5 | 0/5 |

