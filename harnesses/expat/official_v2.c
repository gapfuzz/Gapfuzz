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

// expat 공식 하네스(xml_parse_fuzzer.c)에 gapfuzz 제안을 적용한 버전 (official_v2).
//
// 입력 첫 바이트를 설정으로 쓰고(입력이 2바이트 이상일 때만), 나머지는 공식 하네스와 같이 파싱한다.
//   제안 1 (FIXED)  XML_ParserReset의 encoding: 항상 NULL → 이름 목록에서 입력으로 고름
//   제안 2 (NARROW) XML_ExternalEntityParserCreate의 context: "e1"/NULL만 → 입력 일부를 context 문자열로
//   제안 3 (NARROW) XML_Parse의 s: NULL을 넘긴 적 없음 → 가끔 NULL(길이 1)로도 부름
//   제안 4 (NARROW, XML_SetHashSalt16Bytes에 NULL)는 대조군으로 일부러 적용하지 않음
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

static const char *const kEncodings[] = {NULL,      "UTF-8",    "UTF-16",   "UTF-16LE",
                                         "UTF-16BE", "ISO-8859-1", "US-ASCII", "bogus"};
static uint8_t g_cfg;   // 입력 첫 바이트: 비트 0-2 인코딩, 비트 3 NULL로 XML_Parse, 비트 4 context를 입력에서

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
  if (g_cfg & 0x08)
    XML_Parse(p, NULL, 1, 0);   // 제안 3: s == NULL (길이 0이 아니면 인자 오류 분기)
  XML_Parse(p, (const XML_Char *)data, (int)size, 0);
  if (XML_Parse(p, (const XML_Char *)data, (int)size, 1) == XML_STATUS_ERROR) {
    XML_ErrorString(XML_GetErrorCode(p));
  }
  XML_GetCurrentLineNumber64(p);
  if (size % 2) {
    XML_ParserReset(p, kEncodings[g_cfg & 0x07]);   // 제안 1
  }
}

int
LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  g_cfg = 0;
  if (size >= 2) {
    g_cfg = data[0];
    data++;
    size--;
  }
  // 제안 2: context 문자열을 입력 앞부분(최대 32바이트, '\0'까지)에서 만든다
  char context[33] = "e1";
  if (g_cfg & 0x10) {
    size_t n = size < 32 ? size : 32;
    memcpy(context, data, n);
    context[n] = '\0';
  }

  XML_Parser parentParser = XML_ParserCreate(xstr(ENCODING_FOR_FUZZING));
  assert(parentParser);
  ParseOneInput(parentParser, data, size);
  // not freed yet, but used later and freed then

  XML_Parser namespaceParser = XML_ParserCreateNS(NULL, '!');
  assert(namespaceParser);
  ParseOneInput(namespaceParser, data, size);
  XML_ParserFree(namespaceParser);

  XML_Parser externalEntityParser
      = XML_ExternalEntityParserCreate(parentParser, context, NULL);
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
