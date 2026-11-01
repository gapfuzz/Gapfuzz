# LLM 하네스 수정 — json-c/official, 제안 4

- 모델: `claude-sonnet-5-5`
- 제안: `json_object_to_json_string_length(struct json_object *, int, size_t *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_object_to_json_string_ext`)에서만 불립니다. 내부 호출은 3번째 인자 `length`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1308/1116 |

**채택 후보: 시도 1** (`harnesses/json-c/llm/official_fix4/try1.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -15,6 +15,9 @@
 		}
 	}
 	(void)json_object_to_json_string_ext(obj, JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED);
+	size_t out_len = 0; // [gapfuzz-llm] length 출력 인자를 받을 변수 (직접 호출용)
+	(void)json_object_to_json_string_length(obj, JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED, (size > 0 && (data[0] & 1)) ? &out_len : NULL); // [gapfuzz-llm] 입력 첫 바이트로 length를 널/비널 중에서 골라 612행의 참 분기를 열어줌
+	(void)out_len;
 	
 	json_object_put(obj);
 	json_tokener_free(tok);
```
