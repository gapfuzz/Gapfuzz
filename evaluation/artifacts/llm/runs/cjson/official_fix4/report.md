# LLM 하네스 수정 — cjson/official, 제안 4

- 모델: `claude-sonnet-5-5`
- 제안: `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 1번째 인자 `item`에 하네스가 null을 넘긴 적이 없습니다(40행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1884/2172 |

**채택 후보: 시도 1** (`harnesses/cjson/llm/official_fix4/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -37,7 +37,7 @@
 
     if(buffered)
     {
-        printed_json = cJSON_PrintBuffered(json, 1, formatted);
+        printed_json = cJSON_PrintBuffered(((data[size-2] & 0x07) == 0) ? NULL : json, 1, formatted); // [gapfuzz-llm] item이 NULL일 때의 분기(print_value의 item == NULL)를 닿게 하려고 입력 바이트로 가끔 NULL을 넘김 (그 외에는 기존 json 유지)
     }
     else
     {
@@ -74,4 +74,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```
