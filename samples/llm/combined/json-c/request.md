라이브러리: json-c
하네스 파일: official.cc

아래 제안 4개를 **모두 한 하네스에** 적용하세요.

## 제안 2
`json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_object_object_add`)에서만 불립니다. 내부 호출은 4번째 인자 `opts`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)` 755행, 조건 `(opts & JSON_C_OBJECT_ADD_KEY_IS_NEW)`가 퍼징 중 한 번도 '참'이 되지 않음
```
  751  	// We lookup the entry and replace the value, rather than just deleting
  752  	// and re-adding it, so the existing key remains valid.
  753  	hash = lh_get_hash(JC_OBJECT(jso)->c_object, (const void *)key);
  754  	existing_entry =
  755> 	    (opts & JSON_C_OBJECT_ADD_KEY_IS_NEW)
  756  	        ? NULL
  757  	        : lh_table_lookup_entry_w_hash(JC_OBJECT(jso)->c_object, (const void *)key, hash);
  758  
  759  	// The caller must avoid creating loops in the object tree, but do a
```
- `json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)` 768행, 조건 `!(opts & JSON_C_OBJECT_ADD_CONSTANT_KEY)`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  764  	if (!existing_entry)
  765  	{
  766  		char *key_copy = NULL;
  767  		const void *k = key;
  768> 		if (!(opts & JSON_C_OBJECT_ADD_CONSTANT_KEY))
  769  		{
  770  			key_copy = strdup(key);
  771  			if (key_copy == NULL)
  772  				return -1;
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 제안 3
`json_tokener_new_ex(int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_new`)에서만 불립니다. 내부 호출은 1번째 인자 `depth`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_tokener_new_ex(int)` 157행, 조건 `depth < 1`가 퍼징 중 한 번도 '참'이 되지 않음
```
  153  struct json_tokener *json_tokener_new_ex(int depth)
  154  {
  155  	struct json_tokener *tok;
  156  
  157> 	if (depth < 1)
  158  		return NULL;
  159  
  160  	tok = (struct json_tokener *)calloc(1, sizeof(struct json_tokener));
  161  	if (!tok)
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -4,8 +4,16 @@
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
 {
+	int depth = JSON_TOKENER_DEFAULT_DEPTH; // [gapfuzz-llm] 입력이 비어 있으면 기존 기본 depth(32)를 그대로 사용
+	if (size >= 1) {
+		depth = static_cast<int>(data[0] % 70) - 5; // [gapfuzz-llm] 첫 바이트로 depth를 -5~64에서 고르게 선택(기본값 32와 depth < 1 모두 가능)
+		data += 1; // [gapfuzz-llm] depth 선택에 쓴 첫 바이트는 JSON 입력에서 제외
+		size -= 1; // [gapfuzz-llm] 소비한 바이트만큼 길이 감소
+	}
 	const char *data1 = reinterpret_cast<const char *>(data);
-	json_tokener *tok = json_tokener_new();
+	json_tokener *tok = json_tokener_new_ex(depth); // [gapfuzz-llm] depth < 1 분기를 타도록 json_tokener_new_ex를 직접 호출
+	if (tok == NULL) // [gapfuzz-llm] depth < 1이면 NULL이 반환되며 parse_ex에 NULL을 넘기면 안 되므로 종료
+		return 0;
 	json_object *obj = json_tokener_parse_ex(tok, data1, size);
 	
 	if (json_object_is_type(obj, json_type_object)) {
```

## 제안 4
`json_object_to_json_string_length(struct json_object *, int, size_t *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_object_to_json_string_ext`)에서만 불립니다. 내부 호출은 3번째 인자 `length`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_object_to_json_string_length(struct json_object *, int, size_t *)` 612행, 조건 `length`가 퍼징 중 한 번도 '참'이 되지 않음
```
  608  			r = jso->_pb->buf;
  609  		}
  610  	}
  611  
  612> 	if (length)
  613  		*length = s;
  614  	return r;
  615  }
  616  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 제안 5
`json_object_array_shrink(struct json_object *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_parse_ex`)에서만 불립니다. 내부 호출은 2번째 인자 `empty_slots`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_object_array_shrink(struct json_object *, int)` 1849행, 조건 `empty_slots < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1845  
 1846  int json_object_array_shrink(struct json_object *jso, int empty_slots)
 1847  {
 1848  	assert(json_object_get_type(jso) == json_type_array);
 1849> 	if (empty_slots < 0)
 1850  		json_abort("json_object_array_shrink called with negative empty_slots");
 1851  	return array_list_shrink(JC_ARRAY(jso)->c_array, empty_slots);
 1852  }
 1853  
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  #include <stdint.h>
   2  
   3  #include <json.h>
   4  
   5  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
   6  {
   7  	const char *data1 = reinterpret_cast<const char *>(data);
   8  	json_tokener *tok = json_tokener_new();
   9  	json_object *obj = json_tokener_parse_ex(tok, data1, size);
  10  	
  11  	if (json_object_is_type(obj, json_type_object)) {
  12  		json_object_object_foreach(obj, key, val) {
  13  			(void)json_object_get_type(val);
  14  			(void)json_object_get_string(val);
  15  		}
  16  	}
  17  	(void)json_object_to_json_string_ext(obj, JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED);
  18  	
  19  	json_object_put(obj);
  20  	json_tokener_free(tok);
  21  	return 0;
  22  }
```