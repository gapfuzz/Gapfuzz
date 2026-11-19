# LLM 하네스 수정 — jsoncpp/official, 제안 1,3

- 모델: `claude-sonnet-5-5`
- 제안: `Value::Value(ValueType)`의 1번째 인자 `type`를 하네스가 고정합니다(55행에서 기본값) → 퍼저 입력으로 바꾸세요
- 제안: `Value::Value(Int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`CharReaderBuilder::setDefaults`)에서만 불립니다. 내부 호출은 1번째 인자 `value`를 한 가지 방식으로만 넘기므로 (필드 `int_`를 거쳐 조건에 쓰임) → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 겨냥한 분기: 8개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 7/8 | 1: 5/6, 3: 2/2 | - | 5146/3775 |
| 2 | 통과 | 7/8 | 1: 5/6, 3: 2/2 | - | 7695/3394 |

**채택 후보: 시도 1** (`harnesses/jsoncpp/llm/official_combined/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -26,6 +26,14 @@
   data += sizeof(uint32_t);
   size -= sizeof(uint32_t);
 
+  uint64_t wide_bits = 0; // [gapfuzz-llm] 직접 만들 Value(Int)/Value(Int64)용 값을 담는다(입력이 짧으면 0)
+  if (size >= 2 * sizeof(uint64_t)) { // [gapfuzz-llm] 파서 입력이 최소 8바이트 남도록, 충분히 길 때만 뒤쪽 8바이트를 떼어 쓴다
+    size -= sizeof(uint64_t); // [gapfuzz-llm] 뒤쪽 8바이트를 파서 입력에서 분리해 hash_settings·파서 입력과 겹치지 않게 한다
+    for (size_t i = 0; i < sizeof(uint64_t); ++i) { // [gapfuzz-llm] 떼어낸 8바이트를 리틀엔디안으로 64비트 값으로 조립한다
+      wide_bits |= static_cast<uint64_t>(data[size + i]) << (8 * i); // [gapfuzz-llm] 입력 바이트로 음수·양수·32비트 초과 값을 고르게 만든다
+    }
+  }
+
   builder.settings_["failIfExtra"] = (hash_settings & (1 << 0)) != 0;
   builder.settings_["allowComments"] = (hash_settings & (1 << 1)) != 0;
   builder.settings_["strictRoot"] = (hash_settings & (1 << 2)) != 0;
@@ -52,7 +60,7 @@
 
   std::unique_ptr<Json::CharReader> reader(builder.newCharReader());
 
-  Json::Value root;
+  Json::Value root(static_cast<Json::ValueType>((hash_settings >> 12) & 0x7)); // [gapfuzz-llm] Value 생성자의 type 인자를 입력의 미사용 비트(12~14)에서 골라 0~7(유효한 ValueType 전부)을 만들고, 0이면 기존 nullValue가 됨
   const auto data_str = reinterpret_cast<const char*>(data);
 #if JSON_USE_EXCEPTION
   try {
@@ -62,6 +70,15 @@
   } catch (Json::Exception const&) {
   }
 #endif // JSON_USE_EXCEPTION
+
+  Json::Value int_value(static_cast<Json::Int>(wide_bits & 0xFFFFFFFFu)); // [gapfuzz-llm] Value(Int)를 직접 호출하고 떼어낸 바이트의 하위 32비트로 음수·양수 값을 고르게 넘겨 int_ >= 0 거짓 분기를 만든다
+  (void)int_value.isUInt(); // [gapfuzz-llm] 직접 만든 intValue에 isUInt()를 호출해 1404행의 조건 분기를 실행한다
+
+#if defined(JSON_HAS_INT64)
+  Json::Value wide_value(static_cast<Json::Int64>(wide_bits)); // [gapfuzz-llm] Value(Int64)로 int_가 maxUInt를 넘는 값(2^32 이상)을 넘겨 LargestUInt(int_) <= maxUInt 거짓 경로를 만든다
+  (void)wide_value.isUInt(); // [gapfuzz-llm] 64비트 값이 들어간 intValue에 isUInt()를 호출해 해당 분기를 실행한다
+#endif // JSON_HAS_INT64
+
   // Whether it succeeded or not doesn't matter.
   return 0;
 }
```
