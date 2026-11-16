# LLM 하네스 수정 — zlib/official_example_dict, 제안 1,3,4,5,6,8,9,10

- 모델: `claude-sonnet-5-5`
- 제안: `deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 고정합니다(80행에서 항상 `4`) → 퍼저 입력으로 바꾸세요
- 제안: `deflateSetDictionary(z_streamp, const Bytef *, uInt)`의 1번째 인자 `strm`를 하네스가 고정합니다(65행에서 항상 같은 객체 `&c_stream`) (라이브러리 내부 `deflateStateCheck`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `inflate(z_streamp, int)`의 1번째 인자 `strm`를 하네스가 고정합니다(113행에서 항상 같은 객체 `&d_stream`) (라이브러리 내부 `inflateStateCheck`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`의 7번째 인자 `version`를 하네스가 고정합니다(62행에서 항상 `"1.3.2.1-motley"`) → 퍼저 입력으로 바꾸세요
- 제안: `inflateInit_(z_streamp, const char *, int)`의 2번째 인자 `version`를 하네스가 고정합니다(105행에서 항상 `"1.3.2.1-motley"`) (라이브러리 내부 `inflateInit2_`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `deflateBound(z_streamp, uLong)`의 1번째 인자 `strm`를 하네스가 고정합니다(70행에서 항상 같은 객체 `&c_stream`) → 퍼저 입력으로 바꾸세요
- 제안: `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`의 1번째 인자 `strm`를 하네스가 고정합니다(62행에서 항상 같은 객체 `&c_stream`) → 퍼저 입력으로 바꾸세요
- 제안: `inflateInit_(z_streamp, const char *, int)`의 1번째 인자 `strm`를 하네스가 고정합니다(105행에서 항상 같은 객체 `&d_stream`) (라이브러리 내부 `inflateInit2_`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 24개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 19/24 | 1: 9/11, 3: 2/3, 4: 2/3, 5: 2/2, 6: 2/2, 8: 0/1, 9: 1/1, 10: 1/1 | - | 9516/8677 |
| 2 | 통과 | 23/24 | 1: 11/11, 3: 3/3, 4: 3/3, 5: 2/2, 6: 2/2, 8: 0/1, 9: 1/1, 10: 1/1 | - | 15018/8603 |
| 3 | 통과 | 23/24 | 1: 11/11, 3: 3/3, 4: 3/3, 5: 2/2, 6: 2/2, 8: 0/1, 9: 1/1, 10: 1/1 | - | 21332/6833 |

**채택 후보: 시도 2** (`harnesses/zlib/llm/official_example_dict_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -15,8 +15,11 @@
     } \
 }
 
+#define NUM_CTL 8 // [gapfuzz-llm] 제어용 앞쪽 바이트를 8개로 늘려 새 선택값도 서로 겹치지 않게 배분
+
 static const uint8_t *data;
 static size_t dataLen;
+static uint8_t ctl[NUM_CTL]; // [gapfuzz-llm] 입력 앞쪽 제어 바이트 저장
 static alloc_func zalloc = NULL;
 static free_func zfree = NULL;
 static size_t dictionaryLen = 0;
@@ -28,6 +31,7 @@
 int test_dict_deflate(unsigned char **compr, size_t *comprLen)
 {
     z_stream c_stream; /* compression stream */
+    z_stream c_alt;    // [gapfuzz-llm] state->strm과 주소가 다른 스트림 복사본(s->strm != strm 분기용)
     int err;
     int level = data[0] % 11 - 1; /* [-1..9]
       compression levels
@@ -50,6 +54,16 @@
       #define Z_RLE                 3
       #define Z_FIXED               4
       #define Z_DEFAULT_STRATEGY    0 */
+    int flush = (int)(ctl[0] % 9) - 1; // [gapfuzz-llm] flush를 입력에서 선택(-1..7, 원래 값 Z_FINISH 포함, 범위 밖 값은 라이브러리가 오류 반환)
+    z_streamp initStrm = (ctl[1] % 16 == 0) ? NULL : &c_stream; // [gapfuzz-llm] deflateInit2_의 strm에 NULL도 가끔 전달
+    const char *initVer = (ctl[2] % 8 == 0) ? NULL :
+                          (ctl[2] % 8 == 1) ? "0.0.0" : ZLIB_VERSION; // [gapfuzz-llm] version에 NULL/잘못된 첫 글자/정상 값을 입력으로 선택
+    int dictSel = ctl[3] % 8;        // [gapfuzz-llm] deflateSetDictionary strm 선택(0:NULL, 1:복사본, 그 외:정상)
+    int boundSel = (ctl[3] >> 4) % 8; // [gapfuzz-llm] deflateBound strm 선택(0:NULL, 1:복사본, 그 외:정상)
+    int nullOutProbe = ctl[6] % 2;        // [gapfuzz-llm] next_out이 NULL인 deflate 호출(996행 분기) 여부를 입력에서 선택
+    int postEndProbe = (ctl[6] >> 1) % 2; // [gapfuzz-llm] deflateEnd 이후(state==NULL) 호출 여부를 입력에서 선택
+    int badDeflSel = (ctl[6] >> 2) % 4;   // [gapfuzz-llm] deflate에 넘길 비정상 strm 선택(0:NULL, 1:복사본, 그 외:호출 안 함)
+    z_streamp dictStrm, boundStrm;
 
     /* deflate would fail for no-compression or for speed levels. */
     if (level == 0 || level == 1)
@@ -59,15 +73,34 @@
     c_stream.zfree = zfree;
     c_stream.opaque = (void *)0;
 
-    err = deflateInit2(&c_stream, level, method, windowBits, memLevel, strategy);
+    err = deflateInit2_(initStrm, level, method, windowBits, memLevel, strategy,
+                        initVer, (int)sizeof(z_stream)); // [gapfuzz-llm] strm/version을 퍼저 입력으로 바꿔 호출
+    if (err != Z_OK && initStrm != &c_stream) { // [gapfuzz-llm] 비정상 인자 호출이 실패하면 정상 인자로 재시도해 원래 경로 유지
+        c_stream.zalloc = zalloc;
+        c_stream.zfree = zfree;
+        c_stream.opaque = (void *)0;
+        err = deflateInit2(&c_stream, level, method, windowBits, memLevel, strategy);
+    } else if (err != Z_OK && initVer != ZLIB_VERSION) { // [gapfuzz-llm] version만 잘못된 경우도 정상 값으로 재시도
+        err = deflateInit2(&c_stream, level, method, windowBits, memLevel, strategy);
+    }
     CHECK_ERR(err, "deflateInit");
 
+    c_alt = c_stream; // [gapfuzz-llm] 같은 state를 가리키지만 주소가 다른 복사본 생성(deflateEnd 대상 아님)
+    dictStrm = dictSel == 0 ? NULL : (dictSel == 1 ? &c_alt : &c_stream); // [gapfuzz-llm] 사전 설정용 strm을 입력으로 선택
+    boundStrm = boundSel == 0 ? NULL : (boundSel == 1 ? &c_alt : &c_stream); // [gapfuzz-llm] deflateBound용 strm을 입력으로 선택
+
+    if (dictStrm != &c_stream) // [gapfuzz-llm] 비정상 strm 호출은 오류만 반환하므로 결과를 무시하고 정상 호출을 이어서 수행
+        (void)deflateSetDictionary(
+            dictStrm, (const unsigned char *)data, dictionaryLen);
     err = deflateSetDictionary(
         &c_stream, (const unsigned char *)data, dictionaryLen);
+    if (err != Z_OK) { // [gapfuzz-llm] 오류 시 deflate 상태 누수를 막기 위해 해제
+        deflateEnd(&c_stream);
+    }
     CHECK_ERR(err, "deflateSetDictionary");
 
     /* deflateBound does not provide enough space for low compression levels. */
-    *comprLen = 100 + 2 * deflateBound(&c_stream, dataLen);
+    *comprLen = 100 + 2 * deflateBound(boundStrm, dataLen); // [gapfuzz-llm] deflateBound의 strm을 입력으로 선택
     *compr = (uint8_t *)calloc(1, *comprLen);
 
     dictId = c_stream.adler;
@@ -77,13 +110,36 @@
     c_stream.next_in = (Bytef *)data;
     c_stream.avail_in = dataLen;
 
-    err = deflate(&c_stream, Z_FINISH);
+    if (badDeflSel == 0) // [gapfuzz-llm] NULL strm으로 deflate를 호출해 deflateStateCheck 실패 경로를 열어줌(오류만 반환)
+        (void)deflate(NULL, flush);
+    else if (badDeflSel == 1) // [gapfuzz-llm] state->strm과 주소가 다른 복사본으로 호출(오류만 반환)
+        (void)deflate(&c_alt, flush);
+
+    if (nullOutProbe) { // [gapfuzz-llm] next_out이 NULL이면 deflate가 상태 변경 없이 Z_STREAM_ERROR를 반환하므로 안전하게 분기 확인
+        Bytef *savedOut = c_stream.next_out;
+        c_stream.next_out = Z_NULL;
+        (void)deflate(&c_stream, Z_NO_FLUSH);
+        c_stream.next_out = savedOut; // [gapfuzz-llm] 원래 출력 버퍼 복원
+    }
+
+    err = deflate(&c_stream, flush); // [gapfuzz-llm] flush를 입력에서 고른 값으로 사용
+    if (err != Z_STREAM_END) { // [gapfuzz-llm] 마무리를 위해 Z_FINISH로 이어서 호출해 원래 흐름 유지
+        err = deflate(&c_stream, Z_FINISH);
+    }
     if (err != Z_STREAM_END) {
         fprintf(stderr, "deflate dict should report Z_STREAM_END\n");
+        deflateEnd(&c_stream); // [gapfuzz-llm] 실패 경로에서 스트림 상태 해제
         return 0;
     }
     err = deflateEnd(&c_stream);
     CHECK_ERR(err, "deflateEnd");
+
+    if (postEndProbe) { // [gapfuzz-llm] deflateEnd 후 state가 NULL인 스트림으로 호출(오류만 반환, 해제된 메모리 접근 없음)
+        (void)deflate(&c_stream, flush);
+        (void)deflateSetDictionary(
+            &c_stream, (const unsigned char *)data, dictionaryLen);
+        (void)deflateBound(&c_stream, dataLen);
+    }
     return 0;
 }
 
@@ -93,7 +149,15 @@
 int test_dict_inflate(unsigned char *compr, size_t comprLen) {
   int err;
   z_stream d_stream; /* decompression stream */
+  z_stream d_alt;    // [gapfuzz-llm] state->strm과 주소가 다른 복사본
   unsigned char *uncompr;
+  z_streamp initStrm = (ctl[5] % 8 == 0) ? NULL : &d_stream; // [gapfuzz-llm] inflateInit_의 strm에 NULL도 가끔 전달
+  int verSel = (ctl[5] >> 4) % 8;
+  const char *initVer = verSel == 0 ? NULL :
+                        verSel == 1 ? "0.0.0" : ZLIB_VERSION; // [gapfuzz-llm] version을 입력으로 선택
+  int infSel = ctl[4] % 8; // [gapfuzz-llm] inflate strm 선택(0:NULL, 1:복사본, 그 외:정상)
+  int postEndProbe = ctl[7] % 2; // [gapfuzz-llm] inflateEnd 이후(state==NULL) 호출 여부를 입력에서 선택
+  z_streamp infStrm;
 
   d_stream.zalloc = zalloc;
   d_stream.zfree = zfree;
@@ -102,33 +166,60 @@
   d_stream.next_in = compr;
   d_stream.avail_in = (unsigned int)comprLen;
 
-  err = inflateInit(&d_stream);
+  err = inflateInit_(initStrm, initVer, (int)sizeof(z_stream)); // [gapfuzz-llm] strm/version을 퍼저 입력으로 바꿔 호출
+  if (err != Z_OK) { // [gapfuzz-llm] 비정상 인자로 실패하면 정상 인자로 재시도해 원래 경로 유지
+      d_stream.zalloc = zalloc;
+      d_stream.zfree = zfree;
+      d_stream.opaque = (void *)0;
+      d_stream.next_in = compr;
+      d_stream.avail_in = (unsigned int)comprLen;
+      err = inflateInit(&d_stream);
+  }
   CHECK_ERR(err, "inflateInit");
+
+  d_alt = d_stream; // [gapfuzz-llm] 같은 state를 가리키는 다른 주소의 복사본(inflateEnd 대상 아님)
+  infStrm = infSel == 0 ? NULL : (infSel == 1 ? &d_alt : &d_stream); // [gapfuzz-llm] inflate에 넘길 strm 선택
 
   uncompr = (uint8_t *)calloc(1, dataLen);
   d_stream.next_out = uncompr;
   d_stream.avail_out = (unsigned int)dataLen;
 
   for (;;) {
+    if (infStrm != &d_stream) // [gapfuzz-llm] 비정상 strm 호출은 오류만 반환하므로 결과를 무시하고 정상 호출 수행
+      (void)inflate(infStrm, Z_NO_FLUSH);
     err = inflate(&d_stream, Z_NO_FLUSH);
     if (err == Z_STREAM_END)
       break;
     if (err == Z_NEED_DICT) {
       if (d_stream.adler != dictId) {
         fprintf(stderr, "unexpected dictionary");
+        inflateEnd(&d_stream); // [gapfuzz-llm] 조기 반환 시 상태 해제
+        free(uncompr);         // [gapfuzz-llm] 조기 반환 시 버퍼 해제
         return 0;
       }
       err = inflateSetDictionary(
           &d_stream, (const unsigned char *)data, dictionaryLen);
     }
-    CHECK_ERR(err, "inflate with dict");
+    if (err != Z_OK) { // [gapfuzz-llm] 오류 경로에서 누수 방지를 위해 해제 후 반환
+      fprintf(stderr, "inflate with dict error: %d\n", err);
+      inflateEnd(&d_stream);
+      free(uncompr);
+      return 0;
+    }
   }
 
   err = inflateEnd(&d_stream);
+  if (err != Z_OK) { // [gapfuzz-llm] 오류 경로에서 버퍼 해제
+    free(uncompr);
+  }
   CHECK_ERR(err, "inflateEnd");
+
+  if (postEndProbe) // [gapfuzz-llm] inflateEnd 후 state가 NULL인 스트림으로 호출(오류만 반환, 해제된 메모리 접근 없음)
+    (void)inflate(&d_stream, Z_NO_FLUSH);
 
   if (memcmp(uncompr, data, dataLen)) {
     fprintf(stderr, "bad inflate with dict\n");
+    free(uncompr); // [gapfuzz-llm] 조기 반환 시 버퍼 해제
     return 0;
   }
 
@@ -138,16 +229,17 @@
 
 int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
   size_t comprLen = 0;
-  uint8_t *compr;
+  uint8_t *compr = NULL; // [gapfuzz-llm] 초기화되지 않은 포인터 free 방지
 
   /* Discard inputs larger than 100Kb. */
   static size_t kMaxSize = 100 * 1024;
 
-  if (size < 1 || size > kMaxSize)
+  if (size < NUM_CTL + 1 || size > kMaxSize) // [gapfuzz-llm] 제어 바이트 뒤에 데이터가 최소 1바이트 남도록 조건 조정
     return 0;
 
-  data = d;
-  dataLen = size;
+  memcpy(ctl, d, NUM_CTL); // [gapfuzz-llm] 앞쪽 바이트를 제어값으로 분리
+  data = d + NUM_CTL;      // [gapfuzz-llm] 나머지 바이트를 기존처럼 데이터/사전으로 사용
+  dataLen = size - NUM_CTL; // [gapfuzz-llm] 제어 바이트만큼 길이 감소
 
   /* Set up the contents of the dictionary.  The size of the dictionary is
      intentionally selected to be of unusual size.  To help cover more corner
```
