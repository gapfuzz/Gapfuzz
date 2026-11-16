# LLM 하네스 수정 — zlib/official_compress, 제안 1,2,3,4,8,9,10,11

- 모델: `claude-sonnet-5-5`
- 제안: `compress2(Bytef *, uLongf *, const Bytef *, uLong, int)`의 3번째 인자 `source`에 하네스가 null을 넘긴 적이 없습니다(29행) → nullptr도 넘겨 보세요
- 제안: `compress2(Bytef *, uLongf *, const Bytef *, uLong, int)`의 2번째 인자 `destLen`에 하네스가 null을 넘긴 적이 없습니다(29행) → nullptr도 넘겨 보세요
- 제안: `compress2(Bytef *, uLongf *, const Bytef *, uLong, int)`의 1번째 인자 `dest`에 하네스가 null을 넘긴 적이 없습니다(29행) → nullptr도 넘겨 보세요
- 제안: `uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 3번째 인자 `source`에 하네스가 null을 넘긴 적이 없습니다(30행, 59행) → nullptr도 넘겨 보세요
- 제안: `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 4번째 인자 `windowBits`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 제안: `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 6번째 인자 `strategy`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 제안: `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 3번째 인자 `method`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 제안: `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`deflateInit_`)에서만 불립니다. 내부 호출은 5번째 인자 `memLevel`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 겨냥한 분기: 18개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 15/18 | 1: 1/1, 2: 0/1, 3: 0/1, 4: 1/1, 8: 6/7, 9: 3/3, 10: 2/2, 11: 2/2 | LIBRARY(약) | 8572/4663 |
| 2 | 통과 | 16/18 | 1: 1/1, 2: 1/1, 3: 1/1, 4: 1/1, 8: 5/7, 9: 3/3, 10: 2/2, 11: 2/2 | - | 11548/4472 |
| 3 | 통과 | 18/18 | 1: 1/1, 2: 1/1, 3: 1/1, 4: 1/1, 8: 7/7, 9: 3/3, 10: 2/2, 11: 2/2 | - | 14807/3456 |

**채택 후보: 시도 3** (`harnesses/zlib/llm/official_compress_combined/try3.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 3
@@ -25,13 +25,26 @@
 
 static void check_compress_level(uint8_t *compr, size_t comprLen,
                                  uint8_t *uncompr, size_t uncomprLen,
-                                 int level) {
-  compress2(compr, &comprLen, data, dataLen, level);
-  uncompress(uncompr, &uncomprLen, compr, comprLen);
+                                 int level, unsigned cmode, unsigned umode) { // [gapfuzz-llm] null 인자 선택용 cmode/umode 파라미터 추가
+  /* cmode: 0 -> source=NULL, 1 -> destLen=NULL, 2 -> dest=NULL, 그 외 정상 */
+  int cerr;
+  if (cmode == 1) {
+    /* compress2 래퍼는 destLen을 먼저 역참조하므로, NULL 검사를 하는 compress2_z를 직접 호출 */
+    cerr = compress2_z(compr, NULL, data, dataLen, level);  // [gapfuzz-llm] destLen=nullptr를 실제 검사 지점(compress2_z)까지 전달
+  } else {
+    cerr = compress2(cmode == 2 ? NULL : compr,                       // [gapfuzz-llm] dest에 nullptr도 전달(destLen>0이라 32행 도달)
+                     &comprLen,
+                     cmode == 0 ? NULL : data, dataLen, level);       // [gapfuzz-llm] source에 nullptr도 전달
+  }
+  if (cmode == 1)
+    comprLen = 0;  // [gapfuzz-llm] destLen이 갱신되지 않았으므로 0으로 두어 이후 호출이 안전하게 함
+  uncompress(uncompr, &uncomprLen, umode == 0 ? NULL : compr, comprLen); // [gapfuzz-llm] uncompress source에 nullptr도 전달
 
   /* Make sure compress + uncompress gives back the input data. */
-  assert(dataLen == uncomprLen);
-  assert(0 == memcmp(data, uncompr, dataLen));
+  if (cmode > 2 && umode != 0 && cerr == Z_OK) { // [gapfuzz-llm] null 인자를 넣은 경우 왕복 검증은 건너뜀
+    assert(dataLen == uncomprLen);
+    assert(0 == memcmp(data, uncompr, dataLen));
+  }
 }
 
 #define put_byte(s, i, c) {s[i] = (unsigned char)(c);}
@@ -47,21 +60,23 @@
   put_byte(s, 1, (unsigned char)(header & 0xff));
 }
 
-static void check_decompress(uint8_t *compr, size_t comprLen, unsigned compression_method, unsigned flags) {
+static void check_decompress(uint8_t *compr, size_t comprLen, unsigned compression_method, unsigned flags, unsigned umode) { // [gapfuzz-llm] umode 파라미터 추가
   /* We need to write a valid zlib header of size two bytes. Copy the input data
      in a larger buffer. Do not modify the input data to avoid libFuzzer error:
      fuzz target overwrites its const input. */
   size_t copyLen = dataLen + 2;
   uint8_t *copy = (uint8_t *)malloc(copyLen);
+  if (!copy)
+    return;
   memcpy(copy + 2, data, dataLen);
   write_zlib_header(copy, compression_method, flags);
 
-  uncompress(compr, &comprLen, copy, copyLen);
+  uncompress(compr, &comprLen, umode == 0 ? NULL : copy, copyLen); // [gapfuzz-llm] source에 nullptr도 전달
   free(copy);
 }
 
 int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
-  if (size < 10 || size > 1024 * 1024)
+  if (size < 16 || size > 1024 * 1024) // [gapfuzz-llm] 추가 선택 바이트를 쓰므로 최소 크기를 늘림
     return 0;
 
   const int level = d[0] % 10;
@@ -74,6 +89,16 @@
   d++,size--;
   unsigned flags = d[0] & (2 << 4);
   d++,size--;
+
+  /* 앞쪽 바이트를 겹치지 않게 순서대로 배분 */
+  unsigned cmode = d[0] % 8;   // [gapfuzz-llm] compress2 null 인자 선택(0~2가 null, 각 1/8로 빈도 상향)
+  unsigned umode = d[1] % 16;  // [gapfuzz-llm] uncompress source null 선택(0만 null)
+  int init_wbits = (d[6] & 7) == 0 ? 8
+                   : (int)(d[2] % 50) - 17;  // [gapfuzz-llm] windowBits: 별도 바이트(d[6])로 1/8 확률 8 선택, 나머지는 d[2]로 -17..32 (gzip 범위 >15 복구)
+  int init_method = (d[3] & 7) == 0 ? (int)(d[3] >> 3) : Z_DEFLATED;  // [gapfuzz-llm] method: 대부분 Z_DEFLATED, 가끔 다른 값
+  int init_mem = (int)(d[4] % 12) - 1;  // [gapfuzz-llm] memLevel: -1..10 (8 포함)
+  int init_strategy = (int)(d[5] % 8) - 2;  // [gapfuzz-llm] strategy: -2..5 (유효 범위와 범위 밖 모두)
+  d += 7, size -= 7;  // [gapfuzz-llm] d[6]까지 소비하도록 7바이트 전진
 
   size_t comprLen = compressBound(size);
   size_t uncomprLen = size;
@@ -88,8 +113,15 @@
   if (!uncompr)
     goto err;
 
-  check_compress_level(compr, comprLen, uncompr, uncomprLen, level);
-  check_decompress(compr, comprLen, compression_method, flags);
+  check_compress_level(compr, comprLen, uncompr, uncomprLen, level, cmode, umode);
+  check_decompress(compr, comprLen, compression_method, flags, umode);
+
+  {
+    z_stream strm;  // [gapfuzz-llm] deflateInit2_를 직접 호출
+    memset(&strm, 0, sizeof(strm));
+    if (deflateInit2(&strm, level, init_method, init_wbits, init_mem, init_strategy) == Z_OK)  // [gapfuzz-llm] windowBits/method/memLevel/strategy를 입력에서 선택
+      deflateEnd(&strm);  // [gapfuzz-llm] 성공 시 해제
+  }
 
 err:
   free(compr);
```
