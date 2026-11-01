# LLM 하네스 수정 — expat/official, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)`의 2번째 인자 `context`를 하네스가 `"e1"`, `0` 중에서만 고릅니다(101행, 108행) (라이브러리 내부 `setContext`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 5개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 4/5 | - | 4126/3801 |
| 2 | 통과 | 4/5 | - | 6759/4340 |

**채택 후보: 시도 1** (`harnesses/expat/llm/official_fix2/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -85,6 +85,34 @@
   }
 }
 
+#define CONTEXT_BUF_LEN 33
+
+// Picks the context argument from the fuzzer input. The selector byte decides
+// between the original values ("e1" / NULL) and a NUL-terminated string built
+// from the input bytes (which may contain '=' or '\f' separators).
+static const XML_Char *
+pick_context(const uint8_t *data, size_t size, size_t selector_index,
+             size_t string_offset, XML_Char *buf) {
+  uint8_t selector = selector_index < size ? data[selector_index] : 0;
+  switch (selector % 4) {
+  case 0:
+    return "e1";
+  case 1:
+    return NULL;
+  default: {
+    size_t n = 0;
+    if (string_offset < size) {
+      n = size - string_offset;
+      if (n > CONTEXT_BUF_LEN - 1)
+        n = CONTEXT_BUF_LEN - 1;
+      memcpy(buf, data + string_offset, n);
+    }
+    buf[n] = '\0';
+    return buf;
+  }
+  }
+}
+
 int
 LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   XML_Parser parentParser = XML_ParserCreate(xstr(ENCODING_FOR_FUZZING));
@@ -97,15 +125,18 @@
   ParseOneInput(namespaceParser, data, size);
   XML_ParserFree(namespaceParser);
 
+  XML_Char contextBuf1[CONTEXT_BUF_LEN];
+  XML_Char contextBuf2[CONTEXT_BUF_LEN];
+
   XML_Parser externalEntityParser
-      = XML_ExternalEntityParserCreate(parentParser, "e1", NULL);
+      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 0, 2, contextBuf1), NULL); // [gapfuzz-llm] context를 "e1"/NULL뿐 아니라 입력에서 만든 문자열로도 고르게 하여 setContext 분기 도달
   if (externalEntityParser != NULL) {
     ParseOneInput(externalEntityParser, data, size);
     XML_ParserFree(externalEntityParser);
   }
 
   XML_Parser externalDtdParser
-      = XML_ExternalEntityParserCreate(parentParser, NULL, NULL);
+      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 1, 18, contextBuf2), NULL); // [gapfuzz-llm] NULL 외에 "e1"과 입력 기반 context 문자열도 나오게 함
   if (externalDtdParser != NULL) {
     ParseOneInput(externalDtdParser, data, size);
     XML_ParserFree(externalDtdParser);
```
