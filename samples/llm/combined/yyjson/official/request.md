라이브러리: yyjson
하네스 파일: official.c

아래 제안 6개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`yyjson_read_opts(char *, size_t, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)`의 5번째 인자 `err`를 하네스가 고정합니다(39행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `yyjson_read_opts(char *, size_t, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)` 6273행, 조건 `!err`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 6269      yyjson_doc *doc;
 6270      u8 *hdr = NULL, *eof, *cur;
 6271  
 6272      /* validate input parameters */
 6273>     if (!err) err = &tmp_err;
 6274      if (unlikely(!dat)) return_err(0, INVALID_PARAMETER, "input data is NULL");
 6275      if (unlikely(!len)) return_err(0, INVALID_PARAMETER, "input length is 0");
 6276  
 6277      /* add 4-byte zero padding for input data if necessary */
```
- `yyjson_read_opts(char *, size_t, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)` 6331행, 조건 `err->code != YYJSON_READ_ERROR_MEMORY_ALLOCATION`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 6327      if (likely(doc)) {
 6328          memset(err, 0, sizeof(yyjson_read_err));
 6329      } else {
 6330          /* RFC 8259: JSON text MUST be encoded using UTF-8 */
 6331>         if (err->pos == 0 && err->code != YYJSON_READ_ERROR_MEMORY_ALLOCATION) {
 6332              if (is_utf8_bom(hdr)) err->msg = MSG_ERR_BOM;
 6333              else if (len >= 4 && is_utf32_bom(hdr)) err->msg = MSG_ERR_UTF32;
 6334              else if (len >= 2 && is_utf16_bom(hdr)) err->msg = MSG_ERR_UTF16;
 6335          }
```

## 제안 2
`yyjson_read_opts(char *, size_t, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)`의 4번째 인자 `alc`를 하네스가 고정합니다(39행에서 항상 같은 객체 `&FUZZ_ALC`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_read_opts(char *, size_t, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)` 6268행, 조건 `alc_ptr`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 6264      return NULL; \
 6265  } while (false)
 6266  
 6267      yyjson_read_err tmp_err;
 6268>     yyjson_alc alc = alc_ptr ? *alc_ptr : YYJSON_DEFAULT_ALC;
 6269      yyjson_doc *doc;
 6270      u8 *hdr = NULL, *eof, *cur;
 6271  
 6272      /* validate input parameters */
```

## 제안 3
`yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 3번째 인자 `alc`를 하네스가 고정합니다(41행에서 항상 같은 객체 `&FUZZ_ALC`) (라이브러리 내부 `write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 9744행, 조건 `alc_ptr`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 9740                          char *buf, usize *dat_len,
 9741                          yyjson_write_err *err) {
 9742      yyjson_write_err tmp_err;
 9743      usize tmp_dat_len;
 9744>     yyjson_alc alc = alc_ptr ? *alc_ptr : YYJSON_DEFAULT_ALC;
 9745      yyjson_val *root = constcast(yyjson_val *)val;
 9746  
 9747      if (!err) err = &tmp_err;
 9748      if (!dat_len) dat_len = &tmp_dat_len;
```

## 제안 4
`yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 5번째 인자 `err`를 하네스가 고정합니다(41행에서 항상 `0`) (라이브러리 내부 `write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 9747행, 조건 `!err`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 9743      usize tmp_dat_len;
 9744      yyjson_alc alc = alc_ptr ? *alc_ptr : YYJSON_DEFAULT_ALC;
 9745      yyjson_val *root = constcast(yyjson_val *)val;
 9746  
 9747>     if (!err) err = &tmp_err;
 9748      if (!dat_len) dat_len = &tmp_dat_len;
 9749  
 9750      if (unlikely(!root)) {
 9751          *dat_len = 0;
```

## 제안 5
`yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 4번째 인자 `len`를 하네스가 고정합니다(41행에서 항상 `0`) (라이브러리 내부 `write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` 9748행, 조건 `!dat_len`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 9744      yyjson_alc alc = alc_ptr ? *alc_ptr : YYJSON_DEFAULT_ALC;
 9745      yyjson_val *root = constcast(yyjson_val *)val;
 9746  
 9747      if (!err) err = &tmp_err;
 9748>     if (!dat_len) dat_len = &tmp_dat_len;
 9749  
 9750      if (unlikely(!root)) {
 9751          *dat_len = 0;
 9752          err->msg = "input JSON is NULL";
```

## 제안 9
`yyjson_doc_mut_copy(const yyjson_doc *, const yyjson_alc *)`의 2번째 인자 `alc`를 하네스가 고정합니다(40행에서 항상 같은 객체 `&FUZZ_ALC`) (라이브러리 내부 `yyjson_mut_doc_new`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yyjson_mut_doc_new(const yyjson_alc *)` 2669행, 조건 `!alc`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2665  }
 2666  
 2667  yyjson_mut_doc *yyjson_mut_doc_new(const yyjson_alc *alc) {
 2668      yyjson_mut_doc *doc;
 2669>     if (!alc) alc = &YYJSON_DEFAULT_ALC;
 2670      doc = (yyjson_mut_doc *)alc->malloc(alc->ctx, sizeof(yyjson_mut_doc));
 2671      if (!doc) return NULL;
 2672      memset(doc, 0, sizeof(yyjson_mut_doc));
 2673  
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: yyjson 저장소 fuzz/fuzzer.c (0.13.0, 커밋 6447536) 그대로.
   2  #include <stdlib.h>
   3  #include <string.h>
   4  #include <yyjson.h>
   5  
   6  /* Fuzzer-only allocator cap (not a library limit).
   7     OSS-Fuzz kills processes above ~2560MB RSS. Valid deep nesting with
   8     pretty-print can expand hugely; return NULL before the process is killed. */
   9  #ifndef YYJSON_FUZZ_ALLOC_LIMIT
  10  #   define YYJSON_FUZZ_ALLOC_LIMIT (512u * 1024u * 1024u)
  11  #endif
  12  
  13  static void *fuzz_malloc(void *ctx, size_t size) {
  14      (void)ctx;
  15      if (size > YYJSON_FUZZ_ALLOC_LIMIT) return NULL;
  16      return malloc(size);
  17  }
  18  
  19  static void *fuzz_realloc(void *ctx, void *ptr, size_t old_size, size_t size) {
  20      (void)ctx;
  21      (void)old_size;
  22      if (size > YYJSON_FUZZ_ALLOC_LIMIT) return NULL;
  23      return realloc(ptr, size);
  24  }
  25  
  26  static void fuzz_free(void *ctx, void *ptr) {
  27      (void)ctx;
  28      free(ptr);
  29  }
  30  
  31  static const yyjson_alc FUZZ_ALC = {
  32      fuzz_malloc, fuzz_realloc, fuzz_free, NULL
  33  };
  34  
  35  /*----------------------------------------------------------------------------*/
  36  
  37  static void test_with_flags(const uint8_t *data, size_t size,
  38                              yyjson_read_flag rflg, yyjson_write_flag wflg) {
  39      yyjson_doc *idoc = yyjson_read_opts((char *)data, size, rflg, &FUZZ_ALC, NULL);
  40      yyjson_mut_doc *mdoc = yyjson_doc_mut_copy(idoc, &FUZZ_ALC);
  41      char *ijson = yyjson_write_opts(idoc, wflg, &FUZZ_ALC, NULL, NULL);
  42      if (ijson) FUZZ_ALC.free(FUZZ_ALC.ctx, ijson);
  43      char *mjson = yyjson_mut_write_opts(mdoc, wflg, &FUZZ_ALC, NULL, NULL);
  44      if (mjson) FUZZ_ALC.free(FUZZ_ALC.ctx, mjson);
  45      yyjson_doc_free(idoc);
  46      yyjson_mut_doc_free(mdoc);
  47  }
  48  
  49  int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  50      test_with_flags(data, size,
  51                      YYJSON_READ_NOFLAG,
  52                      YYJSON_WRITE_NOFLAG);
  53      test_with_flags(data, size,
  54                      YYJSON_READ_JSON5,
  55                      YYJSON_WRITE_PRETTY |
  56                      YYJSON_WRITE_ESCAPE_UNICODE |
  57                      YYJSON_WRITE_ESCAPE_SLASHES |
  58                      YYJSON_WRITE_ALLOW_INF_AND_NAN);
  59      return 0;
  60  }
```