// zlib OSS-Fuzz 하네스(zlib_uncompress_fuzzer.cc)에 gapfuzz 제안을 적용한 버전.
//   제안 1 (적용, FIXED):       uncompress의 destLen이 항상 버퍼 전체 크기 → 입력 2번째 바이트로 0~전체 크기 중 고름
//   제안 2 (적용, NARROW):      uncompress의 dest에 null을 넘긴 적 없음 → 옵션 비트로 null도 넘김
//   제안 3 (적용, DIRECT_CALL): inflate를 하네스가 직접 안 부름 (uncompress는 항상 Z_NO_FLUSH) → 직접 불러
//                               flush 값을 입력으로 고름 (Z_NO_FLUSH, Z_PARTIAL_FLUSH, Z_SYNC_FLUSH, Z_FULL_FLUSH, Z_FINISH, Z_BLOCK, Z_TREES)
//   제안 4 (미적용, 대조군):    uncompress의 source에 null을 넘긴 적 없음
// 입력 형식: [옵션 1바이트][destLen 비율 1바이트][압축 데이터]
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "zlib.h"

static Bytef buffer[256 * 1024] = { 0 };

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size < 2) return 0;
  const uint8_t opt = data[0];
  const uint8_t ratio = data[1];
  data += 2;
  size -= 2;

  if (!(opt & 0x80)) {
    // [제안 1] destLen: 기본(전체) 또는 0 ~ 전체 크기
    uLongf buffer_length = (opt & 0x01) ? static_cast<uLongf>(sizeof(buffer)) * ratio / 255
                                        : static_cast<uLongf>(sizeof(buffer));
    // [제안 2] dest에 null도 넘김
    Bytef *dest = (opt & 0x02) ? nullptr : buffer;
    uncompress(dest, &buffer_length, data, static_cast<uLong>(size));
    return 0;
  }

  // [제안 3] inflate를 직접 부르고 flush 값을 입력으로 고름. 출력 버퍼 크기도 입력으로 정해 여러 번 나눠 부른다.
  static const int kFlush[] = {Z_NO_FLUSH, Z_PARTIAL_FLUSH, Z_SYNC_FLUSH, Z_FULL_FLUSH, Z_FINISH, Z_BLOCK, Z_TREES};
  z_stream s;
  memset(&s, 0, sizeof(s));
  if (inflateInit(&s) != Z_OK) return 0;
  s.next_in = const_cast<Bytef *>(data);
  s.avail_in = static_cast<uInt>(size);
  const uInt chunk = 1 + ratio * 64;            // 1 ~ 16321 바이트
  for (int i = 0; i < 64; i++) {
    s.next_out = buffer;
    s.avail_out = chunk;
    const int flush = kFlush[((opt >> 0) + i) % 7];
    const int ret = inflate(&s, flush);
    if (ret == Z_STREAM_END || ret == Z_NEED_DICT || ret == Z_DATA_ERROR || ret == Z_MEM_ERROR ||
        ret == Z_STREAM_ERROR || (ret == Z_BUF_ERROR && s.avail_in == 0))
      break;
  }
  inflateEnd(&s);
  return 0;
}
