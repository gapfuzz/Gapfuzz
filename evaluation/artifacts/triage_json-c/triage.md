# 크래시 원인 귀속 — json-c-v2

- 바이너리: `out/targets/json-c/official_v2/fuzz`
- 크래시 입력 1개 → 서로 다른 크래시 1개 (스택 기준으로 묶음)
- 입력마다 3번씩 다시 실행해 재현 여부 확인

| 분류 | 개수 | 다음 조치 |
|---|---:|---|
| ⓑ 하네스 버그 의심 | 1 | 하네스를 고친 뒤 같은 입력으로 다시 확인 (라이브러리에 보고하지 않음) |

## 1. ⓑ 하네스 버그 의심 (확신 중) — deadly signal
- 판단 근거: 하네스가 직접 부른 API `json_object_array_shrink`가 입구의 인자 검사에서 abort함 — API가 허용하지 않는 인자를 하네스가 넘김 (문서의 인자 범위를 지켜야 함)
  - 오류 지점: `json_abort` @ third_party/json-c/json_object.c:2136 (library)
  - 하네스가 부른 API: `json_object_array_shrink` @ third_party/json-c/json_object.c:1850, 하네스 위치: `LLVMFuzzerTestOneInput` @ harnesses/json-c/official_v2.cc:50
- 오류 스택(우리 코드만): `json_abort [library]` → `json_object_array_shrink [library]` → `LLVMFuzzerTestOneInput [harness]`
- 재현: 3/3
- sanitizer 요약: `libFuzzer: deadly signal`
- 입력 파일 1개: `crash-ff48e5a811379e525195cf66dc824cb68c3d26a6`
- 다음 조치: 하네스를 고친 뒤 같은 입력으로 다시 확인 (라이브러리에 보고하지 않음)

