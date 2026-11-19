// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 2,10,11,12를 OSS-Fuzz 하네스 official_example_large에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/zlib/official_example_large/).
// OSS-Fuzz 하네스: oss-fuzz/projects/zlib/example_large_fuzzer.c 그대로.
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
#include <inttypes.h>
#include "zlib.h"

#define CHECK_ERR(err, msg) { \
    if (err != Z_OK) { \
        fprintf(stderr, "%s error: %d\n", msg, err); \
        return 0; \
    } \
}

/* deflate 스트림이 초기화된 뒤의 오류 처리: 누수 방지를 위해 deflateEnd 후 반환 */
#define CHECK_ERR_DEFLATE_END(err, msg, strm) { \
    if (err != Z_OK) { \
        fprintf(stderr, "%s error: %d\n", msg, err); \
        deflateEnd(strm); \
        return 0; \
    } \
} // [gapfuzz-llm] flush 값이 다양해져 오류 경로가 흔해지므로 deflateEnd로 누수를 막는 매크로 추가

static const uint8_t *data;
static size_t dataLen;
static size_t dataPos; // [gapfuzz-llm] 입력 앞쪽 바이트를 겹치지 않게 순서대로 배분하기 위한 위치
static alloc_func zalloc = NULL;
static free_func zfree = NULL;
static unsigned int diff;

/* 입력 앞쪽 바이트를 순서대로 하나씩 꺼낸다. 입력이 모자라면 0. */
static uint8_t next_byte(void) { // [gapfuzz-llm] 퍼저 입력에서 인자 값을 겹치지 않게 꺼내는 도우미
  if (dataPos < dataLen)
    return data[dataPos++];
  return 0;
}

static int pick_flush(void) { // [gapfuzz-llm] flush를 -1..7에서 고름(0, 4 포함, 범위 밖 값도 포함)
  return (int)(next_byte() % 9) - 1;
}

static int pick_level(void) { // [gapfuzz-llm] level을 -2..10에서 고름(0, 9, -1 포함, 범위 밖 값도 포함)
  return (int)(next_byte() % 13) - 2;
}

static int pick_strategy(void) { // [gapfuzz-llm] strategy를 -1..5에서 고름(0, 1 포함, 범위 밖 값도 포함)
  return (int)(next_byte() % 7) - 1;
}

/* deflate 호출. 가끔 잘못된 스트림(NULL, state==NULL)을 넘겨 deflateStateCheck 실패 경로를 연다. */
static int call_deflate(z_stream *c, int flush) { // [gapfuzz-llm] deflate 자체의 strm 상태 검사 실패 분기를 열기 위한 래퍼
  uint8_t sel = (uint8_t)(next_byte() % 8);
  if (sel == 0) {
    deflate(Z_NULL, flush); /* 문서상 Z_STREAM_ERROR 반환으로 처리됨 */
    return Z_OK; /* 이후 흐름을 계속 진행 */
  } else if (sel == 1) {
    z_stream copy = *c;
    copy.state = Z_NULL; /* state가 NULL인 스트림 */
    deflate(&copy, flush);
    return Z_OK;
  }
  return deflate(c, flush);
}

/* deflateParams 호출. strm 인자를 퍼저 입력으로 고른다. */
static void call_deflate_params(z_stream *c, int level, int strategy) { // [gapfuzz-llm] strm 인자를 입력으로 선택하는 래퍼
  uint8_t sel = (uint8_t)(next_byte() % 5);
  if (sel == 0) {
    deflateParams(Z_NULL, level, strategy); /* NULL은 Z_STREAM_ERROR로 처리됨 */
  } else if (sel == 1) {
    z_stream copy = *c; /* state->strm != &copy 인 스트림 */
    deflateParams(&copy, level, strategy);
  } else if (sel == 2) {
    z_stream copy = *c;
    copy.state = Z_NULL; /* state가 NULL인 스트림 */
    deflateParams(&copy, level, strategy);
  } else if (sel == 3) {
    Bytef *saved = c->next_out;
    c->next_out = Z_NULL; /* 내부 deflate()가 Z_STREAM_ERROR를 내게 함 */
    deflateParams(c, level, strategy);
    c->next_out = saved;
  } else {
    deflateParams(c, level, strategy);
  }
}

/* ===========================================================================
 * Test deflate() with large buffers and dynamic change of compression level
 */
int test_large_deflate(unsigned char *compr, size_t comprLen,
                        unsigned char *uncompr, size_t uncomprLen) {
  z_stream c_stream; /* compression stream */
  int err;

  c_stream.zalloc = zalloc;
  c_stream.zfree = zfree;
  c_stream.opaque = (void *)0;

  err = deflateInit(&c_stream, Z_BEST_COMPRESSION);
  CHECK_ERR(err, "deflateInit");

  c_stream.next_out = compr;
  c_stream.avail_out = (unsigned int)comprLen;

  /* At this point, uncompr is still mostly zeroes, so it should compress
   * very well:
   */
  c_stream.next_in = uncompr;
  c_stream.avail_in = (next_byte() % 4 == 0) ? 0 : (unsigned int)uncomprLen; // [gapfuzz-llm] 입력 없이 NO_FLUSH로 첫 deflate를 호출하는 경우도 만들어 flush == Z_NO_FLUSH 거짓 분기를 연다
  err = call_deflate(&c_stream, pick_flush()); // [gapfuzz-llm] flush와 strm을 입력에서 선택
  CHECK_ERR_DEFLATE_END(err, "deflate large 1", &c_stream);
  if (c_stream.avail_in != 0) {
    fprintf(stderr, "deflate not greedy\n");
    deflateEnd(&c_stream); // [gapfuzz-llm] 조기 반환 시 누수 방지
    return 0;
  }

  /* Feed in already compressed data and switch to no compression: */
  call_deflate_params(&c_stream, pick_level(), pick_strategy()); // [gapfuzz-llm] strm, level, strategy를 입력에서 선택
  diff = (unsigned int)(c_stream.next_out - compr);
  {
    uint8_t in_sel = (uint8_t)(next_byte() % 3); // [gapfuzz-llm] 두 번째 deflate의 입력 종류를 입력으로 선택(원래 압축 데이터 / 큰 버퍼 / 입력 없음)
    if (in_sel == 0) {
      c_stream.next_in = compr;
      c_stream.avail_in = diff;
    } else if (in_sel == 1) {
      c_stream.next_in = uncompr; // [gapfuzz-llm] 큰 버퍼를 입력으로 사용해 deflate_stored의 min_block 이상 경로를 연다
      c_stream.avail_in = (unsigned int)uncomprLen;
    } else {
      c_stream.next_in = compr; // [gapfuzz-llm] 입력 없이 호출해 len == 0 경로(flush != Z_FINISH 판정)를 연다
      c_stream.avail_in = 0;
    }
  }
  {
    Bytef *saved_out = c_stream.next_out; // [gapfuzz-llm] 출력 공간을 일시적으로 좁혀 입력이 윈도우에 쌓이는 left >= min_block 경로를 연다
    unsigned int saved_avail = c_stream.avail_out;
    unsigned int small = 0;
    int limited = 0;
    if (next_byte() % 2 == 0 && saved_avail > 64) {
      small = 64;
      c_stream.avail_out = small;
      limited = 1;
    }
    err = call_deflate(&c_stream, pick_flush()); // [gapfuzz-llm] flush와 strm을 입력에서 선택
    if (limited && c_stream.next_out >= saved_out &&
        (size_t)(c_stream.next_out - saved_out) <= small) {
      unsigned int used = (unsigned int)(c_stream.next_out - saved_out);
      c_stream.avail_out = saved_avail - used; // [gapfuzz-llm] 이후 호출을 위해 남은 출력 공간 복원
    } else if (limited) {
      c_stream.avail_out = saved_avail - (unsigned int)(c_stream.next_out - saved_out); // [gapfuzz-llm] 스트림 상태와 어긋나지 않게 복원
    }
  }
  CHECK_ERR_DEFLATE_END(err, "deflate large 2", &c_stream);

  /* Switch back to compressing mode: */
  call_deflate_params(&c_stream, pick_level(), pick_strategy()); // [gapfuzz-llm] strm, level, strategy를 입력에서 선택
  c_stream.next_in = uncompr;
  c_stream.avail_in = (unsigned int)uncomprLen;
  err = call_deflate(&c_stream, pick_flush()); // [gapfuzz-llm] flush와 strm을 입력에서 선택
  CHECK_ERR_DEFLATE_END(err, "deflate large 3", &c_stream);

  err = call_deflate(&c_stream, pick_flush()); // [gapfuzz-llm] flush와 strm을 입력에서 선택
  if (err != Z_STREAM_END) {
    fprintf(stderr, "deflate large should report Z_STREAM_END\n");
    deflateEnd(&c_stream); // [gapfuzz-llm] 조기 반환 시 누수 방지
    return 0;
  }
  err = deflateEnd(&c_stream);
  CHECK_ERR(err, "deflateEnd");
  return 0;
}

/* ===========================================================================
 * Test inflate() with large buffers
 */
int test_large_inflate(unsigned char *compr, size_t comprLen,
                        unsigned char *uncompr, size_t uncomprLen) {
  int err;
  z_stream d_stream; /* decompression stream */

  d_stream.zalloc = zalloc;
  d_stream.zfree = zfree;
  d_stream.opaque = (void *)0;

  d_stream.next_in = compr;
  d_stream.avail_in = (unsigned int)comprLen;

  err = inflateInit(&d_stream);
  CHECK_ERR(err, "inflateInit");

  for (;;) {
    d_stream.next_out = uncompr; /* discard the output */
    d_stream.avail_out = (unsigned int)uncomprLen;
    err = inflate(&d_stream, Z_NO_FLUSH);
    if (err == Z_STREAM_END)
      break;
    if (err != Z_OK) { // [gapfuzz-llm] 압축 결과가 불완전할 수 있어 오류 시 inflateEnd로 누수 방지
      fprintf(stderr, "large inflate error: %d\n", err);
      inflateEnd(&d_stream);
      return 0;
    }
  }

  err = inflateEnd(&d_stream);
  CHECK_ERR(err, "inflateEnd");

  if (d_stream.total_out != 2 * uncomprLen + diff) {
    fprintf(stderr, "bad large inflate: %zu\n", d_stream.total_out);
    return 0;
  }
  return 0;
}

int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
  size_t comprLen = 100 + 3 * size;
  size_t uncomprLen = comprLen;
  uint8_t *compr, *uncompr;

  /* Discard inputs larger than 512Kb. */
  static size_t kMaxSize = 512 * 1024;

  if (size < 1 || size > kMaxSize)
    return 0;

  data = d;
  dataLen = size;
  dataPos = 0; // [gapfuzz-llm] 매 실행마다 입력 읽기 위치 초기화
  diff = 0; // [gapfuzz-llm] 이전 실행 값이 남지 않도록 초기화
  if (next_byte() % 4 == 0) { // [gapfuzz-llm] 작은 입력에서도 deflate_stored의 min_block(최대 32KB) 이상 구간에 닿도록 버퍼를 128KB 키움
    comprLen += (size_t)1 << 17;
    uncomprLen = comprLen;
  }
  compr = (uint8_t *)calloc(1, comprLen);
  uncompr = (uint8_t *)calloc(1, uncomprLen);

  test_large_deflate(compr, comprLen, uncompr, uncomprLen);
  test_large_inflate(compr, comprLen, uncompr, uncomprLen);

  free(compr);
  free(uncompr);

  /* This function must return 0. */
  return 0;
}
