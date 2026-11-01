# LLM 하네스 수정 — zlib/official, 제안 4

- 모델: `claude-sonnet-5-5`
- 제안: `inflate(z_streamp, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`uncompress2_z`)에서만 불립니다. 내부 호출은 2번째 인자 `flush`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 겨냥한 분기: 7개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 7/7 | - | 2721/3021 |

**채택 후보: 시도 1** (`harnesses/zlib/llm/official_fix4/try1.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -10,13 +10,34 @@
 #include "zlib.h"
 
 static Bytef buffer[256 * 1024] = { 0 };
+static Bytef inflate_out[256 * 1024] = { 0 };  // [gapfuzz-llm] inflate를 직접 호출할 때 쓸 출력 버퍼
 
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
   uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
   if (Z_OK != uncompress(buffer, &buffer_length, data,
                          static_cast<uLong>(size))) {
-    return 0;
+    // [gapfuzz-llm] 기존에는 여기서 바로 return 했지만, 실패한 입력도 inflate 직접 호출에 쓰도록 아래로 이어서 진행
+  }
+
+  if (size > 1) {  // [gapfuzz-llm] 첫 바이트는 flush 선택용, 나머지는 압축 스트림으로 사용
+    static const int kFlushModes[] = {Z_NO_FLUSH, Z_SYNC_FLUSH, Z_FINISH,
+                                      Z_BLOCK, Z_TREES};  // [gapfuzz-llm] inflate가 문서상 허용하는 flush 값들(기존 Z_NO_FLUSH 포함)
+    int flush = kFlushModes[data[0] % (sizeof(kFlushModes) / sizeof(kFlushModes[0]))];  // [gapfuzz-llm] 퍼저 입력으로 flush 값을 골라 Z_BLOCK/Z_TREES/Z_FINISH 분기 도달
+
+    z_stream strm;
+    memset(&strm, 0, sizeof(strm));
+    if (inflateInit(&strm) == Z_OK) {
+      strm.next_in = const_cast<Bytef*>(data + 1);
+      strm.avail_in = static_cast<uInt>(size - 1);
+      for (int iter = 0; iter < 1024; ++iter) {  // [gapfuzz-llm] Z_BLOCK/Z_TREES는 경계마다 반환하므로 반복 호출(무한 루프 방지용 상한)
+        strm.next_out = inflate_out;
+        strm.avail_out = static_cast<uInt>(sizeof(inflate_out));
+        int ret = inflate(&strm, flush);  // [gapfuzz-llm] 하네스가 inflate를 직접 호출하여 다양한 flush 전달
+        if (ret != Z_OK) break;
+      }
+      inflateEnd(&strm);  // [gapfuzz-llm] 할당된 inflate 상태 해제
+    }
   }
   return 0;
 }
```
