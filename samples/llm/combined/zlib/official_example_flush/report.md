# LLM 하네스 수정 — zlib/official_example_flush, 제안 2,8

- 모델: `claude-sonnet-5-5`
- 제안: `deflateInit_(z_streamp, int, const char *, int)`의 2번째 인자 `level`를 하네스가 고정합니다(47행에서 항상 `-1`) (라이브러리 내부 `deflateInit2_`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 `3`, `4` 중에서만 고릅니다(54행, 60행) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 13개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 실패 | 0/13 | 2: 0/4, 8: 0/9 | LIBRARY(약) | 6197/4094 |
| 2 | 통과 | 8/13 | 2: 3/4, 8: 5/9 | - | 10312/4429 |
| 3 | 컴파일 실패 | -/- | - | - | 13900/5165 |

**채택 후보: 시도 2** (`harnesses/zlib/llm/official_example_flush_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -31,6 +31,9 @@
 static size_t dataLen;
 static alloc_func zalloc = NULL;
 static free_func zfree = NULL;
+static int g_level = Z_DEFAULT_COMPRESSION; // [gapfuzz-llm] 퍼저 입력에서 고른 압축 level 보관
+static int g_flush1 = Z_FULL_FLUSH;         // [gapfuzz-llm] 퍼저 입력에서 고른 첫 번째 flush 보관
+static int g_flush2 = Z_FINISH;             // [gapfuzz-llm] 퍼저 입력에서 고른 두 번째 flush 보관
 
 /* ===========================================================================
  * Test deflate() with full flush
@@ -44,21 +47,27 @@
   c_stream.zfree = zfree;
   c_stream.opaque = (void *)0;
 
-  err = deflateInit(&c_stream, Z_DEFAULT_COMPRESSION);
+  err = deflateInit(&c_stream, g_level); // [gapfuzz-llm] level을 -1 고정 대신 퍼저 입력값(범위 밖 포함)으로 사용
   CHECK_ERR(err, "deflateInit");
 
   c_stream.next_in = (Bytef *)data;
   c_stream.next_out = compr;
   c_stream.avail_in = 3;
   c_stream.avail_out = (unsigned int)*comprLen;
-  err = deflate(&c_stream, Z_FULL_FLUSH);
+  err = deflate(&c_stream, g_flush1); // [gapfuzz-llm] flush를 퍼저 입력에서 고른 값(범위 밖 포함)으로 사용
+  if (err != Z_OK) { // [gapfuzz-llm] 오류로 일찍 반환할 때 스트림 누수 방지
+    deflateEnd(&c_stream); // [gapfuzz-llm] 스트림 해제
+  }
   CHECK_ERR(err, "deflate flush 1");
 
   compr[3]++; /* force an error in first compressed block */
   c_stream.avail_in = len - 3;
 
-  err = deflate(&c_stream, Z_FINISH);
+  err = deflate(&c_stream, g_flush2); // [gapfuzz-llm] flush를 퍼저 입력에서 고른 값(범위 밖 포함)으로 사용
   if (err != Z_STREAM_END) {
+    if (err != Z_OK) { // [gapfuzz-llm] 오류로 일찍 반환할 때 스트림 누수 방지
+      deflateEnd(&c_stream); // [gapfuzz-llm] 스트림 해제
+    }
     CHECK_ERR(err, "deflate flush 2");
   }
   err = deflateEnd(&c_stream);
@@ -91,16 +100,23 @@
   d_stream.avail_out = (unsigned int)uncomprLen;
 
   err = inflate(&d_stream, Z_NO_FLUSH);
+  if (err != Z_OK) { // [gapfuzz-llm] deflate 실패로 압축 데이터가 비정상일 때 조기 반환 전에 해제해 누수 방지
+    inflateEnd(&d_stream); // [gapfuzz-llm] 스트림 해제
+  }
   CHECK_ERR(err, "inflate");
 
   d_stream.avail_in = (unsigned int)comprLen - 2; /* read all compressed data */
   err = inflateSync(&d_stream); /* but skip the damaged part */
+  if (err != Z_OK) { // [gapfuzz-llm] 조기 반환 전에 해제해 누수 방지
+    inflateEnd(&d_stream); // [gapfuzz-llm] 스트림 해제
+  }
   CHECK_ERR(err, "inflateSync");
 
   err = inflate(&d_stream, Z_FINISH);
   if (err != Z_DATA_ERROR && err != Z_STREAM_END) {
     fprintf(stderr, "inflate should report DATA_ERROR or Z_STREAM_END\n");
     /* v1.1.11= reports DATA_ERROR because of incorrect adler32. v1.1.12+ reports Z_STREAM END because it skips the adler32 check. */
+    inflateEnd(&d_stream); // [gapfuzz-llm] 조기 반환 전에 스트림 해제해 누수 방지
     return 0;
   }
   err = inflateEnd(&d_stream);
@@ -109,16 +125,26 @@
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
+  // [gapfuzz-llm] 앞 3바이트를 level/flush 선택용으로 쓰므로 최소 크기를 늘림
+  if (size <= 3 + 3 || size > kMaxSize)
     return 0;
+
+  g_level = (int)(d[0] % 13) - 2;  // [gapfuzz-llm] level -2..10 (-1 기본값, 범위 밖 값 포함)
+  g_flush1 = (int)(d[1] % 9) - 1;  // [gapfuzz-llm] flush -1..7 (3, 4 및 범위 밖 값 포함)
+  g_flush2 = (int)(d[2] % 9) - 1;  // [gapfuzz-llm] flush -1..7, 앞 바이트와 겹치지 않게 다음 바이트 사용
+  d += 3;                          // [gapfuzz-llm] 선택용 바이트를 건너뛰고 나머지를 원래대로 사용
+  size -= 3;                       // [gapfuzz-llm] 남은 입력 크기로 조정
+
+  comprLen = 100 + 2 * compressBound(size);
+  uncomprLen = size;
 
   data = d;
   dataLen = size;
```
