// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,3,4,8,9,10,11를 OSS-Fuzz 하네스 official_compress에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: samples/llm/combined/zlib/official_compress/).
// OSS-Fuzz 하네스: oss-fuzz/projects/zlib/compress_fuzzer.c 그대로.
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

static const uint8_t *data;
static size_t dataLen;

static void check_compress_level(uint8_t *compr, size_t comprLen,
                                 uint8_t *uncompr, size_t uncomprLen,
                                 int level, unsigned cmode, unsigned umode) { // [gapfuzz-llm] null 인자 선택용 cmode/umode 파라미터 추가
  /* cmode: 0 -> source=NULL, 1 -> destLen=NULL, 2 -> dest=NULL, 그 외 정상 */
  int cerr;
  if (cmode == 1) {
    /* compress2 래퍼는 destLen을 먼저 역참조하므로, NULL 검사를 하는 compress2_z를 직접 호출 */
    cerr = compress2_z(compr, NULL, data, dataLen, level);  // [gapfuzz-llm] destLen=nullptr를 실제 검사 지점(compress2_z)까지 전달
  } else {
    cerr = compress2(cmode == 2 ? NULL : compr,                       // [gapfuzz-llm] dest에 nullptr도 전달(destLen>0이라 32행 도달)
                     &comprLen,
                     cmode == 0 ? NULL : data, dataLen, level);       // [gapfuzz-llm] source에 nullptr도 전달
  }
  if (cmode == 1)
    comprLen = 0;  // [gapfuzz-llm] destLen이 갱신되지 않았으므로 0으로 두어 이후 호출이 안전하게 함
  uncompress(uncompr, &uncomprLen, umode == 0 ? NULL : compr, comprLen); // [gapfuzz-llm] uncompress source에 nullptr도 전달

  /* Make sure compress + uncompress gives back the input data. */
  if (cmode > 2 && umode != 0 && cerr == Z_OK) { // [gapfuzz-llm] null 인자를 넣은 경우 왕복 검증은 건너뜀
    assert(dataLen == uncomprLen);
    assert(0 == memcmp(data, uncompr, dataLen));
  }
}

#define put_byte(s, i, c) {s[i] = (unsigned char)(c);}

static void write_zlib_header(uint8_t *s, unsigned compression_method, unsigned flags) {
  unsigned int header = (Z_DEFLATED + ((flags)<<4)) << 8;
  header |= (compression_method << 6);

  header += 31 - (header % 31);

  /* s is guaranteed to be longer than 2 bytes. */
  put_byte(s, 0, (unsigned char)(header >> 8));
  put_byte(s, 1, (unsigned char)(header & 0xff));
}

static void check_decompress(uint8_t *compr, size_t comprLen, unsigned compression_method, unsigned flags, unsigned umode) { // [gapfuzz-llm] umode 파라미터 추가
  /* We need to write a valid zlib header of size two bytes. Copy the input data
     in a larger buffer. Do not modify the input data to avoid libFuzzer error:
     fuzz target overwrites its const input. */
  size_t copyLen = dataLen + 2;
  uint8_t *copy = (uint8_t *)malloc(copyLen);
  if (!copy)
    return;
  memcpy(copy + 2, data, dataLen);
  write_zlib_header(copy, compression_method, flags);

  uncompress(compr, &comprLen, umode == 0 ? NULL : copy, copyLen); // [gapfuzz-llm] source에 nullptr도 전달
  free(copy);
}

int LLVMFuzzerTestOneInput(const uint8_t *d, size_t size) {
  if (size < 16 || size > 1024 * 1024) // [gapfuzz-llm] 추가 선택 바이트를 쓰므로 최소 크기를 늘림
    return 0;

  const int level = d[0] % 10;
  d++,size--;

  //https://web.archive.org/web/20200220015003/http://www.onicos.com/staff/iz/formats/gzip.html
  unsigned compression_method = d[0] % 5;
  if (compression_method == 4)  //[4...7] are reserved
    compression_method = 8;
  d++,size--;
  unsigned flags = d[0] & (2 << 4);
  d++,size--;

  /* 앞쪽 바이트를 겹치지 않게 순서대로 배분 */
  unsigned cmode = d[0] % 8;   // [gapfuzz-llm] compress2 null 인자 선택(0~2가 null, 각 1/8로 빈도 상향)
  unsigned umode = d[1] % 16;  // [gapfuzz-llm] uncompress source null 선택(0만 null)
  int init_wbits = (d[6] & 7) == 0 ? 8
                   : (int)(d[2] % 50) - 17;  // [gapfuzz-llm] windowBits: 별도 바이트(d[6])로 1/8 확률 8 선택, 나머지는 d[2]로 -17..32 (gzip 범위 >15 복구)
  int init_method = (d[3] & 7) == 0 ? (int)(d[3] >> 3) : Z_DEFLATED;  // [gapfuzz-llm] method: 대부분 Z_DEFLATED, 가끔 다른 값
  int init_mem = (int)(d[4] % 12) - 1;  // [gapfuzz-llm] memLevel: -1..10 (8 포함)
  int init_strategy = (int)(d[5] % 8) - 2;  // [gapfuzz-llm] strategy: -2..5 (유효 범위와 범위 밖 모두)
  d += 7, size -= 7;  // [gapfuzz-llm] d[6]까지 소비하도록 7바이트 전진

  size_t comprLen = compressBound(size);
  size_t uncomprLen = size;
  uint8_t *compr = NULL, *uncompr = NULL;

  data = d;
  dataLen = size;
  compr = (uint8_t *)calloc(1, comprLen);
  if (!compr)
    goto err;
  uncompr = (uint8_t *)calloc(1, uncomprLen);
  if (!uncompr)
    goto err;

  check_compress_level(compr, comprLen, uncompr, uncomprLen, level, cmode, umode);
  check_decompress(compr, comprLen, compression_method, flags, umode);

  {
    z_stream strm;  // [gapfuzz-llm] deflateInit2_를 직접 호출
    memset(&strm, 0, sizeof(strm));
    if (deflateInit2(&strm, level, init_method, init_wbits, init_mem, init_strategy) == Z_OK)  // [gapfuzz-llm] windowBits/method/memLevel/strategy를 입력에서 선택
      deflateEnd(&strm);  // [gapfuzz-llm] 성공 시 해제
  }

err:
  free(compr);
  free(uncompr);

  /* This function must return 0. */
  return 0;
}
