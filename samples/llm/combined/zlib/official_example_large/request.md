라이브러리: zlib
하네스 파일: official_example_large.c

아래 제안 4개를 **모두 한 하네스에** 적용하세요.

## 제안 2
`deflateParams(z_streamp, int, int)`의 1번째 인자 `strm`를 하네스가 고정합니다(55행에서 항상 같은 객체 `&c_stream`, 63행에서 항상 같은 객체 `&c_stream`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (4개)
- `deflateResetKeep(z_streamp)` 539행, 조건 `strm == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  535   * Check for a valid deflate stream state. Return 0 if ok, 1 if not.
  536   */
  537  local int deflateStateCheck(z_streamp strm) {
  538      deflate_state *s;
  539>     if (strm == Z_NULL ||
  540          strm->zalloc == (alloc_func)0 || strm->zfree == (free_func)0)
  541          return 1;
  542      s = strm->state;
  543      if (s == Z_NULL || s->strm != strm || (s->status != INIT_STATE &&
```
- `deflateResetKeep(z_streamp)` 543행, 조건 `s == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  539      if (strm == Z_NULL ||
  540          strm->zalloc == (alloc_func)0 || strm->zfree == (free_func)0)
  541          return 1;
  542      s = strm->state;
  543>     if (s == Z_NULL || s->strm != strm || (s->status != INIT_STATE &&
  544  #ifdef GZIP
  545                                             s->status != GZIP_STATE &&
  546  #endif
  547                                             s->status != EXTRA_STATE &&
```
- `deflateResetKeep(z_streamp)` 543행, 조건 `s->strm != strm`가 퍼징 중 한 번도 '참'이 되지 않음
```
  539      if (strm == Z_NULL ||
  540          strm->zalloc == (alloc_func)0 || strm->zfree == (free_func)0)
  541          return 1;
  542      s = strm->state;
  543>     if (s == Z_NULL || s->strm != strm || (s->status != INIT_STATE &&
  544  #ifdef GZIP
  545                                             s->status != GZIP_STATE &&
  546  #endif
  547                                             s->status != EXTRA_STATE &&
```
- `deflateParams(z_streamp, int, int)` 801행, 조건 `err == Z_STREAM_ERROR`가 퍼징 중 한 번도 '참'이 되지 않음
```
  797      if ((strategy != s->strategy || func != configuration_table[level].func) &&
  798          s->last_flush != -2) {
  799          /* Flush the last buffer: */
  800          int err = deflate(strm, Z_BLOCK);
  801>         if (err == Z_STREAM_ERROR)
  802              return err;
  803          if (strm->avail_in || (s->strstart - s->block_start) + s->lookahead)
  804              return Z_BUF_ERROR;
  805      }
```

## 제안 10
`deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 `0`, `4` 중에서만 고릅니다(47행, 59행, 66행, 69행) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (14개)
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
- `deflate(z_streamp, int)` 1245행, 조건 `flush == Z_PARTIAL_FLUSH`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1241               * one empty block.
 1242               */
 1243          }
 1244          if (bstate == block_done) {
 1245>             if (flush == Z_PARTIAL_FLUSH) {
 1246                  _tr_align(s);
 1247              } else if (flush != Z_BLOCK) { /* FULL_FLUSH or SYNC_FLUSH */
 1248                  _tr_stored_block(s, (char*)0, 0L, 0);
 1249                  /* For a full flush, this empty block will be recognized
```
- `deflate(z_streamp, int)` 1247행, 조건 `flush != Z_BLOCK`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1243          }
 1244          if (bstate == block_done) {
 1245              if (flush == Z_PARTIAL_FLUSH) {
 1246                  _tr_align(s);
 1247>             } else if (flush != Z_BLOCK) { /* FULL_FLUSH or SYNC_FLUSH */
 1248                  _tr_stored_block(s, (char*)0, 0L, 0);
 1249                  /* For a full flush, this empty block will be recognized
 1250                   * as a special marker by inflate_sync().
 1251                   */
```

## 제안 11
`deflateParams(z_streamp, int, int)`의 2번째 인자 `level`를 하네스가 `0`, `9` 중에서만 고릅니다(55행, 63행) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (5개)
- `deflateParams(z_streamp, int, int)` 790행, 조건 `level == Z_DEFAULT_COMPRESSION`가 퍼징 중 한 번도 '참'이 되지 않음
```
  786  
  787  #ifdef FASTEST
  788      if (level != 0) level = 1;
  789  #else
  790>     if (level == Z_DEFAULT_COMPRESSION) level = 6;
  791  #endif
  792      if (level < 0 || level > 9 || strategy < 0 || strategy > Z_FIXED) {
  793          return Z_STREAM_ERROR;
  794      }
```
- `deflateParams(z_streamp, int, int)` 792행, 조건 `level < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
  788      if (level != 0) level = 1;
  789  #else
  790      if (level == Z_DEFAULT_COMPRESSION) level = 6;
  791  #endif
  792>     if (level < 0 || level > 9 || strategy < 0 || strategy > Z_FIXED) {
  793          return Z_STREAM_ERROR;
  794      }
  795      func = configuration_table[s->level].func;
  796  
```
- `deflateParams(z_streamp, int, int)` 792행, 조건 `level > 9`가 퍼징 중 한 번도 '참'이 되지 않음
```
  788      if (level != 0) level = 1;
  789  #else
  790      if (level == Z_DEFAULT_COMPRESSION) level = 6;
  791  #endif
  792>     if (level < 0 || level > 9 || strategy < 0 || strategy > Z_FIXED) {
  793          return Z_STREAM_ERROR;
  794      }
  795      func = configuration_table[s->level].func;
  796  
```
- `deflateParams(z_streamp, int, int)` 797행, 조건 `func != configuration_table[level].func`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  793          return Z_STREAM_ERROR;
  794      }
  795      func = configuration_table[s->level].func;
  796  
  797>     if ((strategy != s->strategy || func != configuration_table[level].func) &&
  798          s->last_flush != -2) {
  799          /* Flush the last buffer: */
  800          int err = deflate(strm, Z_BLOCK);
  801          if (err == Z_STREAM_ERROR)
```
- `deflateParams(z_streamp, int, int)` 806행, 조건 `s->level != level`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  802              return err;
  803          if (strm->avail_in || (s->strstart - s->block_start) + s->lookahead)
  804              return Z_BUF_ERROR;
  805      }
  806>     if (s->level != level) {
  807          if (s->level == 0 && s->matches != 0) {
  808              if (s->matches == 1)
  809                  slide_hash(s);
  810              else
```

## 제안 12
`deflateParams(z_streamp, int, int)`의 3번째 인자 `strategy`를 하네스가 `0`, `1` 중에서만 고릅니다(55행, 63행) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `deflateParams(z_streamp, int, int)` 792행, 조건 `level < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
  788      if (level != 0) level = 1;
  789  #else
  790      if (level == Z_DEFAULT_COMPRESSION) level = 6;
  791  #endif
  792>     if (level < 0 || level > 9 || strategy < 0 || strategy > Z_FIXED) {
  793          return Z_STREAM_ERROR;
  794      }
  795      func = configuration_table[s->level].func;
  796  
```
- `deflateParams(z_streamp, int, int)` 792행, 조건 `strategy < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
  788      if (level != 0) level = 1;
  789  #else
  790      if (level == Z_DEFAULT_COMPRESSION) level = 6;
  791  #endif
  792>     if (level < 0 || level > 9 || strategy < 0 || strategy > Z_FIXED) {
  793          return Z_STREAM_ERROR;
  794      }
  795      func = configuration_table[s->level].func;
  796  
```
- `deflateParams(z_streamp, int, int)` 792행, 조건 `strategy > Z_FIXED`가 퍼징 중 한 번도 '참'이 되지 않음
```
  788      if (level != 0) level = 1;
  789  #else
  790      if (level == Z_DEFAULT_COMPRESSION) level = 6;
  791  #endif
  792>     if (level < 0 || level > 9 || strategy < 0 || strategy > Z_FIXED) {
  793          return Z_STREAM_ERROR;
  794      }
  795      func = configuration_table[s->level].func;
  796  
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/zlib/example_large_fuzzer.c 그대로.
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
  22  static unsigned int diff;
  23  
  24  /* ===========================================================================
  25   * Test deflate() with large buffers and dynamic change of compression level
  26   */
  27  int test_large_deflate(unsigned char *compr, size_t comprLen,
  28                          unsigned char *uncompr, size_t uncomprLen) {
  29    z_stream c_stream; /* compression stream */
  30    int err;
  31  
  32    c_stream.zalloc = zalloc;
  33    c_stream.zfree = zfree;
  34    c_stream.opaque = (void *)0;
  35  
  36    err = deflateInit(&c_stream, Z_BEST_COMPRESSION);
  37    CHECK_ERR(err, "deflateInit");
  38  
  39    c_stream.next_out = compr;
  40    c_stream.avail_out = (unsigned int)comprLen;
  41  
  42    /* At this point, uncompr is still mostly zeroes, so it should compress
  43     * very well:
  44     */
  45    c_stream.next_in = uncompr;
  46    c_stream.avail_in = (unsigned int)uncomprLen;
  47    err = deflate(&c_stream, Z_NO_FLUSH);
  48    CHECK_ERR(err, "deflate large 1");
  49    if (c_stream.avail_in != 0) {
  50      fprintf(stderr, "deflate not greedy\n");
  51      return 0;
  52    }
  53  
  54    /* Feed in already compressed data and switch to no compression: */
  55    deflateParams(&c_stream, Z_NO_COMPRESSION, Z_DEFAULT_STRATEGY);
  56    c_stream.next_in = compr;
  57    diff = (unsigned int)(c_stream.next_out - compr);
  58    c_stream.avail_in = diff;
  59    err = deflate(&c_stream, Z_NO_FLUSH);
  60    CHECK_ERR(err, "deflate large 2");
  61  
  62    /* Switch back to compressing mode: */
  63    deflateParams(&c_stream, Z_BEST_COMPRESSION, Z_FILTERED);
  64    c_stream.next_in = uncompr;
  65    c_stream.avail_in = (unsigned int)uncomprLen;
  66    err = deflate(&c_stream, Z_NO_FLUSH);
  67    CHECK_ERR(err, "deflate large 3");
  68  
  69    err = deflate(&c_stream, Z_FINISH);
  70    if (err != Z_STREAM_END) {
  71      fprintf(stderr, "deflate large should report Z_STREAM_END\n");
  72      return 0;
  73    }
  74    err = deflateEnd(&c_stream);
  75    CHECK_ERR(err, "deflateEnd");
  76    return 0;
  77  }
  78  
  79  /* ===========================================================================
  80   * Test inflate() with large buffers
  81   */
  82  int test_large_inflate(unsigned char *compr, size_t comprLen,
  83                          unsigned char *uncompr, size_t uncomprLen) {
  84    int err;
  85    z_stream d_stream; /* decompression stream */
  86  
  87    d_stream.zalloc = zalloc;
  88    d_stream.zfree = zfree;
  89    d_stream.opaque = (void *)0;
  90  
  91    d_stream.next_in = compr;
  92    d_stream.avail_in = (unsigned int)comprLen;
  93  
  94    err = inflateInit(&d_stream);
  95    CHECK_ERR(err, "inflateInit");
  96  
  97    for (;;) {
  98      d_stream.next_out = uncompr; /* discard the output */
  99      d_stream.avail_out = (unsigned int)uncomprLen;
 100      err = inflate(&d_stream, Z_NO_FLUSH);
 101      if (err == Z_STREAM_END)
 102        break;
 103      CHECK_ERR(err, "large inflate");
 104    }
 105  
 106    err = inflateEnd(&d_stream);
 107    CHECK_ERR(err, "inflateEnd");
 108  
 109    if (d_stream.total_out != 2 * uncomprLen + diff) {
 110      fprintf(stderr, "bad large inflate: %zu\n", d_stream.total_out);
 111      return 0;
 112    }
 113    return 0;
 114  }
 115  
 116  int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
 117    size_t comprLen = 100 + 3 * size;
 118    size_t uncomprLen = comprLen;
 119    uint8_t *compr, *uncompr;
 120  
 121    /* Discard inputs larger than 512Kb. */
 122    static size_t kMaxSize = 512 * 1024;
 123  
 124    if (size < 1 || size > kMaxSize)
 125      return 0;
 126  
 127    data = d;
 128    dataLen = size;
 129    compr = (uint8_t *)calloc(1, comprLen);
 130    uncompr = (uint8_t *)calloc(1, uncomprLen);
 131  
 132    test_large_deflate(compr, comprLen, uncompr, uncomprLen);
 133    test_large_inflate(compr, comprLen, uncompr, uncomprLen);
 134  
 135    free(compr);
 136    free(uncompr);
 137  
 138    /* This function must return 0. */
 139    return 0;
 140  }
```