라이브러리: json-c
OSS-Fuzz 하네스 4개(official, official_json_array, official_json_object, official_json_pointer)의 커버리지를 모두 합쳐도, 공개 API 100개 중 34개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `json_patch_apply(struct json_object *, struct json_object *, struct json_object **, struct json_patch_error *)` — 새로 실행될 수 있는 코드 영역 294개
```
/**
 * Apply the JSON patch to the base object.
 * The patch object must be formatted as per RFC 6902, i.e.
 * a json_type_array containing patch operations.
 * If the patch is not correctly formatted, an error will
 * be returned.
 *
 * The json_object at *base will be modified in place.
 * Exactly one of *base or copy_from must be non-NULL.
 * If *base is NULL, a new copy of copy_from will allocated and populated
 * using json_object_deep_copy().  In this case json_object_put() _must_ be 
 * used to free *base even if the overall patching operation fails.
 *
 * If anything fails during patching a negative value will be returned,
 * and patch_error (if non-NULL) will be populated with error details.
 *
 * @param base a pointer to the JSON object which to patch
 * @param patch the JSON object that describes the patch to be applied
 * @param copy_from a JSON object to copy to *base
 * @param patch_error optional, details about errors
 *
 * @return negative if an error (or not found), or 0 if patch completely applied
 */
JSON_EXPORT int json_patch_apply(struct json_object *copy_from, struct json_object *patch,
                                 struct json_object **base, struct json_patch_error *patch_error);
```

### 2. `json_object_int_inc(struct json_object *, int64_t)` — 새로 실행될 수 있는 코드 영역 37개
```
/** Increment a json_type_int object by the given amount, which may be negative.
 *
 * If the type of obj is not json_type_int then 0 is returned with no further
 * action taken.
 * If the addition would result in a overflow, the object value
 * is set to INT64_MAX.
 * If the addition would result in a underflow, the object value
 * is set to INT64_MIN.
 * Neither overflow nor underflow affect the return value.
 *
 * @param obj the json_object instance
 * @param val the value to add
 * @returns 1 if the increment succeeded, 0 otherwise
 */
JSON_EXPORT int json_object_int_inc(struct json_object *obj, int64_t val);
/** Get the int value of a json_object
 *
 * The type is coerced to a int64 if the passed object is not a int64.
 * double objects will return their int64 conversion except for NaN values
 * which return INT64_MIN and the errno is set to EINVAL.
 * Strings will be parsed as an int64. If no conversion exists then 0 is
 * returned and errno is set to EINVAL. null is equivalent to 0 (no error values
 * set).
 * Sets errno to ERANGE if the value exceeds the range of int64.
 *
 * NOTE: Set errno to 0 directly before a call to this function to determine
 * whether or not conversion was successful (it does not clear the value for
 * you).
 *
 * @param obj the json_object instance
 * @returns an int64
 */
```

### 3. `json_c_set_serialization_double_format(const char *, int)` — 새로 실행될 수 있는 코드 영역 29개
```
/**
 * Set a global or thread-local json-c option, depending on whether
 *  JSON_C_OPTION_GLOBAL or JSON_C_OPTION_THREAD is passed.
 * Thread-local options default to undefined, and inherit from the global
 *  value, even if the global value is changed after the thread is created.
 * Attempting to set thread-local options when threading is not compiled in
 *  will result in an error.  Be sure to check the return value.
 *
 * double_format is a "%g" printf format, such as "%.20g"
 *
 * @return -1 on errors, 0 on success.
 */
JSON_EXPORT int json_c_set_serialization_double_format(const char *double_format,
                                                       int global_or_thread);
/** Serialize a json_object of type json_type_double to a string.
 *
 * This function isn't meant to be called directly. Instead, you can set a
 * custom format string for the serialization of this double using the
 * following call (where "%.17g" actually is the default):
 *
 * @code
 *   jso = json_object_new_double(d);
 *   json_object_set_serializer(jso, json_object_double_to_json_string,
 *       "%.17g", NULL);
 * @endcode
 *
 * @see printf(3) man page for format strings
 *
 * @param jso The json_type_double object that is serialized.
 * @param pb The destination buffer.
 * @param level Ignored.
 * @param flags Ignored.
 */
```

### 4. `json_object_array_put_with_idx_limit_cb(struct json_object *, const char *, size_t, struct json_object *, void *)` — 새로 실행될 수 있는 코드 영역 10개
```
/**
 * A safer callback for 'json_pointer_set_with_cb()' that enforces a
 * maximum array index.
 *
 * This function can be used as the 'set_cb' argument to prevent OOM.
 * It expects the 'priv' argument to be a valid pointer to a 'size_t' variable
 * that holds the maximum allowed index.
 *
 * @param jso the parent json_object array.
 * @param key the object field where the element is to be placed, should be NULL here.
 * @param idx the index where the element is to be placed.
 * @param jso_new the new json_object to place at the index.
 * @param priv A pointer to a 'size_t' variable specifying the maximum index.
 *             This pointer must not be NULL.
 *
 * @return 0 on success, or a negative value if idx exceeds the limit or 'priv' is NULL.
 */
JSON_EXPORT int json_object_array_put_with_idx_limit_cb(struct json_object *jso, const char *key, size_t idx,
                                                   struct json_object *jso_new, void *priv);
```

### 5. `json_type_to_name(enum json_type)` — 새로 실행될 수 있는 코드 영역 8개
```
/**
 * Return a string describing the type of the object.
 * e.g. "int", or "object", etc...
 */
JSON_EXPORT const char *json_type_to_name(enum json_type o_type);
```

### 6. `json_object_iter_peek_value(const struct json_object_iterator *)` — 새로 실행될 수 있는 코드 영역 7개
```
json_object_iter_peek_value(const struct json_object_iterator *iter);
/** Tests two iterators for equality.  Typically used to test
 *  for end of iteration by comparing an iterator to the
 *  corresponding "end" iterator (that was derived from the same
 *  JSON Object instance).
 *
 *  @note The reason we do not (and MUST NOT) provide
 *        "json_object_iter_is_end(json_object_iterator* iter)"
 *        type of API is because it would limit the underlying
 *        representation of name/value containment (or force us
 *        to add additional, otherwise unnecessary, fields to
 *        the iterator structure). The equality test method, on
 *        the other hand, permits us to cleanly abstract pretty
 *        much any reasonable underlying representation.
 *
 * @param iter1 Pointer to first valid, non-NULL iterator
 * @param iter2 POinter to second valid, non-NULL iterator
 *
 * @warning	if a NULL iterator pointer or an uninitialized
 *       	or invalid iterator, or iterators derived from
 *       	different JSON Object instances are passed, bad things
 *       	will happen!
 *
 * @return json_bool non-zero if iterators are equal (i.e., both
 *         reference the same name/value pair or are both at
 *         "end"); zero if they are not equal.
 */
```

### 7. `json_object_iter_peek_name(const struct json_object_iterator *)` — 새로 실행될 수 있는 코드 영역 7개
```
/** Returns a const pointer to the name of the pair referenced
 *  by the given iterator.
 *
 * @param iter pointer to iterator that references a name/value
 *             pair; MUST be a valid, non-end iterator.
 *
 * @warning	bad things will happen if an invalid or "end" iterator
 *             	is passed.  See the warning on json_object_iter_begin()
 *              for details.
 *
 * @return const char* Pointer to the name of the referenced
 *         name/value pair.  The name memory belongs to the
 *         name/value pair, will be freed when the pair is
 *         deleted or modified, and MUST NOT be modified or
 *         freed by the user.
 */
JSON_EXPORT const char *json_object_iter_peek_name(const struct json_object_iterator *iter);
/** Returns a pointer to the json-c instance representing the
 *  value of the referenced name/value pair, without altering
 *  the instance's reference count.
 *
 * @param iter 	pointer to iterator that references a name/value
 *             	pair; MUST be a valid, non-end iterator.
 *
 * @warning	bad things will happen if an invalid or "end" iterator
 *             	is passed.  See the warning on json_object_iter_begin()
 *              for details.
 *
 * @return struct json_object* Pointer to the json-c value
 *         instance of the referenced name/value pair;  the
 *         value's reference count is not changed by this
 *         function: if you plan to hold on to this json-c node,
 *         take a look at json_object_get() and
 *         json_object_put(). IMPORTANT: json-c API represents
 *         the JSON Null value as a NULL json_object instance
 *         pointer.
 */
```

### 8. `json_object_iter_next(struct json_object_iterator *)` — 새로 실행될 수 있는 코드 영역 7개
```
/** Returns an iterator to the next pair, if any
 *
 * @warning 	Any modification of the fields of the object invalidates
 * 		the iterator, see the warning on json_object_iter_begin()
 *              for details.
 *
 * @param iter [IN/OUT] Pointer to iterator that references a
 *         name/value pair; MUST be a valid, non-end iterator.
 *         WARNING: bad things will happen if invalid or "end"
 *         iterator is passed. Upon return will contain the
 *         reference to the next pair if there is one; if there
 *         are no more pairs, will contain the "end" iterator
 *         value, which may be compared against the return value
 *         of json_object_iter_end() for the same JSON Object
 *         instance.
 */
JSON_EXPORT void json_object_iter_next(struct json_object_iterator *iter);
/** Returns a const pointer to the name of the pair referenced
 *  by the given iterator.
 *
 * @param iter pointer to iterator that references a name/value
 *             pair; MUST be a valid, non-end iterator.
 *
 * @warning	bad things will happen if an invalid or "end" iterator
 *             	is passed.  See the warning on json_object_iter_begin()
 *              for details.
 *
 * @return const char* Pointer to the name of the referenced
 *         name/value pair.  The name memory belongs to the
 *         name/value pair, will be freed when the pair is
 *         deleted or modified, and MUST NOT be modified or
 *         freed by the user.
 */
```

### 9. `json_object_iter_equal(const struct json_object_iterator *, const struct json_object_iterator *)` — 새로 실행될 수 있는 코드 영역 7개
```
/** Tests two iterators for equality.  Typically used to test
 *  for end of iteration by comparing an iterator to the
 *  corresponding "end" iterator (that was derived from the same
 *  JSON Object instance).
 *
 *  @note The reason we do not (and MUST NOT) provide
 *        "json_object_iter_is_end(json_object_iterator* iter)"
 *        type of API is because it would limit the underlying
 *        representation of name/value containment (or force us
 *        to add additional, otherwise unnecessary, fields to
 *        the iterator structure). The equality test method, on
 *        the other hand, permits us to cleanly abstract pretty
 *        much any reasonable underlying representation.
 *
 * @param iter1 Pointer to first valid, non-NULL iterator
 * @param iter2 POinter to second valid, non-NULL iterator
 *
 * @warning	if a NULL iterator pointer or an uninitialized
 *       	or invalid iterator, or iterators derived from
 *       	different JSON Object instances are passed, bad things
 *       	will happen!
 *
 * @return json_bool non-zero if iterators are equal (i.e., both
 *         reference the same name/value pair or are both at
 *         "end"); zero if they are not equal.
 */
JSON_EXPORT json_bool json_object_iter_equal(const struct json_object_iterator *iter1,
                                             const struct json_object_iterator *iter2);
```

### 10. `json_object_iter_end(const struct json_object *)` — 새로 실행될 수 있는 코드 영역 7개
```
/** Retrieves the iterator that represents the position beyond the
 *  last pair of the given JSON Object instance.
 *
 *  @warning Do NOT write code that assumes that the "end"
 *        iterator value is NULL, even if it is so in a
 *        particular instance of the implementation.
 *
 *  @note The reason we do not (and MUST NOT) provide
 *        "json_object_iter_is_end(json_object_iterator* iter)"
 *        type of API is because it would limit the underlying
 *        representation of name/value containment (or force us
 *        to add additional, otherwise unnecessary, fields to
 *        the iterator structure). The "end" iterator and the
 *        equality test method, on the other hand, permit us to
 *        cleanly abstract pretty much any reasonable underlying
 *        representation without burdening the iterator
 *        structure with unnecessary data.
 *
 *  @note For performance reasons, memorize the "end" iterator prior
 *        to any loop.
 *
 * @param obj JSON Object instance (MUST be of type json_object)
 *
 * @return json_object_iterator On return, the iterator refers
 *              to the "end" of the Object instance's pairs
 *              (i.e., NOT the last pair, but "beyond the last
 *              pair" value)
 */
JSON_EXPORT struct json_object_iterator json_object_iter_end(const struct json_object *obj);
/** Returns an iterator to the next pair, if any
 *
 * @warning 	Any modification of the fields of the object invalidates
 * 		the iterator, see the warning on json_object_iter_begin()
 *              for details.
 *
 * @param iter [IN/OUT] Pointer to iterator that references a
 *         name/value pair; MUST be a valid, non-end iterator.
 *         WARNING: bad things will happen if invalid or "end"
 *         iterator is passed. Upon return will contain the
 *         reference to the next pair if there is one; if there
 *         are no more pairs, will contain the "end" iterator
 *         value, which may be compared against the return value
 *         of json_object_iter_end() for the same JSON Object
 *         instance.
 */
```

## 참고: 기존 하네스 official.cc (고치지 마세요. include와 작성 방식만 참고)
```
#include <stdint.h>

#include <json.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
	const char *data1 = reinterpret_cast<const char *>(data);
	json_tokener *tok = json_tokener_new();
	json_object *obj = json_tokener_parse_ex(tok, data1, size);
	
	if (json_object_is_type(obj, json_type_object)) {
		json_object_object_foreach(obj, key, val) {
			(void)json_object_get_type(val);
			(void)json_object_get_string(val);
		}
	}
	(void)json_object_to_json_string_ext(obj, JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED);
	
	json_object_put(obj);
	json_tokener_free(tok);
	return 0;
}

```