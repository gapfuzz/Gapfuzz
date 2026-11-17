# LLM 하네스 수정 — expat/official, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `XML_ParserReset(XML_Parser, const XML_Char *)`의 2번째 인자 `encoding`를 하네스가 고정합니다(84행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 3016/2795 |

**채택 후보: 시도 1** (`harnesses/expat/llm/official_fix1/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -81,7 +81,13 @@
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
   }
 }
```
