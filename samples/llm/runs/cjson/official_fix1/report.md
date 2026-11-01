# LLM 하네스 수정 — cjson/official, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 2번째 인자 `return_parse_end`를 하네스가 고정합니다(34행에서 항상 `0`) (라이브러리 내부 `cJSON_ParseWithLengthOpts`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 2/2 | - | 2107/1835 |

**채택 후보: 시도 1** (`harnesses/cjson/llm/official_fix1/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -17,6 +17,8 @@
     unsigned char *copied;
     char *printed_json = NULL;
     int minify, require_termination, formatted, buffered;
+    const char *parse_end = NULL; // [gapfuzz-llm] return_parse_end 출력용 포인터 변수 (NULL 아님 경로를 위해 필요)
+    const char **return_parse_end; // [gapfuzz-llm] 입력에 따라 NULL 또는 &parse_end를 선택해 넘길 인자
 
 
     if(size <= offset) return 0;
@@ -31,7 +33,8 @@
     formatted           = data[2] == '1' ? 1 : 0;
     buffered            = data[3] == '1' ? 1 : 0;
 
-    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);
+    return_parse_end = (size & 1) ? &parse_end : NULL; // [gapfuzz-llm] 입력 크기의 홀짝으로 NULL(원래 값)과 유효한 포인터를 번갈아 선택
+    json = cJSON_ParseWithOpts((const char*)data + offset, return_parse_end, require_termination); // [gapfuzz-llm] return_parse_end를 항상 NULL로 고정하던 것을 퍼저 입력으로 선택하게 변경
 
     if(json == NULL) return 0;
 
@@ -74,4 +77,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```
