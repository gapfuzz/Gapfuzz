라이브러리: json-c
하네스 파일: official_json_pointer.cc

아래 제안 7개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`json_pointer_set(struct json_object **, const char *, struct json_object *)`의 1번째 인자 `obj`를 하네스가 고정합니다(44행에서 항상 같은 객체 `&jo1`) (라이브러리 내부 `json_pointer_set_with_cb`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `json_pointer_set_with_cb(struct json_object **, const char *, struct json_object *, json_pointer_set_cb, int, void *)` 331행, 조건 `!obj`가 퍼징 중 한 번도 '참'이 되지 않음
```
  327  	char *path_copy = NULL;
  328  	struct json_object *set = NULL;
  329  	int rc;
  330  
  331> 	if (!obj || !path)
  332  	{
  333  		errno = EINVAL;
  334  		return -1;
  335  	}
```
- `json_object_get_type(const struct json_object *)` 530행, 조건 `!jso`가 퍼징 중 한 번도 '참'이 되지 않음
```
  526  }
  527  
  528  enum json_type json_object_get_type(const struct json_object *jso)
  529  {
  530> 	if (!jso)
  531  		return json_type_null;
  532  	return jso->o_type;
  533  }
  534  
```
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

## 제안 2
`json_pointer_getf(struct json_object *, struct json_object **, const char *, ...)`의 2번째 인자 `res`를 하네스가 고정합니다(37행에서 항상 같은 객체 `&jo2`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `json_pointer_getf(struct json_object *, struct json_object **, const char *, ...)` 224행, 조건 `value`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  220  	rc = json_pointer_result_get_recursive(obj, path, &res);
  221  	if (rc)
  222  		return rc;
  223  
  224> 	if (value)
  225  		*value = res.obj;
  226  
  227  	return 0;
  228  }
```
- `json_pointer_getf(struct json_object *, struct json_object **, const char *, ...)` 310행, 조건 `res`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  306  		return rc;
  307  
  308  	if (path_copy[0] == '\0')
  309  	{
  310> 		if (res)
  311  			*res = obj;
  312  		goto out;
  313  	}
  314  
```

## 제안 3
`json_pointer_setf(struct json_object **, struct json_object *, const char *, ...)`의 3번째 인자 `path_fmt`를 하네스가 고정합니다(38행에서 항상 `"%s"`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `json_pointer_setf(struct json_object **, struct json_object *, const char *, ...)` 397행, 조건 `!obj`가 퍼징 중 한 번도 '참'이 되지 않음
```
  393  	struct json_object *set = NULL;
  394  	va_list args;
  395  	int rc = 0;
  396  
  397> 	if (!obj || !path_fmt)
  398  	{
  399  		errno = EINVAL;
  400  		return -1;
  401  	}
```
- `json_pointer_setf(struct json_object **, struct json_object *, const char *, ...)` 397행, 조건 `!path_fmt`가 퍼징 중 한 번도 '참'이 되지 않음
```
  393  	struct json_object *set = NULL;
  394  	va_list args;
  395  	int rc = 0;
  396  
  397> 	if (!obj || !path_fmt)
  398  	{
  399  		errno = EINVAL;
  400  		return -1;
  401  	}
```

## 제안 4
`json_pointer_get(struct json_object *, const char *, struct json_object **)`의 3번째 인자 `res`를 하네스가 고정합니다(43행에서 항상 같은 객체 `&jo2`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_pointer_get(struct json_object *, const char *, struct json_object **)` 283행, 조건 `res`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  279  	rc = json_pointer_get_internal(obj, path, &jpres);
  280  	if (rc)
  281  		return rc;
  282  
  283> 	if (res)
  284  		*res = jpres.obj;
  285  
  286  	return 0;
  287  }
```

## 제안 5
`json_pointer_getf(struct json_object *, struct json_object **, const char *, ...)`의 3번째 인자 `path_fmt`를 하네스가 고정합니다(37행에서 항상 `"%s"`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_pointer_getf(struct json_object *, struct json_object **, const char *, ...)` 295행, 조건 `!path_fmt`가 퍼징 중 한 번도 '참'이 되지 않음
```
  291  	char *path_copy = NULL;
  292  	int rc = 0;
  293  	va_list args;
  294  
  295> 	if (!obj || !path_fmt)
  296  	{
  297  		errno = EINVAL;
  298  		return -1;
  299  	}
```

## 제안 8
`json_pointer_get(struct json_object *, const char *, struct json_object **)`의 2번째 인자 `path`에 하네스가 null을 넘긴 적이 없습니다(43행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_pointer_get(struct json_object *, const char *, struct json_object **)` 236행, 조건 `!path`가 퍼징 중 한 번도 '참'이 되지 않음
```
  232  {
  233  	char *path_copy = NULL;
  234  	int rc;
  235  
  236> 	if (!obj || !path)
  237  	{
  238  		errno = EINVAL;
  239  		return -1;
  240  	}
```

## 제안 9
`json_pointer_set(struct json_object **, const char *, struct json_object *)`의 2번째 인자 `path`에 하네스가 null을 넘긴 적이 없습니다(44행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `json_pointer_set_with_cb(struct json_object **, const char *, struct json_object *, json_pointer_set_cb, int, void *)` 331행, 조건 `!path`가 퍼징 중 한 번도 '참'이 되지 않음
```
  327  	char *path_copy = NULL;
  328  	struct json_object *set = NULL;
  329  	int rc;
  330  
  331> 	if (!obj || !path)
  332  	{
  333  		errno = EINVAL;
  334  		return -1;
  335  	}
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: json-c 저장소 fuzz/json_pointer_fuzzer.cc (커밋 d9b375f) 그대로.
   2  #include <fuzzer/FuzzedDataProvider.h>
   3  
   4  #include "json.h"
   5  
   6  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   7  	FuzzedDataProvider fdp(data, size);
   8  
   9  	struct json_tokener *tokener =
  10  	    json_tokener_new_ex(fdp.ConsumeIntegralInRange<int>(1, JSON_TOKENER_DEFAULT_DEPTH));
  11  	int flags = 0;
  12  	if (fdp.ConsumeBool()) {
  13  		flags |= JSON_TOKENER_VALIDATE_UTF8;
  14  	}
  15  	if (fdp.ConsumeBool()) {
  16  		flags |= JSON_TOKENER_ALLOW_TRAILING_CHARS;
  17  	}
  18  	if (fdp.ConsumeBool()) {
  19  		flags |= JSON_TOKENER_STRICT;
  20  	}
  21  	json_tokener_set_flags(tokener, flags);
  22  
  23  	std::string path = fdp.ConsumeRandomLengthString(5);
  24  	std::string sub_json_str = fdp.ConsumeRandomLengthString(10);
  25  	bool use_format_string = fdp.ConsumeBool();
  26  	std::string json_str = fdp.ConsumeRemainingBytesAsString();
  27  
  28  	struct json_object *jo1 = json_tokener_parse_ex(tokener, json_str.c_str(), json_str.size());
  29  
  30  	struct json_object *sub_json = json_tokener_parse(sub_json_str.c_str());
  31  	if (sub_json == NULL) {
  32  		sub_json = json_object_new_object();
  33  	}
  34  
  35  	struct json_object *jo2 = NULL;
  36  	if (use_format_string) {
  37  		json_pointer_getf(jo1, &jo2, "%s", path.c_str());
  38  		if (json_pointer_setf(&jo1, sub_json, "%s", path.c_str()))
  39  		{
  40  			json_object_put(sub_json);
  41  		}
  42  	} else {
  43  		json_pointer_get(jo1, path.c_str(), &jo2);
  44  		if (json_pointer_set(&jo1, path.c_str(), sub_json))
  45  		{
  46  			json_object_put(sub_json);
  47  		}
  48  	}
  49  
  50  	// Clean up the main JSON object
  51  	json_object_put(jo1);
  52  	json_tokener_free(tokener);
  53  	return 0;
  54  }
```