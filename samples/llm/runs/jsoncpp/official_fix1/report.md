# LLM 하네스 수정 — jsoncpp/official, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `Value::Value(ValueType)`의 1번째 인자 `type`를 하네스가 고정합니다(55행에서 기본값) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 6개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 5/6 | - | 3086/2135 |
| 2 | 통과 | 5/6 | - | 4802/2560 |

**채택 후보: 시도 1** (`harnesses/jsoncpp/llm/official_fix1/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -52,7 +52,7 @@
 
   std::unique_ptr<Json::CharReader> reader(builder.newCharReader());
 
-  Json::Value root;
+  Json::Value root(static_cast<Json::ValueType>((hash_settings >> 12) & 0x7)); // [gapfuzz-llm] Value 생성자의 type 인자를 입력의 미사용 비트(12~14)에서 골라 0~7(유효한 ValueType 전부)을 만들고, 0이면 기존 nullValue가 됨
   const auto data_str = reinterpret_cast<const char*>(data);
 #if JSON_USE_EXCEPTION
   try {
```
