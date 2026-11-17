# LLM 하네스 수정 — cjson/official, 제안 5

- 모델: `claude-sonnet-5-5`
- 제안: `cJSON_Minify(char *)`의 1번째 인자 `json`에 하네스가 null을 넘긴 적이 없습니다(64행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1819/1857 |

**채택 후보: 시도 1** (`harnesses/cjson/llm/official_fix5/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -61,7 +61,7 @@
 
         memcpy(copied, data, size);
 
-        cJSON_Minify((char*)copied + offset);
+        cJSON_Minify((data[size-2] % 4 == 0) ? (char*)NULL : (char*)copied + offset); // [gapfuzz-llm] cJSON_Minify는 NULL을 허용하므로 입력 바이트(data[size-2])로 약 1/4 확률로 NULL을 넘겨 json == NULL 분기를 탐색
 
         free(copied);
     }
@@ -74,4 +74,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```
