# 호출 안 함 API 추가 — zlib/official

- 모델: `claude-sonnet-5-5`
- 수정 전: 공개 API 88개 중 호출 안 함 74개, 라인 24.51% · 분기 18.47%
- 추가를 요청한 API 10개: `compress`, `inflateBack`, `deflateCopy`, `deflateBound`, `deflateParams`, `inflateCopy`, `inflateSync`, `deflateSetDictionary`, `inflateBackInit_`, `adler32_combine`

| 시도 | 결과 | 실행된 API | 호출 안 함 | 라인 | 분기 | 사라진 API | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | 컴파일 실패 | -/- | - | - | - | 0 | - | 5256/10700 |
| 2 | 통과 | 10/10 | 52 | 67.81% | 58.87% | 0 | - | 10857/5259 |

수정 전 수치는 진단 때(기본 120초 × 1회), 시도별 수치는 검사 퍼징(짧음)의 중앙값이라 길이가 다릅니다. 정식 비교는 같은 조건의 긴 실험으로 하세요.

**채택: 시도 2** → `harnesses/zlib/official_ops.cc`. 사람이 읽고 쓰세요.

```diff
--- 수정 전
+++ 시도 2
@@ -1,4 +1,5 @@
-// OSS-Fuzz 공식 하네스: oss-fuzz/projects/zlib/zlib_uncompress_fuzzer.cc 그대로 (zlib 커밋 71747d1).
+// OSS-Fuzz 공식 하네스: oss-fuzz/projects/zlib/zlib_uncompress_fuzzer.cc (zlib 커밋 71747d1)
+// 위에 gapfuzz가 지목한 미호출 API 호출을 추가한 버전.
 // Copyright 2015 The Chromium Authors. All rights reserved.
 // Use of this source code is governed by a BSD-style license that can be
 // found in the LICENSE file.
@@ -7,16 +8,271 @@
 #include <stdint.h>
 #include <string.h>
 
+#include <algorithm>
+#include <vector>
+
 #include "zlib.h"
 
 static Bytef buffer[256 * 1024] = { 0 };
+
+// ---- 추가 코드 -------------------------------------------------------------
+
+namespace {
+
+const size_t kMaxExtraInput = 64 * 1024;       // 추가 블록이 쓰는 입력 상한
+const size_t kMaxOutTotal = 1024 * 1024;       // 출력 상한 (1MB)
+
+// 입력 끝쪽 바이트에서 선택값을 꺼낸다. 입력이 짧으면 0.
+// 앞쪽 바이트는 원래 하네스(uncompress)가 그대로 쓰므로 건드리지 않는다.
+inline uint8_t Sel(const uint8_t* data, size_t size, size_t i) {
+  return i < size ? data[size - 1 - i] : 0;
+}
+
+// inflateBack 콜백용 문맥
+struct BackCtx {
+  const uint8_t* p;
+  size_t n;
+  size_t pos;
+  size_t chunk;
+  size_t out_total;
+};
+
+// 입력 콜백: 퍼저 입력을 chunk 바이트씩 넘겨준다. 끝나면 0 반환.
+unsigned BackIn(void* desc, z_const unsigned char** buf) {
+  BackCtx* c = static_cast<BackCtx*>(desc);
+  if (c->pos >= c->n) return 0;
+  size_t take = std::min(c->chunk, c->n - c->pos);
+  // z_const가 비어 있으면 buf는 const가 아닌 포인터이므로 const를 벗겨서 넘긴다.
+  // inflateBack은 이 입력을 읽기만 한다.
+  *buf = const_cast<unsigned char*>(
+      reinterpret_cast<const unsigned char*>(c->p + c->pos));
+  c->pos += take;
+  return static_cast<unsigned>(take);
+}
+
+// 출력 콜백: 데이터는 버리고 총량만 센다. 1MB 넘으면 0이 아닌 값으로 중단.
+int BackOut(void* desc, unsigned char* /*buf*/, unsigned len) {
+  BackCtx* c = static_cast<BackCtx*>(desc);
+  c->out_total += len;
+  return c->out_total > kMaxOutTotal ? 1 : 0;
+}
+
+// [gapfuzz-ops] compress
+void ExerciseCompress(const uint8_t* data, size_t n) {
+  uLongf dest_len = compressBound(static_cast<uLong>(n));
+  std::vector<Bytef> out(dest_len);
+  // 반환값이 오류면 out은 더 쓰지 않는다.
+  if (compress(out.data(), &dest_len, data, static_cast<uLong>(n)) != Z_OK) {
+    return;
+  }
+}
+
+// [gapfuzz-ops] inflateBackInit_ / inflateBack (inflateBackEnd 포함)
+void ExerciseInflateBack(const uint8_t* data, size_t n, int window_bits,
+                         size_t chunk) {
+  std::vector<unsigned char> window(static_cast<size_t>(1) << window_bits);
+  z_stream s;
+  memset(&s, 0, sizeof(s));  // zalloc/zfree/opaque = Z_NULL
+  // inflateBackInit 매크로가 inflateBackInit_(version, sizeof(z_stream))을 부른다.
+  if (inflateBackInit(&s, window_bits, window.data()) != Z_OK) return;
+  BackCtx ctx = {data, n, 0, chunk ? chunk : 1, 0};
+  inflateBack(&s, BackIn, &ctx, BackOut, &ctx);
+  inflateBackEnd(&s);  // 초기화에 성공했으므로 반드시 해제
+}
+
+// [gapfuzz-ops] deflateBound / deflateSetDictionary / deflateCopy / deflateParams
+// 성공해서 스트림이 끝까지 만들어지면 compressed에 결과를 넣는다.
+void ExerciseDeflate(const uint8_t* data, size_t n, int level, int strategy,
+                     int window_bits, int mem_level, int new_level,
+                     int new_strategy, size_t split_sel, size_t dict_len,
+                     bool use_dict, std::vector<Bytef>* compressed) {
+  z_stream s;
+  memset(&s, 0, sizeof(s));
+  if (deflateInit2(&s, level, Z_DEFLATED, window_bits, mem_level,
+                   strategy) != Z_OK) {
+    return;
+  }
+  // 출력 버퍼 크기는 deflateBound 기반
+  uLong bound = deflateBound(&s, static_cast<uLong>(n));
+  size_t cap = static_cast<size_t>(bound) + 1024;
+  if (cap > kMaxOutTotal) {
+    deflateEnd(&s);
+    return;
+  }
+  std::vector<Bytef> out;
+  std::vector<Bytef> tmp;
+  try {
+    out.resize(cap);
+    tmp.resize(cap);
+  } catch (...) {
+    deflateEnd(&s);
+    return;
+  }
+
+  // 사전 설정: deflateInit 직후, deflate 호출 전에만 부른다.
+  if (use_dict && dict_len > 0) {
+    if (deflateSetDictionary(&s, data, static_cast<uInt>(dict_len)) != Z_OK) {
+      deflateEnd(&s);
+      return;
+    }
+  }
+
+  size_t half = n * split_sel / 255;
+  s.next_out = out.data();
+  s.avail_out = static_cast<uInt>(cap);
+  s.next_in = const_cast<Bytef*>(data);
+  s.avail_in = static_cast<uInt>(half);
+  int r = deflate(&s, Z_NO_FLUSH);
+  if (r == Z_STREAM_ERROR) {
+    deflateEnd(&s);
+    return;
+  }
+
+  // 중간 상태 복사: 성공했을 때만 복사본을 쓰고 끝내면 deflateEnd.
+  {
+    z_stream c;
+    memset(&c, 0, sizeof(c));
+    if (deflateCopy(&c, &s) == Z_OK) {
+      c.next_in = const_cast<Bytef*>(data + half);
+      c.avail_in = static_cast<uInt>(n - half);
+      c.next_out = tmp.data();
+      c.avail_out = static_cast<uInt>(cap);
+      deflate(&c, Z_FINISH);
+      deflateEnd(&c);
+    }
+  }
+
+  // 압축 파라미터 동적 변경 (Z_BUF_ERROR는 허용, Z_STREAM_ERROR면 중단)
+  if (deflateParams(&s, new_level, new_strategy) == Z_STREAM_ERROR) {
+    deflateEnd(&s);
+    return;
+  }
+
+  s.next_in = const_cast<Bytef*>(data + half);
+  s.avail_in = static_cast<uInt>(n - half);
+  bool done = false;
+  for (int i = 0; i < 64; i++) {  // 반복 상한 64
+    r = deflate(&s, Z_FINISH);
+    if (r == Z_STREAM_END) {
+      done = true;
+      break;
+    }
+    if (r != Z_OK && r != Z_BUF_ERROR) break;
+    if (s.avail_out == 0) break;  // 출력 버퍼가 가득 차면 포기
+  }
+  size_t produced = cap - s.avail_out;
+  deflateEnd(&s);
+  if (done) {
+    try {
+      compressed->assign(out.begin(), out.begin() + produced);
+    } catch (...) {
+      compressed->clear();
+    }
+  }
+}
+
+// [gapfuzz-ops] inflateCopy / inflateSync
+void ExerciseInflate(const uint8_t* src, size_t n, size_t split_sel) {
+  if (n == 0) return;
+  std::vector<Bytef> out1, out2;
+  try {
+    out1.resize(32 * 1024);
+    out2.resize(32 * 1024);
+  } catch (...) {
+    return;
+  }
+  z_stream s;
+  memset(&s, 0, sizeof(s));
+  if (inflateInit(&s) != Z_OK) return;
+
+  size_t half = n * split_sel / 255;
+  s.next_in = const_cast<Bytef*>(src);
+  s.avail_in = static_cast<uInt>(half);
+  s.next_out = out1.data();
+  s.avail_out = static_cast<uInt>(out1.size());
+  int r = inflate(&s, Z_NO_FLUSH);
+  if (r == Z_STREAM_ERROR) {
+    inflateEnd(&s);
+    return;
+  }
+
+  // 중간 상태 복사. 실패하면 복사본은 쓰지 않는다.
+  {
+    z_stream c;
+    memset(&c, 0, sizeof(c));
+    if (inflateCopy(&c, &s) == Z_OK) {
+      c.next_in = const_cast<Bytef*>(src + half);
+      c.avail_in = static_cast<uInt>(n - half);
+      c.next_out = out2.data();
+      c.avail_out = static_cast<uInt>(out2.size());
+      inflate(&c, Z_NO_FLUSH);
+      inflateEnd(&c);
+    }
+  }
+
+  // 남은 입력에서 full flush 지점 탐색
+  s.next_in = const_cast<Bytef*>(src + half);
+  s.avail_in = static_cast<uInt>(n - half);
+  inflateSync(&s);
+  inflateEnd(&s);
+}
+
+// [gapfuzz-ops] adler32_combine
+void ExerciseAdlerCombine(const uint8_t* data, size_t n, size_t split_sel) {
+  size_t k = n * split_sel / 255;
+  uLong a1 = adler32(1L, data, static_cast<uInt>(k));
+  uLong a2 = adler32(1L, data + k, static_cast<uInt>(n - k));
+  adler32_combine(a1, a2, static_cast<z_off_t>(n - k));
+}
+
+void ExerciseExtraApis(const uint8_t* data, size_t size) {
+  size_t n = std::min(size, kMaxExtraInput);
+
+  // 새 선택값은 모두 입력 끝쪽 바이트에서 꺼낸다.
+  int level = Sel(data, size, 0) % 10;
+  int strategy = Sel(data, size, 1) % 5;           // 0..4
+  int window_bits = 9 + Sel(data, size, 2) % 7;    // 9..15
+  int mem_level = 1 + Sel(data, size, 3) % 9;      // 1..9
+  int new_level = Sel(data, size, 4) % 10;
+  int new_strategy = Sel(data, size, 5) % 5;
+  int back_bits = 8 + Sel(data, size, 6) % 8;      // 8..15
+  size_t chunk = 1 + Sel(data, size, 7);           // 1..256
+  size_t dict_len = std::min<size_t>(n, Sel(data, size, 8) * 128u);
+  size_t split_sel = Sel(data, size, 9);           // 0..255
+  bool use_dict = (Sel(data, size, 10) & 1) != 0;
+
+  try {
+    ExerciseCompress(data, n);
+    ExerciseInflateBack(data, n, back_bits, chunk);
+
+    std::vector<Bytef> compressed;
+    ExerciseDeflate(data, n, level, strategy, window_bits, mem_level,
+                    new_level, new_strategy, split_sel, dict_len, use_dict,
+                    &compressed);
+
+    // deflate가 만든 유효한 스트림이 있으면 그것을, 없으면 입력 자체를 inflate에 쓴다.
+    if (!compressed.empty()) {
+      ExerciseInflate(compressed.data(), compressed.size(), split_sel);
+    } else {
+      ExerciseInflate(data, n, split_sel);
+    }
+
+    ExerciseAdlerCombine(data, n, split_sel);
+  } catch (...) {
+    // 메모리 부족 등 C++ 예외는 무시
+  }
+}
+
+}  // namespace
+
+// ---------------------------------------------------------------------------
 
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
   uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
-  if (Z_OK != uncompress(buffer, &buffer_length, data,
-                         static_cast<uLong>(size))) {
-    return 0;
-  }
+  // 원래 호출은 그대로 둔다. 실패해도 추가 블록이 실행되도록 조기 반환만 없앴다.
+  uncompress(buffer, &buffer_length, data, static_cast<uLong>(size));
+
+  ExerciseExtraApis(data, size);
   return 0;
 }
```
