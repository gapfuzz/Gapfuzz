# LLM 하네스 수정 — cjson/official, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 1번째 인자 `value`에 하네스가 null을 넘긴 적이 없습니다(34행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 3개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/3 | - | 2264/2832 |
| 2 | 통과 | 3/3 | - | 3693/2500 |

**채택 후보: 시도 2** (`harnesses/cjson/llm/official_fix3/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -17,6 +17,8 @@
     unsigned char *copied;
     char *printed_json = NULL;
     int minify, require_termination, formatted, buffered;
+    int use_null;
+    cJSON *null_json;
 
 
     if(size <= offset) return 0;
@@ -31,7 +33,15 @@
     formatted           = data[2] == '1' ? 1 : 0;
     buffered            = data[3] == '1' ? 1 : 0;
 
-    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);
+    use_null = ((data[size - 2] & 0x0F) == 0x0F); // [gapfuzz-llm] 입력의 끝에서 두 번째 바이트로 value에 NULL을 넘길지 고름 (약 1/16, 나머지는 원래 값 유지)
+
+    if(use_null)
+    {
+        null_json = cJSON_ParseWithLengthOpts(NULL, size - offset, NULL, require_termination); // [gapfuzz-llm] ParseWithOpts는 NULL이면 1135행에서 먼저 반환하므로 ParseWithLengthOpts에 직접 NULL을 넘겨 1156행/1200행 분기를 실행 (cJSON은 NULL을 허용하고 NULL을 반환함)
+        if(null_json != NULL) cJSON_Delete(null_json); // [gapfuzz-llm] 이론상 NULL만 반환되지만 만일에 대비해 해제
+    }
+
+    json = cJSON_ParseWithOpts(use_null ? NULL : (const char*)data + offset, NULL, require_termination); // [gapfuzz-llm] value에 NULL도 가끔 넘겨 NULL 검사 분기를 실행 (cJSON은 NULL을 허용하고 NULL을 반환함)
 
     if(json == NULL) return 0;
 
@@ -74,4 +84,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```
