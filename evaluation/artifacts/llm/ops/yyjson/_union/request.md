라이브러리: yyjson
OSS-Fuzz 하네스 3개(official, official_patch, official_merge_patch)의 커버리지를 모두 합쳐도, 공개 API 405개 중 327개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `yyjson_incr_read(yyjson_incr_state *, size_t, yyjson_read_err *)` — 새로 실행될 수 있는 코드 영역 670개
```
*/
yyjson_api yyjson_doc *yyjson_incr_read(yyjson_incr_state *state, size_t len,
                                        yyjson_read_err *err);
/** Release the incremental read state and free the memory. */
```

### 2. `yyjson_mut_ptr_set(yyjson_mut_val *, const char *, yyjson_mut_val *, yyjson_mut_doc *)` — 새로 실행될 수 있는 코드 영역 481개
```
 */
yyjson_api_inline bool yyjson_mut_ptr_set(yyjson_mut_val *val,
                                          const char *ptr,
                                          yyjson_mut_val *new_val,
                                          yyjson_mut_doc *doc);
/**
 Set value by a JSON pointer.
 @param val The target JSON value.
 @param ptr The JSON pointer string (UTF-8, null-terminator is not required).
 @param len The length of `ptr` in bytes.
 @param new_val The value to be set, pass NULL to remove.
 @param doc Only used to create new values when needed.
 @return true if JSON pointer is valid and new value is set, false otherwise.
 @note The parent nodes will be created if they do not exist.
    If the target value already exists, it will be replaced by the new value.
 */
```

### 3. `yyjson_mut_write_number(const yyjson_mut_val *, char *)` — 새로 실행될 수 있는 코드 영역 222개
```
/** Same as `yyjson_write_number()`. */
yyjson_api_inline char *yyjson_mut_write_number(const yyjson_mut_val *val,
                                                char *buf) {
```

### 4. `yyjson_equals(const yyjson_val *, const yyjson_val *)` — 새로 실행될 수 있는 코드 영역 99개
```
        if the object level is too deep. */
yyjson_api_inline bool yyjson_equals(const yyjson_val *lhs,
                                     const yyjson_val *rhs);
/** Set the value to raw.
    Returns false if `val` is NULL or is object or array.
    @warning This will modify the `immutable` value, use with caution. */
```

### 5. `yyjson_mut_doc_imut_copy(const yyjson_mut_doc *, const yyjson_alc *)` — 새로 실행될 수 있는 코드 영역 81개
```
        if the object level is too deep. */
yyjson_api yyjson_doc *yyjson_mut_doc_imut_copy(const yyjson_mut_doc *doc,
                                                const yyjson_alc *alc);
/** Copies and returns a new immutable document from input,
    returns NULL on error. This makes a `deep-copy` on the mutable value.
    The returned document should be freed with `yyjson_doc_free()`.
    @note `mut_val` -> `imut_doc`.
    @warning This function is recursive and may cause a stack overflow
        if the object level is too deep. */
```

### 6. `yyjson_ptr_get_str(const yyjson_val *, const char *, const char **)` — 새로 실행될 수 있는 코드 영역 66개
```
 */
yyjson_api_inline bool yyjson_ptr_get_str(
    const yyjson_val *root, const char *ptr, const char **value) {
```

### 7. `yyjson_mut_ptr_replace(yyjson_mut_val *, const char *, yyjson_mut_val *)` — 새로 실행될 수 있는 코드 영역 61개
```
 */
yyjson_api_inline yyjson_mut_val *yyjson_mut_ptr_replace(
    yyjson_mut_val *val, const char *ptr, yyjson_mut_val *new_val);
/**
 Replace value by a JSON pointer.
 @param val The target JSON value.
 @param ptr The JSON pointer string (UTF-8, null-terminator is not required).
 @param len The length of `ptr` in bytes.
 @param new_val The new value to replace the old one.
 @return The old value that was replaced, or NULL if not found.
 */
```

### 8. `yyjson_locate_pos(const char *, size_t, size_t, size_t *, size_t *, size_t *)` — 새로 실행될 수 있는 코드 영역 42개
```
 */
yyjson_api bool yyjson_locate_pos(const char *str, size_t len, size_t pos,
                                  size_t *line, size_t *col, size_t *chr);
/*==============================================================================
 * MARK: - JSON Structure
 *============================================================================*/
```

### 9. `yyjson_mut_ptr_add(yyjson_mut_val *, const char *, yyjson_mut_val *, yyjson_mut_doc *)` — 새로 실행될 수 있는 코드 영역 36개
```
 */
yyjson_api_inline bool yyjson_mut_ptr_add(yyjson_mut_val *val,
                                          const char *ptr,
                                          yyjson_mut_val *new_val,
                                          yyjson_mut_doc *doc);
/**
 Add (insert) value by a JSON pointer.
 @param val The target JSON value.
 @param ptr The JSON pointer string (UTF-8, null-terminator is not required).
 @param len The length of `ptr` in bytes.
 @param doc Only used to create new values when needed.
 @param new_val The value to be added.
 @return true if JSON pointer is valid and new value is added, false otherwise.
 @note The parent nodes will be created if they do not exist.
 */
```

### 10. `yyjson_mut_ptr_remove(yyjson_mut_val *, const char *)` — 새로 실행될 수 있는 코드 영역 32개
```
 */
yyjson_api_inline yyjson_mut_val *yyjson_mut_ptr_remove(yyjson_mut_val *val,
                                                        const char *ptr);
/**
 Remove value by a JSON pointer.
 @param val The target JSON value.
 @param ptr The JSON pointer string (UTF-8, null-terminator is not required).
 @param len The length of `ptr` in bytes.
 @return The removed value, or NULL on error.
 */
```

## 참고: 기존 하네스 official.c (고치지 마세요. include와 작성 방식만 참고)
```
// OSS-Fuzz 하네스: yyjson 저장소 fuzz/fuzzer.c (0.13.0, 커밋 6447536) 그대로.
#include <stdlib.h>
#include <string.h>
#include <yyjson.h>

/* Fuzzer-only allocator cap (not a library limit).
   OSS-Fuzz kills processes above ~2560MB RSS. Valid deep nesting with
   pretty-print can expand hugely; return NULL before the process is killed. */
#ifndef YYJSON_FUZZ_ALLOC_LIMIT
#   define YYJSON_FUZZ_ALLOC_LIMIT (512u * 1024u * 1024u)
#endif

static void *fuzz_malloc(void *ctx, size_t size) {
    (void)ctx;
    if (size > YYJSON_FUZZ_ALLOC_LIMIT) return NULL;
    return malloc(size);
}

static void *fuzz_realloc(void *ctx, void *ptr, size_t old_size, size_t size) {
    (void)ctx;
    (void)old_size;
    if (size > YYJSON_FUZZ_ALLOC_LIMIT) return NULL;
    return realloc(ptr, size);
}

static void fuzz_free(void *ctx, void *ptr) {
    (void)ctx;
    free(ptr);
}

static const yyjson_alc FUZZ_ALC = {
    fuzz_malloc, fuzz_realloc, fuzz_free, NULL
};

/*----------------------------------------------------------------------------*/

static void test_with_flags(const uint8_t *data, size_t size,
                            yyjson_read_flag rflg, yyjson_write_flag wflg) {
    yyjson_doc *idoc = yyjson_read_opts((char *)data, size, rflg, &FUZZ_ALC, NULL);
    yyjson_mut_doc *mdoc = yyjson_doc_mut_copy(idoc, &FUZZ_ALC);
    char *ijson = yyjson_write_opts(idoc, wflg, &FUZZ_ALC, NULL, NULL);
    if (ijson) FUZZ_ALC.free(FUZZ_ALC.ctx, ijson);
    char *mjson = yyjson_mut_write_opts(mdoc, wflg, &FUZZ_ALC, NULL, NULL);
    if (mjson) FUZZ_ALC.free(FUZZ_ALC.ctx, mjson);
    yyjson_doc_free(idoc);
    yyjson_mut_doc_free(mdoc);
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    test_with_flags(data, size,
                    YYJSON_READ_NOFLAG,
                    YYJSON_WRITE_NOFLAG);
    test_with_flags(data, size,
                    YYJSON_READ_JSON5,
                    YYJSON_WRITE_PRETTY |
                    YYJSON_WRITE_ESCAPE_UNICODE |
                    YYJSON_WRITE_ESCAPE_SLASHES |
                    YYJSON_WRITE_ALLOW_INF_AND_NAN);
    return 0;
}

```