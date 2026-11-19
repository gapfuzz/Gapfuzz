라이브러리: expat
하네스 파일: official_parsebuffer.c

## gapfuzz의 제안
`XML_SetHashSalt16Bytes(XML_Parser, const uint8_t *)`의 2번째 인자 `entropy`에 하네스가 null을 넘긴 적이 없습니다(72행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XML_SetHashSalt16Bytes(XML_Parser, const uint8_t *)` 2316행, 조건 `entropy == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2312  XML_SetHashSalt16Bytes(XML_Parser parser, const uint8_t entropy[16]) {
 2313    if (parser == NULL)
 2314      return XML_FALSE;
 2315  
 2316>   if (entropy == NULL)
 2317      return XML_FALSE;
 2318  
 2319    const XML_Parser rootParser = getRootParserOf(parser, NULL);
 2320    assert(! rootParser->m_parentParser);
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: libexpat 저장소 expat/fuzz/xml_parsebuffer_fuzzer.c (커밋 f136824) 그대로.
   2  /*
   3   * Copyright (C) 2016 The Android Open Source Project
   4   *
   5   * Licensed under the Apache License, Version 2.0 (the "License");
   6   * you may not use this file except in compliance with the License.
   7   * You may obtain a copy of the License at
   8   *
   9   *      https://www.apache.org/licenses/LICENSE-2.0
  10   *
  11   * Unless required by applicable law or agreed to in writing, software
  12   * distributed under the License is distributed on an "AS IS" BASIS,
  13   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  14   * See the License for the specific language governing permissions and
  15   * limitations under the License.
  16   */
  17  
  18  #include <assert.h>
  19  #include <limits.h> // for INT_MAX
  20  #include <stdint.h>
  21  #include <string.h>
  22  
  23  #include "expat.h"
  24  #include "siphash.h"
  25  
  26  // Macros to convert preprocessor macros to string literals. See
  27  // https://gcc.gnu.org/onlinedocs/gcc-3.4.3/cpp/Stringification.html
  28  #define xstr(s) str(s)
  29  #define str(s) #s
  30  
  31  // The encoder type that we wish to fuzz should come from the compile-time
  32  // definition `ENCODING_FOR_FUZZING`. This allows us to have a separate fuzzer
  33  // binary for
  34  #ifndef ENCODING_FOR_FUZZING
  35  #  error "ENCODING_FOR_FUZZING was not provided to this fuzz target."
  36  #endif
  37  
  38  // 16-byte deterministic hash key.
  39  static unsigned char hash_key_1[16] = "FUZZING IS FUN?";
  40  static unsigned char hash_key_2[16] = "FUZZING IS FUN!";
  41  
  42  static void XMLCALL
  43  start(void *userData, const XML_Char *name, const XML_Char **atts) {
  44    (void)userData;
  45    (void)name;
  46    (void)atts;
  47  }
  48  static void XMLCALL
  49  end(void *userData, const XML_Char *name) {
  50    (void)userData;
  51    (void)name;
  52  }
  53  
  54  static void XMLCALL
  55  may_stop_character_handler(void *userData, const XML_Char *s, int len) {
  56    XML_Parser parser = (XML_Parser)userData;
  57    if (len > 1 && s[0] == 's') {
  58      XML_StopParser(parser, s[1] == 'r' ? XML_FALSE : XML_TRUE);
  59    }
  60  }
  61  
  62  static void
  63  ParseOneInput(XML_Parser p, const uint8_t *data, size_t size) {
  64    // Set the hash salt using siphash to generate a deterministic hash.
  65    // The salt is 16 bytes and siphash24 produces 8, so the input is hashed
  66    // under two keys.
  67    const uint64_t first = siphash24(data, size, sip_keyof(hash_key_1));
  68    const uint64_t second = siphash24(data, size, sip_keyof(hash_key_2));
  69    uint8_t entropy[16];
  70    memcpy(entropy, &first, sizeof(first));
  71    memcpy(entropy + sizeof(first), &second, sizeof(second));
  72    XML_SetHashSalt16Bytes(p, entropy);
  73    (void)sip24_valid;
  74  
  75    XML_SetUserData(p, p);
  76    XML_SetElementHandler(p, start, end);
  77    XML_SetCharacterDataHandler(p, may_stop_character_handler);
  78    assert(size <= INT_MAX);
  79    void *buf = XML_GetBuffer(p, (int)size);
  80    assert(buf);
  81    memcpy(buf, data, size);
  82    XML_ParseBuffer(p, (int)size, 0);
  83    buf = XML_GetBuffer(p, (int)size);
  84    if (buf == NULL) {
  85      return;
  86    }
  87    memcpy(buf, data, size);
  88    if (XML_ParseBuffer(p, (int)size, 1) == XML_STATUS_ERROR) {
  89      XML_ErrorString(XML_GetErrorCode(p));
  90    }
  91    XML_GetCurrentLineNumber64(p);
  92    if (size % 2) {
  93      XML_ParserReset(p, NULL);
  94    }
  95  }
  96  
  97  int
  98  LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  99    if (size == 0)
 100      return 0;
 101  
 102    XML_Parser parentParser = XML_ParserCreate(xstr(ENCODING_FOR_FUZZING));
 103    assert(parentParser);
 104    ParseOneInput(parentParser, data, size);
 105    // not freed yet, but used later and freed then
 106  
 107    XML_Parser namespaceParser = XML_ParserCreateNS(NULL, '!');
 108    assert(namespaceParser);
 109    ParseOneInput(namespaceParser, data, size);
 110    XML_ParserFree(namespaceParser);
 111  
 112    XML_Parser externalEntityParser
 113        = XML_ExternalEntityParserCreate(parentParser, "e1", NULL);
 114    if (externalEntityParser != NULL) {
 115      ParseOneInput(externalEntityParser, data, size);
 116      XML_ParserFree(externalEntityParser);
 117    }
 118  
 119    XML_Parser externalDtdParser
 120        = XML_ExternalEntityParserCreate(parentParser, NULL, NULL);
 121    if (externalDtdParser != NULL) {
 122      ParseOneInput(externalDtdParser, data, size);
 123      XML_ParserFree(externalDtdParser);
 124    }
 125  
 126    // finally frees this parser which served as parent
 127    XML_ParserFree(parentParser);
 128    return 0;
 129  }
```