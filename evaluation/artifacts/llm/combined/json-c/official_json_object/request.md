라이브러리: json-c
하네스 파일: official_json_object.cc

아래 제안 4개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)`의 4번째 인자 `userarg`를 하네스가 고정합니다(28행에서 항상 `NULL`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (25개)
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 24행, 조건 `case JSON_C_VISIT_RETURN_CONTINUE`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
   20  {
   21  	int ret = _json_c_visit(jso, NULL, NULL, NULL, userfunc, userarg);
   22  	switch (ret)
   23  	{
   24> 	case JSON_C_VISIT_RETURN_CONTINUE:
   25  	case JSON_C_VISIT_RETURN_SKIP:
   26  	case JSON_C_VISIT_RETURN_POP:
   27  	case JSON_C_VISIT_RETURN_STOP: return 0;
   28  	default: return JSON_C_VISIT_RETURN_ERROR;
```
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 25행, 조건 `case JSON_C_VISIT_RETURN_SKIP`가 퍼징 중 한 번도 '참'이 되지 않음
```
   21  	int ret = _json_c_visit(jso, NULL, NULL, NULL, userfunc, userarg);
   22  	switch (ret)
   23  	{
   24  	case JSON_C_VISIT_RETURN_CONTINUE:
   25> 	case JSON_C_VISIT_RETURN_SKIP:
   26  	case JSON_C_VISIT_RETURN_POP:
   27  	case JSON_C_VISIT_RETURN_STOP: return 0;
   28  	default: return JSON_C_VISIT_RETURN_ERROR;
   29  	}
```
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 26행, 조건 `case JSON_C_VISIT_RETURN_POP`가 퍼징 중 한 번도 '참'이 되지 않음
```
   22  	switch (ret)
   23  	{
   24  	case JSON_C_VISIT_RETURN_CONTINUE:
   25  	case JSON_C_VISIT_RETURN_SKIP:
   26> 	case JSON_C_VISIT_RETURN_POP:
   27  	case JSON_C_VISIT_RETURN_STOP: return 0;
   28  	default: return JSON_C_VISIT_RETURN_ERROR;
   29  	}
   30  }
```
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 27행, 조건 `case JSON_C_VISIT_RETURN_STOP`가 퍼징 중 한 번도 '참'이 되지 않음
```
   23  	{
   24  	case JSON_C_VISIT_RETURN_CONTINUE:
   25  	case JSON_C_VISIT_RETURN_SKIP:
   26  	case JSON_C_VISIT_RETURN_POP:
   27> 	case JSON_C_VISIT_RETURN_STOP: return 0;
   28  	default: return JSON_C_VISIT_RETURN_ERROR;
   29  	}
   30  }
   31  static int _json_c_visit(json_object *jso, json_object *parent_jso, const char *jso_key,
```
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 28행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
   24  	case JSON_C_VISIT_RETURN_CONTINUE:
   25  	case JSON_C_VISIT_RETURN_SKIP:
   26  	case JSON_C_VISIT_RETURN_POP:
   27  	case JSON_C_VISIT_RETURN_STOP: return 0;
   28> 	default: return JSON_C_VISIT_RETURN_ERROR;
   29  	}
   30  }
   31  static int _json_c_visit(json_object *jso, json_object *parent_jso, const char *jso_key,
   32                           size_t *jso_index, json_c_visit_userfunc *userfunc, void *userarg)
```
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 37행, 조건 `case JSON_C_VISIT_RETURN_CONTINUE`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
   33  {
   34  	int userret = userfunc(jso, 0, parent_jso, jso_key, jso_index, userarg);
   35  	switch (userret)
   36  	{
   37> 	case JSON_C_VISIT_RETURN_CONTINUE: break;
   38  	case JSON_C_VISIT_RETURN_SKIP:
   39  	case JSON_C_VISIT_RETURN_POP:
   40  	case JSON_C_VISIT_RETURN_STOP:
   41  	case JSON_C_VISIT_RETURN_ERROR: return userret;
```
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 38행, 조건 `case JSON_C_VISIT_RETURN_SKIP`가 퍼징 중 한 번도 '참'이 되지 않음
```
   34  	int userret = userfunc(jso, 0, parent_jso, jso_key, jso_index, userarg);
   35  	switch (userret)
   36  	{
   37  	case JSON_C_VISIT_RETURN_CONTINUE: break;
   38> 	case JSON_C_VISIT_RETURN_SKIP:
   39  	case JSON_C_VISIT_RETURN_POP:
   40  	case JSON_C_VISIT_RETURN_STOP:
   41  	case JSON_C_VISIT_RETURN_ERROR: return userret;
   42  	default:
```
- `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)` 39행, 조건 `case JSON_C_VISIT_RETURN_POP`가 퍼징 중 한 번도 '참'이 되지 않음
```
   35  	switch (userret)
   36  	{
   37  	case JSON_C_VISIT_RETURN_CONTINUE: break;
   38  	case JSON_C_VISIT_RETURN_SKIP:
   39> 	case JSON_C_VISIT_RETURN_POP:
   40  	case JSON_C_VISIT_RETURN_STOP:
   41  	case JSON_C_VISIT_RETURN_ERROR: return userret;
   42  	default:
   43  		fprintf(stderr, "ERROR: invalid return value from json_c_visit userfunc: %d\n",
```

## 제안 2
`json_object_deep_copy(struct json_object *, struct json_object **, json_c_shallow_copy_fn *)`의 2번째 인자 `dst`를 하네스가 고정합니다(40행에서 항상 같은 객체 `&dst`) (라이브러리 내부 `json_object_deep_copy_recursive` → `json_object_object_add` → `json_object_object_add_ex`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `json_object_object_add_ex(struct json_object *, const char *const, struct json_object *const, const unsigned int)` 761행, 조건 `jso == val`가 퍼징 중 한 번도 '참'이 되지 않음
```
  757  	        : lh_table_lookup_entry_w_hash(JC_OBJECT(jso)->c_object, (const void *)key, hash);
  758  
  759  	// The caller must avoid creating loops in the object tree, but do a
  760  	// quick check anyway to make sure we're not creating a trivial loop.
  761> 	if (jso == val)
  762  		return -1;
  763  
  764  	if (!existing_entry)
  765  	{
```
- `json_object_deep_copy(struct json_object *, struct json_object **, json_c_shallow_copy_fn *)` 2113행, 조건 `!dst`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2109  {
 2110  	int rc;
 2111  
 2112  	/* Check if arguments are sane ; *dst must not point to a non-NULL object */
 2113> 	if (!src || !dst || *dst)
 2114  	{
 2115  		errno = EINVAL;
 2116  		return -1;
 2117  	}
```
- `json_object_deep_copy(struct json_object *, struct json_object **, json_c_shallow_copy_fn *)` 2113행, 조건 `*dst`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2109  {
 2110  	int rc;
 2111  
 2112  	/* Check if arguments are sane ; *dst must not point to a non-NULL object */
 2113> 	if (!src || !dst || *dst)
 2114  	{
 2115  		errno = EINVAL;
 2116  		return -1;
 2117  	}
```

## 제안 3
`json_object_deep_copy(struct json_object *, struct json_object **, json_c_shallow_copy_fn *)`의 3번째 인자 `shallow_copy`에 하네스가 null을 넘긴 적이 없습니다(40행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_object_deep_copy(struct json_object *, struct json_object **, json_c_shallow_copy_fn *)` 2119행, 조건 `shallow_copy == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2115  		errno = EINVAL;
 2116  		return -1;
 2117  	}
 2118  
 2119> 	if (shallow_copy == NULL)
 2120  		shallow_copy = json_c_shallow_copy_default;
 2121  
 2122  	rc = json_object_deep_copy_recursive(src, NULL, NULL, UINT_MAX, dst, shallow_copy);
 2123  	if (rc < 0)
```

## 제안 4
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

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: json-c 저장소 fuzz/json_object_fuzzer.cc (커밋 d9b375f) 그대로.
   2  #include <fuzzer/FuzzedDataProvider.h>
   3  
   4  #include "json.h"
   5  #include "json_visit.h"
   6  
   7  // Function to test json_c_visit
   8  static int emit_object(json_object *jso, int flags, json_object *parent_jso, const char *jso_key,
   9                         size_t *jso_index, void *userarg) {
  10  	return JSON_C_VISIT_RETURN_CONTINUE;
  11  }
  12  
  13  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  14  	FuzzedDataProvider fdp(data, size);
  15  	json_object *jso = json_tokener_parse(fdp.ConsumeRandomLengthString(20).c_str());
  16  
  17  	json_object_get_boolean(jso);
  18  	json_object_get_double(jso);
  19  	json_object_get_int(jso);
  20  	json_object_get_int64(jso);
  21  	json_object_get_uint64(jso);
  22  	json_object_get_string(jso);
  23  	json_object_get_string_len(jso);
  24  	json_object_get_object(jso);
  25  	json_object_get_array(jso);
  26  	json_object_get_type(jso);
  27  
  28  	json_c_visit(jso, 0, emit_object, NULL);
  29  
  30  	json_object_set_int(jso, fdp.ConsumeIntegral<int>());
  31  	json_object_set_int64(jso, fdp.ConsumeIntegral<int64_t>());
  32  	json_object_set_uint64(jso, fdp.ConsumeIntegral<uint64_t>());
  33  	json_object_set_double(jso, fdp.ConsumeFloatingPoint<double>());
  34  	json_object_set_string(jso, fdp.ConsumeRandomLengthString(10).c_str());
  35  	json_object_set_boolean(jso, fdp.ConsumeBool());
  36  	std::string str = fdp.ConsumeRandomLengthString(10);
  37  	json_object_set_string_len(jso, str.c_str(), str.size());
  38  
  39  	json_object *dst = NULL;
  40  	json_object_deep_copy(jso, &dst, json_c_shallow_copy_default);
  41  	json_object_put(dst);
  42  
  43  	json_object_put(jso);
  44  	return 0;
  45  }
```