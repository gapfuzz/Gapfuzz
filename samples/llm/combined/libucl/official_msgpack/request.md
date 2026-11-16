라이브러리: libucl
하네스 파일: official_msgpack.c

아래 제안 3개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)`의 6번째 인자 `parse_type`를 하네스가 고정합니다(17행에서 항상 `UCL_PARSE_MSGPACK`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (6개)
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3662행, 조건 `parse_type == UCL_PARSE_AUTO`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3658  				len = nlen;
 3659  			}
 3660  		}
 3661  
 3662> 		if (parse_type == UCL_PARSE_AUTO && len > 0) {
 3663  			/* We need to detect parse type by the first symbol */
 3664  			if (len >= 3 && data[0] == 0xd9 && data[1] == 0xd9 &&
 3665  				data[2] == 0xf7) {
 3666  				/*
```
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3724행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3720  			}
 3721  
 3722  			/* Need to parse something */
 3723  			switch (parse_type) {
 3724> 			default:
 3725  			case UCL_PARSE_UCL:
 3726  				return ucl_state_machine(parser);
 3727  			case UCL_PARSE_MSGPACK:
 3728  				return ucl_parse_msgpack(parser);
```
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3725행, 조건 `case UCL_PARSE_UCL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3721  
 3722  			/* Need to parse something */
 3723  			switch (parse_type) {
 3724  			default:
 3725> 			case UCL_PARSE_UCL:
 3726  				return ucl_state_machine(parser);
 3727  			case UCL_PARSE_MSGPACK:
 3728  				return ucl_parse_msgpack(parser);
 3729  			case UCL_PARSE_CBOR:
```
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3727행, 조건 `case UCL_PARSE_MSGPACK`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 3723  			switch (parse_type) {
 3724  			default:
 3725  			case UCL_PARSE_UCL:
 3726  				return ucl_state_machine(parser);
 3727> 			case UCL_PARSE_MSGPACK:
 3728  				return ucl_parse_msgpack(parser);
 3729  			case UCL_PARSE_CBOR:
 3730  				return ucl_parse_cbor(parser);
 3731  			case UCL_PARSE_CSEXP:
```
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3729행, 조건 `case UCL_PARSE_CBOR`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3725  			case UCL_PARSE_UCL:
 3726  				return ucl_state_machine(parser);
 3727  			case UCL_PARSE_MSGPACK:
 3728  				return ucl_parse_msgpack(parser);
 3729> 			case UCL_PARSE_CBOR:
 3730  				return ucl_parse_cbor(parser);
 3731  			case UCL_PARSE_CSEXP:
 3732  				return ucl_parse_csexp(parser);
 3733  			}
```
- `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` 3731행, 조건 `case UCL_PARSE_CSEXP`가 퍼징 중 한 번도 '참'이 되지 않음
```
 3727  			case UCL_PARSE_MSGPACK:
 3728  				return ucl_parse_msgpack(parser);
 3729  			case UCL_PARSE_CBOR:
 3730  				return ucl_parse_cbor(parser);
 3731> 			case UCL_PARSE_CSEXP:
 3732  				return ucl_parse_csexp(parser);
 3733  			}
 3734  		}
 3735  		else {
```

## 제안 3
`ucl_object_unref(ucl_object_t *)`의 1번째 인자 `obj`에 하네스가 null을 넘긴 적이 없습니다(21행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `ucl_object_unref(ucl_object_t *)` 302행, 조건 `obj == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  298  {
  299  	struct ucl_dtor_worklist wl = {NULL};
  300  	ucl_object_t *cur, *sub, *tmp;
  301  
  302> 	if (obj == NULL) {
  303  		return;
  304  	}
  305  
  306  	/*
```
- `ucl_object_unref(ucl_object_t *)` 4235행, 조건 `obj != NULL`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 4231  }
 4232  
 4233  void ucl_object_unref(ucl_object_t *obj)
 4234  {
 4235> 	if (obj != NULL) {
 4236  #ifdef HAVE_ATOMIC_BUILTINS
 4237  		unsigned int rc = __sync_sub_and_fetch(&obj->ref, 1);
 4238  		if (rc == 0) {
 4239  #else
```

## 제안 10
`ucl_parser_set_filevars(struct ucl_parser *, const char *, bool)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`ucl_parser_new`)에서만 불립니다. 내부 호출은 2번째 인자 `filename`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `ucl_parser_set_filevars(struct ucl_parser *, const char *, bool)` 2304행, 조건 `filename != NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2300  bool ucl_parser_set_filevars(struct ucl_parser *parser, const char *filename, bool need_expand)
 2301  {
 2302  	char realbuf[PATH_MAX], *curdir;
 2303  
 2304> 	if (filename != NULL) {
 2305  		if (need_expand) {
 2306  			if (ucl_realpath(filename, realbuf) == NULL) {
 2307  				return false;
 2308  			}
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: libucl 저장소 tests/fuzzers/ucl_msgpack_fuzzer.c (0.10.0, 커밋 d6659c1) 그대로.
   2  #include <stdio.h>
   3  #include <errno.h>
   4  #include <unistd.h>
   5  #include "ucl.h"
   6  
   7  int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   8  	if (size < 3) {
   9  		return 0;
  10  	}
  11  
  12  	struct ucl_parser *parser = ucl_parser_new(UCL_PARSER_KEY_LOWERCASE);
  13  	if (parser == NULL) {
  14  		return 0;
  15  	}
  16  
  17  	if (ucl_parser_add_chunk_full(parser, (const unsigned char *)data, size,
  18  			0, UCL_DUPLICATE_APPEND, UCL_PARSE_MSGPACK)) {
  19  		ucl_object_t *obj = ucl_parser_get_object(parser);
  20  		if (obj != NULL) {
  21  			ucl_object_unref(obj);
  22  		}
  23  	}
  24  
  25  	ucl_parser_free(parser);
  26  	return 0;
  27  }
```