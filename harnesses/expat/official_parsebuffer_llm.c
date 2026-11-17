// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 3를 OSS-Fuzz 하네스 official_parsebuffer에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/expat/official_parsebuffer/).
// OSS-Fuzz 하네스: libexpat 저장소 expat/fuzz/xml_parsebuffer_fuzzer.c (커밋 f136824) 그대로.
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
  // 입력 첫 바이트의 최하위 비트가 1이면 entropy에 NULL을 넘기고, 아니면 기존 값을 넘김
  // (XML_SetHashSalt16Bytes는 NULL entropy를 문서상 허용하며 XML_FALSE를 반환함)
  XML_SetHashSalt16Bytes(p, (data[0] & 1) ? NULL : entropy); // [gapfuzz-llm] entropy == NULL 분기를 도달시키기 위해 입력 첫 바이트로 NULL을 고르게 함
  (void)sip24_valid;

  XML_SetUserData(p, p);
  XML_SetElementHandler(p, start, end);
  XML_SetCharacterDataHandler(p, may_stop_character_handler);
  assert(size <= INT_MAX);
  void *buf = XML_GetBuffer(p, (int)size);
  assert(buf);
  memcpy(buf, data, size);
  XML_ParseBuffer(p, (int)size, 0);
  buf = XML_GetBuffer(p, (int)size);
  if (buf == NULL) {
    return;
  }
  memcpy(buf, data, size);
  if (XML_ParseBuffer(p, (int)size, 1) == XML_STATUS_ERROR) {
    XML_ErrorString(XML_GetErrorCode(p));
  }
  XML_GetCurrentLineNumber64(p);
  if (size % 2) {
    XML_ParserReset(p, NULL);
  }
}

int
LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  if (size == 0)
    return 0;

  XML_Parser parentParser = XML_ParserCreate(xstr(ENCODING_FOR_FUZZING));
  assert(parentParser);
  ParseOneInput(parentParser, data, size);
  // not freed yet, but used later and freed then

  XML_Parser namespaceParser = XML_ParserCreateNS(NULL, '!');
  assert(namespaceParser);
  ParseOneInput(namespaceParser, data, size);
  XML_ParserFree(namespaceParser);

  XML_Parser externalEntityParser
      = XML_ExternalEntityParserCreate(parentParser, "e1", NULL);
  if (externalEntityParser != NULL) {
    ParseOneInput(externalEntityParser, data, size);
    XML_ParserFree(externalEntityParser);
  }

  XML_Parser externalDtdParser
      = XML_ExternalEntityParserCreate(parentParser, NULL, NULL);
  if (externalDtdParser != NULL) {
    ParseOneInput(externalDtdParser, data, size);
    XML_ParserFree(externalDtdParser);
  }

  // finally frees this parser which served as parent
  XML_ParserFree(parentParser);
  return 0;
}
