라이브러리: libyaml
하네스 파일: official_deconstructor.c

아래 제안 6개를 **모두 한 하네스에** 적용하세요.

## 제안 2
`yaml_scalar_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, const yaml_char_t *, int, int, int, yaml_scalar_style_t)`의 2번째 인자 `anchor`를 하네스가 고정합니다(117행에서 항상 `0`, 126행에서 항상 `0`, 140행에서 항상 `0`, 149행에서 항상 `0`, 170행에서 항상 `0`, 179행에서 항상 `0`, 192행에서 항상 `0`, 201행에서 항상 `0`, 217행에서 항상 `0`, 235행에서 항상 `0`, 245행에서 항상 `0`, 254행에서 항상 `0`, 264행에서 항상 `0`, 286행에서 항상 `0`, 315행에서 항상 `0`, 324행에서 항상 `0`, 334행에서 항상 `0`, 343행에서 항상 `0`, 369행에서 항상 `0`, 378행에서 항상 `0`, 394행에서 항상 `0`, 403행에서 항상 `0`, 412행에서 항상 `0`, 421행에서 항상 `0`, 436행에서 항상 `0`, 445행에서 항상 `0`, 454행에서 항상 `0`, 463행에서 항상 `0`, 477행에서 항상 `0`, 486행에서 항상 `0`, 498행에서 항상 `0`, 507행에서 항상 `0`, 521행에서 항상 `0`, 530행에서 항상 `0`, 543행에서 항상 `0`, 552행에서 항상 `0`, 564행에서 항상 `0`, 582행에서 항상 `0`, 591행에서 항상 `0`, 602행에서 항상 `0`, 611행에서 항상 `0`, 635행에서 항상 `0`, 644행에서 항상 `0`, 671행에서 항상 `0`, 680행에서 항상 `0`, 693행에서 항상 `0`, 702행에서 항상 `0`, 716행에서 항상 `0`, 725행에서 항상 `0`, 736행에서 항상 `0`, 745행에서 항상 `0`, 762행에서 항상 `0`, 771행에서 항상 `0`, 790행에서 항상 `0`, 799행에서 항상 `0`, 812행에서 항상 `0`, 821행에서 항상 `0`, 834행에서 항상 `0`, 843행에서 항상 `0`, 857행에서 항상 `0`, 866행에서 항상 `0`, 877행에서 항상 `0`, 886행에서 항상 `0`, 903행에서 항상 `0`, 912행에서 항상 `0`, 931행에서 항상 `0`, 940행에서 항상 `0`) (라이브러리 내부 `yaml_strdup`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)` 63행, 조건 `!str`가 퍼징 중 한 번도 '참'이 되지 않음
```
   59  
   60  YAML_DECLARE(yaml_char_t *)
   61  yaml_strdup(const yaml_char_t *str)
   62  {
   63>     if (!str)
   64          return NULL;
   65  
   66      return (yaml_char_t *)strdup((char *)str);
   67  }
```
- `yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)` 647행, 조건 `pointer+width > end`가 퍼징 중 한 번도 '참'이 되지 않음
```
  643                  (octet & 0xE0) == 0xC0 ? octet & 0x1F :
  644                  (octet & 0xF0) == 0xE0 ? octet & 0x0F :
  645                  (octet & 0xF8) == 0xF0 ? octet & 0x07 : 0;
  646          if (!width) return 0;
  647>         if (pointer+width > end) return 0;
  648          for (k = 1; k < width; k ++) {
  649              octet = pointer[k];
  650              if ((octet & 0xC0) != 0x80) return 0;
  651              value = (value << 6) + (octet & 0x3F);
```
- `yaml_scalar_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, const yaml_char_t *, int, int, int, yaml_scalar_style_t)` 835행, 조건 `anchor`가 퍼징 중 한 번도 '참'이 되지 않음
```
  831  
  832      assert(event);      /* Non-NULL event object is expected. */
  833      assert(value);      /* Non-NULL anchor is expected. */
  834  
  835>     if (anchor) {
  836          if (!yaml_check_utf8(anchor, strlen((char *)anchor))) goto error;
  837          anchor_copy = yaml_strdup(anchor);
  838          if (!anchor_copy) goto error;
  839      }
```

## 제안 3
`yaml_sequence_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_sequence_style_t)`의 3번째 인자 `tag`를 하네스가 고정합니다(82행에서 항상 `"tag:yaml.org,2002:seq"`, 295행에서 항상 `"tag:yaml.org,2002:seq"`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `yaml_sequence_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_sequence_style_t)` 891행, 조건 `tag`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  887          anchor_copy = yaml_strdup(anchor);
  888          if (!anchor_copy) goto error;
  889      }
  890  
  891>     if (tag) {
  892          if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
  893          tag_copy = yaml_strdup(tag);
  894          if (!tag_copy) goto error;
  895      }
```
- `yaml_sequence_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_sequence_style_t)` 892행, 조건 `!yaml_check_utf8(tag, strlen((char *)tag))`가 퍼징 중 한 번도 '참'이 되지 않음
```
  888          if (!anchor_copy) goto error;
  889      }
  890  
  891      if (tag) {
  892>         if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
  893          tag_copy = yaml_strdup(tag);
  894          if (!tag_copy) goto error;
  895      }
  896  
```

## 제안 4
`yaml_mapping_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_mapping_style_t)`의 3번째 인자 `tag`를 하네스가 고정합니다(103행에서 항상 `"tag:yaml.org,2002:map"`, 226행에서 항상 `"tag:yaml.org,2002:map"`, 306행에서 항상 `"tag:yaml.org,2002:map"`, 573행에서 항상 `"tag:yaml.org,2002:map"`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `yaml_mapping_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_mapping_style_t)` 946행, 조건 `tag`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  942          anchor_copy = yaml_strdup(anchor);
  943          if (!anchor_copy) goto error;
  944      }
  945  
  946>     if (tag) {
  947          if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
  948          tag_copy = yaml_strdup(tag);
  949          if (!tag_copy) goto error;
  950      }
```
- `yaml_mapping_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_mapping_style_t)` 947행, 조건 `!yaml_check_utf8(tag, strlen((char *)tag))`가 퍼징 중 한 번도 '참'이 되지 않음
```
  943          if (!anchor_copy) goto error;
  944      }
  945  
  946      if (tag) {
  947>         if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
  948          tag_copy = yaml_strdup(tag);
  949          if (!tag_copy) goto error;
  950      }
  951  
```

## 제안 5
`yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)`의 2번째 인자 `version_directive`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)` 725행, 조건 `version_directive`가 퍼징 중 한 번도 '참'이 되지 않음
```
  721      assert((tag_directives_start && tag_directives_end) ||
  722              (tag_directives_start == tag_directives_end));
  723                              /* Valid tag directives are expected. */
  724  
  725>     if (version_directive) {
  726          version_directive_copy = YAML_MALLOC_STATIC(yaml_version_directive_t);
  727          if (!version_directive_copy) goto error;
  728          version_directive_copy->major = version_directive->major;
  729          version_directive_copy->minor = version_directive->minor;
```

## 제안 6
`yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)`의 3번째 인자 `tag_directives_start`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)` 732행, 조건 `tag_directives_start != tag_directives_end`가 퍼징 중 한 번도 '참'이 되지 않음
```
  728          version_directive_copy->major = version_directive->major;
  729          version_directive_copy->minor = version_directive->minor;
  730      }
  731  
  732>     if (tag_directives_start != tag_directives_end) {
  733          yaml_tag_directive_t *tag_directive;
  734          if (!STACK_INIT(&context, tag_directives_copy, yaml_tag_directive_t*))
  735              goto error;
  736          for (tag_directive = tag_directives_start;
```

## 제안 10
`yaml_scalar_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, const yaml_char_t *, int, int, int, yaml_scalar_style_t)`의 3번째 인자 `tag`를 하네스가 `"tag:yaml.org,2002:str"`, `"tag:yaml.org,2002:int"`, `"tag:yaml.org,2002:bool"` 중에서만 고릅니다(117행, 126행, 140행, 149행, 170행, 179행, 192행, 201행, 217행, 235행, 245행, 254행, 264행, 286행, 315행, 324행, 334행, 343행, 369행, 378행, 394행, 403행, 412행, 421행, 436행, 445행, 454행, 463행, 477행, 486행, 498행, 507행, 521행, 530행, 543행, 552행, 564행, 582행, 591행, 602행, 611행, 635행, 644행, 671행, 680행, 693행, 702행, 716행, 725행, 736행, 745행, 762행, 771행, 790행, 799행, 812행, 821행, 834행, 843행, 857행, 866행, 877행, 886행, 903행, 912행, 931행, 940행) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `yaml_scalar_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, const yaml_char_t *, int, int, int, yaml_scalar_style_t)` 841행, 조건 `tag`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  837          anchor_copy = yaml_strdup(anchor);
  838          if (!anchor_copy) goto error;
  839      }
  840  
  841>     if (tag) {
  842          if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
  843          tag_copy = yaml_strdup(tag);
  844          if (!tag_copy) goto error;
  845      }
```
- `yaml_scalar_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, const yaml_char_t *, int, int, int, yaml_scalar_style_t)` 842행, 조건 `!yaml_check_utf8(tag, strlen((char *)tag))`가 퍼징 중 한 번도 '참'이 되지 않음
```
  838          if (!anchor_copy) goto error;
  839      }
  840  
  841      if (tag) {
  842>         if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
  843          tag_copy = yaml_strdup(tag);
  844          if (!tag_copy) goto error;
  845      }
  846  
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/libyaml/libyaml_deconstructor_fuzzer.c 그대로.
   2  // Copyright 2020 Google LLC
   3  //
   4  // Licensed under the Apache License, Version 2.0 (the "License");
   5  // you may not use this file except in compliance with the License.
   6  // You may obtain a copy of the License at
   7  //
   8  //      http://www.apache.org/licenses/LICENSE-2.0
   9  //
  10  // Unless required by applicable law or agreed to in writing, software
  11  // distributed under the License is distributed on an "AS IS" BASIS,
  12  // WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  13  // See the License for the specific language governing permissions and
  14  // limitations under the License.
  15  
  16  #include "yaml.h"
  17  #include "yaml_write_handler.h"
  18  #include <assert.h>
  19  #include <stdbool.h>
  20  #include <stdint.h>
  21  #include <stdio.h>
  22  #include <stdlib.h>
  23  #include <string.h>
  24  
  25  #ifdef NDEBUG
  26  #undef NDEBUG
  27  #endif
  28  
  29  int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  30    if (size < 2)
  31      return 0;
  32  
  33    bool done = false;
  34    bool is_canonical = data[0] & 1;
  35    bool is_unicode = data[1] & 1;
  36    data += 2;
  37    size -= 2;
  38  
  39    yaml_parser_t parser;
  40    yaml_emitter_t emitter;
  41    yaml_event_t input_event;
  42    yaml_event_t output_event;
  43  
  44    /* Initialize the parser and emitter objects. */
  45  
  46    if (!yaml_parser_initialize(&parser)) {
  47      return 1;
  48    }
  49  
  50    if (!yaml_emitter_initialize(&emitter)) {
  51      yaml_parser_delete(&parser);
  52      return 1;
  53    }
  54  
  55    /* Set the parser parameters. */
  56  
  57    yaml_parser_set_input_string(&parser, data, size);
  58  
  59    /* Set the emitter parameters. */
  60    yaml_output_buffer_t out = {/*buf=*/NULL, /*size=*/0, /*capacity=*/1000};
  61    yaml_emitter_set_output(&emitter, yaml_write_handler, &out);
  62  
  63    yaml_emitter_set_canonical(&emitter, is_canonical);
  64    yaml_emitter_set_unicode(&emitter, is_unicode);
  65  
  66    /* Create and emit the STREAM-START event. */
  67  
  68    if (!yaml_stream_start_event_initialize(&output_event, YAML_UTF8_ENCODING))
  69      goto error;
  70    if (!yaml_emitter_emit(&emitter, &output_event))
  71      goto error;
  72  
  73    /* Create and emit the DOCUMENT-START event. */
  74  
  75    if (!yaml_document_start_event_initialize(&output_event, NULL, NULL, NULL, 0))
  76      goto error;
  77    if (!yaml_emitter_emit(&emitter, &output_event))
  78      goto error;
  79  
  80    /* Create and emit the SEQUENCE-START event. */
  81  
  82    if (!yaml_sequence_start_event_initialize(
  83            &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:seq", 1,
  84            YAML_BLOCK_SEQUENCE_STYLE))
  85      goto error;
  86    if (!yaml_emitter_emit(&emitter, &output_event))
  87      goto error;
  88  
  89    /* Loop through the input events. */
  90  
  91    while (!done) {
  92      /* Get the next event. */
  93  
  94      if (!yaml_parser_parse(&parser, &input_event))
  95        goto error;
  96  
  97      /* Check if this is the stream end. */
  98  
  99      done = (input_event.type == YAML_STREAM_END_EVENT);
 100  
 101      /* Create and emit a MAPPING-START event. */
 102  
 103      if (!yaml_mapping_start_event_initialize(
 104              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map", 1,
 105              YAML_BLOCK_MAPPING_STYLE))
 106        goto error;
 107      if (!yaml_emitter_emit(&emitter, &output_event))
 108        goto error;
 109  
 110      /* Analyze the event. */
 111  
 112      switch (input_event.type) {
 113      case YAML_STREAM_START_EVENT:
 114  
 115        /* Write 'type'. */
 116  
 117        if (!yaml_scalar_event_initialize(
 118                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 119                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 120          goto error;
 121        if (!yaml_emitter_emit(&emitter, &output_event))
 122          goto error;
 123  
 124        /* Write 'STREAM-START'. */
 125  
 126        if (!yaml_scalar_event_initialize(
 127                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 128                (yaml_char_t *)"STREAM-START", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 129          goto error;
 130        if (!yaml_emitter_emit(&emitter, &output_event))
 131          goto error;
 132  
 133        /* Display encoding information. */
 134  
 135        if (input_event.data.stream_start.encoding) {
 136          yaml_encoding_t encoding = input_event.data.stream_start.encoding;
 137  
 138          /* Write 'encoding'. */
 139  
 140          if (!yaml_scalar_event_initialize(
 141                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 142                  (yaml_char_t *)"encoding", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 143            goto error;
 144          if (!yaml_emitter_emit(&emitter, &output_event))
 145            goto error;
 146  
 147          /* Write the stream encoding. */
 148  
 149          if (!yaml_scalar_event_initialize(
 150                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 151                  (yaml_char_t *)(encoding == YAML_UTF8_ENCODING
 152                                      ? "utf-8"
 153                                      : encoding == YAML_UTF16LE_ENCODING
 154                                            ? "utf-16-le"
 155                                            : encoding == YAML_UTF16BE_ENCODING
 156                                                  ? "utf-16-be"
 157                                                  : "unknown"),
 158                  -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 159            goto error;
 160          if (!yaml_emitter_emit(&emitter, &output_event))
 161            goto error;
 162        }
 163  
 164        break;
 165  
 166      case YAML_STREAM_END_EVENT:
 167  
 168        /* Write 'type'. */
 169  
 170        if (!yaml_scalar_event_initialize(
 171                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 172                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 173          goto error;
 174        if (!yaml_emitter_emit(&emitter, &output_event))
 175          goto error;
 176  
 177        /* Write 'STREAM-END'. */
 178  
 179        if (!yaml_scalar_event_initialize(
 180                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 181                (yaml_char_t *)"STREAM-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 182          goto error;
 183        if (!yaml_emitter_emit(&emitter, &output_event))
 184          goto error;
 185  
 186        break;
 187  
 188      case YAML_DOCUMENT_START_EVENT:
 189  
 190        /* Write 'type'. */
 191  
 192        if (!yaml_scalar_event_initialize(
 193                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 194                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 195          goto error;
 196        if (!yaml_emitter_emit(&emitter, &output_event))
 197          goto error;
 198  
 199        /* Write 'DOCUMENT-START'. */
 200  
 201        if (!yaml_scalar_event_initialize(&output_event, NULL,
 202                                          (yaml_char_t *)"tag:yaml.org,2002:str",
 203                                          (yaml_char_t *)"DOCUMENT-START", -1, 1,
 204                                          1, YAML_PLAIN_SCALAR_STYLE))
 205          goto error;
 206        if (!yaml_emitter_emit(&emitter, &output_event))
 207          goto error;
 208  
 209        /* Display the document version numbers. */
 210  
 211        if (input_event.data.document_start.version_directive) {
 212          yaml_version_directive_t *version =
 213              input_event.data.document_start.version_directive;
 214          char number[64];
 215  
 216          /* Write 'version'. */
 217          if (!yaml_scalar_event_initialize(
 218                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 219                  (yaml_char_t *)"version", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 220            goto error;
 221          if (!yaml_emitter_emit(&emitter, &output_event))
 222            goto error;
 223  
 224          /* Write '{'. */
 225  
 226          if (!yaml_mapping_start_event_initialize(
 227                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map", 1,
 228                  YAML_FLOW_MAPPING_STYLE))
 229            goto error;
 230          if (!yaml_emitter_emit(&emitter, &output_event))
 231            goto error;
 232  
 233          /* Write 'major'. */
 234  
 235          if (!yaml_scalar_event_initialize(
 236                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 237                  (yaml_char_t *)"major", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 238            goto error;
 239          if (!yaml_emitter_emit(&emitter, &output_event))
 240            goto error;
 241  
 242          /* Write a number. */
 243  
 244          sprintf(number, "%d", version->major);
 245          if (!yaml_scalar_event_initialize(
 246                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:int",
 247                  (yaml_char_t *)number, -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 248            goto error;
 249          if (!yaml_emitter_emit(&emitter, &output_event))
 250            goto error;
 251  
 252          /* Write 'minor'. */
 253  
 254          if (!yaml_scalar_event_initialize(
 255                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 256                  (yaml_char_t *)"minor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 257            goto error;
 258          if (!yaml_emitter_emit(&emitter, &output_event))
 259            goto error;
 260  
 261          /* Write a number. */
 262  
 263          sprintf(number, "%d", version->minor);
 264          if (!yaml_scalar_event_initialize(
 265                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:int",
 266                  (yaml_char_t *)number, -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 267            goto error;
 268          if (!yaml_emitter_emit(&emitter, &output_event))
 269            goto error;
 270  
 271          /* Write '}'. */
 272  
 273          if (!yaml_mapping_end_event_initialize(&output_event))
 274            goto error;
 275          if (!yaml_emitter_emit(&emitter, &output_event))
 276            goto error;
 277        }
 278  
 279        /* Display the document tag directives. */
 280  
 281        if (input_event.data.document_start.tag_directives.start !=
 282            input_event.data.document_start.tag_directives.end) {
 283          yaml_tag_directive_t *tag;
 284  
 285          /* Write 'tags'. */
 286          if (!yaml_scalar_event_initialize(
 287                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 288                  (yaml_char_t *)"tags", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 289            goto error;
 290          if (!yaml_emitter_emit(&emitter, &output_event))
 291            goto error;
 292  
 293          /* Start a block sequence. */
 294  
 295          if (!yaml_sequence_start_event_initialize(
 296                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:seq", 1,
 297                  YAML_BLOCK_SEQUENCE_STYLE))
 298            goto error;
 299          if (!yaml_emitter_emit(&emitter, &output_event))
 300            goto error;
 301  
 302          for (tag = input_event.data.document_start.tag_directives.start;
 303               tag != input_event.data.document_start.tag_directives.end; tag++) {
 304            /* Write '{'. */
 305  
 306            if (!yaml_mapping_start_event_initialize(
 307                    &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map",
 308                    1, YAML_FLOW_MAPPING_STYLE))
 309              goto error;
 310            if (!yaml_emitter_emit(&emitter, &output_event))
 311              goto error;
 312  
 313            /* Write 'handle'. */
 314  
 315            if (!yaml_scalar_event_initialize(
 316                    &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 317                    (yaml_char_t *)"handle", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 318              goto error;
 319            if (!yaml_emitter_emit(&emitter, &output_event))
 320              goto error;
 321  
 322            /* Write the tag directive handle. */
 323  
 324            if (!yaml_scalar_event_initialize(
 325                    &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 326                    (yaml_char_t *)tag->handle, -1, 0, 1,
 327                    YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 328              goto error;
 329            if (!yaml_emitter_emit(&emitter, &output_event))
 330              goto error;
 331  
 332            /* Write 'prefix'. */
 333  
 334            if (!yaml_scalar_event_initialize(
 335                    &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 336                    (yaml_char_t *)"prefix", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 337              goto error;
 338            if (!yaml_emitter_emit(&emitter, &output_event))
 339              goto error;
 340  
 341            /* Write the tag directive prefix. */
 342  
 343            if (!yaml_scalar_event_initialize(
 344                    &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 345                    (yaml_char_t *)tag->prefix, -1, 0, 1,
 346                    YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 347              goto error;
 348            if (!yaml_emitter_emit(&emitter, &output_event))
 349              goto error;
 350  
 351            /* Write '}'. */
 352  
 353            if (!yaml_mapping_end_event_initialize(&output_event))
 354              goto error;
 355            if (!yaml_emitter_emit(&emitter, &output_event))
 356              goto error;
 357          }
 358  
 359          /* End a block sequence. */
 360  
 361          if (!yaml_sequence_end_event_initialize(&output_event))
 362            goto error;
 363          if (!yaml_emitter_emit(&emitter, &output_event))
 364            goto error;
 365        }
 366  
 367        /* Write 'implicit'. */
 368  
 369        if (!yaml_scalar_event_initialize(
 370                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 371                (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 372          goto error;
 373        if (!yaml_emitter_emit(&emitter, &output_event))
 374          goto error;
 375  
 376        /* Write if the document is implicit. */
 377  
 378        if (!yaml_scalar_event_initialize(
 379                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
 380                (yaml_char_t *)(input_event.data.document_start.implicit
 381                                    ? "true"
 382                                    : "false"),
 383                -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
 384          goto error;
 385        if (!yaml_emitter_emit(&emitter, &output_event))
 386          goto error;
 387  
 388        break;
 389  
 390      case YAML_DOCUMENT_END_EVENT:
 391  
 392        /* Write 'type'. */
 393  
 394        if (!yaml_scalar_event_initialize(
 395                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 396                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 397          goto error;
 398        if (!yaml_emitter_emit(&emitter, &output_event))
 399          goto error;
 400  
 401        /* Write 'DOCUMENT-END'. */
 402  
 403        if (!yaml_scalar_event_initialize(
 404                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 405                (yaml_char_t *)"DOCUMENT-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 406          goto error;
 407        if (!yaml_emitter_emit(&emitter, &output_event))
 408          goto error;
 409  
 410        /* Write 'implicit'. */
 411  
 412        if (!yaml_scalar_event_initialize(
 413                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 414                (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 415          goto error;
 416        if (!yaml_emitter_emit(&emitter, &output_event))
 417          goto error;
 418  
 419        /* Write if the document is implicit. */
 420  
 421        if (!yaml_scalar_event_initialize(
 422                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
 423                (yaml_char_t *)(input_event.data.document_end.implicit ? "true"
 424                                                                       : "false"),
 425                -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
 426          goto error;
 427        if (!yaml_emitter_emit(&emitter, &output_event))
 428          goto error;
 429  
 430        break;
 431  
 432      case YAML_ALIAS_EVENT:
 433  
 434        /* Write 'type'. */
 435  
 436        if (!yaml_scalar_event_initialize(
 437                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 438                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 439          goto error;
 440        if (!yaml_emitter_emit(&emitter, &output_event))
 441          goto error;
 442  
 443        /* Write 'ALIAS'. */
 444  
 445        if (!yaml_scalar_event_initialize(
 446                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 447                (yaml_char_t *)"ALIAS", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 448          goto error;
 449        if (!yaml_emitter_emit(&emitter, &output_event))
 450          goto error;
 451  
 452        /* Write 'anchor'. */
 453  
 454        if (!yaml_scalar_event_initialize(
 455                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 456                (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 457          goto error;
 458        if (!yaml_emitter_emit(&emitter, &output_event))
 459          goto error;
 460  
 461        /* Write the alias anchor. */
 462  
 463        if (!yaml_scalar_event_initialize(&output_event, NULL,
 464                                          (yaml_char_t *)"tag:yaml.org,2002:str",
 465                                          input_event.data.alias.anchor, -1, 0, 1,
 466                                          YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 467          goto error;
 468        if (!yaml_emitter_emit(&emitter, &output_event))
 469          goto error;
 470  
 471        break;
 472  
 473      case YAML_SCALAR_EVENT:
 474  
 475        /* Write 'type'. */
 476  
 477        if (!yaml_scalar_event_initialize(
 478                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 479                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 480          goto error;
 481        if (!yaml_emitter_emit(&emitter, &output_event))
 482          goto error;
 483  
 484        /* Write 'SCALAR'. */
 485  
 486        if (!yaml_scalar_event_initialize(
 487                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 488                (yaml_char_t *)"SCALAR", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 489          goto error;
 490        if (!yaml_emitter_emit(&emitter, &output_event))
 491          goto error;
 492  
 493        /* Display the scalar anchor. */
 494  
 495        if (input_event.data.scalar.anchor) {
 496          /* Write 'anchor'. */
 497  
 498          if (!yaml_scalar_event_initialize(
 499                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 500                  (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 501            goto error;
 502          if (!yaml_emitter_emit(&emitter, &output_event))
 503            goto error;
 504  
 505          /* Write the scalar anchor. */
 506  
 507          if (!yaml_scalar_event_initialize(
 508                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 509                  input_event.data.scalar.anchor, -1, 0, 1,
 510                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 511            goto error;
 512          if (!yaml_emitter_emit(&emitter, &output_event))
 513            goto error;
 514        }
 515  
 516        /* Display the scalar tag. */
 517  
 518        if (input_event.data.scalar.tag) {
 519          /* Write 'tag'. */
 520  
 521          if (!yaml_scalar_event_initialize(
 522                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 523                  (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 524            goto error;
 525          if (!yaml_emitter_emit(&emitter, &output_event))
 526            goto error;
 527  
 528          /* Write the scalar tag. */
 529  
 530          if (!yaml_scalar_event_initialize(
 531                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 532                  input_event.data.scalar.tag, -1, 0, 1,
 533                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 534            goto error;
 535          if (!yaml_emitter_emit(&emitter, &output_event))
 536            goto error;
 537        }
 538  
 539        /* Display the scalar value. */
 540  
 541        /* Write 'value'. */
 542  
 543        if (!yaml_scalar_event_initialize(
 544                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 545                (yaml_char_t *)"value", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 546          goto error;
 547        if (!yaml_emitter_emit(&emitter, &output_event))
 548          goto error;
 549  
 550        /* Write the scalar value. */
 551  
 552        if (!yaml_scalar_event_initialize(
 553                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 554                input_event.data.scalar.value, input_event.data.scalar.length, 0,
 555                1, YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 556          goto error;
 557        if (!yaml_emitter_emit(&emitter, &output_event))
 558          goto error;
 559  
 560        /* Display if the scalar tag is implicit. */
 561  
 562        /* Write 'implicit'. */
 563  
 564        if (!yaml_scalar_event_initialize(
 565                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 566                (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 567          goto error;
 568        if (!yaml_emitter_emit(&emitter, &output_event))
 569          goto error;
 570  
 571        /* Write '{'. */
 572  
 573        if (!yaml_mapping_start_event_initialize(
 574                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map", 1,
 575                YAML_FLOW_MAPPING_STYLE))
 576          goto error;
 577        if (!yaml_emitter_emit(&emitter, &output_event))
 578          goto error;
 579  
 580        /* Write 'plain'. */
 581  
 582        if (!yaml_scalar_event_initialize(
 583                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 584                (yaml_char_t *)"plain", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 585          goto error;
 586        if (!yaml_emitter_emit(&emitter, &output_event))
 587          goto error;
 588  
 589        /* Write if the scalar is implicit in the plain style. */
 590  
 591        if (!yaml_scalar_event_initialize(
 592                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
 593                (yaml_char_t *)(input_event.data.scalar.plain_implicit ? "true"
 594                                                                       : "false"),
 595                -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
 596          goto error;
 597        if (!yaml_emitter_emit(&emitter, &output_event))
 598          goto error;
 599  
 600        /* Write 'quoted'. */
 601  
 602        if (!yaml_scalar_event_initialize(
 603                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 604                (yaml_char_t *)"non-plain", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 605          goto error;
 606        if (!yaml_emitter_emit(&emitter, &output_event))
 607          goto error;
 608  
 609        /* Write if the scalar is implicit in a non-plain style. */
 610  
 611        if (!yaml_scalar_event_initialize(
 612                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
 613                (yaml_char_t *)(input_event.data.scalar.quoted_implicit
 614                                    ? "true"
 615                                    : "false"),
 616                -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
 617          goto error;
 618        if (!yaml_emitter_emit(&emitter, &output_event))
 619          goto error;
 620  
 621        /* Write '}'. */
 622  
 623        if (!yaml_mapping_end_event_initialize(&output_event))
 624          goto error;
 625        if (!yaml_emitter_emit(&emitter, &output_event))
 626          goto error;
 627  
 628        /* Display the style information. */
 629  
 630        if (input_event.data.scalar.style) {
 631          yaml_scalar_style_t style = input_event.data.scalar.style;
 632  
 633          /* Write 'style'. */
 634  
 635          if (!yaml_scalar_event_initialize(
 636                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 637                  (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 638            goto error;
 639          if (!yaml_emitter_emit(&emitter, &output_event))
 640            goto error;
 641  
 642          /* Write the scalar style. */
 643  
 644          if (!yaml_scalar_event_initialize(
 645                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 646                  (yaml_char_t
 647                       *)(style == YAML_PLAIN_SCALAR_STYLE
 648                              ? "plain"
 649                              : style == YAML_SINGLE_QUOTED_SCALAR_STYLE
 650                                    ? "single-quoted"
 651                                    : style == YAML_DOUBLE_QUOTED_SCALAR_STYLE
 652                                          ? "double-quoted"
 653                                          : style == YAML_LITERAL_SCALAR_STYLE
 654                                                ? "literal"
 655                                                : style ==
 656                                                          YAML_FOLDED_SCALAR_STYLE
 657                                                      ? "folded"
 658                                                      : "unknown"),
 659                  -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 660            goto error;
 661          if (!yaml_emitter_emit(&emitter, &output_event))
 662            goto error;
 663        }
 664  
 665        break;
 666  
 667      case YAML_SEQUENCE_START_EVENT:
 668  
 669        /* Write 'type'. */
 670  
 671        if (!yaml_scalar_event_initialize(
 672                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 673                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 674          goto error;
 675        if (!yaml_emitter_emit(&emitter, &output_event))
 676          goto error;
 677  
 678        /* Write 'SEQUENCE-START'. */
 679  
 680        if (!yaml_scalar_event_initialize(&output_event, NULL,
 681                                          (yaml_char_t *)"tag:yaml.org,2002:str",
 682                                          (yaml_char_t *)"SEQUENCE-START", -1, 1,
 683                                          1, YAML_PLAIN_SCALAR_STYLE))
 684          goto error;
 685        if (!yaml_emitter_emit(&emitter, &output_event))
 686          goto error;
 687  
 688        /* Display the sequence anchor. */
 689  
 690        if (input_event.data.sequence_start.anchor) {
 691          /* Write 'anchor'. */
 692  
 693          if (!yaml_scalar_event_initialize(
 694                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 695                  (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 696            goto error;
 697          if (!yaml_emitter_emit(&emitter, &output_event))
 698            goto error;
 699  
 700          /* Write the sequence anchor. */
 701  
 702          if (!yaml_scalar_event_initialize(
 703                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 704                  input_event.data.sequence_start.anchor, -1, 0, 1,
 705                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 706            goto error;
 707          if (!yaml_emitter_emit(&emitter, &output_event))
 708            goto error;
 709        }
 710  
 711        /* Display the sequence tag. */
 712  
 713        if (input_event.data.sequence_start.tag) {
 714          /* Write 'tag'. */
 715  
 716          if (!yaml_scalar_event_initialize(
 717                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 718                  (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 719            goto error;
 720          if (!yaml_emitter_emit(&emitter, &output_event))
 721            goto error;
 722  
 723          /* Write the sequence tag. */
 724  
 725          if (!yaml_scalar_event_initialize(
 726                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 727                  input_event.data.sequence_start.tag, -1, 0, 1,
 728                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 729            goto error;
 730          if (!yaml_emitter_emit(&emitter, &output_event))
 731            goto error;
 732        }
 733  
 734        /* Write 'implicit'. */
 735  
 736        if (!yaml_scalar_event_initialize(
 737                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 738                (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 739          goto error;
 740        if (!yaml_emitter_emit(&emitter, &output_event))
 741          goto error;
 742  
 743        /* Write if the sequence tag is implicit. */
 744  
 745        if (!yaml_scalar_event_initialize(
 746                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
 747                (yaml_char_t *)(input_event.data.sequence_start.implicit
 748                                    ? "true"
 749                                    : "false"),
 750                -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
 751          goto error;
 752        if (!yaml_emitter_emit(&emitter, &output_event))
 753          goto error;
 754  
 755        /* Display the style information. */
 756  
 757        if (input_event.data.sequence_start.style) {
 758          yaml_sequence_style_t style = input_event.data.sequence_start.style;
 759  
 760          /* Write 'style'. */
 761  
 762          if (!yaml_scalar_event_initialize(
 763                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 764                  (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 765            goto error;
 766          if (!yaml_emitter_emit(&emitter, &output_event))
 767            goto error;
 768  
 769          /* Write the scalar style. */
 770  
 771          if (!yaml_scalar_event_initialize(
 772                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 773                  (yaml_char_t *)(style == YAML_BLOCK_SEQUENCE_STYLE
 774                                      ? "block"
 775                                      : style == YAML_FLOW_SEQUENCE_STYLE
 776                                            ? "flow"
 777                                            : "unknown"),
 778                  -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 779            goto error;
 780          if (!yaml_emitter_emit(&emitter, &output_event))
 781            goto error;
 782        }
 783  
 784        break;
 785  
 786      case YAML_SEQUENCE_END_EVENT:
 787  
 788        /* Write 'type'. */
 789  
 790        if (!yaml_scalar_event_initialize(
 791                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 792                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 793          goto error;
 794        if (!yaml_emitter_emit(&emitter, &output_event))
 795          goto error;
 796  
 797        /* Write 'SEQUENCE-END'. */
 798  
 799        if (!yaml_scalar_event_initialize(
 800                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 801                (yaml_char_t *)"SEQUENCE-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 802          goto error;
 803        if (!yaml_emitter_emit(&emitter, &output_event))
 804          goto error;
 805  
 806        break;
 807  
 808      case YAML_MAPPING_START_EVENT:
 809  
 810        /* Write 'type'. */
 811  
 812        if (!yaml_scalar_event_initialize(
 813                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 814                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 815          goto error;
 816        if (!yaml_emitter_emit(&emitter, &output_event))
 817          goto error;
 818  
 819        /* Write 'MAPPING-START'. */
 820  
 821        if (!yaml_scalar_event_initialize(&output_event, NULL,
 822                                          (yaml_char_t *)"tag:yaml.org,2002:str",
 823                                          (yaml_char_t *)"MAPPING-START", -1, 1,
 824                                          1, YAML_PLAIN_SCALAR_STYLE))
 825          goto error;
 826        if (!yaml_emitter_emit(&emitter, &output_event))
 827          goto error;
 828  
 829        /* Display the mapping anchor. */
 830  
 831        if (input_event.data.mapping_start.anchor) {
 832          /* Write 'anchor'. */
 833  
 834          if (!yaml_scalar_event_initialize(
 835                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 836                  (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 837            goto error;
 838          if (!yaml_emitter_emit(&emitter, &output_event))
 839            goto error;
 840  
 841          /* Write the mapping anchor. */
 842  
 843          if (!yaml_scalar_event_initialize(
 844                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 845                  input_event.data.mapping_start.anchor, -1, 0, 1,
 846                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 847            goto error;
 848          if (!yaml_emitter_emit(&emitter, &output_event))
 849            goto error;
 850        }
 851  
 852        /* Display the mapping tag. */
 853  
 854        if (input_event.data.mapping_start.tag) {
 855          /* Write 'tag'. */
 856  
 857          if (!yaml_scalar_event_initialize(
 858                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 859                  (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 860            goto error;
 861          if (!yaml_emitter_emit(&emitter, &output_event))
 862            goto error;
 863  
 864          /* Write the mapping tag. */
 865  
 866          if (!yaml_scalar_event_initialize(
 867                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 868                  input_event.data.mapping_start.tag, -1, 0, 1,
 869                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
 870            goto error;
 871          if (!yaml_emitter_emit(&emitter, &output_event))
 872            goto error;
 873        }
 874  
 875        /* Write 'implicit'. */
 876  
 877        if (!yaml_scalar_event_initialize(
 878                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 879                (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 880          goto error;
 881        if (!yaml_emitter_emit(&emitter, &output_event))
 882          goto error;
 883  
 884        /* Write if the mapping tag is implicit. */
 885  
 886        if (!yaml_scalar_event_initialize(
 887                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
 888                (yaml_char_t *)(input_event.data.mapping_start.implicit
 889                                    ? "true"
 890                                    : "false"),
 891                -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
 892          goto error;
 893        if (!yaml_emitter_emit(&emitter, &output_event))
 894          goto error;
 895  
 896        /* Display the style information. */
 897  
 898        if (input_event.data.mapping_start.style) {
 899          yaml_mapping_style_t style = input_event.data.mapping_start.style;
 900  
 901          /* Write 'style'. */
 902  
 903          if (!yaml_scalar_event_initialize(
 904                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 905                  (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 906            goto error;
 907          if (!yaml_emitter_emit(&emitter, &output_event))
 908            goto error;
 909  
 910          /* Write the scalar style. */
 911  
 912          if (!yaml_scalar_event_initialize(
 913                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 914                  (yaml_char_t *)(style == YAML_BLOCK_MAPPING_STYLE
 915                                      ? "block"
 916                                      : style == YAML_FLOW_MAPPING_STYLE
 917                                            ? "flow"
 918                                            : "unknown"),
 919                  -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 920            goto error;
 921          if (!yaml_emitter_emit(&emitter, &output_event))
 922            goto error;
 923        }
 924  
 925        break;
 926  
 927      case YAML_MAPPING_END_EVENT:
 928  
 929        /* Write 'type'. */
 930  
 931        if (!yaml_scalar_event_initialize(
 932                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 933                (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 934          goto error;
 935        if (!yaml_emitter_emit(&emitter, &output_event))
 936          goto error;
 937  
 938        /* Write 'MAPPING-END'. */
 939  
 940        if (!yaml_scalar_event_initialize(
 941                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
 942                (yaml_char_t *)"MAPPING-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
 943          goto error;
 944        if (!yaml_emitter_emit(&emitter, &output_event))
 945          goto error;
 946  
 947        break;
 948  
 949      default:
 950        /* It couldn't really happen. */
 951        break;
 952      }
 953  
 954      /* Delete the event object. */
 955  
 956      yaml_event_delete(&input_event);
 957  
 958      /* Create and emit a MAPPING-END event. */
 959  
 960      if (!yaml_mapping_end_event_initialize(&output_event))
 961        goto error;
 962      if (!yaml_emitter_emit(&emitter, &output_event))
 963        goto error;
 964    }
 965  
 966    /* Create and emit the SEQUENCE-END event. */
 967  
 968    if (!yaml_sequence_end_event_initialize(&output_event))
 969      goto error;
 970    if (!yaml_emitter_emit(&emitter, &output_event))
 971      goto error;
 972  
 973    /* Create and emit the DOCUMENT-END event. */
 974  
 975    if (!yaml_document_end_event_initialize(&output_event, 0))
 976      goto error;
 977    if (!yaml_emitter_emit(&emitter, &output_event))
 978      goto error;
 979  
 980    /* Create and emit the STREAM-END event. */
 981  
 982    if (!yaml_stream_end_event_initialize(&output_event))
 983      goto error;
 984    yaml_emitter_emit(&emitter, &output_event);
 985  
 986  error:
 987  
 988    free(out.buf);
 989  
 990    yaml_event_delete(&input_event);
 991    yaml_parser_delete(&parser);
 992    yaml_emitter_delete(&emitter);
 993  
 994    return 0;
 995  }
```