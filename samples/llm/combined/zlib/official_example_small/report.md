# LLM 하네스 수정 — zlib/official_example_small, 제안 9

- 모델: `claude-sonnet-5-5`
- 제안: `deflate(z_streamp, int)`의 2번째 인자 `flush`를 하네스가 `0`, `4` 중에서만 고릅니다(43행, 49행) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 8개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 실패 | 1/8 | 9: 1/8 | LIBRARY(약) | 4500/3791 |
| 2 | 실패 | 5/8 | 9: 5/8 | HARNESS(약) | 7888/4785 |
| 3 | 통과 | 5/8 | 9: 5/8 | - | 12001/4817 |

**채택 후보: 시도 3** (`harnesses/zlib/llm/official_example_small_combined/try3.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 3
@@ -19,6 +19,12 @@
 static size_t dataLen;
 static alloc_func zalloc = NULL;
 static free_func zfree = NULL;
+static uint8_t flushSelA; // [gapfuzz-llm] 입력 첫 바이트로 첫 번째 루프의 flush 선택
+static uint8_t flushSelB; // [gapfuzz-llm] 입력 두 번째 바이트로 두 번째 루프의 flush 선택
+static uint8_t flushSelC; // [gapfuzz-llm] 입력 세 번째 바이트로 스트림 종료 후 추가 deflate 호출의 flush/next_out 선택
+
+/* [gapfuzz-llm] 유효한 flush 값 0~5와 범위 밖 값(-1, 6)을 모두 후보로 둠. 0(Z_NO_FLUSH)과 4(Z_FINISH)도 유지 */
+static const int kFlushValues[8] = {0, 1, 2, 3, 4, 5, -1, 6};
 
 /* ===========================================================================
  * Test deflate() with small buffers
@@ -26,6 +32,9 @@
 int test_deflate(unsigned char *compr, size_t comprLen) {
   z_stream c_stream; /* compression stream */
   int err;
+  int flush;
+  int first = 1;
+  int finished = 0; // [gapfuzz-llm] 스트림이 Z_STREAM_END로 끝났는지 기록
   unsigned long len = dataLen;
 
   c_stream.zalloc = zalloc;
@@ -40,19 +49,47 @@
 
   while (c_stream.total_in != len && c_stream.total_out < comprLen) {
     c_stream.avail_in = c_stream.avail_out = 1; /* force small buffers */
-    err = deflate(&c_stream, Z_NO_FLUSH);
-    CHECK_ERR(err, "deflate small 1");
+    err = deflate(&c_stream, kFlushValues[flushSelA & 7]); // [gapfuzz-llm] flush를 퍼저 입력에서 선택
+    if (err != Z_OK) { // [gapfuzz-llm] 오류가 나도 반환하지 않고 루프만 빠져나와 아래에서 Z_FINISH로 정상 종료 시도
+      break;
+    }
   }
   /* Finish the stream, still forcing small buffers: */
   for (;;) {
+    if (c_stream.total_out >= comprLen) // [gapfuzz-llm] flush마다 출력이 compressBound를 넘을 수 있어 compr 버퍼 오버플로 발생 → 용량 소진 시 중단
+      break;
     c_stream.avail_out = 1;
-    err = deflate(&c_stream, Z_FINISH);
-    if (err == Z_STREAM_END)
+    flush = first ? kFlushValues[flushSelB & 7] : Z_FINISH; // [gapfuzz-llm] 첫 호출만 입력 기반 flush, 이후엔 Z_FINISH로 종료 보장
+    err = deflate(&c_stream, flush); // [gapfuzz-llm] 고정 Z_FINISH 대신 선택된 flush 사용
+    if (err == Z_STREAM_END) {
+      finished = 1; // [gapfuzz-llm] 정상 종료 기록
       break;
-    CHECK_ERR(err, "deflate small 2");
+    }
+    if (first && (err == Z_STREAM_ERROR || err == Z_BUF_ERROR)) { // [gapfuzz-llm] 첫 호출의 거부(상태 불변)는 무시하고 Z_FINISH로 계속 진행
+      first = 0;
+      continue;
+    }
+    first = 0;
+    if (err != Z_OK) { // [gapfuzz-llm] 예기치 않은 오류 시 스트림 해제 후 종료(누수 방지)
+      fprintf(stderr, "deflate small 2 error: %d\n", err);
+      deflateEnd(&c_stream);
+      return 0;
+    }
+  }
+
+  /* [gapfuzz-llm] 종료된 스트림에 선택된 flush로 한 번 더 호출(문서상 오류 반환만 함). 일부는 next_out을 NULL로 하여 오류 경로 도달 */
+  if (finished) { // [gapfuzz-llm] 완전히 끝난 스트림에서만 호출: 대기 출력이 없어 버퍼 밖에 쓰지 않음
+    Bytef *saved_out = c_stream.next_out;
+    c_stream.avail_out = 1; // [gapfuzz-llm] avail_out 0이 아니게 유지
+    if (flushSelC & 0x80)
+      c_stream.next_out = Z_NULL; // [gapfuzz-llm] next_out == NULL은 문서상 Z_STREAM_ERROR를 돌려주는 호출
+    (void)deflate(&c_stream, kFlushValues[flushSelC & 7]); // [gapfuzz-llm] FINISH_STATE에서 flush != Z_FINISH 분기 유도
+    c_stream.next_out = saved_out; // [gapfuzz-llm] 해제 전에 원래 값 복원
   }
 
   err = deflateEnd(&c_stream);
+  if (!finished) // [gapfuzz-llm] 미완료 스트림은 deflateEnd가 Z_DATA_ERROR를 줄 수 있으나 메모리는 해제되므로 정상 처리
+    return 0;
   CHECK_ERR(err, "deflateEnd");
   return 0;
 }
@@ -81,7 +118,11 @@
     err = inflate(&d_stream, Z_NO_FLUSH);
     if (err == Z_STREAM_END)
       break;
-    CHECK_ERR(err, "inflate");
+    if (err != Z_OK) { // [gapfuzz-llm] 불완전한 압축 데이터로 오류가 나도 inflateEnd로 상태를 해제(누수 수정)
+      fprintf(stderr, "inflate error: %d\n", err);
+      inflateEnd(&d_stream);
+      return 0;
+    }
   }
 
   err = inflateEnd(&d_stream);
@@ -95,15 +136,24 @@
 }
 
 int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
-  size_t comprLen = compressBound(size);
-  size_t uncomprLen = size;
+  size_t comprLen;
+  size_t uncomprLen;
   uint8_t *compr, *uncompr;
 
   /* Discard inputs larger than 1Mb. */
   static size_t kMaxSize = 1024 * 1024;
 
-  if (size < 1 || size > kMaxSize)
+  if (size < 4 || size > kMaxSize) // [gapfuzz-llm] 앞 3바이트를 선택용으로 쓰므로 최소 크기를 4로 올림
     return 0;
+
+  flushSelA = d[0]; // [gapfuzz-llm] 첫 바이트: 첫 번째 flush 선택
+  flushSelB = d[1]; // [gapfuzz-llm] 둘째 바이트: 두 번째 flush 선택
+  flushSelC = d[2]; // [gapfuzz-llm] 셋째 바이트: 종료 후 추가 호출 선택
+  d += 3; // [gapfuzz-llm] 나머지 바이트는 기존처럼 압축 대상 데이터로 사용
+  size -= 3;
+
+  comprLen = compressBound(size);
+  uncomprLen = size;
 
   data = d;
   dataLen = size;
```
