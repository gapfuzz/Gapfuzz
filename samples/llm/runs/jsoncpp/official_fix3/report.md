# LLM 하네스 수정 — jsoncpp/official, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `Value::Value(Int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`CharReaderBuilder::setDefaults`)에서만 불립니다. 내부 호출은 1번째 인자 `value`를 한 가지 방식으로만 넘기므로 (필드 `int_`를 거쳐 조건에 쓰임) → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/2 | - | 2701/2618 |
| 2 | 통과 | 2/2 | - | 4563/3174 |

**채택 후보: 시도 2** (`harnesses/jsoncpp/llm/official_fix3/try2.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -62,6 +62,20 @@
   } catch (Json::Exception const&) {
   }
 #endif // JSON_USE_EXCEPTION
+
+  Json::Value int_value(static_cast<Json::Int>(hash_settings)); // [gapfuzz-llm] Value(Int)를 직접 호출하고 입력 앞 4바이트로 음수·양수 값을 고르게 넘겨 int_ >= 0 거짓 분기를 만든다
+  (void)int_value.isUInt(); // [gapfuzz-llm] 직접 만든 intValue에 isUInt()를 호출해 1404행의 조건 분기를 실행한다
+
+#if defined(JSON_HAS_INT64)
+  uint64_t wide_high = 0; // [gapfuzz-llm] Json::Int(32비트)로는 int_가 maxUInt를 넘을 수 없으므로 상위 32비트를 입력에서 따로 모은다
+  for (size_t i = 0; i < size && i < sizeof(uint32_t); ++i) { // [gapfuzz-llm] 파서 입력은 건드리지 않고 남은 바이트를 최대 4개 읽어 상위 32비트를 만든다(없으면 0이라 원래 범위 값도 계속 나온다)
+    wide_high |= static_cast<uint64_t>(data[i]) << (8 * i); // [gapfuzz-llm] 입력 바이트로 상위 32비트를 채운다
+  }
+  const uint64_t wide_bits = (wide_high << 32) | hash_settings; // [gapfuzz-llm] 상위는 입력 바이트, 하위는 hash_settings로 64비트 값을 구성한다
+  Json::Value wide_value(static_cast<Json::Int64>(wide_bits)); // [gapfuzz-llm] 같은 intValue 타입을 만드는 Value(Int64) 생성자로 int_가 maxUInt를 넘는 값(예: 2^32 이상)을 넘긴다
+  (void)wide_value.isUInt(); // [gapfuzz-llm] LargestUInt(int_) <= maxUInt 조건이 거짓이 되는 경로를 실행한다
+#endif // JSON_HAS_INT64
+
   // Whether it succeeded or not doesn't matter.
   return 0;
 }
```
