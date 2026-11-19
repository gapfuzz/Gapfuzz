# 크래시 원인 귀속 — fuzz

- 바이너리: `out/targets/jsoncpp/official_v2/fuzz`
- 크래시 입력 1개 → 서로 다른 크래시 1개 (스택 기준으로 묶음)
- 입력마다 3번씩 다시 실행해 재현 여부 확인

| 분류 | 개수 | 다음 조치 |
|---|---:|---|
| ⓑ 하네스 버그 의심 | 1 | 하네스를 고친 뒤 같은 입력으로 다시 확인 (라이브러리에 보고하지 않음) |

## 1. ⓑ 하네스 버그 의심 (확신 강) — deadly signal
- 판단 근거: 라이브러리 API `Json::CharReaderBuilder::newCharReader`가 던진 예외 `Json::LogicError`를 하네스가 잡지 않아 프로그램이 종료됨 — 그 호출을 try/catch로 감싸거나 API 문서의 인자 범위를 지켜야 함
  - 오류 지점: `Json::throwLogicError` @ third_party/jsoncpp/src/lib_json/json_value.cpp:240 (library)
  - 예외: Json::LogicError (LargestInt out of UInt range)
  - 하네스가 부른 API: `Json::CharReaderBuilder::newCharReader` @ third_party/jsoncpp/src/lib_json/json_reader.cpp:1949, 하네스 위치: `LLVMFuzzerTestOneInput` @ harnesses/jsoncpp/official_v2.cpp:60
- 오류 스택(우리 코드만): `Json::throwLogicError [library]` → `Json::Value::asUInt [library]` → `Json::CharReaderBuilder::newCharReader [library]` → `LLVMFuzzerTestOneInput [harness]`
- 재현: 3/3
- sanitizer 요약: `libFuzzer: deadly signal`
- 입력 파일 1개: `crash-41a5a85e6b239f4562e2989491c81c13915ddd9c`
- 다음 조치: 하네스를 고친 뒤 같은 입력으로 다시 확인 (라이브러리에 보고하지 않음)

