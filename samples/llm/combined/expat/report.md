# LLM 하네스 수정 — expat/official, 제안 1,2,3

- 모델: `claude-sonnet-5-5`
- 제안: `XML_ParserReset(XML_Parser, const XML_Char *)`의 2번째 인자 `encoding`를 하네스가 고정합니다(84행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)`의 2번째 인자 `context`를 하네스가 `"e1"`, `0` 중에서만 고릅니다(101행, 108행) (라이브러리 내부 `setContext`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 제안: `XML_Parse(XML_Parser, const char *, int, int)`의 2번째 인자 `s`에 하네스가 null을 넘긴 적이 없습니다(78행, 79행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 7개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 6/7 | 1: 1/1, 2: 4/5, 3: 1/1 | - | 7385/4710 |
| 2 | 통과 | 6/7 | 1: 1/1, 2: 4/5, 3: 1/1 | - | 11092/6562 |

**채택 후보: 시도 1** (`harnesses/expat/llm/official_combined/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -58,6 +58,15 @@
   }
 }
 
+// 입력 앞쪽 바이트 배분 (서로 겹치지 않음):
+//   data[0]      : XML_ParserReset의 encoding 선택
+//   data[1]      : XML_Parse 두 호출의 s에 NULL을 넘길지 선택 (하위 3비트 / 다음 3비트)
+//   data[2]      : 첫 번째 ExternalEntityParserCreate의 context 선택
+//   data[3]      : 두 번째 ExternalEntityParserCreate의 context 선택
+//   data[4..19]  : 첫 번째 context 문자열 재료
+//   data[20..35] : 두 번째 context 문자열 재료
+#define CONTEXT_BUF_LEN 17 // [gapfuzz-llm] context 문자열 버퍼 (최대 16자 + NUL)
+
 static void
 ParseOneInput(XML_Parser p, const uint8_t *data, size_t size) {
   // Set the hash salt using siphash to generate a deterministic hash.
@@ -75,13 +84,45 @@
   XML_SetElementHandler(p, start, end);
   XML_SetCharacterDataHandler(p, may_stop_character_handler);
   assert(size <= INT_MAX);
-  XML_Parse(p, (const XML_Char *)data, (int)size, 0);
-  if (XML_Parse(p, (const XML_Char *)data, (int)size, 1) == XML_STATUS_ERROR) {
+  const XML_Char *buf1 = (size > 1 && (data[1] & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] data[1] 하위 3비트로 가끔 s에 NULL을 넘겨 XML_Parse의 (s == NULL) 분기 도달 (그 외에는 원래 값)
+  const XML_Char *buf2 = (size > 1 && ((data[1] >> 3) & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] 같은 바이트의 다른 비트로 두 번째 호출의 NULL 여부를 독립적으로 선택 (라이브러리가 INVALID_ARGUMENT로 안전하게 처리)
+  XML_Parse(p, buf1, (int)size, 0); // [gapfuzz-llm] s가 NULL일 수 있도록 buf1 사용
+  if (XML_Parse(p, buf2, (int)size, 1) == XML_STATUS_ERROR) { // [gapfuzz-llm] s가 NULL일 수 있도록 buf2 사용
     XML_ErrorString(XML_GetErrorCode(p));
   }
   XML_GetCurrentLineNumber64(p);
   if (size % 2) {
-    XML_ParserReset(p, NULL);
+    static const XML_Char *const reset_encodings[] = {
+        NULL, "UTF-8", "UTF-16", "ISO-8859-1", "US-ASCII", "UTF-16LE", "UTF-16BE"}; // [gapfuzz-llm] NULL 외에 실제 인코딩 이름 후보를 마련해 encodingName 참 분기 도달
+    const size_t reset_encoding_count
+        = sizeof(reset_encodings) / sizeof(reset_encodings[0]);
+    const XML_Char *reset_encoding
+        = reset_encodings[data[0] % reset_encoding_count]; // [gapfuzz-llm] 입력 첫 바이트로 인코딩을 고르며 NULL(원래 값)도 계속 나옴 (size가 홀수라 data[0] 접근 안전)
+    XML_ParserReset(p, reset_encoding); // [gapfuzz-llm] 고정된 NULL 대신 퍼저 입력에서 고른 encoding을 전달
+  }
+}
+
+// [gapfuzz-llm] context 인자를 입력에서 고르는 헬퍼: "e1" / NULL / 입력으로 만든 문자열('=' 또는 '\f' 구분자 포함 가능)
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
   }
 }
 
@@ -97,15 +138,18 @@
   ParseOneInput(namespaceParser, data, size);
   XML_ParserFree(namespaceParser);
 
+  XML_Char contextBuf1[CONTEXT_BUF_LEN]; // [gapfuzz-llm] 첫 번째 context 문자열 버퍼
+  XML_Char contextBuf2[CONTEXT_BUF_LEN]; // [gapfuzz-llm] 두 번째 context 문자열 버퍼
+
   XML_Parser externalEntityParser
-      = XML_ExternalEntityParserCreate(parentParser, "e1", NULL);
+      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 2, 4, contextBuf1), NULL); // [gapfuzz-llm] context를 "e1"/NULL뿐 아니라 입력에서 만든 문자열로도 고르게 하여 setContext 분기 도달 (다른 수정과 안 겹치게 data[2], data[4..19] 사용)
   if (externalEntityParser != NULL) {
     ParseOneInput(externalEntityParser, data, size);
     XML_ParserFree(externalEntityParser);
   }
 
   XML_Parser externalDtdParser
-      = XML_ExternalEntityParserCreate(parentParser, NULL, NULL);
+      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 3, 20, contextBuf2), NULL); // [gapfuzz-llm] NULL 외에 "e1"과 입력 기반 context 문자열도 나오게 함 (data[3], data[20..35] 사용)
   if (externalDtdParser != NULL) {
     ParseOneInput(externalDtdParser, data, size);
     XML_ParserFree(externalDtdParser);
```
