# LLM 하네스 수정 — json-c/official, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: `json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_object_object_add`)에서만 불립니다. 내부 호출은 4번째 인자 `opts`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 2/2 | - | 1761/2940 |

**채택 후보: 시도 1** (`harnesses/json-c/llm/official_fix2/try1.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -1,10 +1,12 @@
 #include <stdint.h>
+#include <string.h>
 
 #include <json.h>
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
 {
 	const char *data1 = reinterpret_cast<const char *>(data);
+	char keybuf[33] = {0}; // [gapfuzz-llm] CONSTANT_KEY 사용 시 키가 객체보다 오래 살아야 하므로 함수 범위의 널 종료 버퍼를 둠
 	json_tokener *tok = json_tokener_new();
 	json_object *obj = json_tokener_parse_ex(tok, data1, size);
 	
@@ -13,6 +15,24 @@
 			(void)json_object_get_type(val);
 			(void)json_object_get_string(val);
 		}
+		if (size > 1) { // [gapfuzz-llm] json_object_object_add_ex를 직접 호출해 opts 값을 다양하게 시험
+			size_t klen = size - 1 < 32 ? size - 1 : 32; // [gapfuzz-llm] 키 길이를 제한해 입력에서 키를 고름
+			memcpy(keybuf, data + 1, klen); // [gapfuzz-llm] 키를 퍼저 입력에서 가져옴 (기존 키와 겹칠 수도 있음)
+			keybuf[klen] = '\0'; // [gapfuzz-llm] 널 종료 보장
+			unsigned int opts = 0; // [gapfuzz-llm] opts 0(원래 동작)도 계속 나오게 함
+			switch (data[0] % 4) { // [gapfuzz-llm] 첫 바이트로 opts 조합 선택
+			case 1: opts = JSON_C_OBJECT_ADD_CONSTANT_KEY; break; // [gapfuzz-llm] 키 복사 생략 분기 도달
+			case 2: opts = JSON_C_OBJECT_ADD_KEY_IS_NEW; break; // [gapfuzz-llm] 새 키 표시 분기 도달
+			case 3: opts = JSON_C_OBJECT_ADD_KEY_IS_NEW | JSON_C_OBJECT_ADD_CONSTANT_KEY; break; // [gapfuzz-llm] 두 옵션 조합
+			default: break;
+			}
+			json_object *tmp = NULL; // [gapfuzz-llm] 키 존재 여부 확인용
+			if ((opts & JSON_C_OBJECT_ADD_KEY_IS_NEW) && json_object_object_get_ex(obj, keybuf, &tmp)) // [gapfuzz-llm] 이미 있는 키에 KEY_IS_NEW를 쓰면 문서상 잘못된 사용이므로 제거
+				opts &= ~(unsigned int)JSON_C_OBJECT_ADD_KEY_IS_NEW; // [gapfuzz-llm] 중복 키 삽입 방지
+			json_object *newval = json_object_new_int(data[0]); // [gapfuzz-llm] 추가할 값 생성
+			if (newval && json_object_object_add_ex(obj, keybuf, newval, opts) < 0) // [gapfuzz-llm] 직접 호출
+				json_object_put(newval); // [gapfuzz-llm] 실패 시 소유권이 넘어가지 않으므로 해제
+		}
 	}
 	(void)json_object_to_json_string_ext(obj, JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED);
```
