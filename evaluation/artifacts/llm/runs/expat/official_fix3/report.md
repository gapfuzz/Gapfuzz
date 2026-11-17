# LLM 하네스 수정 — expat/official, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `XML_Parse(XML_Parser, const char *, int, int)`의 2번째 인자 `s`에 하네스가 null을 넘긴 적이 없습니다(78행, 79행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 3083/3077 |

**채택 후보: 시도 1** (`harnesses/expat/llm/official_fix3/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -75,8 +75,10 @@
   XML_SetElementHandler(p, start, end);
   XML_SetCharacterDataHandler(p, may_stop_character_handler);
   assert(size <= INT_MAX);
-  XML_Parse(p, (const XML_Char *)data, (int)size, 0);
-  if (XML_Parse(p, (const XML_Char *)data, (int)size, 1) == XML_STATUS_ERROR) {
+  const XML_Char *buf1 = (size > 0 && (data[0] & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] 입력 첫 바이트로 가끔 s에 NULL을 넘겨 XML_Parse의 (s == NULL) 분기를 도달시킴 (그 외에는 원래 값)
+  const XML_Char *buf2 = (size > 0 && ((data[0] >> 3) & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] 두 번째 호출도 입력 바이트로 NULL 여부를 독립적으로 선택 (라이브러리가 INVALID_ARGUMENT로 안전하게 처리)
+  XML_Parse(p, buf1, (int)size, 0); // [gapfuzz-llm] s가 NULL일 수 있도록 buf1 사용
+  if (XML_Parse(p, buf2, (int)size, 1) == XML_STATUS_ERROR) { // [gapfuzz-llm] s가 NULL일 수 있도록 buf2 사용
     XML_ErrorString(XML_GetErrorCode(p));
   }
   XML_GetCurrentLineNumber64(p);
```
