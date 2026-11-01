# LLM 하네스 수정 — cjson/official, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 2번째 인자 `prebuffer`를 하네스가 고정합니다(40행에서 항상 `1`) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1929/1878 |

**채택 후보: 시도 1** (`harnesses/cjson/llm/official_fix2/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -37,7 +37,7 @@
 
     if(buffered)
     {
-        printed_json = cJSON_PrintBuffered(json, 1, formatted);
+        printed_json = cJSON_PrintBuffered(json, (int)(int8_t)data[size - 2], formatted); // [gapfuzz-llm] prebuffer를 입력 바이트(-128~127)에서 골라 음수 분기와 기존 값 1이 모두 나오게 함
     }
     else
     {
@@ -74,4 +74,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```
