라이브러리: zlib
하네스 파일: official.cc

아래 제안 3개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 2번째 인자 `destLen`를 하네스가 고정합니다(17행에서 항상 같은 객체 `&buffer_length`) (라이브러리 내부 `uncompress2` → `uncompress2_z`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 36행, 조건 `sourceLen == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 37행, 조건 `destLen == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   33      const uInt max = (uInt)-1;
   34      z_size_t len, left;
   35  
   36      if (sourceLen == NULL || (*sourceLen > 0 && source == NULL) ||
   37>         destLen == NULL || (*destLen > 0 && dest == NULL))
   38          return Z_STREAM_ERROR;
   39  
   40      len = *sourceLen;
   41      left = *destLen;
```
- `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 37행, 조건 `*destLen > 0`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
   33      const uInt max = (uInt)-1;
   34      z_size_t len, left;
   35  
   36      if (sourceLen == NULL || (*sourceLen > 0 && source == NULL) ||
   37>         destLen == NULL || (*destLen > 0 && dest == NULL))
   38          return Z_STREAM_ERROR;
   39  
   40      len = *sourceLen;
   41      left = *destLen;
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -14,6 +14,19 @@
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
   uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
+  if (size >= 1) {  // [gapfuzz-llm] 입력 첫 바이트를 destLen 선택용으로 사용하기 위해 확인
+    uint8_t selector = data[0];  // [gapfuzz-llm] 첫 바이트로 destLen을 원래 값으로 둘지 바꿀지 결정
+    data++;  // [gapfuzz-llm] 선택용 바이트를 소비하고 나머지를 압축 데이터로 사용
+    size--;  // [gapfuzz-llm] 소비한 만큼 입력 크기 감소
+    if ((selector & 1) && size >= 3) {  // [gapfuzz-llm] 홀수일 때만 destLen을 입력에서 가져와 원래 값(전체 버퍼)도 계속 나오게 함
+      uint32_t v = (static_cast<uint32_t>(data[0]) << 16) |
+                   (static_cast<uint32_t>(data[1]) << 8) |
+                   static_cast<uint32_t>(data[2]);  // [gapfuzz-llm] 입력 3바이트로 destLen 후보 값 생성
+      buffer_length = static_cast<uLongf>(v % (sizeof(buffer) + 1));  // [gapfuzz-llm] 0부터 버퍼 크기까지(0 포함)로 제한해 버퍼 오버플로 방지
+      data += 3;  // [gapfuzz-llm] destLen용으로 쓴 바이트 소비
+      size -= 3;  // [gapfuzz-llm] 소비한 만큼 입력 크기 감소
+    }
+  }
   if (Z_OK != uncompress(buffer, &buffer_length, data,
                          static_cast<uLong>(size))) {
     return 0;
```

## 제안 3
`uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 1번째 인자 `dest`에 하네스가 null을 넘긴 적이 없습니다(17행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `uncompress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t *)` 37행, 조건 `dest == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
   33      const uInt max = (uInt)-1;
   34      z_size_t len, left;
   35  
   36      if (sourceLen == NULL || (*sourceLen > 0 && source == NULL) ||
   37>         destLen == NULL || (*destLen > 0 && dest == NULL))
   38          return Z_STREAM_ERROR;
   39  
   40      len = *sourceLen;
   41      left = *destLen;
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -14,7 +14,8 @@
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
   uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
-  if (Z_OK != uncompress(buffer, &buffer_length, data,
+  Bytef* dest = (size > 0 && (data[0] & 0x07) == 0) ? nullptr : buffer;  // [gapfuzz-llm] 입력 첫 바이트로 dest에 nullptr도 가끔(약 1/8) 넘겨 dest == NULL 분기 도달
+  if (Z_OK != uncompress(dest, &buffer_length, data,  // [gapfuzz-llm] 고정 buffer 대신 입력으로 고른 dest 사용 (나머지 7/8은 원래 buffer)
                          static_cast<uLong>(size))) {
     return 0;
   }
```

## 제안 4
`inflate(z_streamp, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`uncompress2_z`)에서만 불립니다. 내부 호출은 2번째 인자 `flush`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (7개)
- `inflate(z_streamp, int)` 717행, 조건 `flush == Z_BLOCK`가 퍼징 중 한 번도 '참'이 되지 않음
```
  713              strm->adler = state->check = adler32(0L, Z_NULL, 0);
  714              state->mode = TYPE;
  715                  /* fallthrough */
  716          case TYPE:
  717>             if (flush == Z_BLOCK || flush == Z_TREES) goto inf_leave;
  718                  /* fallthrough */
  719          case TYPEDO:
  720              if (state->last) {
  721                  BYTEBITS();
```
- `inflate(z_streamp, int)` 717행, 조건 `flush == Z_TREES`가 퍼징 중 한 번도 '참'이 되지 않음
```
  713              strm->adler = state->check = adler32(0L, Z_NULL, 0);
  714              state->mode = TYPE;
  715                  /* fallthrough */
  716          case TYPE:
  717>             if (flush == Z_BLOCK || flush == Z_TREES) goto inf_leave;
  718                  /* fallthrough */
  719          case TYPEDO:
  720              if (state->last) {
  721                  BYTEBITS();
```
- `inflate(z_streamp, int)` 739행, 조건 `flush == Z_TREES`가 퍼징 중 한 번도 '참'이 되지 않음
```
  735                  inflate_fixed(state);
  736                  Tracev((stderr, "inflate:     fixed codes block%s\n",
  737                          state->last ? " (last)" : ""));
  738                  state->mode = LEN_;             /* decode codes */
  739>                 if (flush == Z_TREES) {
  740                      DROPBITS(2);
  741                      goto inf_leave;
  742                  }
  743                  break;
```
- `inflate(z_streamp, int)` 768행, 조건 `flush == Z_TREES`가 퍼징 중 한 번도 '참'이 되지 않음
```
  764              Tracev((stderr, "inflate:       stored length %u\n",
  765                      state->length));
  766              INITBITS();
  767              state->mode = COPY_;
  768>             if (flush == Z_TREES) goto inf_leave;
  769                  /* fallthrough */
  770          case COPY_:
  771              state->mode = COPY;
  772                  /* fallthrough */
```
- `inflate(z_streamp, int)` 917행, 조건 `flush == Z_TREES`가 퍼징 중 한 번도 '참'이 되지 않음
```
  913                  break;
  914              }
  915              Tracev((stderr, "inflate:       codes ok\n"));
  916              state->mode = LEN_;
  917>             if (flush == Z_TREES) goto inf_leave;
  918                  /* fallthrough */
  919          case LEN_:
  920              state->mode = LEN;
  921                  /* fallthrough */
```
- `inflate(z_streamp, int)` 1142행, 조건 `flush != Z_FINISH`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1138       */
 1139    inf_leave:
 1140      RESTORE();
 1141      if (state->wsize || (out != strm->avail_out && state->mode < BAD &&
 1142>             (state->mode < CHECK || flush != Z_FINISH)))
 1143          if (updatewindow(strm, strm->next_out, out - strm->avail_out)) {
 1144              state->mode = MEM;
 1145              return Z_MEM_ERROR;
 1146          }
```
- `inflate(z_streamp, int)` 1158행, 조건 `flush == Z_FINISH`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1154              UPDATE_CHECK(state->check, strm->next_out - out, out);
 1155      strm->data_type = (int)state->bits + (state->last ? 64 : 0) +
 1156                        (state->mode == TYPE ? 128 : 0) +
 1157                        (state->mode == LEN_ || state->mode == COPY_ ? 256 : 0);
 1158>     if (((in == 0 && out == 0) || flush == Z_FINISH) && ret == Z_OK)
 1159          ret = Z_BUF_ERROR;
 1160      return ret;
 1161  }
 1162  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 공식 하네스: oss-fuzz/projects/zlib/zlib_uncompress_fuzzer.cc 그대로 (zlib 커밋 71747d1).
   2  // Copyright 2015 The Chromium Authors. All rights reserved.
   3  // Use of this source code is governed by a BSD-style license that can be
   4  // found in the LICENSE file.
   5  
   6  #include <stddef.h>
   7  #include <stdint.h>
   8  #include <string.h>
   9  
  10  #include "zlib.h"
  11  
  12  static Bytef buffer[256 * 1024] = { 0 };
  13  
  14  // Entry point for LibFuzzer.
  15  extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  16    uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
  17    if (Z_OK != uncompress(buffer, &buffer_length, data,
  18                           static_cast<uLong>(size))) {
  19      return 0;
  20    }
  21    return 0;
  22  }
```