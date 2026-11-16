라이브러리: zlib
하네스 파일: official_example_flush.c

아래 제안 2개를 **모두 한 하네스에** 적용하세요.

## 제안 2
`deflateInit_(z_streamp, int, const char *, int)`의 2번째 인자 `level`를 하네스가 고정합니다(47행에서 항상 `-1`) (라이브러리 내부 `deflateInit2_`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (4개)
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 419행, 조건 `level == Z_DEFAULT_COMPRESSION`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  415  
  416  #ifdef FASTEST
  417      if (level != 0) level = 1;
  418  #else
  419>     if (level == Z_DEFAULT_COMPRESSION) level = 6;
  420  #endif
  421  
  422      if (windowBits < 0) { /* suppress zlib wrapper */
  423          wrap = 0;
```
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 434행, 조건 `memLevel < 1`가 퍼징 중 한 번도 '참'이 되지 않음
```
  430          wrap = 2;       /* write gzip wrapper instead */
  431          windowBits -= 16;
  432      }
  433  #endif
  434>     if (memLevel < 1 || memLevel > MAX_MEM_LEVEL || method != Z_DEFLATED ||
  435          windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||
  436          strategy < 0 || strategy > Z_FIXED || (windowBits == 8 && wrap != 1)) {
  437          return Z_STREAM_ERROR;
  438      }
```
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 435행, 조건 `level < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
  431          windowBits -= 16;
  432      }
  433  #endif
  434      if (memLevel < 1 || memLevel > MAX_MEM_LEVEL || method != Z_DEFLATED ||
  435>         windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||
  436          strategy < 0 || strategy > Z_FIXED || (windowBits == 8 && wrap != 1)) {
  437          return Z_STREAM_ERROR;
  438      }
  439      if (windowBits == 8) windowBits = 9;  /* until 256-byte window bug fixed */
```
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 435행, 조건 `level > 9`가 퍼징 중 한 번도 '참'이 되지 않음
```
  431          windowBits -= 16;
  432      }
  433  #endif
  434      if (memLevel < 1 || memLevel > MAX_MEM_LEVEL || method != Z_DEFLATED ||
  435>         windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||
  436          strategy < 0 || strategy > Z_FIXED || (windowBits == 8 && wrap != 1)) {
  437          return Z_STREAM_ERROR;
  438      }
  439      if (windowBits == 8) windowBits = 9;  /* until 256-byte window bug fixed */
```

## 제안 8
`deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 `3`, `4` 중에서만 고릅니다(54행, 60행) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (9개)
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
- `deflate(z_streamp, int)` 1024행, 조건 `strm->avail_in == 0`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `deflate(z_streamp, int)` 1219행, 조건 `strm->avail_in != 0`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1215  #endif
 1216  
 1217      /* Start a new block or continue the current one.
 1218       */
 1219>     if (strm->avail_in != 0 || s->lookahead != 0 ||
 1220          (flush != Z_NO_FLUSH && s->status != FINISH_STATE)) {
 1221          block_state bstate;
 1222  
 1223          bstate = s->level == 0 ? deflate_stored(s, flush) :
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
- `deflate(z_streamp, int)` 1247행, 조건 `flush != Z_BLOCK`가 퍼징 중 한 번도 '거짓'이 되지 않음
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

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/zlib/example_flush_fuzzer.c 그대로.
   2  /* Copyright 2022 Google LLC
   3  Licensed under the Apache License, Version 2.0 (the "License");
   4  you may not use this file except in compliance with the License.
   5  You may obtain a copy of the License at
   6        http://www.apache.org/licenses/LICENSE-2.0
   7  Unless required by applicable law or agreed to in writing, software
   8  distributed under the License is distributed on an "AS IS" BASIS,
   9  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  10  See the License for the specific language governing permissions and
  11  limitations under the License.
  12  */
  13  
  14  #include <stdio.h>
  15  #include <stddef.h>
  16  #include <stdint.h>
  17  #include <string.h>
  18  #include <assert.h>
  19  #include <stdlib.h>
  20  #include <inttypes.h>
  21  #include "zlib.h"
  22  
  23  #define CHECK_ERR(err, msg) { \
  24      if (err != Z_OK) { \
  25          fprintf(stderr, "%s error: %d\n", msg, err); \
  26          return 0; \
  27      } \
  28  }
  29  
  30  static const uint8_t *data;
  31  static size_t dataLen;
  32  static alloc_func zalloc = NULL;
  33  static free_func zfree = NULL;
  34  
  35  /* ===========================================================================
  36   * Test deflate() with full flush
  37   */
  38  int test_flush(unsigned char *compr, z_size_t *comprLen) {
  39    z_stream c_stream; /* compression stream */
  40    int err;
  41    unsigned int len = dataLen;
  42  
  43    c_stream.zalloc = zalloc;
  44    c_stream.zfree = zfree;
  45    c_stream.opaque = (void *)0;
  46  
  47    err = deflateInit(&c_stream, Z_DEFAULT_COMPRESSION);
  48    CHECK_ERR(err, "deflateInit");
  49  
  50    c_stream.next_in = (Bytef *)data;
  51    c_stream.next_out = compr;
  52    c_stream.avail_in = 3;
  53    c_stream.avail_out = (unsigned int)*comprLen;
  54    err = deflate(&c_stream, Z_FULL_FLUSH);
  55    CHECK_ERR(err, "deflate flush 1");
  56  
  57    compr[3]++; /* force an error in first compressed block */
  58    c_stream.avail_in = len - 3;
  59  
  60    err = deflate(&c_stream, Z_FINISH);
  61    if (err != Z_STREAM_END) {
  62      CHECK_ERR(err, "deflate flush 2");
  63    }
  64    err = deflateEnd(&c_stream);
  65    CHECK_ERR(err, "deflateEnd");
  66  
  67    *comprLen = (z_size_t)c_stream.total_out;
  68  
  69    return 0;
  70  }
  71  
  72  /* ===========================================================================
  73   * Test inflateSync()
  74   */
  75  int test_sync(unsigned char *compr, size_t comprLen, unsigned char *uncompr,
  76                 size_t uncomprLen) {
  77    int err;
  78    z_stream d_stream; /* decompression stream */
  79  
  80    d_stream.zalloc = zalloc;
  81    d_stream.zfree = zfree;
  82    d_stream.opaque = (void *)0;
  83  
  84    d_stream.next_in = compr;
  85    d_stream.avail_in = 2; /* just read the zlib header */
  86  
  87    err = inflateInit(&d_stream);
  88    CHECK_ERR(err, "inflateInit");
  89  
  90    d_stream.next_out = uncompr;
  91    d_stream.avail_out = (unsigned int)uncomprLen;
  92  
  93    err = inflate(&d_stream, Z_NO_FLUSH);
  94    CHECK_ERR(err, "inflate");
  95  
  96    d_stream.avail_in = (unsigned int)comprLen - 2; /* read all compressed data */
  97    err = inflateSync(&d_stream); /* but skip the damaged part */
  98    CHECK_ERR(err, "inflateSync");
  99  
 100    err = inflate(&d_stream, Z_FINISH);
 101    if (err != Z_DATA_ERROR && err != Z_STREAM_END) {
 102      fprintf(stderr, "inflate should report DATA_ERROR or Z_STREAM_END\n");
 103      /* v1.1.11= reports DATA_ERROR because of incorrect adler32. v1.1.12+ reports Z_STREAM END because it skips the adler32 check. */
 104      return 0;
 105    }
 106    err = inflateEnd(&d_stream);
 107    CHECK_ERR(err, "inflateEnd");
 108    return 0;
 109  }
 110  
 111  int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
 112    size_t comprLen = 100 + 2 * compressBound(size);
 113    size_t uncomprLen = size;
 114    uint8_t *compr, *uncompr;
 115  
 116    /* Discard inputs larger than 1Mb. */
 117    static size_t kMaxSize = 1024 * 1024;
 118  
 119    // This test requires at least 3 bytes of input data.
 120    if (size <= 3 || size > kMaxSize)
 121      return 0;
 122  
 123    data = d;
 124    dataLen = size;
 125    compr = (uint8_t *)calloc(1, comprLen);
 126    uncompr = (uint8_t *)calloc(1, uncomprLen);
 127  
 128    test_flush(compr, &comprLen);
 129    test_sync(compr, comprLen, uncompr, uncomprLen);
 130  
 131    free(compr);
 132    free(uncompr);
 133  
 134    /* This function must return 0. */
 135    return 0;
 136  }
```