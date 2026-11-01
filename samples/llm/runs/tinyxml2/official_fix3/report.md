# LLM 하네스 수정 — tinyxml2/official, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(13행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1235/1186 |

**채택 후보: 시도 1** (`harnesses/llm/official_fix3/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -10,6 +10,6 @@
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
-    doc.Parse(data_string.c_str());
+    doc.Parse((size > 0 && data[0] % 16 == 0) ? nullptr : data_string.c_str()); // [gapfuzz-llm] 입력 첫 바이트로 약 1/16 확률로 nullptr을 넘겨 Parse의 `!xml` 분기를 도달시킴 (나머지는 기존 문자열 그대로, Parse가 null을 EMPTY_DOCUMENT 오류로 안전하게 처리함)
     return 0;
 }
```
