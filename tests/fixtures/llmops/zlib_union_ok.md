(시험용으로 사람이 미리 써 둔 응답입니다. Claude가 쓴 것이 아닙니다.)

```cpp
// zlib: OSS-Fuzz 하네스 전체가 부르지 않는 API를 부르는 새 하네스 (시험용)
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include <algorithm>
#include <vector>

#include "zlib.h"

namespace {

const size_t kMaxInput = 64 * 1024;
const size_t kMaxOut = 1024 * 1024;

struct BackCtx {
  const uint8_t* p;
  size_t n, pos, chunk, out_total;
};

unsigned BackIn(void* desc, z_const unsigned char** buf) {
  BackCtx* c = static_cast<BackCtx*>(desc);
  if (c->pos >= c->n) return 0;
  size_t take = std::min(c->chunk, c->n - c->pos);
  *buf = const_cast<unsigned char*>(c->p + c->pos);
  c->pos += take;
  return static_cast<unsigned>(take);
}

int BackOut(void* desc, unsigned char*, unsigned len) {
  BackCtx* c = static_cast<BackCtx*>(desc);
  c->out_total += len;
  return c->out_total > kMaxOut ? 1 : 0;
}

// [gapfuzz-ops] inflateBackInit_ / inflateBack / inflateBackEnd
void DoInflateBack(const uint8_t* data, size_t n, int bits, size_t chunk) {
  std::vector<unsigned char> window(static_cast<size_t>(1) << bits);
  z_stream s;
  memset(&s, 0, sizeof(s));
  if (inflateBackInit(&s, bits, window.data()) != Z_OK) return;
  BackCtx ctx = {data, n, 0, chunk ? chunk : 1, 0};
  inflateBack(&s, BackIn, &ctx, BackOut, &ctx);
  inflateBackEnd(&s);
}

// [gapfuzz-ops] deflatePrime / deflateCopy / deflateGetDictionary
void DoDeflate(const uint8_t* data, size_t n, int level, int prime_bits, int prime_val, size_t split,
               std::vector<Bytef>* out_stream) {
  z_stream s;
  memset(&s, 0, sizeof(s));
  if (deflateInit2(&s, level, Z_DEFLATED, -15, 8, Z_DEFAULT_STRATEGY) != Z_OK) return;  // raw: deflatePrime은 raw에서 의미가 있다
  std::vector<Bytef> out(compressBound(static_cast<uLong>(n)) + 64), tmp(out.size());
  deflatePrime(&s, prime_bits, prime_val);
  size_t half = n * split / 255;
  s.next_in = const_cast<Bytef*>(data);
  s.avail_in = static_cast<uInt>(half);
  s.next_out = out.data();
  s.avail_out = static_cast<uInt>(out.size());
  if (deflate(&s, Z_SYNC_FLUSH) == Z_STREAM_ERROR) { deflateEnd(&s); return; }

  z_stream c;
  memset(&c, 0, sizeof(c));
  if (deflateCopy(&c, &s) == Z_OK) {
    c.next_in = const_cast<Bytef*>(data + half);
    c.avail_in = static_cast<uInt>(n - half);
    c.next_out = tmp.data();
    c.avail_out = static_cast<uInt>(tmp.size());
    deflate(&c, Z_FINISH);
    deflateEnd(&c);
  }

  Bytef dict[32768];
  uInt dict_len = 0;
  deflateGetDictionary(&s, dict, &dict_len);

  s.next_in = const_cast<Bytef*>(data + half);
  s.avail_in = static_cast<uInt>(n - half);
  int r = deflate(&s, Z_FINISH);
  size_t produced = out.size() - s.avail_out;
  deflateEnd(&s);
  if (r == Z_STREAM_END && prime_bits == 0) out_stream->assign(out.begin(), out.begin() + produced);
}

// [gapfuzz-ops] inflatePrime / inflateValidate / inflateCopy / inflateGetDictionary
void DoInflate(const uint8_t* src, size_t n, int prime_bits, int prime_val, int validate, size_t split) {
  z_stream s;
  memset(&s, 0, sizeof(s));
  if (inflateInit2(&s, -15) != Z_OK) return;
  inflateValidate(&s, validate);
  inflatePrime(&s, prime_bits, prime_val);
  std::vector<Bytef> o1(32 * 1024), o2(32 * 1024);
  size_t half = n * split / 255;
  s.next_in = const_cast<Bytef*>(src);
  s.avail_in = static_cast<uInt>(half);
  s.next_out = o1.data();
  s.avail_out = static_cast<uInt>(o1.size());
  int r = inflate(&s, Z_NO_FLUSH);
  if (r == Z_STREAM_ERROR) { inflateEnd(&s); return; }

  z_stream c;
  memset(&c, 0, sizeof(c));
  if (inflateCopy(&c, &s) == Z_OK) {
    c.next_in = const_cast<Bytef*>(src + half);
    c.avail_in = static_cast<uInt>(n - half);
    c.next_out = o2.data();
    c.avail_out = static_cast<uInt>(o2.size());
    inflate(&c, Z_NO_FLUSH);
    inflateEnd(&c);
  }

  Bytef dict[32768];
  uInt dict_len = 0;
  inflateGetDictionary(&s, dict, &dict_len);
  inflateEnd(&s);
}

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size < 8) return 0;
  // 앞 8바이트는 선택값, 나머지가 데이터
  int level = data[0] % 10;
  int back_bits = 8 + data[1] % 8;
  size_t chunk = 1 + data[2];
  int prime_bits = data[3] % 17;         // 0..16
  int prime_val = data[4];
  size_t split = data[5];
  int validate = data[6] & 1;
  int which = data[7];
  const uint8_t* p = data + 8;
  size_t n = std::min(size - 8, kMaxInput);

  // [gapfuzz-ops] zlibCompileFlags
  if (which & 1) (void)zlibCompileFlags();

  try {
    if (which & 2) DoInflateBack(p, n, back_bits, chunk);
    std::vector<Bytef> stream;
    if (which & 4) DoDeflate(p, n, level, (which & 16) ? prime_bits : 0, prime_val, split, &stream);
    if (which & 8) {
      if (!stream.empty()) DoInflate(stream.data(), stream.size(), 0, 0, validate, split);
      else DoInflate(p, n, (which & 32) ? prime_bits : 0, prime_val, validate, split);
    }
  } catch (...) {
  }
  return 0;
}
```

넣은 것: inflateBackInit_, inflateBack, deflatePrime, deflateCopy, deflateGetDictionary, inflatePrime, inflateValidate, inflateCopy, inflateGetDictionary, zlibCompileFlags.
