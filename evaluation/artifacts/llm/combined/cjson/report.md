# LLM 하네스 수정 — cjson/official, 제안 1,2,3,4

- 모델: `claude-sonnet-5-5`
- 제안: `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 2번째 인자 `return_parse_end`를 하네스가 고정합니다(34행에서 항상 `0`) (라이브러리 내부 `cJSON_ParseWithLengthOpts`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 2번째 인자 `prebuffer`를 하네스가 고정합니다(40행에서 항상 `1`) → 퍼저 입력으로 바꾸세요
- 제안: `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 1번째 인자 `value`에 하네스가 null을 넘긴 적이 없습니다(34행) → nullptr도 넘겨 보세요
- 제안: `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 1번째 인자 `item`에 하네스가 null을 넘긴 적이 없습니다(40행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 7개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 7/7 | 1: 2/2, 2: 1/1, 3: 3/3, 4: 1/1 | - | 5726/3939 |

**채택 후보: 시도 1** (`harnesses/cjson/llm/official_combined/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -17,6 +17,12 @@
     unsigned char *copied;
     char *printed_json = NULL;
     int minify, require_termination, formatted, buffered;
+    const char *parse_end = NULL; // [gapfuzz-llm] return_parse_end 출력용 포인터 변수 (NULL 아님 경로를 위해 필요)
+    const char **return_parse_end = NULL; // [gapfuzz-llm] 입력에 따라 NULL 또는 &parse_end를 선택해 넘길 인자
+    int prebuffer = 1; // [gapfuzz-llm] prebuffer를 입력에서 고르기 위한 변수 (기본값은 원래 값 1)
+    int use_null_value = 0; // [gapfuzz-llm] value에 NULL을 넘길지 여부 (기본은 넘기지 않음)
+    int use_null_item = 0; // [gapfuzz-llm] PrintBuffered의 item에 NULL을 넘길지 여부 (기본은 넘기지 않음)
+    cJSON *null_json; // [gapfuzz-llm] NULL 입력 파싱 결과를 받아 해제하기 위한 변수
 
 
     if(size <= offset) return 0;
@@ -31,13 +37,29 @@
     formatted           = data[2] == '1' ? 1 : 0;
     buffered            = data[3] == '1' ? 1 : 0;
 
-    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);
+    if(size >= offset + 5) // [gapfuzz-llm] 헤더(앞 4바이트)와 겹치지 않을 때만 끝쪽 바이트 4개(size-2 ~ size-5)를 각각 다른 용도로 나눠 사용
+    {
+        return_parse_end = (data[size - 2] & 1) ? &parse_end : NULL; // [gapfuzz-llm] 끝에서 2번째 바이트로 return_parse_end를 NULL(원래 값)과 유효한 포인터 중에서 선택
+        prebuffer        = (int)(int8_t)data[size - 3]; // [gapfuzz-llm] 끝에서 3번째 바이트로 prebuffer를 -128~127에서 골라 음수 분기와 기존 값 1이 모두 나오게 함
+        use_null_value   = ((data[size - 4] & 0x0F) == 0x0F); // [gapfuzz-llm] 끝에서 4번째 바이트로 value에 NULL을 넘길지 고름 (약 1/16)
+        use_null_item    = ((data[size - 5] & 0x07) == 0); // [gapfuzz-llm] 끝에서 5번째 바이트로 item에 NULL을 넘길지 고름 (약 1/8)
+    }
+
+    if(use_null_value) // [gapfuzz-llm] value가 NULL인 경우의 분기(1135행, 1156행, 1200행)를 실행
+    {
+        null_json = cJSON_ParseWithOpts(NULL, NULL, require_termination); // [gapfuzz-llm] ParseWithOpts에 NULL을 직접 넘김 (cJSON은 NULL을 허용하고 NULL을 반환함)
+        if(null_json != NULL) cJSON_Delete(null_json); // [gapfuzz-llm] 이론상 NULL만 반환되지만 만일에 대비해 해제
+        null_json = cJSON_ParseWithLengthOpts(NULL, size - offset, NULL, require_termination); // [gapfuzz-llm] ParseWithOpts는 NULL이면 먼저 반환하므로 ParseWithLengthOpts에도 NULL을 직접 넘겨 내부 분기를 실행
+        if(null_json != NULL) cJSON_Delete(null_json); // [gapfuzz-llm] 이론상 NULL만 반환되지만 만일에 대비해 해제
+    }
+
+    json = cJSON_ParseWithOpts((const char*)data + offset, return_parse_end, require_termination); // [gapfuzz-llm] return_parse_end를 항상 NULL로 고정하던 것을 퍼저 입력으로 선택하게 변경 (실제 파싱은 원래 입력으로 계속 진행)
 
     if(json == NULL) return 0;
 
     if(buffered)
     {
-        printed_json = cJSON_PrintBuffered(json, 1, formatted);
+        printed_json = cJSON_PrintBuffered(use_null_item ? NULL : json, prebuffer, formatted); // [gapfuzz-llm] item에 가끔 NULL을, prebuffer에 입력에서 고른 값(음수 포함)을 넘겨 막힌 분기를 실행
     }
     else
     {
@@ -57,7 +79,7 @@
     if(minify)
     {
         copied = (unsigned char*)malloc(size);
-        if(copied == NULL) return 0;
+        if(copied == NULL) { cJSON_Delete(json); return 0; } // [gapfuzz-llm] 기존에는 이 경로에서 json이 해제되지 않았으므로 누수 방지를 위해 해제
 
         memcpy(copied, data, size);
 
@@ -74,4 +96,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```
