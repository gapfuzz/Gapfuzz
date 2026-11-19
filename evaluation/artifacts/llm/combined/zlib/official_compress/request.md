라이브러리: zlib
하네스 파일: official_compress.c

아래 제안 8개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`compress2(Bytef *, uLongf *, const Bytef *, uLong, int)`의 3번째 인자 `source`에 하네스가 null을 넘긴 적이 없습니다(29행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `compress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t, int)` 31행, 조건 `source == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   27      int err;
   28      const uInt max = (uInt)-1;
   29      z_size_t left;
   30  
   31>     if ((sourceLen > 0 && source == NULL) ||
   32          destLen == NULL || (*destLen > 0 && dest == NULL))
   33          return Z_STREAM_ERROR;
   34  
   35      left = *destLen;
```

## 제안 2
`compress2(Bytef *, uLongf *, const Bytef *, uLong, int)`의 2번째 인자 `destLen`에 하네스가 null을 넘긴 적이 없습니다(29행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `compress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t, int)` 32행, 조건 `destLen == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   28      const uInt max = (uInt)-1;
   29      z_size_t left;
   30  
   31      if ((sourceLen > 0 && source == NULL) ||
   32>         destLen == NULL || (*destLen > 0 && dest == NULL))
   33          return Z_STREAM_ERROR;
   34  
   35      left = *destLen;
   36      *destLen = 0;
```

## 제안 3
`compress2(Bytef *, uLongf *, const Bytef *, uLong, int)`의 1번째 인자 `dest`에 하네스가 null을 넘긴 적이 없습니다(29행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `compress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t, int)` 32행, 조건 `dest == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   28      const uInt max = (uInt)-1;
   29      z_size_t left;
   30  
   31      if ((sourceLen > 0 && source == NULL) ||
   32>         destLen == NULL || (*destLen > 0 && dest == NULL))
   33          return Z_STREAM_ERROR;
   34  
   35      left = *destLen;
   36      *destLen = 0;
```

## 제안 4
`uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 3번째 인자 `source`에 하네스가 null을 넘긴 적이 없습니다(30행, 59행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 36행, 조건 `source == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   32      int err;
   33      const uInt max = (uInt)-1;
   34      z_size_t len, left;
   35  
   36>     if (sourceLen == NULL || (*sourceLen > 0 && source == NULL) ||
   37          destLen == NULL || (*destLen > 0 && dest == NULL))
   38          return Z_STREAM_ERROR;
   39  
   40      len = *sourceLen;
```

## 제안 8
`deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 4번째 인자 `windowBits`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (7개)
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 422행, 조건 `windowBits < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
  418  #else
  419      if (level == Z_DEFAULT_COMPRESSION) level = 6;
  420  #endif
  421  
  422>     if (windowBits < 0) { /* suppress zlib wrapper */
  423          wrap = 0;
  424          if (windowBits < -15)
  425              return Z_STREAM_ERROR;
  426          windowBits = -windowBits;
```
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 429행, 조건 `windowBits > 15`가 퍼징 중 한 번도 '참'이 되지 않음
```
  425              return Z_STREAM_ERROR;
  426          windowBits = -windowBits;
  427      }
  428  #ifdef GZIP
  429>     else if (windowBits > 15) {
  430          wrap = 2;       /* write gzip wrapper instead */
  431          windowBits -= 16;
  432      }
  433  #endif
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
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 435행, 조건 `windowBits < 8`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 435행, 조건 `windowBits > 15`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 436행, 조건 `windowBits == 8`가 퍼징 중 한 번도 '참'이 되지 않음
```
  432      }
  433  #endif
  434      if (memLevel < 1 || memLevel > MAX_MEM_LEVEL || method != Z_DEFLATED ||
  435          windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||
  436>         strategy < 0 || strategy > Z_FIXED || (windowBits == 8 && wrap != 1)) {
  437          return Z_STREAM_ERROR;
  438      }
  439      if (windowBits == 8) windowBits = 9;  /* until 256-byte window bug fixed */
  440      s = (deflate_state *) ZALLOC(strm, 1, sizeof(deflate_state));
```
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 439행, 조건 `windowBits == 8`가 퍼징 중 한 번도 '참'이 되지 않음
```
  435          windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||
  436          strategy < 0 || strategy > Z_FIXED || (windowBits == 8 && wrap != 1)) {
  437          return Z_STREAM_ERROR;
  438      }
  439>     if (windowBits == 8) windowBits = 9;  /* until 256-byte window bug fixed */
  440      s = (deflate_state *) ZALLOC(strm, 1, sizeof(deflate_state));
  441      if (s == Z_NULL) return Z_MEM_ERROR;
  442      zmemzero(s, sizeof(deflate_state));
  443      strm->state = (struct internal_state FAR *)s;
```

## 제안 9
`deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 6번째 인자 `strategy`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
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
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 436행, 조건 `strategy < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
  432      }
  433  #endif
  434      if (memLevel < 1 || memLevel > MAX_MEM_LEVEL || method != Z_DEFLATED ||
  435          windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||
  436>         strategy < 0 || strategy > Z_FIXED || (windowBits == 8 && wrap != 1)) {
  437          return Z_STREAM_ERROR;
  438      }
  439      if (windowBits == 8) windowBits = 9;  /* until 256-byte window bug fixed */
  440      s = (deflate_state *) ZALLOC(strm, 1, sizeof(deflate_state));
```
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 436행, 조건 `strategy > Z_FIXED`가 퍼징 중 한 번도 '참'이 되지 않음
```
  432      }
  433  #endif
  434      if (memLevel < 1 || memLevel > MAX_MEM_LEVEL || method != Z_DEFLATED ||
  435          windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||
  436>         strategy < 0 || strategy > Z_FIXED || (windowBits == 8 && wrap != 1)) {
  437          return Z_STREAM_ERROR;
  438      }
  439      if (windowBits == 8) windowBits = 9;  /* until 256-byte window bug fixed */
  440      s = (deflate_state *) ZALLOC(strm, 1, sizeof(deflate_state));
```

## 제안 10
`deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 3번째 인자 `method`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
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
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 434행, 조건 `method != Z_DEFLATED`가 퍼징 중 한 번도 '참'이 되지 않음
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

## 제안 11
`deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 5번째 인자 `memLevel`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
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
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 434행, 조건 `memLevel > MAX_MEM_LEVEL`가 퍼징 중 한 번도 '참'이 되지 않음
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

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/zlib/compress_fuzzer.c 그대로.
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
  23  static const uint8_t *data;
  24  static size_t dataLen;
  25  
  26  static void check_compress_level(uint8_t *compr, size_t comprLen,
  27                                   uint8_t *uncompr, size_t uncomprLen,
  28                                   int level) {
  29    compress2(compr, &comprLen, data, dataLen, level);
  30    uncompress(uncompr, &uncomprLen, compr, comprLen);
  31  
  32    /* Make sure compress + uncompress gives back the input data. */
  33    assert(dataLen == uncomprLen);
  34    assert(0 == memcmp(data, uncompr, dataLen));
  35  }
  36  
  37  #define put_byte(s, i, c) {s[i] = (unsigned char)(c);}
  38  
  39  static void write_zlib_header(uint8_t *s, unsigned compression_method, unsigned flags) {
  40    unsigned int header = (Z_DEFLATED + ((flags)<<4)) << 8;
  41    header |= (compression_method << 6);
  42  
  43    header += 31 - (header % 31);
  44  
  45    /* s is guaranteed to be longer than 2 bytes. */
  46    put_byte(s, 0, (unsigned char)(header >> 8));
  47    put_byte(s, 1, (unsigned char)(header & 0xff));
  48  }
  49  
  50  static void check_decompress(uint8_t *compr, size_t comprLen, unsigned compression_method, unsigned flags) {
  51    /* We need to write a valid zlib header of size two bytes. Copy the input data
  52       in a larger buffer. Do not modify the input data to avoid libFuzzer error:
  53       fuzz target overwrites its const input. */
  54    size_t copyLen = dataLen + 2;
  55    uint8_t *copy = (uint8_t *)malloc(copyLen);
  56    memcpy(copy + 2, data, dataLen);
  57    write_zlib_header(copy, compression_method, flags);
  58  
  59    uncompress(compr, &comprLen, copy, copyLen);
  60    free(copy);
  61  }
  62  
  63  int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
  64    if (size < 10 || size > 1024 * 1024)
  65      return 0;
  66  
  67    const int level = d[0] % 10;
  68    d++,size--;
  69  
  70    //https://web.archive.org/web/20200220015003/http://www.onicos.com/staff/iz/formats/gzip.html
  71    unsigned compression_method = d[0] % 5;
  72    if (compression_method == 4)  //[4...7] are reserved
  73      compression_method = 8;
  74    d++,size--;
  75    unsigned flags = d[0] & (2 << 4);
  76    d++,size--;
  77  
  78    size_t comprLen = compressBound(size);
  79    size_t uncomprLen = size;
  80    uint8_t *compr = NULL, *uncompr = NULL;
  81  
  82    data = d;
  83    dataLen = size;
  84    compr = (uint8_t *)calloc(1, comprLen);
  85    if (!compr)
  86      goto err;
  87    uncompr = (uint8_t *)calloc(1, uncomprLen);
  88    if (!uncompr)
  89      goto err;
  90  
  91    check_compress_level(compr, comprLen, uncompr, uncomprLen, level);
  92    check_decompress(compr, comprLen, compression_method, flags);
  93  
  94  err:
  95    free(compr);
  96    free(uncompr);
  97  
  98    /* This function must return 0. */
  99    return 0;
 100  }
```