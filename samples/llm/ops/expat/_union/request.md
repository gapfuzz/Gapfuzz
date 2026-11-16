라이브러리: expat
OSS-Fuzz 하네스 2개(official, official_parsebuffer)의 커버리지를 모두 합쳐도, 공개 API 83개 중 66개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `XML_SetPropertyDouble(XML_Parser, enum XML_Parser_Property, double)` — 새로 실행될 수 있는 코드 영역 33개
```
XML_SetPropertyDouble(XML_Parser parser, enum XML_Parser_Property property,
                      double value);
```

### 2. `XML_ResumeParser(XML_Parser)` — 새로 실행될 수 있는 코드 영역 26개
```
XML_ResumeParser(XML_Parser parser);
```

### 3. `XML_SetPropertyUInt64(XML_Parser, enum XML_Parser_Property, uint64_t)` — 새로 실행될 수 있는 코드 영역 25개
```
XML_SetPropertyUInt64(XML_Parser parser, enum XML_Parser_Property property,
                      uint64_t value);
```

### 4. `XML_GetInputContext(XML_Parser, int *, int *)` — 새로 실행될 수 있는 코드 영역 25개
```
XML_GetInputContext(XML_Parser parser, int *offset, int *size);
```

### 5. `XML_SetPropertyBool(XML_Parser, enum XML_Parser_Property, XML_Bool)` — 새로 실행될 수 있는 코드 영역 23개
```
XML_SetPropertyBool(XML_Parser parser, enum XML_Parser_Property property,
                    XML_Bool value);
```

### 6. `XML_DefaultCurrent(XML_Parser)` — 새로 실행될 수 있는 코드 영역 23개
```
XML_DefaultCurrent(XML_Parser parser);
/* If do_nst is non-zero, and namespace processing is in effect, and
   a name has a prefix (i.e. an explicit namespace qualifier) then
   that name is returned as a triplet in a single string separated by
   the separator character specified when the parser was created: URI
   + sep + local_name + sep + prefix.

   If do_nst is zero, then namespace information is returned in the
   default manner (URI + sep + local_name) whether or not the name
   has a prefix.

   Note: Calling XML_SetReturnNSTriplet after XML_Parse or
     XML_ParseBuffer has no effect.
*/
```

### 7. `XML_SetEncoding(XML_Parser, const XML_Char *)` — 새로 실행될 수 있는 코드 영역 18개
```
XML_SetEncoding(XML_Parser parser, const XML_Char *encoding);
/* If this function is called, then the parser will be passed as the
   first argument to callbacks instead of userData.  The userData will
   still be accessible using XML_GetUserData.
*/
```

### 8. `XML_GetFeatureList(void)` — 새로 실행될 수 있는 코드 영역 16개
```
XML_GetFeatureList(void);
/* Added in Expat 2.9.0. */
```

### 9. `XML_SetHashSalt(XML_Parser, unsigned long)` — 새로 실행될 수 있는 코드 영역 15개
```
XML_SetHashSalt(XML_Parser parser, unsigned long hash_salt);
/* Sets the hash salt to use for internal hash calculations.
   Helps in preventing DoS attacks based on predicting hash function behavior.
   This must be called before parsing is started.
   Returns XML_TRUE if successful, XML_FALSE when called after parsing has
   started or when parser is NULL.
   Added in Expat 2.8.0.
*/
```

### 10. `XML_SetBase(XML_Parser, const XML_Char *)` — 새로 실행될 수 있는 코드 영역 14개
```
XML_SetBase(XML_Parser parser, const XML_Char *base);
```

## 참고: 기존 하네스 official.c (고치지 마세요. include와 작성 방식만 참고)
```
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
  XML_SetHashSalt16Bytes(p, entropy);
  (void)sip24_valid;

  XML_SetUserData(p, p);
  XML_SetElementHandler(p, start, end);
  XML_SetCharacterDataHandler(p, may_stop_character_handler);
  assert(size <= INT_MAX);
  XML_Parse(p, (const XML_Char *)data, (int)size, 0);
  if (XML_Parse(p, (const XML_Char *)data, (int)size, 1) == XML_STATUS_ERROR) {
    XML_ErrorString(XML_GetErrorCode(p));
  }
  XML_GetCurrentLineNumber64(p);
  if (size % 2) {
    XML_ParserReset(p, NULL);
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

```