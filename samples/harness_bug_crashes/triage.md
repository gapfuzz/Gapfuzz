# 크래시 원인 귀속 — stateful_before_fix

- 바이너리: `(수정 전 하네스로 빌드한 fuzz 바이너리)`
- 크래시 입력 2개 → 서로 다른 크래시 1개 (스택 기준으로 묶음)
- 입력마다 3번씩 다시 실행해 재현 여부 확인

| 분류 | 개수 | 다음 조치 |
|---|---:|---|
| ⓑ 하네스 버그 의심 | 1 | 하네스를 고친 뒤 같은 입력으로 다시 확인 (라이브러리에 보고하지 않음) |

## 1. ⓑ 하네스 버그 의심 (확신 강) — heap-use-after-free
- 판단 근거: 메모리를 해제한 곳이 하네스 — 하네스가 넘긴 메모리의 수명이 라이브러리 사용보다 짧음
  - 오류 지점: `tinyxml2::XMLPrinter::Write` @ third_party/tinyxml2/tinyxml2.h:2342 (library)
  - 해제 위치: `LLVMFuzzerTestOneInput` @ samples/harness_bug_crashes/stateful_before_fix.cpp:236 (harness)
  - 할당 위치: `FuzzedDataProvider::ConsumeRandomLengthString[abi:cxx11]` @ harnesses/include/fuzzer/FuzzedDataProvider.h:175 (harness)
- 오류 스택(우리 코드만): `tinyxml2::XMLPrinter::Write [library]` → `tinyxml2::XMLPrinter::OpenElement [library]` → `tinyxml2::XMLPrinter::VisitEnter [library]` → `tinyxml2::XMLElement::Accept [library]`
- 재현: 3/3
- sanitizer 요약: `AddressSanitizer: heap-use-after-free /home/claude/gapfuzz/third_party/tinyxml2/tinyxml2.h:2342:55 in tinyxml2::XMLPrinter::Write(char const*)`
- 입력 파일 2개: `crash-53ea33affa0f17847507da4a5615a21de43dafc4`, `crash-fa82dabc3c6edc047ea5a64316b12c574669ffaa`
- 다음 조치: 하네스를 고친 뒤 같은 입력으로 다시 확인 (라이브러리에 보고하지 않음)

