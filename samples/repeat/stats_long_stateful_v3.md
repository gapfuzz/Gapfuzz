# 반복 측정 결과 — stateful vs stateful_v3

조건: 각 10회/10회, 회당 3600초, 같은 회차는 같은 퍼저 시드, 같은 딕셔너리, ASan+UBSan.
값은 **중앙값 [최솟값–최댓값]**. 커버리지는 라이브러리 소스만 집계 (하네스 코드 제외).

## 커버리지

| 지표 | stateful | stateful_v3 | A12 | p (Mann-Whitney U, 양측) |
|---|---|---|---:|---:|
| 라인 | 77.51% [77.07–77.69] | 78.46% [78.13–78.57] | 1.00 | 1.1e-05 |
| 함수 | 71.61% [71.61–71.61] | 71.88% [71.88–71.88] | 1.00 | 1.1e-05 |
| 영역 | 83.10% [82.59–83.27] | 84.06% [83.66–84.17] | 1.00 | 1.1e-05 |
| 분기 | 79.76% [78.80–80.30] | 83.08% [82.61–83.56] | 1.00 | 1.1e-05 |

A12는 무작위로 하나씩 뽑았을 때 오른쪽 하네스가 더 높을 확률(0.5면 차이 없음, 1.0이면 항상 높음).
표본이 10개씩일 때 양측 정확검정으로 나올 수 있는 가장 작은 p는 1.1e-05입니다.

## 공개 API 분류 (gapfuzz)

| 분류 | stateful | stateful_v3 |
|---|---|---|
| 호출 안 함 | 103 [103–103] | 102 [102–102] |
| 조건에 막힘 | 0 [0–0] | 0 [0–0] |
| 일부 분기 미실행 | 36 [34–38] | 22 [21–23] |
| 완전 도달 | 164 [162–166] | 179 [178–180] |

## 분류 안정성

같은 하네스를 반복했을 때 API 분류가 얼마나 일관된지 봅니다.

| | stateful | stateful_v3 |
|---|---:|---:|
| 모든 회차에서 분류가 같은 API | 299/303 | 300/303 |
| 한 번이라도 도달한 API | 200 | 201 |
| 매 회차 도달한 API | 200 | 201 |

stateful에서 회차마다 분류가 바뀐 API:
- `XMLPrinter::VisitEnter(const XMLDocument &)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::IsNameStartChar(unsigned char)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ReadBOM(const char *, bool *)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ToUnsigned(const char *, unsigned int *)`: 완전 도달 / 일부 분기 미실행

stateful_v3에서 회차마다 분류가 바뀐 API:
- `XMLUtil::IsNameStartChar(unsigned char)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ReadBOM(const char *, bool *)`: 완전 도달 / 일부 분기 미실행
- `XMLUtil::ToUnsigned(const char *, unsigned int *)`: 완전 도달 / 일부 분기 미실행

stateful_v3에서 매번 도달했지만 stateful에서는 한 번도 도달하지 못한 API: **1개**

## 크래시

| | stateful | stateful_v3 |
|---|---:|---:|
| 크래시가 난 회차 | 0/10 | 0/10 |

