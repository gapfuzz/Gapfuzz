# LLM 하네스 수정 — jsoncpp/official, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: `CharReaderBuilder::validate(Value *) const`의 1번째 인자 `invalid`를 하네스가 고정합니다(49행에서 항상 `nullptr`) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 2349/2454 |

**채택 후보: 시도 1** (`harnesses/jsoncpp/llm/official_fix2/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -46,7 +46,9 @@
 
   // An unknown key is silently ignored by newCharReader(), so a typo here
   // would quietly stop the fuzzer from exercising that setting.
-  if (!builder.validate(nullptr)) {
+  Json::Value invalid_keys; // [gapfuzz-llm] validate()의 invalid 인자로 넘길 수 있도록 스택에 Value를 둠(자동 해제)
+  Json::Value* invalid_arg = (hash_settings & (1 << 12)) ? &invalid_keys : nullptr; // [gapfuzz-llm] 입력의 12번 비트로 nullptr과 실제 포인터를 번갈아 선택해 invalid가 참인 분기 도달
+  if (!builder.validate(invalid_arg)) { // [gapfuzz-llm] 고정된 nullptr 대신 입력으로 고른 invalid 인자를 전달
     std::abort();
   }
```
