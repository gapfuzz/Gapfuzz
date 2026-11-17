라이브러리: json-c
하네스 파일: official_json_array.cc

아래 제안 4개를 **모두 한 하네스에** 적용하세요.

## 제안 2
`json_tokener_parse_ex(struct json_tokener *, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_parse_verbose`)에서만 불립니다. 내부 호출은 1번째 인자 `tok`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (52개)
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 396행, 조건 `(!ADVANCE_CHAR(str, tok))`가 퍼징 중 한 번도 '참'이 되지 않음
```
  392  		case json_tokener_state_eatws:
  393  			/* Advance until we change state */
  394  			while (is_ws_char(c))
  395  			{
  396> 				if ((!ADVANCE_CHAR(str, tok)) || (!PEEK_CHAR(c, tok)))
  397  					goto out;
  398  			}
  399  			if (c == '/' && !(tok->flags & JSON_TOKENER_STRICT))
  400  			{
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 396행, 조건 `(!PEEK_CHAR(c, tok))`가 퍼징 중 한 번도 '참'이 되지 않음
```
  392  		case json_tokener_state_eatws:
  393  			/* Advance until we change state */
  394  			while (is_ws_char(c))
  395  			{
  396> 				if ((!ADVANCE_CHAR(str, tok)) || (!PEEK_CHAR(c, tok)))
  397  					goto out;
  398  			}
  399  			if (c == '/' && !(tok->flags & JSON_TOKENER_STRICT))
  400  			{
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 399행, 조건 `!(tok->flags & JSON_TOKENER_STRICT)`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  395  			{
  396  				if ((!ADVANCE_CHAR(str, tok)) || (!PEEK_CHAR(c, tok)))
  397  					goto out;
  398  			}
  399> 			if (c == '/' && !(tok->flags & JSON_TOKENER_STRICT))
  400  			{
  401  				printbuf_reset(tok->pb);
  402  				printbuf_memappend_checked(tok->pb, &c, 1);
  403  				state = json_tokener_state_comment_start;
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 419행, 조건 `current == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  415  			case '{':
  416  				state = json_tokener_state_eatws;
  417  				saved_state = json_tokener_state_object_field_start;
  418  				current = json_object_new_object();
  419> 				if (current == NULL)
  420  				{
  421  					tok->err = json_tokener_error_memory;
  422  					goto out;
  423  				}
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 429행, 조건 `current == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  425  			case '[':
  426  				state = json_tokener_state_eatws;
  427  				saved_state = json_tokener_state_array;
  428  				current = json_object_new_array();
  429> 				if (current == NULL)
  430  				{
  431  					tok->err = json_tokener_error_memory;
  432  					goto out;
  433  				}
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 448행, 조건 `tok->flags & JSON_TOKENER_STRICT`가 퍼징 중 한 번도 '참'이 되지 않음
```
  444  				printbuf_reset(tok->pb);
  445  				tok->st_pos = 0;
  446  				goto redo_char;
  447  			case '\'':
  448> 				if (tok->flags & JSON_TOKENER_STRICT)
  449  				{
  450  					/* in STRICT mode only double-quote are allowed */
  451  					tok->err = json_tokener_error_parse_unexpected;
  452  					goto out;
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 511행, 조건 `(tok->flags & JSON_TOKENER_STRICT)`가 퍼징 중 한 번도 '참'이 되지 않음
```
  507  			while (tok->st_pos < (int)json_inf_str_len)
  508  			{
  509  				char inf_char = *str;
  510  				if (inf_char != json_inf_str[tok->st_pos] &&
  511> 				    ((tok->flags & JSON_TOKENER_STRICT) ||
  512  				      inf_char != json_inf_str_invert[tok->st_pos])
  513  				   )
  514  				{
  515  					tok->err = json_tokener_error_parse_unexpected;
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 520행, 조건 `!PEEK_CHAR`가 퍼징 중 한 번도 '참'이 되지 않음
```
  516  					goto out;
  517  				}
  518  				tok->st_pos++;
  519  				(void)ADVANCE_CHAR(str, tok);
  520> 				if (!PEEK_CHAR(c, tok))
  521  				{
  522  					/* out of input chars, for now at least */
  523  					goto out;
  524  				}
```

## 제안 3
`json_tokener_parse_ex(struct json_tokener *, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_parse_verbose`)에서만 불립니다. 내부 호출은 3번째 인자 `len`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (12개)
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 349행, 조건 `(len < -1)`가 퍼징 중 한 번도 '참'이 되지 않음
```
  345  	 * so the function limits the maximum string size to INT32_MAX (2GB).
  346  	 * If the function is called with len == -1 then strlen is called to check
  347  	 * the string length is less than INT32_MAX (2GB)
  348  	 */
  349> 	if ((len < -1) || (len == -1 && strlen(str) > INT32_MAX))
  350  	{
  351  		tok->err = json_tokener_error_size;
  352  		return NULL;
  353  	}
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 349행, 조건 `len == -1`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  345  	 * so the function limits the maximum string size to INT32_MAX (2GB).
  346  	 * If the function is called with len == -1 then strlen is called to check
  347  	 * the string length is less than INT32_MAX (2GB)
  348  	 */
  349> 	if ((len < -1) || (len == -1 && strlen(str) > INT32_MAX))
  350  	{
  351  		tok->err = json_tokener_error_size;
  352  		return NULL;
  353  	}
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 396행, 조건 `(!ADVANCE_CHAR(str, tok))`가 퍼징 중 한 번도 '참'이 되지 않음
```
  392  		case json_tokener_state_eatws:
  393  			/* Advance until we change state */
  394  			while (is_ws_char(c))
  395  			{
  396> 				if ((!ADVANCE_CHAR(str, tok)) || (!PEEK_CHAR(c, tok)))
  397  					goto out;
  398  			}
  399  			if (c == '/' && !(tok->flags & JSON_TOKENER_STRICT))
  400  			{
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 396행, 조건 `(!PEEK_CHAR(c, tok))`가 퍼징 중 한 번도 '참'이 되지 않음
```
  392  		case json_tokener_state_eatws:
  393  			/* Advance until we change state */
  394  			while (is_ws_char(c))
  395  			{
  396> 				if ((!ADVANCE_CHAR(str, tok)) || (!PEEK_CHAR(c, tok)))
  397  					goto out;
  398  			}
  399  			if (c == '/' && !(tok->flags & JSON_TOKENER_STRICT))
  400  			{
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 520행, 조건 `!PEEK_CHAR`가 퍼징 중 한 번도 '참'이 되지 않음
```
  516  					goto out;
  517  				}
  518  				tok->st_pos++;
  519  				(void)ADVANCE_CHAR(str, tok);
  520> 				if (!PEEK_CHAR(c, tok))
  521  				{
  522  					/* out of input chars, for now at least */
  523  					goto out;
  524  				}
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 613행, 조건 `!PEEK_CHAR`가 퍼징 중 한 번도 '참'이 되지 않음
```
  609  			/* Advance until we change state */
  610  			const char *case_start = str;
  611  			while (c != '*')
  612  			{
  613> 				if (!ADVANCE_CHAR(str, tok) || !PEEK_CHAR(c, tok))
  614  				{
  615  					printbuf_memappend_checked(tok->pb, case_start,
  616  					                           str - case_start);
  617  					goto out;
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 631행, 조건 `!PEEK_CHAR`가 퍼징 중 한 번도 '참'이 되지 않음
```
  627  			/* Advance until we change state */
  628  			const char *case_start = str;
  629  			while (c != '\n')
  630  			{
  631> 				if (!ADVANCE_CHAR(str, tok) || !PEEK_CHAR(c, tok))
  632  				{
  633  					printbuf_memappend_checked(tok->pb, case_start,
  634  					                           str - case_start);
  635  					goto out;
```
- `json_tokener_parse_ex(struct json_tokener *, const char *, int)` 692행, 조건 `!PEEK_CHAR`가 퍼징 중 한 번도 '참'이 되지 않음
```
  688  					// Disallow control characters in strict mode
  689  					tok->err = json_tokener_error_parse_string;
  690  					goto out;
  691  				}
  692> 				if (!ADVANCE_CHAR(str, tok) || !PEEK_CHAR(c, tok))
  693  				{
  694  					printbuf_memappend_checked(tok->pb, case_start,
  695  					                           str - case_start);
  696  					goto out;
```

## 제안 4
`json_tokener_free(struct json_tokener *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_parse_verbose`)에서만 불립니다. 내부 호출은 1번째 인자 `tok`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `json_tokener_free(struct json_tokener *)` 188행, 조건 `!tok`가 퍼징 중 한 번도 '참'이 되지 않음
```
  184  }
  185  
  186  void json_tokener_free(struct json_tokener *tok)
  187  {
  188> 	if (!tok)
  189  		return;
  190  	json_tokener_reset(tok);
  191  	if (tok->pb)
  192  		printbuf_free(tok->pb);
```
- `json_tokener_free(struct json_tokener *)` 191행, 조건 `tok->pb`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  187  {
  188  	if (!tok)
  189  		return;
  190  	json_tokener_reset(tok);
  191> 	if (tok->pb)
  192  		printbuf_free(tok->pb);
  193  	free(tok->stack);
  194  	free(tok);
  195  }
```

## 제안 7
`json_tokener_reset(struct json_tokener *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_free`, `json_tokener_new_ex`)에서만 불립니다. 내부 호출은 1번째 인자 `tok`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_tokener_reset(struct json_tokener *)` 210행, 조건 `!tok`가 퍼징 중 한 번도 '참'이 되지 않음
```
  206  
  207  void json_tokener_reset(struct json_tokener *tok)
  208  {
  209  	int i;
  210> 	if (!tok)
  211  		return;
  212  
  213  	for (i = tok->depth; i >= 0; i--)
  214  		json_tokener_reset_level(tok, i);
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: json-c 저장소 fuzz/json_array_fuzzer.cc (커밋 d9b375f) 그대로.
   2  #include <fuzzer/FuzzedDataProvider.h>
   3  
   4  #include "json.h"
   5  
   6  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   7  	FuzzedDataProvider fdp(data, size);
   8  	json_object *my_array = json_object_new_array();
   9  	for (int i = 0; i < 3; ++i) {
  10  		json_object *jso = json_tokener_parse(fdp.ConsumeRandomLengthString(10).c_str());
  11  		if (jso == NULL) {
  12  			continue;
  13  		}
  14  		json_object_array_add(my_array, jso);
  15  	}
  16  	json_object_array_insert_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10),
  17  	                             json_object_new_int(fdp.ConsumeIntegral<int>()));
  18  	json_object_array_get_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10));
  19  	json_object_array_put_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10),
  20  	                          json_object_new_int(fdp.ConsumeIntegral<int>()));
  21  	json_object_array_del_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10),
  22  	                          fdp.ConsumeIntegralInRange<size_t>(0, 10));
  23  	json_object_array_shrink(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10));
  24  	json_object_array_sort(my_array, [](const void *a, const void *b) { return 0; });
  25  	json_object_array_length(my_array);
  26  	json_object_put(my_array);
  27  	return 0;
  28  }
```