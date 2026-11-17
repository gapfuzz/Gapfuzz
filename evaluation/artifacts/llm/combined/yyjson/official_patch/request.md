라이브러리: yyjson
하네스 파일: official_patch.c

아래 제안 10개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 2번째 인자 `flg`를 하네스가 고정합니다(42행에서 항상 `YYJSON_WRITE_NOFLAG`) (라이브러리 내부 `mut_write_root` → `mut_write_root_single` → `write_root_single`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 9276행, 조건 `newline`가 퍼징 중 한 번도 '참'이 되지 않음
```
 9272          default:
 9273              goto fail_type;
 9274      }
 9275  
 9276>     if (newline) *cur++ = '\n';
 9277      *cur = '\0';
 9278      *dat_len = (usize)(cur - hdr);
 9279      memset(err, 0, sizeof(yyjson_write_err));
 9280      return hdr;
```
- `yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 10127행, 조건 `newline`가 퍼징 중 한 번도 '참'이 되지 않음
```
10123          goto ctn_end;
10124      }
10125  
10126  doc_end:
10127>     if (newline) {
10128          incr_len(2);
10129          *(cur - 1) = '\n';
10130          cur++;
10131      }
```
- `yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 10416행, 조건 `flg & (YYJSON_WRITE_PRETTY | YYJSON_WRITE_PRETTY_TWO_SPACES)`가 퍼징 중 한 번도 '참'이 되지 않음
```
10412      }
10413  
10414      if (!unsafe_yyjson_is_ctn(root) || unsafe_yyjson_get_len(root) == 0) {
10415          return (char *)mut_write_root_single(root, flg, alc, buf, dat_len, err);
10416>     } else if (flg & (YYJSON_WRITE_PRETTY | YYJSON_WRITE_PRETTY_TWO_SPACES)) {
10417          return (char *)mut_write_root_pretty(root, estimated_val_num,
10418                                               flg, alc, buf, dat_len, err);
10419      } else {
10420          return (char *)mut_write_root_minify(root, estimated_val_num,
```

## 제안 4
`yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 3번째 인자 `alc`를 하네스가 고정합니다(42행에서 항상 같은 객체 `&FUZZ_ALC`) (라이브러리 내부 `mut_write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 10401행, 조건 `alc_ptr`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
10397                              char *buf, usize *dat_len,
10398                              yyjson_write_err *err) {
10399      yyjson_write_err tmp_err;
10400      usize tmp_dat_len;
10401>     yyjson_alc alc = alc_ptr ? *alc_ptr : YYJSON_DEFAULT_ALC;
10402      yyjson_mut_val *root = constcast(yyjson_mut_val *)val;
10403  
10404      if (!err) err = &tmp_err;
10405      if (!dat_len) dat_len = &tmp_dat_len;
```

## 제안 5
`yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 5번째 인자 `err`를 하네스가 고정합니다(42행에서 항상 `0`) (라이브러리 내부 `mut_write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 10404행, 조건 `!err`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
10400      usize tmp_dat_len;
10401      yyjson_alc alc = alc_ptr ? *alc_ptr : YYJSON_DEFAULT_ALC;
10402      yyjson_mut_val *root = constcast(yyjson_mut_val *)val;
10403  
10404>     if (!err) err = &tmp_err;
10405      if (!dat_len) dat_len = &tmp_dat_len;
10406  
10407      if (unlikely(!root)) {
10408          *dat_len = 0;
```

## 제안 6
`yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 4번째 인자 `len`를 하네스가 고정합니다(42행에서 항상 `0`) (라이브러리 내부 `mut_write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_mut_val_write_opts(const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 10405행, 조건 `!dat_len`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
10401      yyjson_alc alc = alc_ptr ? *alc_ptr : YYJSON_DEFAULT_ALC;
10402      yyjson_mut_val *root = constcast(yyjson_mut_val *)val;
10403  
10404      if (!err) err = &tmp_err;
10405>     if (!dat_len) dat_len = &tmp_dat_len;
10406  
10407      if (unlikely(!root)) {
10408          *dat_len = 0;
10409          err->msg = "input JSON is NULL";
```

## 제안 8
`yyjson_patch(yyjson_mut_doc *, const yyjson_val *, const yyjson_val *, yyjson_patch_err *)`의 4번째 인자 `err`를 하네스가 고정합니다(61행에서 항상 같은 객체 `&err`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_patch(yyjson_mut_doc *, const yyjson_val *, const yyjson_val *, yyjson_patch_err *)` 11127행, 조건 `!err`가 퍼징 중 한 번도 '참'이 되지 않음
```
11123      yyjson_mut_val *root;
11124      yyjson_val *obj;
11125      yyjson_arr_iter iter;
11126      yyjson_patch_err err_tmp;
11127>     if (!err) err = &err_tmp;
11128      memset(err, 0, sizeof(*err));
11129      memset(&iter, 0, sizeof(iter));
11130  
11131      if (unlikely(!doc || !orig || !patch)) {
```

## 제안 9
`yyjson_mut_patch(yyjson_mut_doc *, const yyjson_mut_val *, const yyjson_mut_val *, yyjson_patch_err *)`의 4번째 인자 `err`를 하네스가 고정합니다(77행에서 항상 같은 객체 `&err`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_mut_patch(yyjson_mut_doc *, const yyjson_mut_val *, const yyjson_mut_val *, yyjson_patch_err *)` 11246행, 조건 `!err`가 퍼징 중 한 번도 '참'이 되지 않음
```
11242                                   yyjson_patch_err *err) {
11243      yyjson_mut_val *root, *obj;
11244      yyjson_mut_arr_iter iter;
11245      yyjson_patch_err err_tmp;
11246>     if (!err) err = &err_tmp;
11247      memset(err, 0, sizeof(*err));
11248      memset(&iter, 0, sizeof(iter));
11249  
11250      if (unlikely(!doc || !orig || !patch)) {
```

## 제안 10
`yyjson_doc_get_root(const yyjson_doc *)`의 1번째 인자 `doc`에 하네스가 null을 넘긴 적이 없습니다(48행, 49행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_doc_get_root(const yyjson_doc *)` 5336행, 조건 `doc`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 5332   * MARK: - JSON Document API (Implementation)
 5333   *============================================================================*/
 5334  
 5335  yyjson_api_inline yyjson_val *yyjson_doc_get_root(const yyjson_doc *doc) {
 5336>     return doc ? doc->root : NULL;
 5337  }
 5338  
 5339  yyjson_api_inline size_t yyjson_doc_get_read_size(const yyjson_doc *doc) {
 5340      return doc ? doc->dat_read : 0;
```

## 제안 12
`yyjson_patch(yyjson_mut_doc *, const yyjson_val *, const yyjson_val *, yyjson_patch_err *)`의 1번째 인자 `doc`에 하네스가 null을 넘긴 적이 없습니다(61행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_mut_val_mut_copy(yyjson_mut_doc *, const yyjson_mut_val *)` 2832행, 조건 `doc`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 2828  }
 2829  
 2830  yyjson_mut_val *yyjson_mut_val_mut_copy(yyjson_mut_doc *doc,
 2831                                          const yyjson_mut_val *val) {
 2832>     if (doc && val) return unsafe_yyjson_mut_val_mut_copy(doc, val);
 2833      return NULL;
 2834  }
 2835  
 2836  /* Count the number of values and the total length of the strings. */
```

## 제안 13
`yyjson_obj_get(const yyjson_val *, const char *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`yyjson_patch`)에서만 불립니다. 내부 호출은 2번째 인자 `key`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_obj_get(const yyjson_val *, const char *)` 5707행, 조건 `key`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 5703  }
 5704  
 5705  yyjson_api_inline yyjson_val *yyjson_obj_get(const yyjson_val *obj,
 5706                                               const char *key) {
 5707>     return yyjson_obj_getn(obj, key, key ? strlen(key) : 0);
 5708  }
 5709  
 5710  yyjson_api_inline yyjson_val *yyjson_obj_getn(const yyjson_val *obj,
 5711                                                const char *_key,
```

## 제안 14
`yyjson_mut_obj_get(const yyjson_mut_val *, const char *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`yyjson_mut_patch`)에서만 불립니다. 내부 호출은 2번째 인자 `key`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_mut_obj_get(const yyjson_mut_val *, const char *)` 6986행, 조건 `key`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 6982  }
 6983  
 6984  yyjson_api_inline yyjson_mut_val *yyjson_mut_obj_get(const yyjson_mut_val *obj,
 6985                                                       const char *key) {
 6986>     return yyjson_mut_obj_getn(obj, key, key ? strlen(key) : 0);
 6987  }
 6988  
 6989  yyjson_api_inline yyjson_mut_val *yyjson_mut_obj_getn(const yyjson_mut_val *obj,
 6990                                                        const char *_key,
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: yyjson 저장소 fuzz/patch_fuzzer.c (0.13.0, 커밋 6447536) 그대로.
   2  #include <stdlib.h>
   3  #include <string.h>
   4  #include <yyjson.h>
   5  
   6  #define YYJSON_PATCH_MAX_INPUT_SIZE 8192
   7  
   8  /* Fuzzer-only allocator cap (not a library limit).
   9     OSS-Fuzz kills processes above ~2560MB RSS. Valid JSON Patch "copy" from
  10     the root can grow exponentially; return NULL before the process is killed. */
  11  #ifndef YYJSON_PATCH_FUZZ_ALLOC_LIMIT
  12  #   define YYJSON_PATCH_FUZZ_ALLOC_LIMIT (128u * 1024u * 1024u)
  13  #endif
  14  
  15  static void *fuzz_malloc(void *ctx, size_t size) {
  16      (void)ctx;
  17      if (size > YYJSON_PATCH_FUZZ_ALLOC_LIMIT) return NULL;
  18      return malloc(size);
  19  }
  20  
  21  static void *fuzz_realloc(void *ctx, void *ptr, size_t old_size, size_t size) {
  22      (void)ctx;
  23      (void)old_size;
  24      if (size > YYJSON_PATCH_FUZZ_ALLOC_LIMIT) return NULL;
  25      return realloc(ptr, size);
  26  }
  27  
  28  static void fuzz_free(void *ctx, void *ptr) {
  29      (void)ctx;
  30      free(ptr);
  31  }
  32  
  33  static const yyjson_alc FUZZ_ALC = {
  34      fuzz_malloc, fuzz_realloc, fuzz_free, NULL
  35  };
  36  
  37  /*----------------------------------------------------------------------------*/
  38  
  39  static void write_and_free_mut_val(yyjson_mut_val *val) {
  40      char *json;
  41      if (!val) return;
  42      json = yyjson_mut_val_write_opts(val, YYJSON_WRITE_NOFLAG, &FUZZ_ALC,
  43                                       NULL, NULL);
  44      if (json) FUZZ_ALC.free(FUZZ_ALC.ctx, json);
  45  }
  46  
  47  static void run_json_patch(yyjson_doc *base_doc, yyjson_doc *patch_doc) {
  48      yyjson_val *base_root = yyjson_doc_get_root(base_doc);
  49      yyjson_val *patch_root = yyjson_doc_get_root(patch_doc);
  50  
  51      if (base_root == NULL || patch_root == NULL) {
  52          return;
  53      }
  54  
  55      yyjson_mut_doc *result_doc = yyjson_mut_doc_new(&FUZZ_ALC);
  56      if (result_doc != NULL) {
  57          yyjson_patch_err err;
  58          memset(&err, 0, sizeof(err));
  59  
  60          yyjson_mut_val *result =
  61              yyjson_patch(result_doc, base_root, patch_root, &err);
  62          write_and_free_mut_val(result);
  63  
  64          yyjson_mut_doc_free(result_doc);
  65      }
  66  
  67      yyjson_mut_doc *mut_doc = yyjson_mut_doc_new(&FUZZ_ALC);
  68      if (mut_doc != NULL) {
  69          yyjson_mut_val *base_mut = yyjson_val_mut_copy(mut_doc, base_root);
  70          yyjson_mut_val *patch_mut = yyjson_val_mut_copy(mut_doc, patch_root);
  71  
  72          if (base_mut != NULL && patch_mut != NULL) {
  73              yyjson_patch_err err;
  74              memset(&err, 0, sizeof(err));
  75  
  76              yyjson_mut_val *result =
  77                  yyjson_mut_patch(mut_doc, base_mut, patch_mut, &err);
  78              write_and_free_mut_val(result);
  79          }
  80  
  81          yyjson_mut_doc_free(mut_doc);
  82      }
  83  }
  84  
  85  int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  86      if (data == NULL ||
  87          size < sizeof(uint16_t) + 1 ||
  88          size > YYJSON_PATCH_MAX_INPUT_SIZE) {
  89          return 0;
  90      }
  91  
  92      uint16_t split_len_raw;
  93      memcpy(&split_len_raw, data, sizeof(split_len_raw));
  94  
  95      data += sizeof(split_len_raw);
  96      size -= sizeof(split_len_raw);
  97  
  98      size_t base_size = split_len_raw % (size + 1);
  99      size_t patch_size = size - base_size;
 100  
 101      const uint8_t *base_data = data;
 102      const uint8_t *patch_data = data + base_size;
 103  
 104      yyjson_read_flag flags =
 105          YYJSON_READ_ALLOW_INVALID_UNICODE |
 106          YYJSON_READ_ALLOW_COMMENTS;
 107  
 108      yyjson_doc *base_doc =
 109          yyjson_read_opts((char *)(void *)base_data, base_size, flags,
 110                           &FUZZ_ALC, NULL);
 111      yyjson_doc *patch_doc =
 112          yyjson_read_opts((char *)(void *)patch_data, patch_size, flags,
 113                           &FUZZ_ALC, NULL);
 114  
 115      if (base_doc != NULL && patch_doc != NULL) {
 116          run_json_patch(base_doc, patch_doc);
 117      }
 118  
 119      yyjson_doc_free(base_doc);
 120      yyjson_doc_free(patch_doc);
 121  
 122      return 0;
 123  }
```