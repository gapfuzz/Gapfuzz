라이브러리: zlib
하네스 파일: official_example_small.c

## gapfuzz의 제안
`deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 `0`, `4` 중에서만 고릅니다(43행, 49행) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (8개)
- `deflate(z_streamp, int)` 991행, 조건 `deflateStateCheck(strm)`가 퍼징 중 한 번도 '참'이 되지 않음
```
  987  int ZEXPORT deflate(z_streamp strm, int flush) {
  988      int old_flush; /* value of flush param for previous deflate call */
  989      deflate_state *s;
  990  
  991>     if (deflateStateCheck(strm) || flush > Z_BLOCK || flush < 0) {
  992          return Z_STREAM_ERROR;
  993      }
  994      s = strm->state;
  995  
```
- `deflate(z_streamp, int)` 991행, 조건 `flush > Z_BLOCK`가 퍼징 중 한 번도 '참'이 되지 않음
```
  987  int ZEXPORT deflate(z_streamp strm, int flush) {
  988      int old_flush; /* value of flush param for previous deflate call */
  989      deflate_state *s;
  990  
  991>     if (deflateStateCheck(strm) || flush > Z_BLOCK || flush < 0) {
  992          return Z_STREAM_ERROR;
  993      }
  994      s = strm->state;
  995  
```
- `deflate(z_streamp, int)` 991행, 조건 `flush < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
  987  int ZEXPORT deflate(z_streamp strm, int flush) {
  988      int old_flush; /* value of flush param for previous deflate call */
  989      deflate_state *s;
  990  
  991>     if (deflateStateCheck(strm) || flush > Z_BLOCK || flush < 0) {
  992          return Z_STREAM_ERROR;
  993      }
  994      s = strm->state;
  995  
```
- `deflate(z_streamp, int)` 996행, 조건 `strm->next_out == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  992          return Z_STREAM_ERROR;
  993      }
  994      s = strm->state;
  995  
  996>     if (strm->next_out == Z_NULL ||
  997          (strm->avail_in != 0 && strm->next_in == Z_NULL) ||
  998          (s->status == FINISH_STATE && flush != Z_FINISH)) {
  999          ERR_RETURN(strm, Z_STREAM_ERROR);
 1000      }
```
- `deflate(z_streamp, int)` 998행, 조건 `flush != Z_FINISH`가 퍼징 중 한 번도 '참'이 되지 않음
```
  994      s = strm->state;
  995  
  996      if (strm->next_out == Z_NULL ||
  997          (strm->avail_in != 0 && strm->next_in == Z_NULL) ||
  998>         (s->status == FINISH_STATE && flush != Z_FINISH)) {
  999          ERR_RETURN(strm, Z_STREAM_ERROR);
 1000      }
 1001      if (strm->avail_out == 0) ERR_RETURN(strm, Z_BUF_ERROR);
 1002  
```
- `deflate(z_streamp, int)` 1024행, 조건 `RANK(flush) <= RANK`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1020      /* Make sure there is something to do and avoid duplicate consecutive
 1021       * flushes. For repeated and useless calls with Z_FINISH, we keep
 1022       * returning Z_STREAM_END instead of Z_BUF_ERROR.
 1023       */
 1024>     } else if (strm->avail_in == 0 && RANK(flush) <= RANK(old_flush) &&
 1025                 flush != Z_FINISH) {
 1026          ERR_RETURN(strm, Z_BUF_ERROR);
 1027      }
 1028  
```
- `deflate(z_streamp, int)` 1220행, 조건 `flush != Z_NO_FLUSH`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1216  
 1217      /* Start a new block or continue the current one.
 1218       */
 1219      if (strm->avail_in != 0 || s->lookahead != 0 ||
 1220>         (flush != Z_NO_FLUSH && s->status != FINISH_STATE)) {
 1221          block_state bstate;
 1222  
 1223          bstate = s->level == 0 ? deflate_stored(s, flush) :
 1224                   s->strategy == Z_HUFFMAN_ONLY ? deflate_huff(s, flush) :
```
- `deflate(z_streamp, int)` 1269행, 조건 `flush != Z_FINISH`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1265              }
 1266          }
 1267      }
 1268  
 1269>     if (flush != Z_FINISH) return Z_OK;
 1270      if (s->wrap <= 0) return Z_STREAM_END;
 1271  
 1272      /* Write the trailer */
 1273  #ifdef GZIP
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/zlib/example_small_fuzzer.c 그대로.
   2  #include <stdio.h>
   3  #include <stddef.h>
   4  #include <stdint.h>
   5  #include <string.h>
   6  #include <assert.h>
   7  #include <stdlib.h>
   8  #include <inttypes.h>
   9  #include "zlib.h"
  10  
  11  #define CHECK_ERR(err, msg) { \
  12      if (err != Z_OK) { \
  13          fprintf(stderr, "%s error: %d\n", msg, err); \
  14          return 0; \
  15      } \
  16  }
  17  
  18  static const uint8_t *data;
  19  static size_t dataLen;
  20  static alloc_func zalloc = NULL;
  21  static free_func zfree = NULL;
  22  
  23  /* ===========================================================================
  24   * Test deflate() with small buffers
  25   */
  26  int test_deflate(unsigned char *compr, size_t comprLen) {
  27    z_stream c_stream; /* compression stream */
  28    int err;
  29    unsigned long len = dataLen;
  30  
  31    c_stream.zalloc = zalloc;
  32    c_stream.zfree = zfree;
  33    c_stream.opaque = (void *)0;
  34  
  35    err = deflateInit(&c_stream, Z_DEFAULT_COMPRESSION);
  36    CHECK_ERR(err, "deflateInit");
  37  
  38    c_stream.next_in = (Bytef *)data;
  39    c_stream.next_out = compr;
  40  
  41    while (c_stream.total_in != len && c_stream.total_out < comprLen) {
  42      c_stream.avail_in = c_stream.avail_out = 1; /* force small buffers */
  43      err = deflate(&c_stream, Z_NO_FLUSH);
  44      CHECK_ERR(err, "deflate small 1");
  45    }
  46    /* Finish the stream, still forcing small buffers: */
  47    for (;;) {
  48      c_stream.avail_out = 1;
  49      err = deflate(&c_stream, Z_FINISH);
  50      if (err == Z_STREAM_END)
  51        break;
  52      CHECK_ERR(err, "deflate small 2");
  53    }
  54  
  55    err = deflateEnd(&c_stream);
  56    CHECK_ERR(err, "deflateEnd");
  57    return 0;
  58  }
  59  
  60  /* ===========================================================================
  61   * Test inflate() with small buffers
  62   */
  63  int test_inflate(unsigned char *compr, size_t comprLen, unsigned char *uncompr,
  64                    size_t uncomprLen) {
  65    int err;
  66    z_stream d_stream; /* decompression stream */
  67  
  68    d_stream.zalloc = zalloc;
  69    d_stream.zfree = zfree;
  70    d_stream.opaque = (void *)0;
  71  
  72    d_stream.next_in = compr;
  73    d_stream.avail_in = 0;
  74    d_stream.next_out = uncompr;
  75  
  76    err = inflateInit(&d_stream);
  77    CHECK_ERR(err, "inflateInit");
  78  
  79    while (d_stream.total_out < uncomprLen && d_stream.total_in < comprLen) {
  80      d_stream.avail_in = d_stream.avail_out = 1; /* force small buffers */
  81      err = inflate(&d_stream, Z_NO_FLUSH);
  82      if (err == Z_STREAM_END)
  83        break;
  84      CHECK_ERR(err, "inflate");
  85    }
  86  
  87    err = inflateEnd(&d_stream);
  88    CHECK_ERR(err, "inflateEnd");
  89  
  90    if (memcmp(uncompr, data, dataLen)) {
  91      fprintf(stderr, "bad inflate\n");
  92      return 0;
  93    }
  94    return 0;
  95  }
  96  
  97  int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
  98    size_t comprLen = compressBound(size);
  99    size_t uncomprLen = size;
 100    uint8_t *compr, *uncompr;
 101  
 102    /* Discard inputs larger than 1Mb. */
 103    static size_t kMaxSize = 1024 * 1024;
 104  
 105    if (size < 1 || size > kMaxSize)
 106      return 0;
 107  
 108    data = d;
 109    dataLen = size;
 110    compr = (uint8_t *)calloc(1, comprLen);
 111    uncompr = (uint8_t *)calloc(1, uncomprLen);
 112  
 113    test_deflate(compr, comprLen);
 114    test_inflate(compr, comprLen, uncompr, uncomprLen);
 115  
 116    free(compr);
 117    free(uncompr);
 118  
 119    /* This function must return 0. */
 120    return 0;
 121  }
```