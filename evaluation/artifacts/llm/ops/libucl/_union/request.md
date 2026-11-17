라이브러리: libucl
OSS-Fuzz 하네스 2개(official, official_msgpack)의 커버리지를 모두 합쳐도, 공개 API 130개 중 82개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `ucl_object_validate_root(const ucl_object_t *, const ucl_object_t *, const ucl_object_t *, struct ucl_schema_error *)` — 새로 실행될 수 있는 코드 영역 1101개
```
/**
 * Validate object `obj` using schema object `schema` and root schema at `root`.
 * @param schema schema object
 * @param obj object to validate
 * @param root root schema object
 * @param err error pointer, if this parameter is not NULL and error has been
 * occurred, then `err` is filled with the exact error definition.
 * @return true if `obj` is valid using `schema`
 */
UCL_EXTERN bool ucl_object_validate_root(const ucl_object_t *schema,
										 const ucl_object_t *obj,
										 const ucl_object_t *root,
										 struct ucl_schema_error *err);
/**
 * Validate object `obj` using schema object `schema` and root schema at `root`
 * using some external references provided.
 * @param schema schema object
 * @param obj object to validate
 * @param root root schema object
 * @param ext_refs external references (might be modified during validation)
 * @param err error pointer, if this parameter is not NULL and error has been
 * occurred, then `err` is filled with the exact error definition.
 * @return true if `obj` is valid using `schema`
 */
```

### 2. `ucl_object_merge(ucl_object_t *, ucl_object_t *, bool)` — 새로 실행될 수 있는 코드 영역 233개
```
/**
 * Merge the keys from one object to another object. Overwrite on conflict
 * @param top destination object (must be of type UCL_OBJECT)
 * @param elt element to insert (must be of type UCL_OBJECT)
 * @param copy copy rather than reference the elements
 * @return true if all keys have been merged
 */
UCL_EXTERN bool ucl_object_merge(ucl_object_t *top, ucl_object_t *elt, bool copy);
/**
 * Delete a object associated with key 'key', old object will be unrefered,
 * @param top object
 * @param key key associated to the object to remove
 * @param keylen length of the key (or 0 for NULL terminated keys)
 */
```

### 3. `ucl_object_sort_keys(ucl_object_t *, enum ucl_object_keys_sort_flags)` — 새로 실행될 수 있는 코드 영역 150개
```
/***
 * Sorts keys in object in place
 * @param obj
 * @param how
 */
UCL_EXTERN void ucl_object_sort_keys(ucl_object_t *obj,
									 enum ucl_object_keys_sort_flags how);
/**
 * Get the priority for specific UCL object
 * @param obj any ucl object
 * @return priority of an object
 */
```

### 4. `ucl_comments_add(ucl_object_t *, const ucl_object_t *, const char *)` — 새로 실행될 수 있는 코드 영역 94개
```
/**
 * Adds a new comment for an object
 * @param comments comments object
 * @param obj object to add comment to
 * @param comment string representation of a comment
 */
UCL_EXTERN void ucl_comments_add(ucl_object_t *comments,
								 const ucl_object_t *obj, const char *comment);
/**
 * Add new public key to parser for signatures check
 * @param parser parser object
 * @param key PEM representation of a key
 * @param len length of the key
 * @param err if *err is NULL it is set to parser error
 * @return true if a key has been successfully added
 */
```

### 5. `ucl_object_pop_key(ucl_object_t *, const char *)` — 새로 실행될 수 있는 코드 영역 84개
```
/**
 * Removes `key` from `top` object returning the object that was removed. This
 * object is not released, caller must unref the returned object when it is no
 * longer needed.
 * @param top object
 * @param key key to remove
 * @return removed object or NULL if object has not been found
 */
UCL_EXTERN ucl_object_t *ucl_object_pop_key(ucl_object_t *top, const char *key)
	UCL_WARN_UNUSED_RESULT;
/**
 * Insert a object 'elt' to the hash 'top' and associate it with key 'key', if
 * the specified key exist, try to merge its content
 * @param top destination object (must be of type UCL_OBJECT)
 * @param elt element to insert (must NOT be NULL)
 * @param key key to associate with this object (either const or preallocated)
 * @param keylen length of the key (or 0 for NULL terminated keys)
 * @param copy_key make an internal copy of key
 * @return true if key has been inserted
 */
```

### 6. `ucl_parser_insert_chunk(struct ucl_parser *, const unsigned char *, size_t)` — 새로 실행될 수 있는 코드 영역 64개
```
/**
 * Insert new chunk to a parser (must have previously processed data with an existing top object)
 * @param parser parser structure
 * @param data the pointer to the beginning of a chunk
 * @param len the length of a chunk
 * @return true if chunk has been added and false in case of error
 */
UCL_EXTERN bool ucl_parser_insert_chunk(struct ucl_parser *parser,
										const unsigned char *data, size_t len);
/**
 * Full version of ucl_add_chunk with priority and duplicate strategy
 * @param parser parser structure
 * @param data the pointer to the beginning of a chunk
 * @param len the length of a chunk
 * @param priority the desired priority of a chunk (only 4 least significant bits
 * are considered for this parameter)
 * @param strat duplicates merging strategy
 * @param parse_type input format
 * @return true if chunk has been added and false in case of error
 */
```

### 7. `ucl_object_reserve(ucl_object_t *, size_t)` — 새로 실행될 수 있는 코드 영역 61개
```
/**
 * Reserve space in ucl array or object for `elt` elements
 * @param obj object to reserve
 * @param reserved size to reserve in an object
 * @return 0 on success, -1 on failure (i.e. ENOMEM)
 */
UCL_EXTERN bool ucl_object_reserve(ucl_object_t *obj, size_t reserved);
/**
 * Append an element to the end of array object
 * @param top destination object (must NOT be NULL)
 * @param elt element to append (must NOT be NULL)
 * @return true if value has been inserted
 */
```

### 8. `ucl_array_prepend(ucl_object_t *, ucl_object_t *)` — 새로 실행될 수 있는 코드 영역 59개
```
/**
 * Append an element to the start of array object
 * @param top destination object (must NOT be NULL)
 * @param elt element to append (must NOT be NULL)
 * @return true if value has been inserted
 */
UCL_EXTERN bool ucl_array_prepend(ucl_object_t *top,
								  ucl_object_t *elt);
/**
 * Merge all elements of second array into the first array
 * @param top destination array (must be of type UCL_ARRAY)
 * @param elt array to copy elements from (must be of type UCL_ARRAY)
 * @param copy copy elements instead of referencing them
 * @return true if arrays were merged
 */
```

### 9. `ucl_object_emit(const ucl_object_t *, enum ucl_emitter)` — 새로 실행될 수 있는 코드 영역 49개
```
/**
 * Emit object to a string
 * @param obj object
 * @param emit_type if type is #UCL_EMIT_JSON then emit json, if type is
 * #UCL_EMIT_CONFIG then emit config like object
 * @return dump of an object (must be freed after using) or NULL in case of error
 */
UCL_EXTERN unsigned char *ucl_object_emit(const ucl_object_t *obj,
										  enum ucl_emitter emit_type);
/**
 * Emit object to a string that can contain `\0` inside
 * @param obj object
 * @param emit_type if type is #UCL_EMIT_JSON then emit json, if type is
 * #UCL_EMIT_CONFIG then emit config like object
 * @param len the resulting length
 * @return dump of an object (must be freed after using) or NULL in case of error
 */
```

### 10. `ucl_object_lookup_path(const ucl_object_t *, const char *)` — 새로 실행될 수 있는 코드 영역 36개
```
/**
 * Return object identified by dot notation string
 * @param obj object to search in
 * @param path dot.notation.path to the path to lookup. May use numeric .index on arrays
 * @return object matched the specified path or NULL if path is not found
 */
UCL_EXTERN const ucl_object_t *ucl_object_lookup_path(const ucl_object_t *obj,
													  const char *path);
```

## 참고: 기존 하네스 official.c (고치지 마세요. include와 작성 방식만 참고)
```
// OSS-Fuzz 하네스: libucl 저장소 tests/fuzzers/ucl_add_string_fuzzer.c (0.10.0, 커밋 d6659c1) 그대로.
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include "ucl.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	// If size is 0 we need a null-terminated string.
	// We dont null-terminate the string and by the design
	// of the API passing 0 as size with non null-terminated string
	// gives undefined behavior. 	
	if(size==0){
		return 0;
	}
	struct ucl_parser *parser;
       	parser = ucl_parser_new(0);
	
	ucl_parser_add_string(parser, (char *)data, size);
	
	if (ucl_parser_get_error(parser) != NULL) {
		ucl_parser_free (parser);
		return 0;
	}

	ucl_parser_free (parser);
        return 0;
}

```