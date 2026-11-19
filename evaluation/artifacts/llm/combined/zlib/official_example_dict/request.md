라이브러리: zlib
하네스 파일: official_example_dict.c

아래 제안 8개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 고정합니다(80행에서 항상 `4`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (11개)
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
- `deflate(z_streamp, int)` 2119행, 조건 `flush == Z_NO_FLUSH`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2115           * for the longest run, plus one for the unrolled loop.
 2116           */
 2117          if (s->lookahead <= MAX_MATCH) {
 2118              fill_window(s);
 2119>             if (s->lookahead <= MAX_MATCH && flush == Z_NO_FLUSH) {
 2120                  return need_more;
 2121              }
 2122              if (s->lookahead == 0) break; /* flush the current block */
 2123          }
```

## 제안 3
`deflateSetDictionary(z_streamp, const Bytef *, uInt)`의 1번째 인자 `strm`를 하네스가 고정합니다(65행에서 항상 같은 객체 `&c_stream`) (라이브러리 내부 `deflateStateCheck`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `deflateSetDictionary(z_streamp, const Bytef *, uInt)` 539행, 조건 `strm == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `deflateSetDictionary(z_streamp, const Bytef *, uInt)` 543행, 조건 `s == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `deflateSetDictionary(z_streamp, const Bytef *, uInt)` 543행, 조건 `s->strm != strm`가 퍼징 중 한 번도 '참'이 되지 않음
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

## 제안 4
`inflate(z_streamp, int)`의 1번째 인자 `strm`를 하네스가 고정합니다(113행에서 항상 같은 객체 `&d_stream`) (라이브러리 내부 `inflateStateCheck`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `inflateResetKeep(z_streamp)` 90행, 조건 `strm == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   86  #include "inffast.h"
   87  
   88  local int inflateStateCheck(z_streamp strm) {
   89      struct inflate_state FAR *state;
   90>     if (strm == Z_NULL ||
   91          strm->zalloc == (alloc_func)0 || strm->zfree == (free_func)0)
   92          return 1;
   93      state = (struct inflate_state FAR *)strm->state;
   94      if (state == Z_NULL || state->strm != strm ||
```
- `inflateResetKeep(z_streamp)` 94행, 조건 `state == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   90      if (strm == Z_NULL ||
   91          strm->zalloc == (alloc_func)0 || strm->zfree == (free_func)0)
   92          return 1;
   93      state = (struct inflate_state FAR *)strm->state;
   94>     if (state == Z_NULL || state->strm != strm ||
   95          state->mode < HEAD || state->mode > SYNC)
   96          return 1;
   97      return 0;
   98  }
```
- `inflateResetKeep(z_streamp)` 94행, 조건 `state->strm != strm`가 퍼징 중 한 번도 '참'이 되지 않음
```
   90      if (strm == Z_NULL ||
   91          strm->zalloc == (alloc_func)0 || strm->zfree == (free_func)0)
   92          return 1;
   93      state = (struct inflate_state FAR *)strm->state;
   94>     if (state == Z_NULL || state->strm != strm ||
   95          state->mode < HEAD || state->mode > SYNC)
   96          return 1;
   97      return 0;
   98  }
```

## 제안 5
`deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`의 7번째 인자 `version`를 하네스가 고정합니다(62행에서 항상 `"1.3.2.1-motley"`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 394행, 조건 `version == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  390      deflate_state *s;
  391      int wrap = 1;
  392      static const char my_version[] = ZLIB_VERSION;
  393  
  394>     if (version == Z_NULL || version[0] != my_version[0] ||
  395          stream_size != sizeof(z_stream)) {
  396          return Z_VERSION_ERROR;
  397      }
  398      if (strm == Z_NULL) return Z_STREAM_ERROR;
```
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 394행, 조건 `version[0] != my_version[0]`가 퍼징 중 한 번도 '참'이 되지 않음
```
  390      deflate_state *s;
  391      int wrap = 1;
  392      static const char my_version[] = ZLIB_VERSION;
  393  
  394>     if (version == Z_NULL || version[0] != my_version[0] ||
  395          stream_size != sizeof(z_stream)) {
  396          return Z_VERSION_ERROR;
  397      }
  398      if (strm == Z_NULL) return Z_STREAM_ERROR;
```

## 제안 6
`inflateInit_(z_streamp, const char *, int)`의 2번째 인자 `version`를 하네스가 고정합니다(105행에서 항상 `"1.3.2.1-motley"`) (라이브러리 내부 `inflateInit2_`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `inflateInit2_(z_streamp, int, const char *, int)` 186행, 조건 `version == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  182                            const char *version, int stream_size) {
  183      int ret;
  184      struct inflate_state FAR *state;
  185  
  186>     if (version == Z_NULL || version[0] != ZLIB_VERSION[0] ||
  187          stream_size != (int)(sizeof(z_stream)))
  188          return Z_VERSION_ERROR;
  189      if (strm == Z_NULL) return Z_STREAM_ERROR;
  190      strm->msg = Z_NULL;                 /* in case we return an error */
```
- `inflateInit2_(z_streamp, int, const char *, int)` 186행, 조건 `version[0] != ZLIB_VERSION[0]`가 퍼징 중 한 번도 '참'이 되지 않음
```
  182                            const char *version, int stream_size) {
  183      int ret;
  184      struct inflate_state FAR *state;
  185  
  186>     if (version == Z_NULL || version[0] != ZLIB_VERSION[0] ||
  187          stream_size != (int)(sizeof(z_stream)))
  188          return Z_VERSION_ERROR;
  189      if (strm == Z_NULL) return Z_STREAM_ERROR;
  190      strm->msg = Z_NULL;                 /* in case we return an error */
```

## 제안 8
`deflateBound(z_streamp, uLong)`의 1번째 인자 `strm`를 하네스가 고정합니다(70행에서 항상 같은 객체 `&c_stream`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `deflateBound(z_streamp, uLong)` 937행, 조건 `(uLong)bound != bound`가 퍼징 중 한 번도 '참'이 되지 않음
```
  933      return bound < sourceLen ? (z_size_t)-1 : bound;
  934  }
  935  uLong ZEXPORT deflateBound(z_streamp strm, uLong sourceLen) {
  936      z_size_t bound = deflateBound_z(strm, sourceLen);
  937>     return (uLong)bound != bound ? (uLong)-1 : (uLong)bound;
  938  }
  939  
  940  /* =========================================================================
  941   * Put a short in the pending buffer. The 16-bit value is put in MSB order.
```

## 제안 9
`deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`의 1번째 인자 `strm`를 하네스가 고정합니다(62행에서 항상 같은 객체 `&c_stream`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` 398행, 조건 `strm == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  394      if (version == Z_NULL || version[0] != my_version[0] ||
  395          stream_size != sizeof(z_stream)) {
  396          return Z_VERSION_ERROR;
  397      }
  398>     if (strm == Z_NULL) return Z_STREAM_ERROR;
  399  
  400      strm->msg = Z_NULL;
  401      if (strm->zalloc == (alloc_func)0) {
  402  #ifdef Z_SOLO
```

## 제안 10
`inflateInit_(z_streamp, const char *, int)`의 1번째 인자 `strm`를 하네스가 고정합니다(105행에서 항상 같은 객체 `&d_stream`) (라이브러리 내부 `inflateInit2_`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `inflateInit2_(z_streamp, int, const char *, int)` 189행, 조건 `strm == Z_NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
  185  
  186      if (version == Z_NULL || version[0] != ZLIB_VERSION[0] ||
  187          stream_size != (int)(sizeof(z_stream)))
  188          return Z_VERSION_ERROR;
  189>     if (strm == Z_NULL) return Z_STREAM_ERROR;
  190      strm->msg = Z_NULL;                 /* in case we return an error */
  191      if (strm->zalloc == (alloc_func)0) {
  192  #ifdef Z_SOLO
  193          return Z_STREAM_ERROR;
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/zlib/example_dict_fuzzer.c 그대로.
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
  22  static size_t dictionaryLen = 0;
  23  static unsigned long dictId; /* Adler32 value of the dictionary */
  24  
  25  /* ===========================================================================
  26   * Test deflate() with preset dictionary
  27   */
  28  int test_dict_deflate(unsigned char **compr, size_t *comprLen)
  29  {
  30      z_stream c_stream; /* compression stream */
  31      int err;
  32      int level = data[0] % 11 - 1; /* [-1..9]
  33        compression levels
  34        #define Z_NO_COMPRESSION         0
  35        #define Z_BEST_SPEED             1
  36        #define Z_BEST_COMPRESSION       9
  37        #define Z_DEFAULT_COMPRESSION  (-1) */
  38  
  39      int method = Z_DEFLATED; /* The deflate compression method (the only one
  40                                  supported in this version) */
  41      int windowBits = 8 + data[0] % 8; /* The windowBits parameter is the base
  42        two logarithm of the window size (the size of the history buffer).  It
  43        should be in the range 8..15 for this version of the library. */
  44      int memLevel = 1 + data[0] % 9;   /* memLevel=1 uses minimum memory but is
  45        slow and reduces compression ratio; memLevel=9 uses maximum memory for
  46        optimal speed. */
  47      int strategy = data[0] % 5;       /* [0..4]
  48        #define Z_FILTERED            1
  49        #define Z_HUFFMAN_ONLY        2
  50        #define Z_RLE                 3
  51        #define Z_FIXED               4
  52        #define Z_DEFAULT_STRATEGY    0 */
  53  
  54      /* deflate would fail for no-compression or for speed levels. */
  55      if (level == 0 || level == 1)
  56        level = -1;
  57  
  58      c_stream.zalloc = zalloc;
  59      c_stream.zfree = zfree;
  60      c_stream.opaque = (void *)0;
  61  
  62      err = deflateInit2(&c_stream, level, method, windowBits, memLevel, strategy);
  63      CHECK_ERR(err, "deflateInit");
  64  
  65      err = deflateSetDictionary(
  66          &c_stream, (const unsigned char *)data, dictionaryLen);
  67      CHECK_ERR(err, "deflateSetDictionary");
  68  
  69      /* deflateBound does not provide enough space for low compression levels. */
  70      *comprLen = 100 + 2 * deflateBound(&c_stream, dataLen);
  71      *compr = (uint8_t *)calloc(1, *comprLen);
  72  
  73      dictId = c_stream.adler;
  74      c_stream.next_out = *compr;
  75      c_stream.avail_out = (unsigned int)(*comprLen);
  76  
  77      c_stream.next_in = (Bytef *)data;
  78      c_stream.avail_in = dataLen;
  79  
  80      err = deflate(&c_stream, Z_FINISH);
  81      if (err != Z_STREAM_END) {
  82          fprintf(stderr, "deflate dict should report Z_STREAM_END\n");
  83          return 0;
  84      }
  85      err = deflateEnd(&c_stream);
  86      CHECK_ERR(err, "deflateEnd");
  87      return 0;
  88  }
  89  
  90  /* ===========================================================================
  91   * Test inflate() with a preset dictionary
  92   */
  93  int test_dict_inflate(unsigned char *compr, size_t comprLen) {
  94    int err;
  95    z_stream d_stream; /* decompression stream */
  96    unsigned char *uncompr;
  97  
  98    d_stream.zalloc = zalloc;
  99    d_stream.zfree = zfree;
 100    d_stream.opaque = (void *)0;
 101  
 102    d_stream.next_in = compr;
 103    d_stream.avail_in = (unsigned int)comprLen;
 104  
 105    err = inflateInit(&d_stream);
 106    CHECK_ERR(err, "inflateInit");
 107  
 108    uncompr = (uint8_t *)calloc(1, dataLen);
 109    d_stream.next_out = uncompr;
 110    d_stream.avail_out = (unsigned int)dataLen;
 111  
 112    for (;;) {
 113      err = inflate(&d_stream, Z_NO_FLUSH);
 114      if (err == Z_STREAM_END)
 115        break;
 116      if (err == Z_NEED_DICT) {
 117        if (d_stream.adler != dictId) {
 118          fprintf(stderr, "unexpected dictionary");
 119          return 0;
 120        }
 121        err = inflateSetDictionary(
 122            &d_stream, (const unsigned char *)data, dictionaryLen);
 123      }
 124      CHECK_ERR(err, "inflate with dict");
 125    }
 126  
 127    err = inflateEnd(&d_stream);
 128    CHECK_ERR(err, "inflateEnd");
 129  
 130    if (memcmp(uncompr, data, dataLen)) {
 131      fprintf(stderr, "bad inflate with dict\n");
 132      return 0;
 133    }
 134  
 135    free(uncompr);
 136    return 0;
 137  }
 138  
 139  int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
 140    size_t comprLen = 0;
 141    uint8_t *compr;
 142  
 143    /* Discard inputs larger than 100Kb. */
 144    static size_t kMaxSize = 100 * 1024;
 145  
 146    if (size < 1 || size > kMaxSize)
 147      return 0;
 148  
 149    data = d;
 150    dataLen = size;
 151  
 152    /* Set up the contents of the dictionary.  The size of the dictionary is
 153       intentionally selected to be of unusual size.  To help cover more corner
 154       cases, the size of the dictionary is read from the input data.  */
 155    dictionaryLen = data[0];
 156    if (dictionaryLen > dataLen)
 157      dictionaryLen = dataLen;
 158  
 159    test_dict_deflate(&compr, &comprLen);
 160    test_dict_inflate(compr, comprLen);
 161  
 162    free(compr);
 163  
 164    /* This function must return 0. */
 165    return 0;
 166  }
```