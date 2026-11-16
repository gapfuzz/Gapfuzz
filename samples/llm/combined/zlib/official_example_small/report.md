# LLM 하네스 수정 — zlib/official_example_small, 제안 9

- 모델: `claude-sonnet-5-5`
- 제안: `deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 `0`, `4` 중에서만 고릅니다(43행, 49행) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 8개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 4/8 | 9: 4/8 | LIBRARY(약) | 4500/4507 |
| 2 | 통과 | 4/8 | 9: 4/8 | LIBRARY(약) | 7204/5142 |

**채택 후보: 시도 1** (`harnesses/zlib/llm/official_example_small_combined/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -20,10 +20,17 @@
 static alloc_func zalloc = NULL;
 static free_func zfree = NULL;
 
+/* 퍼저 입력 nibble(0~7)을 flush 값으로 바꾼다: 0~5는 그대로, 6은 범위 초과, 7은 음수 */
+static int pick_flush(unsigned n) { // [gapfuzz-llm] flush 값을 입력에서 고르기 위한 보조 함수
+  n &= 7;
+  if (n == 7) return -1;
+  return (int)n;
+}
+
 /* ===========================================================================
  * Test deflate() with small buffers
  */
-int test_deflate(unsigned char *compr, size_t comprLen) {
+int test_deflate(unsigned char *compr, size_t comprLen, int flush1, int flush2) { // [gapfuzz-llm] flush 인자를 받도록 확장
   z_stream c_stream; /* compression stream */
   int err;
   unsigned long len = dataLen;
@@ -40,16 +47,25 @@
 
   while (c_stream.total_in != len && c_stream.total_out < comprLen) {
     c_stream.avail_in = c_stream.avail_out = 1; /* force small buffers */
-    err = deflate(&c_stream, Z_NO_FLUSH);
-    CHECK_ERR(err, "deflate small 1");
+    err = deflate(&c_stream, flush1); // [gapfuzz-llm] flush를 입력에서 고른 값으로 사용
+    if (err != Z_OK) { // [gapfuzz-llm] 조기 종료 시 스트림 누수 방지
+      fprintf(stderr, "deflate small 1 error: %d\n", err);
+      deflateEnd(&c_stream);
+      return 0;
+    }
   }
   /* Finish the stream, still forcing small buffers: */
   for (;;) {
+    if (c_stream.total_out >= comprLen) break; // [gapfuzz-llm] 출력 버퍼 초과 쓰기 방지
     c_stream.avail_out = 1;
-    err = deflate(&c_stream, Z_FINISH);
+    err = deflate(&c_stream, flush2); // [gapfuzz-llm] flush를 입력에서 고른 값으로 사용
     if (err == Z_STREAM_END)
       break;
-    CHECK_ERR(err, "deflate small 2");
+    if (err != Z_OK) { // [gapfuzz-llm] 조기 종료 시 스트림 누수 방지
+      fprintf(stderr, "deflate small 2 error: %d\n", err);
+      deflateEnd(&c_stream);
+      return 0;
+    }
   }
 
   err = deflateEnd(&c_stream);
@@ -95,22 +111,27 @@
 }
 
 int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
+  /* Discard inputs larger than 1Mb. */
+  static size_t kMaxSize = 1024 * 1024;
+
+  if (size < 2 || size > kMaxSize) // [gapfuzz-llm] 첫 바이트를 flush 선택용으로 쓰므로 최소 크기 2
+    return 0;
+
+  int flush1 = pick_flush(d[0] & 0x0F);        // [gapfuzz-llm] 첫 바이트 하위 4비트로 첫 deflate의 flush 선택
+  int flush2 = pick_flush((d[0] >> 4) & 0x0F); // [gapfuzz-llm] 첫 바이트 상위 4비트로 마무리 deflate의 flush 선택
+  d += 1;    // [gapfuzz-llm] 선택용 바이트를 제외한 나머지를 압축 데이터로 사용
+  size -= 1; // [gapfuzz-llm] 위와 동일
+
   size_t comprLen = compressBound(size);
   size_t uncomprLen = size;
   uint8_t *compr, *uncompr;
-
-  /* Discard inputs larger than 1Mb. */
-  static size_t kMaxSize = 1024 * 1024;
-
-  if (size < 1 || size > kMaxSize)
-    return 0;
 
   data = d;
   dataLen = size;
   compr = (uint8_t *)calloc(1, comprLen);
   uncompr = (uint8_t *)calloc(1, uncomprLen);
 
-  test_deflate(compr, comprLen);
+  test_deflate(compr, comprLen, flush1, flush2); // [gapfuzz-llm] 선택한 flush 값 전달
   test_inflate(compr, comprLen, uncompr, uncomprLen);
 
   free(compr);
```
