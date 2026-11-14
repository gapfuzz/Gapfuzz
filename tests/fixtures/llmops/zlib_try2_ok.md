```cpp
// OSS-Fuzz 공식 하네스: oss-fuzz/projects/zlib/zlib_uncompress_fuzzer.cc 그대로 (zlib 커밋 71747d1).
// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "zlib.h"

static Bytef buffer[256 * 1024] = { 0 };

// [gapfuzz-ops] inflateBack에 넘길 입력·출력 콜백
struct BackIn { const uint8_t* data; size_t left; };
static unsigned back_in(void* desc, z_const unsigned char** buf) {
  BackIn* in = static_cast<BackIn*>(desc);
  if (in->left == 0) { *buf = Z_NULL; return 0; }
  *buf = const_cast<unsigned char*>(in->data);
  unsigned n = static_cast<unsigned>(in->left);
  in->left = 0;
  return n;
}
static int back_out(void*, unsigned char*, unsigned) { return 0; }

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
  uncompress(buffer, &buffer_length, data, static_cast<uLong>(size));  // 원래 호출은 그대로

  if (size == 0 || size > 64 * 1024) return 0;       // 추가 호출은 64KB 이하 입력에만
  const uint8_t sel = data[size - 1];                 // 선택값은 입력 끝 바이트에서
  const uInt n = static_cast<uInt>(size);

  // [gapfuzz-ops] compress
  {
    uLongf cap = compressBound(n);
    Bytef* out = static_cast<Bytef*>(malloc(cap));
    if (out) { compress(out, &cap, data, n); free(out); }
  }

  // [gapfuzz-ops] deflateSetDictionary, deflateBound, deflateParams, deflateCopy
  {
    z_stream ds;
    memset(&ds, 0, sizeof(ds));
    if (deflateInit(&ds, sel % 10) == Z_OK) {
      deflateSetDictionary(&ds, data, n < 64 ? n : 64);
      uLong cap = deflateBound(&ds, n) + 1024;
      Bytef* out = static_cast<Bytef*>(malloc(cap));
      if (out) {
        ds.next_in = const_cast<Bytef*>(data);
        ds.avail_in = n / 2;
        ds.next_out = out;
        ds.avail_out = static_cast<uInt>(cap);
        deflate(&ds, Z_NO_FLUSH);
        deflateParams(&ds, (sel >> 4) % 10, (sel >> 1) % 5);
        z_stream cp;
        if (deflateCopy(&cp, &ds) == Z_OK) deflateEnd(&cp);
        ds.next_in = const_cast<Bytef*>(data) + n / 2;
        ds.avail_in = n - n / 2;
        deflate(&ds, Z_FINISH);
        free(out);
      }
      deflateEnd(&ds);
    }
  }

  // [gapfuzz-ops] inflateSync, inflateCopy
  {
    z_stream is;
    memset(&is, 0, sizeof(is));
    if (inflateInit(&is) == Z_OK) {
      is.next_in = const_cast<Bytef*>(data);
      is.avail_in = n;
      is.next_out = buffer;
      is.avail_out = static_cast<uInt>(sizeof(buffer));
      inflate(&is, Z_NO_FLUSH);
      inflateSync(&is);
      z_stream cp;
      if (inflateCopy(&cp, &is) == Z_OK) inflateEnd(&cp);
      inflateEnd(&is);
    }
  }

  // [gapfuzz-ops] inflateBack
  {
    static unsigned char window[32768];
    z_stream bs;
    memset(&bs, 0, sizeof(bs));
    if (inflateBackInit(&bs, 15, window) == Z_OK) {
      BackIn in = { data, size };
      inflateBack(&bs, back_in, &in, back_out, Z_NULL);
      inflateBackEnd(&bs);
    }
  }
  return 0;
}
```
compress, deflate 계열 4개, inflate 계열 2개, inflateBack을 추가했습니다. 뺀 API는 없습니다.
