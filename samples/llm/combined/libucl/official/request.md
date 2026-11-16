라이브러리: libucl
하네스 파일: official.c

아래 제안 9개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`ucl_parser_new(int)`의 1번째 인자 `flags`를 하네스가 고정합니다(16행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `ucl_parser_new(int)` 3415행, 조건 `flags & UCL_PARSER_SAVE_COMMENTS`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3411  	 * untrusted data opt into them explicitly via ucl_parser_set_limits().
 3412  	 */
 3413  	parser->limits.max_depth = UCL_MAX_NESTING;
 3414  
 3415> 	if (flags & UCL_PARSER_SAVE_COMMENTS) {
 3416  		parser->comments = ucl_object_typed_new(UCL_OBJECT);
 3417  	}
 3418  
 3419  	if (!(flags & UCL_PARSER_NO_FILEVARS)) {
```
- `ucl_parser_new(int)` 3419행, 조건 `!(flags & UCL_PARSER_NO_FILEVARS)`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 3415  	if (flags & UCL_PARSER_SAVE_COMMENTS) {
 3416  		parser->comments = ucl_object_typed_new(UCL_OBJECT);
 3417  	}
 3418  
 3419> 	if (!(flags & UCL_PARSER_NO_FILEVARS)) {
 3420  		/* Initial assumption about filevars */
 3421  		ucl_parser_set_filevars(parser, NULL, false);
 3422  	}
 3423  
```

## 제안 2
`ucl_parser_add_string(struct ucl_parser *, const char *, size_t)`의 1번째 인자 `parser`에 하네스가 null을 넘긴 적이 없습니다(18행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (4개)
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 2182행, 조건 `parser == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2178  ucl_parser_get_container(struct ucl_parser *parser)
 2179  {
 2180  	ucl_object_t *t, *obj = NULL;
 2181  
 2182> 	if (parser == NULL || parser->stack == NULL || parser->stack->obj == NULL) {
 2183  		return NULL;
 2184  	}
 2185  
 2186  	if (parser->stack->obj->type == UCL_ARRAY) {
```
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3597행, 조건 `parser == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3593  {
 3594  	struct ucl_chunk *chunk;
 3595  	struct ucl_parser_special_handler *special_handler;
 3596  
 3597> 	if (parser == NULL) {
 3598  		return false;
 3599  	}
 3600  
 3601  	if (data == NULL && len != 0) {
```
- `ucl_parser_add_chunk_priority(struct ucl_parser *, const unsigned char *, size_t, unsigned int)` 3759행, 조건 `parser == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3755  bool ucl_parser_add_chunk_priority(struct ucl_parser *parser,
 3756  								   const unsigned char *data, size_t len, unsigned priority)
 3757  {
 3758  	/* We dereference parser, so this check is essential */
 3759> 	if (parser == NULL) {
 3760  		return false;
 3761  	}
 3762  
 3763  	return ucl_parser_add_chunk_full(parser, data, len,
```
- `ucl_parser_add_string(struct ucl_parser *, const char *, size_t)` 3897행, 조건 `parser == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3893  
 3894  bool ucl_parser_add_string(struct ucl_parser *parser, const char *data,
 3895  						   size_t len)
 3896  {
 3897> 	if (parser == NULL) {
 3898  		return false;
 3899  	}
 3900  
 3901  	return ucl_parser_add_string_priority(parser,
```

## 제안 3
`ucl_parser_add_string(struct ucl_parser *, const char *, size_t)`의 2번째 인자 `data`에 하네스가 null을 넘긴 적이 없습니다(18행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3601행, 조건 `data == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3597  	if (parser == NULL) {
 3598  		return false;
 3599  	}
 3600  
 3601> 	if (data == NULL && len != 0) {
 3602  		ucl_create_err(&parser->err, "invalid chunk added");
 3603  		return false;
 3604  	}
 3605  
```
- `ucl_parser_add_string_priority(struct ucl_parser *, const char *, size_t, unsigned int)` 3882행, 조건 `data == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3878  
 3879  bool ucl_parser_add_string_priority(struct ucl_parser *parser, const char *data,
 3880  									size_t len, unsigned priority)
 3881  {
 3882> 	if (data == NULL) {
 3883  		ucl_create_err(&parser->err, "invalid string added");
 3884  		return false;
 3885  	}
 3886  	if (len == 0) {
```

## 제안 4
`ucl_parser_get_error(struct ucl_parser *)`의 1번째 인자 `parser`에 하네스가 null을 넘긴 적이 없습니다(20행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `ucl_parser_get_error(struct ucl_parser *)` 770행, 조건 `parser == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  766  
  767  const char *
  768  ucl_parser_get_error(struct ucl_parser *parser)
  769  {
  770> 	if (parser == NULL) {
  771  		return NULL;
  772  	}
  773  
  774  	if (parser->err == NULL) {
```

## 제안 5
`ucl_parser_free(struct ucl_parser *)`의 1번째 인자 `parser`에 하네스가 null을 넘긴 적이 없습니다(21행, 25행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `ucl_parser_free(struct ucl_parser *)` 695행, 조건 `parser == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  691  	struct ucl_pubkey *key, *ktmp;
  692  	struct ucl_variable *var, *vtmp;
  693  	ucl_object_t *tr, *trtmp;
  694  
  695> 	if (parser == NULL) {
  696  		return;
  697  	}
  698  
  699  	if (parser->top_obj != NULL) {
```

## 제안 6
`ucl_parser_register_variable(struct ucl_parser *, const char *, const char *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`ucl_parser_set_filevars`)에서만 불립니다. 내부 호출은 2번째 인자 `var`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `ucl_parser_register_variable(struct ucl_parser *, const char *, const char *)` 3534행, 조건 `var == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3530  								  const char *value)
 3531  {
 3532  	struct ucl_variable *new = NULL, *cur;
 3533  
 3534> 	if (var == NULL) {
 3535  		return;
 3536  	}
 3537  
 3538  	/* Find whether a variable already exists */
```
- `ucl_parser_register_variable(struct ucl_parser *, const char *, const char *)` 3541행, 조건 `strcmp(cur->var, var) == 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3537  
 3538  	/* Find whether a variable already exists */
 3539  	LL_FOREACH(parser->variables, cur)
 3540  	{
 3541> 		if (strcmp(cur->var, var) == 0) {
 3542  			new = cur;
 3543  			break;
 3544  		}
 3545  	}
```

## 제안 7
`ucl_object_iterate_with_error(const ucl_object_t *, ucl_object_iter_t *, bool, int *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`ucl_include_common`, `ucl_priority_handler`)에서만 불립니다. 내부 호출은 3번째 인자 `expand_values`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `ucl_object_iterate_with_error(const ucl_object_t *, ucl_object_iter_t *, bool, int *)` 3148행, 조건 `expand_values`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 3144  	if (obj == NULL || iter == NULL) {
 3145  		return NULL;
 3146  	}
 3147  
 3148> 	if (expand_values) {
 3149  		switch (obj->type) {
 3150  		case UCL_OBJECT:
 3151  			return (const ucl_object_t *) ucl_hash_iterate2(obj->value.ov, iter, ep);
 3152  			break;
```

## 제안 8
`ucl_parser_register_macro(struct ucl_parser *, const char *, ucl_macro_handler, void *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`ucl_parser_new`)에서만 불립니다. 내부 호출은 2번째 인자 `macro`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `ucl_parser_register_macro(struct ucl_parser *, const char *, ucl_macro_handler, void *)` 3481행, 조건 `macro == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3477  							   ucl_macro_handler handler, void *ud)
 3478  {
 3479  	struct ucl_macro *new;
 3480  
 3481> 	if (macro == NULL || handler == NULL) {
 3482  		return false;
 3483  	}
 3484  
 3485  	new = UCL_ALLOC(sizeof(struct ucl_macro));
```

## 제안 9
`ucl_parser_register_context_macro(struct ucl_parser *, const char *, ucl_context_macro_handler, void *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`ucl_parser_new`)에서만 불립니다. 내부 호출은 2번째 인자 `macro`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `ucl_parser_register_context_macro(struct ucl_parser *, const char *, ucl_context_macro_handler, void *)` 3507행, 조건 `macro == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3503  									   ucl_context_macro_handler handler, void *ud)
 3504  {
 3505  	struct ucl_macro *new;
 3506  
 3507> 	if (macro == NULL || handler == NULL) {
 3508  		return false;
 3509  	}
 3510  
 3511  	new = UCL_ALLOC(sizeof(struct ucl_macro));
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: libucl 저장소 tests/fuzzers/ucl_add_string_fuzzer.c (0.10.0, 커밋 d6659c1) 그대로.
   2  #include <stdio.h>
   3  #include <errno.h>
   4  #include <unistd.h>
   5  #include "ucl.h"
   6  
   7  int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   8  	// If size is 0 we need a null-terminated string.
   9  	// We dont null-terminate the string and by the design
  10  	// of the API passing 0 as size with non null-terminated string
  11  	// gives undefined behavior. 	
  12  	if(size==0){
  13  		return 0;
  14  	}
  15  	struct ucl_parser *parser;
  16         	parser = ucl_parser_new(0);
  17  	
  18  	ucl_parser_add_string(parser, (char *)data, size);
  19  	
  20  	if (ucl_parser_get_error(parser) != NULL) {
  21  		ucl_parser_free (parser);
  22  		return 0;
  23  	}
  24  
  25  	ucl_parser_free (parser);
  26          return 0;
  27  }
```