// [gapfuzz-ops] 이 파일은 Claude(claude-sonnet-5-5)가 새로 쓴 하네스입니다. OSS-Fuzz 하네스 전체를 합쳐도 불리지 않던 API 10개를 부릅니다.
// [gapfuzz-ops] gapfuzz가 검사해 통과했습니다 (python3 -m gapfuzz llmops zlib --union, 기록: evaluation/artifacts/llm/ops/zlib/_union/).
// zlib 새 하네스: 기존 하네스가 부르지 않는 API를 입력 바이트로 고른 순서대로 호출한다.
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include <vector>

#include "zlib.h"

namespace {

constexpr size_t kMaxInput = 64 * 1024;        // 입력 상한 64KB
constexpr size_t kOutSize = 64 * 1024;         // 출력 버퍼 64KB (1MB 이하)
constexpr size_t kBackOutLimit = 1024 * 1024;  // inflateBack 총 출력 상한 1MB
constexpr int kMaxOps = 32;                    // 반복 상한 (64회 이하)

static uint8_t g_out[kOutSize];
static volatile uLong g_sink;

// inflateBack 콜백용 설명자
struct BackDesc {
  const uint8_t* p;
  size_t left;
  size_t chunk;
  size_t out_total;
  bool abort_on_out;
};

static unsigned BackIn(void* d, z_const unsigned char** buf) {
  BackDesc* bd = static_cast<BackDesc*>(d);
  if (bd->left == 0) {
    *buf = Z_NULL;
    return 0;
  }
  size_t n = bd->chunk < bd->left ? bd->chunk : bd->left;
  // z_const 정의 여부와 관계없이 컴파일되도록 const를 제거해 대입한다
  *buf = const_cast<unsigned char*>(bd->p);
  bd->p += n;
  bd->left -= n;
  return static_cast<unsigned>(n);
}

static int BackOut(void* d, unsigned char* buf, unsigned len) {
  BackDesc* bd = static_cast<BackDesc*>(d);
  bd->out_total += len;
  if (len) g_sink += buf[0] + buf[len - 1];  // 출력 버퍼를 읽어본다
  if (bd->abort_on_out || bd->out_total > kBackOutLimit) return 1;  // 중단
  return 0;
}

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size > kMaxInput) size = kMaxInput;
  if (size < 5) return 0;

  // 앞쪽 바이트: 스트림 설정 선택값
  const uint8_t cfg_def = data[0];
  const uint8_t cfg_def2 = data[1];
  const uint8_t cfg_inf = data[2];
  int num_ops = 1 + (data[3] % kMaxOps);
  size_t pos = 4;
  if (static_cast<size_t>(num_ops) > size - pos) num_ops = static_cast<int>(size - pos);
  const uint8_t* ops = data + pos;
  pos += num_ops;
  const uint8_t* payload = data + pos;
  const size_t payload_len = size - pos;
  size_t off = 0;  // 페이로드 소비 위치

  // deflate 스트림 초기화
  z_stream def;
  memset(&def, 0, sizeof(def));
  {
    int wb = 9 + (cfg_def % 7);
    int wrap = (cfg_def >> 3) % 3;
    int wbits = wrap == 0 ? -wb : (wrap == 1 ? wb : wb + 16);
    int level = static_cast<int>(cfg_def2 % 11) - 1;
    int mem = 1 + ((cfg_def2 >> 4) % 9);
    int strat = (cfg_def >> 5) % 5;
    if (deflateInit2(&def, level, Z_DEFLATED, wbits, mem, strat) != Z_OK) return 0;
  }

  // inflate 스트림 초기화
  z_stream inf;
  memset(&inf, 0, sizeof(inf));
  {
    int wb = 8 + (cfg_inf % 8);
    int wrap = (cfg_inf >> 3) % 4;
    int wbits = wrap == 0 ? -wb : (wrap == 1 ? wb : (wrap == 2 ? wb + 16 : wb + 32));
    if (inflateInit2(&inf, wbits) != Z_OK) {
      deflateEnd(&def);
      return 0;
    }
  }

  for (int i = 0; i < num_ops; i++) {
    const int op = ops[i] & 0x0F;
    const int param = ops[i] >> 4;
    size_t want = (static_cast<size_t>(param) + 1) * 512;
    size_t n = payload_len - off;
    if (n > want) n = want;
    const uint8_t* chunk = payload + off;

    switch (op % 11) {
      case 0: {
        // [gapfuzz-ops] deflatePrime
        int bits = param % 18;  // 범위 밖 값도 일부러 허용(오류 반환 경로)
        int value = n >= 2 ? (chunk[0] | (chunk[1] << 8)) : param;
        g_sink += deflatePrime(&def, bits, value);
        break;
      }
      case 1: {
        // 준비 호출: deflate로 데이터 주입
        static const int flushes[] = {Z_NO_FLUSH, Z_SYNC_FLUSH, Z_FULL_FLUSH, Z_FINISH};
        def.next_in = const_cast<Bytef*>(chunk);
        def.avail_in = static_cast<uInt>(n);
        def.next_out = g_out;
        def.avail_out = kOutSize;
        g_sink += deflate(&def, flushes[param % 4]);
        def.next_in = Z_NULL;
        def.avail_in = 0;
        off += n;
        break;
      }
      case 2: {
        // [gapfuzz-ops] deflateCopy
        z_stream cp;
        memset(&cp, 0, sizeof(cp));
        int r = deflateCopy(&cp, &def);
        if (r == Z_OK) {
          cp.next_in = const_cast<Bytef*>(chunk);
          cp.avail_in = static_cast<uInt>(n);
          cp.next_out = g_out;
          cp.avail_out = kOutSize;
          g_sink += deflate(&cp, (param & 1) ? Z_FINISH : Z_SYNC_FLUSH);
          deflateEnd(&cp);
          off += n;
        }
        break;
      }
      case 3: {
        // [gapfuzz-ops] deflateGetDictionary
        std::vector<Bytef> dict(32768);
        uInt len = 0;
        if (param & 1) {
          if (deflateGetDictionary(&def, dict.data(), &len) == Z_OK && len <= dict.size())
            g_sink += len ? dict[len - 1] : 0;
        } else {
          // dictionary가 Z_NULL이면 길이만 구한다
          g_sink += deflateGetDictionary(&def, Z_NULL, &len);
        }
        break;
      }
      case 4: {
        // [gapfuzz-ops] inflatePrime
        int bits = (param % 19) - 1;  // -1(비우기) ~ 17
        int value = n >= 2 ? (chunk[0] | (chunk[1] << 8)) : param;
        g_sink += inflatePrime(&inf, bits, value);
        break;
      }
      case 5: {
        // 준비 호출: inflate로 데이터 주입
        static const int flushes[] = {Z_NO_FLUSH, Z_SYNC_FLUSH, Z_BLOCK, Z_NO_FLUSH};
        inf.next_in = const_cast<Bytef*>(chunk);
        inf.avail_in = static_cast<uInt>(n);
        inf.next_out = g_out;
        inf.avail_out = kOutSize;
        int r = inflate(&inf, flushes[param % 4]);
        g_sink += r;
        inf.next_in = Z_NULL;
        inf.avail_in = 0;
        if (r != Z_OK && r != Z_BUF_ERROR) {
          // 종료/오류 후에는 초기 상태로 되돌려 계속 쓸 수 있게 한다
          if (inflateReset(&inf) != Z_OK) {
            inflateEnd(&inf);
            deflateEnd(&def);
            return 0;
          }
        }
        off += n;
        break;
      }
      case 6: {
        // [gapfuzz-ops] inflateCopy
        z_stream cp;
        memset(&cp, 0, sizeof(cp));
        int r = inflateCopy(&cp, &inf);
        if (r == Z_OK) {
          cp.next_in = const_cast<Bytef*>(chunk);
          cp.avail_in = static_cast<uInt>(n);
          cp.next_out = g_out;
          cp.avail_out = kOutSize;
          g_sink += inflate(&cp, Z_SYNC_FLUSH);
          // 복사본에서도 사전 조회
          uInt len = 0;
          g_sink += inflateGetDictionary(&cp, Z_NULL, &len);
          inflateEnd(&cp);
          off += n;
        }
        break;
      }
      case 7: {
        // [gapfuzz-ops] inflateGetDictionary
        std::vector<Bytef> dict(32768);
        uInt len = 0;
        if (param & 1) {
          if (inflateGetDictionary(&inf, dict.data(), &len) == Z_OK && len <= dict.size())
            g_sink += len ? dict[len - 1] : 0;
        } else {
          g_sink += inflateGetDictionary(&inf, Z_NULL, &len);
        }
        break;
      }
      case 8: {
        // [gapfuzz-ops] inflateValidate
        g_sink += inflateValidate(&inf, param & 1);
        break;
      }
      case 9: {
        // [gapfuzz-ops] zlibCompileFlags
        g_sink += zlibCompileFlags();
        break;
      }
      case 10: {
        // 별도의 raw inflate 스트림으로 콜백 방식 해제
        z_stream bs;
        memset(&bs, 0, sizeof(bs));
        int wbits = 8 + (param % 8);  // 8..15
        std::vector<unsigned char> window(static_cast<size_t>(1) << wbits);
        // [gapfuzz-ops] inflateBackInit_
        if (inflateBackInit(&bs, wbits, window.data()) == Z_OK) {
          BackDesc bd;
          bd.p = payload + off;
          bd.left = payload_len - off;
          bd.chunk = 1 + (static_cast<size_t>(ops[i]) * 37 % 4096);
          bd.out_total = 0;
          bd.abort_on_out = (param == 15);
          // [gapfuzz-ops] inflateBack
          for (int k = 0; k < 2; k++) {
            int r = inflateBack(&bs, BackIn, &bd, BackOut, &bd);
            g_sink += r;
            if (r != Z_STREAM_END || bd.left == 0) break;
          }
          inflateBackEnd(&bs);
        }
        off = payload_len;
        break;
      }
    }
  }

  inflateEnd(&inf);
  deflateEnd(&def);
  return 0;
}
