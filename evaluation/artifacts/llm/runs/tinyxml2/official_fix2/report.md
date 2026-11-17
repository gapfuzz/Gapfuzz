# LLM 하네스 수정 — tinyxml2/official, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 고정합니다(12행에서 기본값) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1366/1113 |

**채택 후보: 시도 1** (`harnesses/llm/official_fix2/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -9,7 +9,7 @@
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
     std::string data_string(reinterpret_cast<const char *>(data), size);
-    XMLDocument doc;
+    XMLDocument doc(true, static_cast<Whitespace>(size > 0 ? data[0] % 3 : 0)); // [gapfuzz-llm] whitespaceMode가 기본값(PRESERVE)으로 고정되어 PEDANTIC 분기에 못 가므로 입력 첫 바이트로 세 모드(0=PRESERVE, 1=COLLAPSE, 2=PEDANTIC)를 고름
     doc.Parse(data_string.c_str());
     return 0;
 }
```
