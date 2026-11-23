# 하네스 전체 기준 실험 — zlib

라이브러리의 하네스를 모두 따로 돌린 뒤 묶음별로 커버리지를 합쳐서 비교합니다.
하네스마다 3600초씩, 같은 회차는 같은 시드. 값은 중앙값 [최솟값–최댓값].

- **A 기준**: OSS-Fuzz 하네스 전체. 하네스 9개 × 3600초 = 회차당 CPU 9.0시간 (official, official_checksum, official_compress, official_example_dict, official_example_flush, official_example_large, official_example_small, official_uncompress2, official_uncompress3)
- **B 수정**: 고친 버전이 있는 하네스는 고친 것으로 바꿈 (하네스 수는 A와 같음). 하네스 9개 × 3600초 = 회차당 CPU 9.0시간 (official_llm, official_checksum, official_compress_llm, official_example_dict_llm, official_example_flush_llm, official_example_large_llm, official_example_small_llm, official_uncompress2, official_uncompress3)
- **C 수정 + gapfuzz_ops**: B + gapfuzz_ops. 하네스 10개 × 3600초 = 회차당 CPU 10.0시간 (official_llm, official_checksum, official_compress_llm, official_example_dict_llm, official_example_flush_llm, official_example_large_llm, official_example_small_llm, official_uncompress2, official_uncompress3, gapfuzz_ops)
- **C 동일 계산량**: C와 같은 하네스, 총 퍼징 시간을 B와 맞춤. 하네스 10개 × 3240초 = 회차당 CPU 9.0시간

gapfuzz_ops 생성 상태: COMPLETE · API 10/10 · 검사 퍼징 크래시 0

| 묶음 | 회차 | 회차당 CPU 시간 | 라인 | 분기 | 어느 하네스도 안 부르는 API |
|---|---:|---:|---|---|---:|
| A 기준 | 10 | 9.0 | 65.17% [65.17–65.30] | 54.13% [54.13–54.21] | 54 / 88 |
| B 수정 | 10 | 9.0 | 68.45% [68.33–68.56] | 61.64% [61.49–61.66] | 54 / 88 |
| C 수정 + gapfuzz_ops | 10 | 10.0 | 82.44% [82.31–83.03] | 74.74% [74.60–75.19] | 43 / 88 |
| C 동일 계산량 | 10 | 9.0 | 82.39% [82.31–83.03] | 74.70% [74.60–75.19] | 43 / 88 |

## 회차별 차이

같은 회차끼리(같은 시드, 같은 컴퓨터) 뒤 묶음에서 앞 묶음을 뺀 값입니다. p는 Wilcoxon 부호순위 검정(양측, 정확).
고치지 않은 하네스는 묶음들이 같은 실행 기록을 같이 쓰므로, 독립 표본 검정이 아니라 회차별 대응 비교를 씁니다.

| 비교 | 회차 | 분기 커버리지 차이 | 오른 회차 | p | 안 부르는 API 수 차이 | 뜻 |
|---|---:|---|---:|---:|---:|---|
| A → B | 10 | +7.47%p [+7.36 – +7.53] | 10/10 | 0.002 | 0 | 기존 하네스를 고친 효과 (하네스 수와 총 시간이 같음) |
| B → C | 10 | +13.13%p [+13.06 – +13.53] | 10/10 | 0.002 | -11 | gapfuzz_ops를 하나 더 돌린 효과 (C가 하네스 1개만큼 시간을 더 씀) |
| B → C 동일 계산량 | 10 | +13.11%p [+12.98 – +13.53] | 10/10 | 0.002 | -11 | 같은 총 시간에서 gapfuzz_ops를 넣은 효과 |
| A → C | 10 | +20.59%p [+20.47 – +21.06] | 10/10 | 0.002 | -11 | 전체 효과 |

동일 계산량: C의 하네스 10개를 각각 3240초 시점에서 끊어 합쳤습니다 (10 × 3240초 ≈ B의 9 × 3600초). 퍼징을 다시 돌리지 않고, 실행 중 그 시각에 찍어 둔 코퍼스로 쟀습니다.
주의: 회차 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]는 실행 중 스냅샷이 없는 예전 기록이 섞여 파일 시각으로 근사했습니다. 실제보다 낮게 나올 수 있습니다.
