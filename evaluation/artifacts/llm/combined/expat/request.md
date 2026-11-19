라이브러리: expat
하네스 파일: official.c

아래 제안 3개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`XML_ParserReset(XML_Parser, const XML_Char *)`의 2번째 인자 `encoding`를 하네스가 고정합니다(84행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XML_ParserReset(XML_Parser, const XML_Char *)` 1668행, 조건 `encodingName`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1664  #endif
 1665  
 1666    // NOTE: This effectively checks for `copyString` having failed during the
 1667    //       call to `parserInit` above
 1668>   if (encodingName && ! parser->m_protocolEncodingName) {
 1669      parser->m_errorCode = XML_ERROR_NO_MEMORY;
 1670      return XML_FALSE;
 1671    }
 1672    return XML_TRUE;
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -81,7 +81,13 @@
   }
   XML_GetCurrentLineNumber64(p);
   if (size % 2) {
-    XML_ParserReset(p, NULL);
+    static const XML_Char *const reset_encodings[] = {
+        NULL, "UTF-8", "UTF-16", "ISO-8859-1", "US-ASCII", "UTF-16LE", "UTF-16BE"}; // [gapfuzz-llm] NULL 외에 실제 인코딩 이름 후보를 마련해 encodingName 참 분기 도달
+    const size_t reset_encoding_count
+        = sizeof(reset_encodings) / sizeof(reset_encodings[0]);
+    const XML_Char *reset_encoding
+        = reset_encodings[data[0] % reset_encoding_count]; // [gapfuzz-llm] 입력 첫 바이트로 인코딩을 고르며 NULL(원래 값)도 계속 나옴 (size가 홀수라 data[0] 접근 안전)
+    XML_ParserReset(p, reset_encoding); // [gapfuzz-llm] 고정된 NULL 대신 퍼저 입력에서 고른 encoding을 전달
   }
 }
```

## 제안 2
`XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)`의 2번째 인자 `context`를 하네스가 `"e1"`, `0` 중에서만 고릅니다(101행, 108행) (라이브러리 내부 `setContext`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (5개)
- `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8298행, 조건 `context == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 8294  }
 8295  
 8296  static XML_Bool
 8297  setContext(XML_Parser parser, const XML_Char *context) {
 8298>   if (context == NULL) {
 8299      return XML_FALSE;
 8300    }
 8301  
 8302    DTD *const dtd = parser->m_dtd; /* save one level of indirection */
```
- `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8306행, 조건 `*s == CONTEXT_SEP`가 퍼징 중 한 번도 '참'이 되지 않음
```
 8302    DTD *const dtd = parser->m_dtd; /* save one level of indirection */
 8303    const XML_Char *s = context;
 8304  
 8305    while (*context != XML_T('\0')) {
 8306>     if (*s == CONTEXT_SEP || *s == XML_T('\0')) {
 8307        ENTITY *e;
 8308        if (! poolAppendChar(&parser->m_tempPool, XML_T('\0')))
 8309          return XML_FALSE;
 8310        e = (ENTITY *)lookup(parser, &dtd->generalEntities,
```
- `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8314행, 조건 `*s != XML_T`가 퍼징 중 한 번도 '참'이 되지 않음
```
 8310        e = (ENTITY *)lookup(parser, &dtd->generalEntities,
 8311                             poolStart(&parser->m_tempPool), 0);
 8312        if (e)
 8313          e->open = true;
 8314>       if (*s != XML_T('\0'))
 8315          s++;
 8316        context = s;
 8317        poolDiscard(&parser->m_tempPool);
 8318      } else if (*s == XML_T(ASCII_EQUALS)) {
```
- `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8345행, 조건 `*context != CONTEXT_SEP`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 8341            return XML_FALSE;
 8342  
 8343          poolDiscard(&parser->m_tempPool);
 8344        }
 8345>       for (context = s + 1; *context != CONTEXT_SEP && *context != XML_T('\0');
 8346             context++)
 8347          if (! poolAppendChar(&parser->m_tempPool, *context))
 8348            return XML_FALSE;
 8349        if (! poolAppendChar(&parser->m_tempPool, XML_T('\0')))
```
- `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8356행, 조건 `*context != XML_T`가 퍼징 중 한 번도 '참'이 되지 않음
```
 8352                       &parser->m_inheritedBindings)
 8353            != XML_ERROR_NONE)
 8354          return XML_FALSE;
 8355        poolDiscard(&parser->m_tempPool);
 8356>       if (*context != XML_T('\0'))
 8357          ++context;
 8358        s = context;
 8359      } else {
 8360        if (! poolAppendChar(&parser->m_tempPool, *s))
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -85,6 +85,34 @@
   }
 }
 
+#define CONTEXT_BUF_LEN 33
+
+// Picks the context argument from the fuzzer input. The selector byte decides
+// between the original values ("e1" / NULL) and a NUL-terminated string built
+// from the input bytes (which may contain '=' or '\f' separators).
+static const XML_Char *
+pick_context(const uint8_t *data, size_t size, size_t selector_index,
+             size_t string_offset, XML_Char *buf) {
+  uint8_t selector = selector_index < size ? data[selector_index] : 0;
+  switch (selector % 4) {
+  case 0:
+    return "e1";
+  case 1:
+    return NULL;
+  default: {
+    size_t n = 0;
+    if (string_offset < size) {
+      n = size - string_offset;
+      if (n > CONTEXT_BUF_LEN - 1)
+        n = CONTEXT_BUF_LEN - 1;
+      memcpy(buf, data + string_offset, n);
+    }
+    buf[n] = '\0';
+    return buf;
+  }
+  }
+}
+
 int
 LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   XML_Parser parentParser = XML_ParserCreate(xstr(ENCODING_FOR_FUZZING));
@@ -97,15 +125,18 @@
   ParseOneInput(namespaceParser, data, size);
   XML_ParserFree(namespaceParser);
 
+  XML_Char contextBuf1[CONTEXT_BUF_LEN];
+  XML_Char contextBuf2[CONTEXT_BUF_LEN];
+
   XML_Parser externalEntityParser
-      = XML_ExternalEntityParserCreate(parentParser, "e1", NULL);
+      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 0, 2, contextBuf1), NULL); // [gapfuzz-llm] context를 "e1"/NULL뿐 아니라 입력에서 만든 문자열로도 고르게 하여 setContext 분기 도달
   if (externalEntityParser != NULL) {
     ParseOneInput(externalEntityParser, data, size);
     XML_ParserFree(externalEntityParser);
   }
 
   XML_Parser externalDtdParser
-      = XML_ExternalEntityParserCreate(parentParser, NULL, NULL);
+      = XML_ExternalEntityParserCreate(parentParser, pick_context(data, size, 1, 18, contextBuf2), NULL); // [gapfuzz-llm] NULL 외에 "e1"과 입력 기반 context 문자열도 나오게 함
   if (externalDtdParser != NULL) {
     ParseOneInput(externalDtdParser, data, size);
     XML_ParserFree(externalDtdParser);
```

## 제안 3
`XML_Parse(XML_Parser, const char *, int, int)`의 2번째 인자 `s`에 하네스가 null을 넘긴 적이 없습니다(78행, 79행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XML_Parse(XML_Parser, const char *, int, int)` 2339행, 조건 `(s == NULL)`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2335  enum XML_Status XMLCALL
 2336  XML_Parse(XML_Parser parser, const char *s, int len, int isFinal) {
 2337    if (parser == NULL || isCalledFromInsideHandler(parser))
 2338      return XML_STATUS_ERROR;
 2339>   if ((len < 0) || ((s == NULL) && (len != 0))) {
 2340      parser->m_errorCode = XML_ERROR_INVALID_ARGUMENT;
 2341      return XML_STATUS_ERROR;
 2342    }
 2343    switch (parser->m_parsingStatus.parsing) {
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -75,8 +75,10 @@
   XML_SetElementHandler(p, start, end);
   XML_SetCharacterDataHandler(p, may_stop_character_handler);
   assert(size <= INT_MAX);
-  XML_Parse(p, (const XML_Char *)data, (int)size, 0);
-  if (XML_Parse(p, (const XML_Char *)data, (int)size, 1) == XML_STATUS_ERROR) {
+  const XML_Char *buf1 = (size > 0 && (data[0] & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] 입력 첫 바이트로 가끔 s에 NULL을 넘겨 XML_Parse의 (s == NULL) 분기를 도달시킴 (그 외에는 원래 값)
+  const XML_Char *buf2 = (size > 0 && ((data[0] >> 3) & 7) == 0) ? NULL : (const XML_Char *)data; // [gapfuzz-llm] 두 번째 호출도 입력 바이트로 NULL 여부를 독립적으로 선택 (라이브러리가 INVALID_ARGUMENT로 안전하게 처리)
+  XML_Parse(p, buf1, (int)size, 0); // [gapfuzz-llm] s가 NULL일 수 있도록 buf1 사용
+  if (XML_Parse(p, buf2, (int)size, 1) == XML_STATUS_ERROR) { // [gapfuzz-llm] s가 NULL일 수 있도록 buf2 사용
     XML_ErrorString(XML_GetErrorCode(p));
   }
   XML_GetCurrentLineNumber64(p);
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  /*
   2   * Copyright (C) 2016 The Android Open Source Project
   3   *
   4   * Licensed under the Apache License, Version 2.0 (the "License");
   5   * you may not use this file except in compliance with the License.
   6   * You may obtain a copy of the License at
   7   *
   8   *      https://www.apache.org/licenses/LICENSE-2.0
   9   *
  10   * Unless required by applicable law or agreed to in writing, software
  11   * distributed under the License is distributed on an "AS IS" BASIS,
  12   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  13   * See the License for the specific language governing permissions and
  14   * limitations under the License.
  15   */
  16  
  17  #include <assert.h>
  18  #include <limits.h> // for INT_MAX
  19  #include <stdint.h>
  20  #include <string.h>
  21  
  22  #include "expat.h"
  23  #include "siphash.h"
  24  
  25  // Macros to convert preprocessor macros to string literals. See
  26  // https://gcc.gnu.org/onlinedocs/gcc-3.4.3/cpp/Stringification.html
  27  #define xstr(s) str(s)
  28  #define str(s) #s
  29  
  30  // The encoder type that we wish to fuzz should come from the compile-time
  31  // definition `ENCODING_FOR_FUZZING`. This allows us to have a separate fuzzer
  32  // binary for
  33  #ifndef ENCODING_FOR_FUZZING
  34  #  error "ENCODING_FOR_FUZZING was not provided to this fuzz target."
  35  #endif
  36  
  37  // 16-byte deterministic hash key.
  38  static unsigned char hash_key_1[16] = "FUZZING IS FUN?";
  39  static unsigned char hash_key_2[16] = "FUZZING IS FUN!";
  40  
  41  static void XMLCALL
  42  start(void *userData, const XML_Char *name, const XML_Char **atts) {
  43    (void)userData;
  44    (void)name;
  45    (void)atts;
  46  }
  47  static void XMLCALL
  48  end(void *userData, const XML_Char *name) {
  49    (void)userData;
  50    (void)name;
  51  }
  52  
  53  static void XMLCALL
  54  may_stop_character_handler(void *userData, const XML_Char *s, int len) {
  55    XML_Parser parser = (XML_Parser)userData;
  56    if (len > 1 && s[0] == 's') {
  57      XML_StopParser(parser, s[1] == 'r' ? XML_FALSE : XML_TRUE);
  58    }
  59  }
  60  
  61  static void
  62  ParseOneInput(XML_Parser p, const uint8_t *data, size_t size) {
  63    // Set the hash salt using siphash to generate a deterministic hash.
  64    // The salt is 16 bytes and siphash24 produces 8, so the input is hashed
  65    // under two keys.
  66    const uint64_t first = siphash24(data, size, sip_keyof(hash_key_1));
  67    const uint64_t second = siphash24(data, size, sip_keyof(hash_key_2));
  68    uint8_t entropy[16];
  69    memcpy(entropy, &first, sizeof(first));
  70    memcpy(entropy + sizeof(first), &second, sizeof(second));
  71    XML_SetHashSalt16Bytes(p, entropy);
  72    (void)sip24_valid;
  73  
  74    XML_SetUserData(p, p);
  75    XML_SetElementHandler(p, start, end);
  76    XML_SetCharacterDataHandler(p, may_stop_character_handler);
  77    assert(size <= INT_MAX);
  78    XML_Parse(p, (const XML_Char *)data, (int)size, 0);
  79    if (XML_Parse(p, (const XML_Char *)data, (int)size, 1) == XML_STATUS_ERROR) {
  80      XML_ErrorString(XML_GetErrorCode(p));
  81    }
  82    XML_GetCurrentLineNumber64(p);
  83    if (size % 2) {
  84      XML_ParserReset(p, NULL);
  85    }
  86  }
  87  
  88  int
  89  LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  90    XML_Parser parentParser = XML_ParserCreate(xstr(ENCODING_FOR_FUZZING));
  91    assert(parentParser);
  92    ParseOneInput(parentParser, data, size);
  93    // not freed yet, but used later and freed then
  94  
  95    XML_Parser namespaceParser = XML_ParserCreateNS(NULL, '!');
  96    assert(namespaceParser);
  97    ParseOneInput(namespaceParser, data, size);
  98    XML_ParserFree(namespaceParser);
  99  
 100    XML_Parser externalEntityParser
 101        = XML_ExternalEntityParserCreate(parentParser, "e1", NULL);
 102    if (externalEntityParser != NULL) {
 103      ParseOneInput(externalEntityParser, data, size);
 104      XML_ParserFree(externalEntityParser);
 105    }
 106  
 107    XML_Parser externalDtdParser
 108        = XML_ExternalEntityParserCreate(parentParser, NULL, NULL);
 109    if (externalDtdParser != NULL) {
 110      ParseOneInput(externalDtdParser, data, size);
 111      XML_ParserFree(externalDtdParser);
 112    }
 113  
 114    // finally frees this parser which served as parent
 115    XML_ParserFree(parentParser);
 116    return 0;
 117  }
```