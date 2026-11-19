// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 2,8를 OSS-Fuzz 하네스 official_example_flush에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/zlib/official_example_flush/).
// OSS-Fuzz 하네스: oss-fuzz/projects/zlib/example_flush_fuzzer.c 그대로.
/* Copyright 2022 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

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

static const uint8_t *data;
static size_t dataLen;
static alloc_func zalloc = NULL;
static free_func zfree = NULL;
static int g_level = Z_DEFAULT_COMPRESSION; // [gapfuzz-llm] 퍼저 입력에서 고른 압축 level 보관
static int g_flush1 = Z_FULL_FLUSH;         // [gapfuzz-llm] 퍼저 입력에서 고른 첫 번째 flush 보관
static int g_flush2 = Z_FINISH;             // [gapfuzz-llm] 퍼저 입력에서 고른 두 번째 flush 보관

/* ===========================================================================
 * Test deflate() with full flush
 */
int test_flush(unsigned char *compr, z_size_t *comprLen) {
  z_stream c_stream; /* compression stream */
  int err;
  unsigned int len = dataLen;

  c_stream.zalloc = zalloc;
  c_stream.zfree = zfree;
  c_stream.opaque = (void *)0;

  err = deflateInit(&c_stream, g_level); // [gapfuzz-llm] level을 -1 고정 대신 퍼저 입력값(범위 밖 포함)으로 사용
  CHECK_ERR(err, "deflateInit");

  c_stream.next_in = (Bytef *)data;
  c_stream.next_out = compr;
  c_stream.avail_in = 3;
  c_stream.avail_out = (unsigned int)*comprLen;
  err = deflate(&c_stream, g_flush1); // [gapfuzz-llm] flush를 퍼저 입력에서 고른 값(범위 밖 포함)으로 사용
  if (err != Z_OK) { // [gapfuzz-llm] 오류로 일찍 반환할 때 스트림 누수 방지
    deflateEnd(&c_stream); // [gapfuzz-llm] 스트림 해제
  }
  CHECK_ERR(err, "deflate flush 1");

  compr[3]++; /* force an error in first compressed block */
  c_stream.avail_in = len - 3;

  err = deflate(&c_stream, g_flush2); // [gapfuzz-llm] flush를 퍼저 입력에서 고른 값(범위 밖 포함)으로 사용
  if (err != Z_STREAM_END) {
    if (err != Z_OK) { // [gapfuzz-llm] 오류로 일찍 반환할 때 스트림 누수 방지
      deflateEnd(&c_stream); // [gapfuzz-llm] 스트림 해제
    }
    CHECK_ERR(err, "deflate flush 2");
  }
  err = deflateEnd(&c_stream);
  CHECK_ERR(err, "deflateEnd");

  *comprLen = (z_size_t)c_stream.total_out;

  return 0;
}

/* ===========================================================================
 * Test inflateSync()
 */
int test_sync(unsigned char *compr, size_t comprLen, unsigned char *uncompr,
               size_t uncomprLen) {
  int err;
  z_stream d_stream; /* decompression stream */

  d_stream.zalloc = zalloc;
  d_stream.zfree = zfree;
  d_stream.opaque = (void *)0;

  d_stream.next_in = compr;
  d_stream.avail_in = 2; /* just read the zlib header */

  err = inflateInit(&d_stream);
  CHECK_ERR(err, "inflateInit");

  d_stream.next_out = uncompr;
  d_stream.avail_out = (unsigned int)uncomprLen;

  err = inflate(&d_stream, Z_NO_FLUSH);
  if (err != Z_OK) { // [gapfuzz-llm] deflate 실패로 압축 데이터가 비정상일 때 조기 반환 전에 해제해 누수 방지
    inflateEnd(&d_stream); // [gapfuzz-llm] 스트림 해제
  }
  CHECK_ERR(err, "inflate");

  d_stream.avail_in = (unsigned int)comprLen - 2; /* read all compressed data */
  err = inflateSync(&d_stream); /* but skip the damaged part */
  if (err != Z_OK) { // [gapfuzz-llm] 조기 반환 전에 해제해 누수 방지
    inflateEnd(&d_stream); // [gapfuzz-llm] 스트림 해제
  }
  CHECK_ERR(err, "inflateSync");

  err = inflate(&d_stream, Z_FINISH);
  if (err != Z_DATA_ERROR && err != Z_STREAM_END) {
    fprintf(stderr, "inflate should report DATA_ERROR or Z_STREAM_END\n");
    /* v1.1.11= reports DATA_ERROR because of incorrect adler32. v1.1.12+ reports Z_STREAM END because it skips the adler32 check. */
    inflateEnd(&d_stream); // [gapfuzz-llm] 조기 반환 전에 스트림 해제해 누수 방지
    return 0;
  }
  err = inflateEnd(&d_stream);
  CHECK_ERR(err, "inflateEnd");
  return 0;
}

int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
  size_t comprLen;
  size_t uncomprLen;
  uint8_t *compr, *uncompr;

  /* Discard inputs larger than 1Mb. */
  static size_t kMaxSize = 1024 * 1024;

  // This test requires at least 3 bytes of input data.
  // [gapfuzz-llm] 앞 3바이트를 level/flush 선택용으로 쓰므로 최소 크기를 늘림
  if (size <= 3 + 3 || size > kMaxSize)
    return 0;

  g_level = (int)(d[0] % 13) - 2;  // [gapfuzz-llm] level -2..10 (-1 기본값, 범위 밖 값 포함)
  g_flush1 = (int)(d[1] % 9) - 1;  // [gapfuzz-llm] flush -1..7 (3, 4 및 범위 밖 값 포함)
  g_flush2 = (int)(d[2] % 9) - 1;  // [gapfuzz-llm] flush -1..7, 앞 바이트와 겹치지 않게 다음 바이트 사용
  d += 3;                          // [gapfuzz-llm] 선택용 바이트를 건너뛰고 나머지를 원래대로 사용
  size -= 3;                       // [gapfuzz-llm] 남은 입력 크기로 조정

  comprLen = 100 + 2 * compressBound(size);
  uncomprLen = size;

  data = d;
  dataLen = size;
  compr = (uint8_t *)calloc(1, comprLen);
  uncompr = (uint8_t *)calloc(1, uncomprLen);

  test_flush(compr, &comprLen);
  test_sync(compr, comprLen, uncompr, uncomprLen);

  free(compr);
  free(uncompr);

  /* This function must return 0. */
  return 0;
}
