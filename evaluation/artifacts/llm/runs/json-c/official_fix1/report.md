# LLM 하네스 수정 — json-c/official, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `json_tokener_free(struct json_tokener *)`의 1번째 인자 `tok`에 하네스가 null을 넘긴 적이 없습니다(20행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/2 | - | 1427/1405 |
| 2 | 통과 | 2/2 | - | 2261/1598 |

**채택 후보: 시도 2** (`harnesses/json-c/llm/official_fix1/try2.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -17,6 +17,10 @@
 	(void)json_object_to_json_string_ext(obj, JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED);
 	
 	json_object_put(obj);
-	json_tokener_free(tok);
+	const bool reset_null = size > 0 && ((data[0] >> 2) & 3) == 0; // [gapfuzz-llm] 입력 첫 바이트의 다른 비트로 reset에 nullptr를 넘길지 선택(약 1/4)
+	json_tokener_reset(reset_null ? nullptr : tok); // [gapfuzz-llm] json_tokener_reset을 직접 호출하며 nullptr도 넘겨 210행 !tok 분기를 실행
+	const bool free_null = size > 0 && (data[0] & 3) == 0; // [gapfuzz-llm] 입력 첫 바이트로 free에 nullptr를 넘길지 선택(약 1/4), 나머지는 원래대로 tok 전달
+	json_tokener_free(free_null ? nullptr : tok); // [gapfuzz-llm] json_tokener_free에 nullptr도 넘겨 !tok 분기를 실행
+	if (free_null) json_tokener_free(tok); // [gapfuzz-llm] nullptr를 넘긴 경우 실제 tok이 누수되지 않도록 해제
 	return 0;
 }
```
