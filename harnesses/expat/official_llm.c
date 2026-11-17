// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,3를 OSS-Fuzz 하네스에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness.py, 기록: evaluation/artifacts/llm/combined/expat/).
/*
 * Copyright (C) 2016 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <assert.h>
#include <limits.h> // for INT_MAX
#include <stdint.h>
#include <string.h>

#include "expat.h"
#include "siphash.h"

// Macros to convert preprocessor macros to string literals. See
// https://gcc.gnu.org/onlinedocs/gcc-3.4.3/cpp/Stringification.html
#define xstr(s) str(s)
#define str(s) #s

// The encoder type that we wish to fuzz should come from the compile-time
// definition `ENCODING_FOR_FUZZING`. This allows us to have a separate fuzzer
// binary for
#ifndef ENCODING_FOR_FUZZING
#  error "ENCODING_FOR_FUZZING was not provided to this fuzz target."
#endif

// 16-byte deterministic hash key.
static unsigned char hash_key_1[16] = "FUZZING IS FUN?";
static unsigned char hash_key_2[16] = "FUZZING IS FUN!";

static void XMLCALL
start(void *userData, const XML_Char *name, const XML_Char **atts) {
  (void)userData;
  (void)name;
  (void)atts;
}
static void XMLCALL
end(void *userData, const XML_Char *name) {
  (void)userData;
  (void)name;
}

static void XMLCALL
may_stop_character_handler(void *userData, const XML_Char *s, int len) {
  XML_Parser parser = (XML_Parser)userData;
  if (len > 1 && s[0] == 's') {
    XML_StopParser(parser, s[1] == 'r' ? XML_FALSE : XML_TRUE);
  }
}

// 입력 앞쪽 바이트 배분 (서로 겹치지 않음):
//   data[0]      : XML_ParserReset의 encoding 선택
//   data[1]      : XML_Parse 두 호출의 s에 NULL을 넘길지 선택 (하위 3비트 / 다음 3비트)
//   data[2]      : 첫 번째 ExternalEntityParserCreate의 context 선택
//   data[3]      : 두 번째 ExternalEntityParserCreate의 context 선택
//   data[4..19]  : 첫 번째 context 문자열 재료
//   data[20..35] : 두 번째 context 문자열 재료
#define CONTEXT_BUF_LEN 17 // [gapfuzz-llm] context 문자열 버퍼 (최대 16자 + NUL)

static void
ParseOneInput(XML_Parser p, const uint8_t *data, size_t size) {
  // Set the hash salt using siphash to generate a deterministic hash.
  // The salt is 16 bytes and siphash24 produces 8, so the input is hashed
  // under two keys.
  const uint64_t first = siphash24(data, size, sip_keyof(hash_key_1));
  const uint64_t second = siphash24(data, size, sip_keyof(hash_key_2));
  uint8_t entropy[16];
  memcpy(entropy, &first, sizeof(first));
  memcpy(entropy + sizeof(first), &second, sizeof(second));
  XML_SetHashSalt16Bytes(p, entropy);
  (void)sip24_valid;

  XML_SetUserData(p, p);
  XML_SetElementHandler(p, start, end);
  XML_SetCharacterDataHandler(p, may_stop_character_handler);
  assert(size <= INT_MAX);
  const XML_Char *buf1 = (size > 1 && (data[1] & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] data[1] 하위 3비트로 가끔 s에 NULL을 넘겨 XML_Parse의 (s == NULL) 분기 도달 (그 외에는 원래 값)
  const XML_Char *buf2 = (size > 1 && ((data[1] >> 3) & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] 같은 바이트의 다른 비트로 두 번째 호출의 NULL 여부를 독립적으로 선택 (라이브러리가 INVALID_ARGUMENT로 안전하게 처리)
  XML_Parse(p, buf1, (int)size, 0); // [gapfuzz-llm] s가 NULL일 수 있도록 buf1 사용
  if (XML_Parse(p, buf2, (int)size, 1) == XML_STATUS_ERROR) { // [gapfuzz-llm] s가 NULL일 수 있도록 buf2 사용
    XML_ErrorString(XML_GetErrorCode(p));
  }
  XML_GetCurrentLineNumber64(p);
  if (size % 2) {
    static const XML_Char *const reset_encodings[] = {
        NULL, "UTF-8", "UTF-16", "ISO-8859-1", "US-ASCII", "UTF-16LE", "UTF-16BE"}; // [gapfuzz-llm] NULL 외에 실제 인코딩 이름 후보를 마련해 encodingName 참 분기 도달
    const size_t reset_encoding_count
        = sizeof(reset_encodings) / sizeof(reset_encodings[0]);
    const XML_Char *reset_encoding
        = reset_encodings[data[0] % reset_encoding_count]; // [gapfuzz-llm] 입력 첫 바이트로 인코딩을 고르며 NULL(원래 값)도 계속 나옴 (size가 홀수라 data[0] 접근 안전)
    XML_ParserReset(p, reset_encoding); // [gapfuzz-llm] 고정된 NULL 대신 퍼저 입력에서 고른 encoding을 전달
  }
}

// [gapfuzz-llm] context 인자를 입력에서 고르는 헬퍼: "e1" / NULL / 입력으로 만든 문자열('=' 또는 '\f' 구분자 포함 가능)
static const XML_Char *
pick_context(const uint8_t *data, size_t size, size_t selector_index,
             size_t string_offset, XML_Char *buf) {
  uint8_t selector = selector_index < size ? data[selector_index] : 0;
  switch (selector % 4) {
  case 0:
    return "e1";
  case 1:
    return NULL;
  default: {
    size_t n = 0;
    if (string_offset < size) {
      n = size - string_offset;
      if (n > CONTEXT_BUF_LEN - 1)
        n = CONTEXT_BUF_LEN - 1;
      memcpy(buf, data + string_offset, n);
    }
    buf[n] = '\0';
    return buf;
  }
  }
}

int
LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  XML_Parser parentParser = XML_ParserCreate(xstr(ENCODING_FOR_FUZZING));
  assert(parentParser);
  ParseOneInput(parentParser, data, size);
  // not freed yet, but used later and freed then

  XML_Parser namespaceParser = XML_ParserCreateNS(NULL, '!');
  assert(namespaceParser);
  ParseOneInput(namespaceParser, data, size);
  XML_ParserFree(namespaceParser);

  XML_Char contextBuf1[CONTEXT_BUF_LEN]; // [gapfuzz-llm] 첫 번째 context 문자열 버퍼
  XML_Char contextBuf2[CONTEXT_BUF_LEN]; // [gapfuzz-llm] 두 번째 context 문자열 버퍼

  XML_Parser externalEntityParser
      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 2, 4, contextBuf1), NULL); // [gapfuzz-llm] context를 "e1"/NULL뿐 아니라 입력에서 만든 문자열로도 고르게 하여 setContext 분기 도달 (다른 수정과 안 겹치게 data[2], data[4..19] 사용)
  if (externalEntityParser != NULL) {
    ParseOneInput(externalEntityParser, data, size);
    XML_ParserFree(externalEntityParser);
  }

  XML_Parser externalDtdParser
      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 3, 20, contextBuf2), NULL); // [gapfuzz-llm] NULL 외에 "e1"과 입력 기반 context 문자열도 나오게 함 (data[3], data[20..35] 사용)
  if (externalDtdParser != NULL) {
    ParseOneInput(externalDtdParser, data, size);
    XML_ParserFree(externalDtdParser);
  }

  // finally frees this parser which served as parent
  XML_ParserFree(parentParser);
  return 0;
}
