# LLM 하네스 수정 — zlib/official_example_flush, 제안 2,8

- 모델: `claude-sonnet-5-5`
- 제안: `deflateInit_(z_streamp, int, const char *, int)`의 2번째 인자 `level`를 하네스가 고정합니다(47행에서 항상 `-1`) (라이브러리 내부 `deflateInit2_`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 `3`, `4` 중에서만 고릅니다(54행, 60행) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 13개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 2/13 | 2: 2/4, 8: 0/9 | LIBRARY(약) | 6197/4453 |
| 2 | 통과 | 11/13 | 2: 3/4, 8: 8/9 | LIBRARY(약) | 9765/6606 |
| 3 | 통과 | 11/13 | 2: 3/4, 8: 8/9 | LIBRARY(약) | 14030/5744 |

**채택 후보: 시도 2** (`harnesses/zlib/llm/official_example_flush_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -31,6 +31,11 @@
 static size_t dataLen;
 static alloc_func zalloc = NULL;
 static free_func zfree = NULL;
+static int g_level = Z_DEFAULT_COMPRESSION; // [gapfuzz-llm] level을 퍼저 입력에서 받기 위한 전역 변수
+static int g_flush1 = Z_FULL_FLUSH; // [gapfuzz-llm] 첫 번째 flush 값을 퍼저 입력에서 받기 위한 전역 변수
+static int g_flush2 = Z_FINISH; // [gapfuzz-llm] 두 번째 flush 값을 퍼저 입력에서 받기 위한 전역 변수
+static int g_memLevel = 8; // [gapfuzz-llm] memLevel도 퍼저 입력에서 받음(기본 deflateInit과 같은 8도 계속 나옴)
+static unsigned g_mode = 1; // [gapfuzz-llm] 스트림 상태/버퍼/avail_in 변형을 고르는 입력 바이트
 
 /* ===========================================================================
  * Test deflate() with full flush
@@ -40,26 +45,46 @@
   int err;
   unsigned int len = dataLen;
 
+  if ((g_mode & 7) == 2) { // [gapfuzz-llm] 초기화되지 않은(0으로 채운) 스트림으로 deflate를 호출해 deflateStateCheck 참 분기 도달
+    z_stream bad;
+    memset(&bad, 0, sizeof(bad));
+    deflate(&bad, g_flush1); // 문서상 Z_STREAM_ERROR를 반환하는 정상적인 오류 경로
+    return 1;
+  }
+
   c_stream.zalloc = zalloc;
   c_stream.zfree = zfree;
   c_stream.opaque = (void *)0;
 
-  err = deflateInit(&c_stream, Z_DEFAULT_COMPRESSION);
-  CHECK_ERR(err, "deflateInit");
+  err = deflateInit2(&c_stream, g_level, Z_DEFLATED, MAX_WBITS, g_memLevel,
+                     Z_DEFAULT_STRATEGY); // [gapfuzz-llm] level과 memLevel을 고정값 대신 퍼저 입력으로 선택(deflateInit은 memLevel 8 고정)
+  if (err != Z_OK) { // [gapfuzz-llm] 잘못된 level/memLevel이면 초기화 실패이므로 이후 단계를 건너뜀
+    return 1;
+  }
 
   c_stream.next_in = (Bytef *)data;
   c_stream.next_out = compr;
-  c_stream.avail_in = 3;
+  c_stream.avail_in = ((g_mode & 7) == 3) ? 0 : 3; // [gapfuzz-llm] 가끔 avail_in 0으로 시작해 avail_in==0 분기 도달
   c_stream.avail_out = (unsigned int)*comprLen;
-  err = deflate(&c_stream, Z_FULL_FLUSH);
-  CHECK_ERR(err, "deflate flush 1");
+  if ((g_mode & 7) == 4) { // [gapfuzz-llm] 가끔 next_out을 NULL로 두어 오류 반환 분기 도달(deflate가 Z_STREAM_ERROR로 처리)
+    c_stream.next_out = Z_NULL;
+    c_stream.avail_out = 0;
+  }
+  err = deflate(&c_stream, g_flush1); // [gapfuzz-llm] flush 값을 퍼저 입력으로 선택
+  if (err != Z_OK) { // [gapfuzz-llm] 오류 시 스트림 누수를 막기 위해 deflateEnd 호출
+    fprintf(stderr, "deflate flush 1 error: %d\n", err);
+    deflateEnd(&c_stream);
+    return 1; // [gapfuzz-llm] 압축 결과가 없으므로 test_sync 건너뜀
+  }
 
   compr[3]++; /* force an error in first compressed block */
-  c_stream.avail_in = len - 3;
+  c_stream.avail_in = ((g_mode & 24) == 8) ? 0 : len - 3; // [gapfuzz-llm] 가끔 두 번째 avail_in을 0으로 해 avail_in==0 / 거짓 분기 도달
 
-  err = deflate(&c_stream, Z_FINISH);
-  if (err != Z_STREAM_END) {
-    CHECK_ERR(err, "deflate flush 2");
+  err = deflate(&c_stream, g_flush2); // [gapfuzz-llm] flush 값을 퍼저 입력으로 선택
+  if (err != Z_STREAM_END && err != Z_OK) { // [gapfuzz-llm] 오류 시 스트림 누수를 막기 위해 deflateEnd 호출
+    fprintf(stderr, "deflate flush 2 error: %d\n", err);
+    deflateEnd(&c_stream);
+    return 0;
   }
   err = deflateEnd(&c_stream);
   CHECK_ERR(err, "deflateEnd");
@@ -109,24 +134,36 @@
 }
 
 int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
-  size_t comprLen = 100 + 2 * compressBound(size);
-  size_t uncomprLen = size;
+  size_t comprLen;
+  size_t uncomprLen;
   uint8_t *compr, *uncompr;
 
   /* Discard inputs larger than 1Mb. */
   static size_t kMaxSize = 1024 * 1024;
 
   // This test requires at least 3 bytes of input data.
-  if (size <= 3 || size > kMaxSize)
+  // [gapfuzz-llm] 앞 5바이트를 파라미터용으로 쓰므로 최소 크기를 5바이트 늘림
+  if (size <= 8 || size > kMaxSize)
     return 0;
+
+  g_level = (int)(d[0] % 14) - 3; // [gapfuzz-llm] level: -3..10 (원래 값 -1, 유효 범위 0..9, 범위 밖 값 모두 포함)
+  g_flush1 = (int)(d[1] % 10) - 1; // [gapfuzz-llm] flush: -1..8 (기존 값 3,4와 나머지 값 모두 포함)
+  g_flush2 = (int)(d[2] % 10) - 1; // [gapfuzz-llm] flush: -1..8 (앞 바이트와 겹치지 않게 별도 바이트 사용)
+  g_memLevel = (int)(d[3] % 11); // [gapfuzz-llm] memLevel: 0..10 (원래 8, memLevel<1 및 >9 분기 포함)
+  g_mode = d[4]; // [gapfuzz-llm] 스트림 상태/버퍼/avail_in 변형 선택용 바이트
+  d += 5; // [gapfuzz-llm] 파라미터 바이트를 제외한 나머지를 원래 데이터로 사용
+  size -= 5; // [gapfuzz-llm] 파라미터 바이트만큼 크기 조정
+
+  comprLen = 100 + 2 * compressBound(size); // [gapfuzz-llm] 조정된 size 기준으로 계산
+  uncomprLen = size; // [gapfuzz-llm] 조정된 size 기준으로 계산
 
   data = d;
   dataLen = size;
   compr = (uint8_t *)calloc(1, comprLen);
   uncompr = (uint8_t *)calloc(1, uncomprLen);
 
-  test_flush(compr, &comprLen);
-  test_sync(compr, comprLen, uncompr, uncomprLen);
+  if (test_flush(compr, &comprLen) == 0) // [gapfuzz-llm] 초기화/압축 실패 시 test_sync를 건너뜀
+    test_sync(compr, comprLen, uncompr, uncomprLen);
 
   free(compr);
   free(uncompr);
```
