라이브러리: libyaml
하네스 파일: official_deconstructor_alt.c

아래 제안 8개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`yaml_emitter_open(yaml_emitter_t *)`의 1번째 인자 `emitter`를 하네스가 고정합니다(70행에서 항상 같은 객체 `&emitter`) (라이브러리 내부 `yaml_emitter_emit` → `yaml_emitter_state_machine` → `yaml_emitter_emit_flow_mapping_key` → `yaml_emitter_check_simple_key`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (5개)
- `yaml_emitter_emit(yaml_emitter_t *, yaml_event_t *)` 1154행, 조건 `case YAML_ALIAS_EVENT`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1150      size_t length = 0;
 1151  
 1152      switch (event->type)
 1153      {
 1154>         case YAML_ALIAS_EVENT:
 1155              length += emitter->anchor_data.anchor_length;
 1156              break;
 1157  
 1158          case YAML_SCALAR_EVENT:
```
- `yaml_emitter_emit(yaml_emitter_t *, yaml_event_t *)` 1158행, 조건 `case YAML_SCALAR_EVENT`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1154          case YAML_ALIAS_EVENT:
 1155              length += emitter->anchor_data.anchor_length;
 1156              break;
 1157  
 1158>         case YAML_SCALAR_EVENT:
 1159              if (emitter->scalar_data.multiline)
 1160                  return 0;
 1161              length += emitter->anchor_data.anchor_length
 1162                  + emitter->tag_data.handle_length
```
- `yaml_emitter_emit(yaml_emitter_t *, yaml_event_t *)` 1167행, 조건 `case YAML_SEQUENCE_START_EVENT`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1163                  + emitter->tag_data.suffix_length
 1164                  + emitter->scalar_data.length;
 1165              break;
 1166  
 1167>         case YAML_SEQUENCE_START_EVENT:
 1168              if (!yaml_emitter_check_empty_sequence(emitter))
 1169                  return 0;
 1170              length += emitter->anchor_data.anchor_length
 1171                  + emitter->tag_data.handle_length
```
- `yaml_emitter_emit(yaml_emitter_t *, yaml_event_t *)` 1175행, 조건 `case YAML_MAPPING_START_EVENT`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1171                  + emitter->tag_data.handle_length
 1172                  + emitter->tag_data.suffix_length;
 1173              break;
 1174  
 1175>         case YAML_MAPPING_START_EVENT:
 1176              if (!yaml_emitter_check_empty_mapping(emitter))
 1177                  return 0;
 1178              length += emitter->anchor_data.anchor_length
 1179                  + emitter->tag_data.handle_length
```
- `yaml_emitter_emit(yaml_emitter_t *, yaml_event_t *)` 1183행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1179                  + emitter->tag_data.handle_length
 1180                  + emitter->tag_data.suffix_length;
 1181              break;
 1182  
 1183>         default:
 1184              return 0;
 1185      }
 1186  
 1187      if (length > 128)
```

## 제안 2
`yaml_document_add_sequence(yaml_document_t *, const yaml_char_t *, yaml_sequence_style_t)`의 2번째 인자 `tag`를 하네스가 고정합니다(80행에서 항상 `0`, 266행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `yaml_document_add_sequence(yaml_document_t *, const yaml_char_t *, yaml_sequence_style_t)` 1262행, 조건 `!tag`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1258      yaml_node_t node;
 1259  
 1260      assert(document);   /* Non-NULL document object is expected. */
 1261  
 1262>     if (!tag) {
 1263          tag = (yaml_char_t *)YAML_DEFAULT_SEQUENCE_TAG;
 1264      }
 1265  
 1266      if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
```
- `yaml_document_add_sequence(yaml_document_t *, const yaml_char_t *, yaml_sequence_style_t)` 1266행, 조건 `!yaml_check_utf8(tag, strlen((char *)tag))`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1262      if (!tag) {
 1263          tag = (yaml_char_t *)YAML_DEFAULT_SEQUENCE_TAG;
 1264      }
 1265  
 1266>     if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
 1267      tag_copy = yaml_strdup(tag);
 1268      if (!tag_copy) goto error;
 1269  
 1270      if (!STACK_INIT(&context, items, yaml_node_item_t*)) goto error;
```

## 제안 3
`yaml_document_add_mapping(yaml_document_t *, const yaml_char_t *, yaml_mapping_style_t)`의 2번째 인자 `tag`를 하네스가 고정합니다(101행에서 항상 `0`, 210행에서 항상 `0`, 278행에서 항상 `0`, 490행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `yaml_document_add_mapping(yaml_document_t *, const yaml_char_t *, yaml_mapping_style_t)` 1307행, 조건 `!tag`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1303      yaml_node_t node;
 1304  
 1305      assert(document);   /* Non-NULL document object is expected. */
 1306  
 1307>     if (!tag) {
 1308          tag = (yaml_char_t *)YAML_DEFAULT_MAPPING_TAG;
 1309      }
 1310  
 1311      if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
```
- `yaml_document_add_mapping(yaml_document_t *, const yaml_char_t *, yaml_mapping_style_t)` 1311행, 조건 `!yaml_check_utf8(tag, strlen((char *)tag))`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1307      if (!tag) {
 1308          tag = (yaml_char_t *)YAML_DEFAULT_MAPPING_TAG;
 1309      }
 1310  
 1311>     if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
 1312      tag_copy = yaml_strdup(tag);
 1313      if (!tag_copy) goto error;
 1314  
 1315      if (!STACK_INIT(&context, pairs, yaml_node_pair_t*)) goto error;
```

## 제안 4
`yaml_emitter_dump(yaml_emitter_t *, yaml_document_t *)`의 1번째 인자 `emitter`를 하네스가 고정합니다(819행에서 항상 같은 객체 `&emitter`) (라이브러리 내부 `yaml_emitter_dump_node`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `yaml_emitter_dump(yaml_emitter_t *, yaml_document_t *)` 270행, 조건 `anchor_id`가 퍼징 중 한 번도 '참'이 되지 않음
```
  266      yaml_node_t *node = emitter->document->nodes.start + index - 1;
  267      int anchor_id = emitter->anchors[index-1].anchor;
  268      yaml_char_t *anchor = NULL;
  269  
  270>     if (anchor_id) {
  271          anchor = yaml_emitter_generate_anchor(emitter, anchor_id);
  272          if (!anchor) return 0;
  273      }
  274  
```
- `yaml_emitter_dump(yaml_emitter_t *, yaml_document_t *)` 288행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
  284          case YAML_SEQUENCE_NODE:
  285              return yaml_emitter_dump_sequence(emitter, node, anchor);
  286          case YAML_MAPPING_NODE:
  287              return yaml_emitter_dump_mapping(emitter, node, anchor);
  288>         default:
  289              assert(0);      /* Could not happen. */
  290              break;
  291      }
  292  
```

## 제안 5
`yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)`의 2번째 인자 `version_directive`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)` 1066행, 조건 `version_directive`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1062                              /* Valid tag directives are expected. */
 1063  
 1064      if (!STACK_INIT(&context, nodes, yaml_node_t*)) goto error;
 1065  
 1066>     if (version_directive) {
 1067          version_directive_copy = YAML_MALLOC_STATIC(yaml_version_directive_t);
 1068          if (!version_directive_copy) goto error;
 1069          version_directive_copy->major = version_directive->major;
 1070          version_directive_copy->minor = version_directive->minor;
```

## 제안 6
`yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)`의 3번째 인자 `tag_directives_start`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)` 1073행, 조건 `tag_directives_start != tag_directives_end`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1069          version_directive_copy->major = version_directive->major;
 1070          version_directive_copy->minor = version_directive->minor;
 1071      }
 1072  
 1073>     if (tag_directives_start != tag_directives_end) {
 1074          yaml_tag_directive_t *tag_directive;
 1075          if (!STACK_INIT(&context, tag_directives_copy, yaml_tag_directive_t*))
 1076              goto error;
 1077          for (tag_directive = tag_directives_start;
```

## 제안 8
`yaml_document_delete(yaml_document_t *)`의 1번째 인자 `document`를 하네스가 고정합니다(829행에서 항상 같은 객체 `&output_document`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `yaml_document_delete(yaml_document_t *)` 1142행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1138                  break;
 1139              case YAML_MAPPING_NODE:
 1140                  STACK_DEL(&context, node.data.mapping.pairs);
 1141                  break;
 1142>             default:
 1143                  assert(0);  /* Should not happen. */
 1144          }
 1145      }
 1146      STACK_DEL(&context, document->nodes);
```

## 제안 9
`yaml_document_add_scalar(yaml_document_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_scalar_style_t)`의 2번째 인자 `tag`를 하네스가 `0`, `"tag:yaml.org,2002:int"`, `"tag:yaml.org,2002:bool"` 중에서만 고릅니다(115행, 120행, 134행, 139행, 162행, 167행, 182행, 187행, 205행, 220행, 226행, 237행, 243행, 261행, 287행, 292행, 302행, 307행, 319행, 324행, 341행, 346행, 357행, 362행, 379행, 384행, 395행, 400행, 415행, 420행, 432행, 437행, 450행, 455행, 467행, 472행, 485행, 500행, 505행, 517행, 522행, 539행, 544행, 572행, 577행, 589행, 594행, 607행, 612행, 624행, 629행, 647행, 652행, 673행, 678행, 693행, 698행, 710행, 715행, 728행, 733행, 745행, 750행, 768행, 773행, 793행, 798행) (라이브러리 내부 `yaml_strdup`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)` 63행, 조건 `!str`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)` 647행, 조건 `pointer+width > end`가 퍼징 중 한 번도 '참'이 되지 않음
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
- `yaml_document_add_scalar(yaml_document_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_scalar_style_t)` 1214행, 조건 `!yaml_check_utf8(tag, strlen((char *)tag))`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1210      if (!tag) {
 1211          tag = (yaml_char_t *)YAML_DEFAULT_SCALAR_TAG;
 1212      }
 1213  
 1214>     if (!yaml_check_utf8(tag, strlen((char *)tag))) goto error;
 1215      tag_copy = yaml_strdup(tag);
 1216      if (!tag_copy) goto error;
 1217  
 1218      if (length < 0) {
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/libyaml/libyaml_deconstructor_alt_fuzzer.c 그대로.
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
  42    yaml_document_t output_document;
  43  
  44    int root;
  45  
  46    /* Initialize the parser and emitter objects. */
  47  
  48    if (!yaml_parser_initialize(&parser)) {
  49      return 1;
  50    }
  51  
  52    if (!yaml_emitter_initialize(&emitter)) {
  53      yaml_parser_delete(&parser);
  54      return 1;
  55    }
  56  
  57    /* Set the parser parameters. */
  58  
  59    yaml_parser_set_input_string(&parser, data, size);
  60  
  61    /* Set the emitter parameters. */
  62    yaml_output_buffer_t out = {/*buf=*/NULL, /*size=*/0, /*capacity=*/1000};
  63    yaml_emitter_set_output(&emitter, yaml_write_handler, &out);
  64  
  65    yaml_emitter_set_canonical(&emitter, is_canonical);
  66    yaml_emitter_set_unicode(&emitter, is_unicode);
  67  
  68    /* Create and emit the STREAM-START event. */
  69  
  70    if (!yaml_emitter_open(&emitter))
  71      goto error;
  72  
  73    /* Create a output_document object. */
  74  
  75    if (!yaml_document_initialize(&output_document, NULL, NULL, NULL, 0, 0))
  76      goto error;
  77  
  78    /* Create the root sequence. */
  79  
  80    root = yaml_document_add_sequence(&output_document, NULL,
  81                                      YAML_BLOCK_SEQUENCE_STYLE);
  82    if (!root)
  83      goto error;
  84  
  85    /* Loop through the input events. */
  86  
  87    while (!done) {
  88      int properties, key, value, map, seq;
  89  
  90      /* Get the next event. */
  91  
  92      if (!yaml_parser_parse(&parser, &input_event))
  93        goto error;
  94  
  95      /* Check if this is the stream end. */
  96  
  97      done = (input_event.type == YAML_STREAM_END_EVENT);
  98  
  99      /* Create a mapping node and attach it to the root sequence. */
 100  
 101      properties = yaml_document_add_mapping(&output_document, NULL,
 102                                             YAML_BLOCK_MAPPING_STYLE);
 103      if (!properties)
 104        goto error;
 105      if (!yaml_document_append_sequence_item(&output_document, root, properties))
 106        goto error;
 107  
 108      /* Analyze the event. */
 109  
 110      switch (input_event.type) {
 111      case YAML_STREAM_START_EVENT:
 112  
 113        /* Add 'type': 'STREAM-START'. */
 114  
 115        key = yaml_document_add_scalar(&output_document, NULL,
 116                                       (yaml_char_t *)"type", -1,
 117                                       YAML_PLAIN_SCALAR_STYLE);
 118        if (!key)
 119          goto error;
 120        value = yaml_document_add_scalar(&output_document, NULL,
 121                                         (yaml_char_t *)"STREAM-START", -1,
 122                                         YAML_PLAIN_SCALAR_STYLE);
 123        if (!value)
 124          goto error;
 125        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 126                                               value))
 127          goto error;
 128  
 129        /* Add 'encoding': <encoding>. */
 130  
 131        if (input_event.data.stream_start.encoding) {
 132          yaml_encoding_t encoding = input_event.data.stream_start.encoding;
 133  
 134          key = yaml_document_add_scalar(&output_document, NULL,
 135                                         (yaml_char_t *)"encoding", -1,
 136                                         YAML_PLAIN_SCALAR_STYLE);
 137          if (!key)
 138            goto error;
 139          value = yaml_document_add_scalar(
 140              &output_document, NULL,
 141              (encoding == YAML_UTF8_ENCODING
 142                   ? (yaml_char_t *)"utf-8"
 143                   : encoding == YAML_UTF16LE_ENCODING
 144                         ? (yaml_char_t *)"utf-16-le"
 145                         : encoding == YAML_UTF16BE_ENCODING
 146                               ? (yaml_char_t *)"utf-16-be"
 147                               : (yaml_char_t *)"unknown"),
 148              -1, YAML_PLAIN_SCALAR_STYLE);
 149          if (!value)
 150            goto error;
 151          if (!yaml_document_append_mapping_pair(&output_document, properties,
 152                                                 key, value))
 153            goto error;
 154        }
 155  
 156        break;
 157  
 158      case YAML_STREAM_END_EVENT:
 159  
 160        /* Add 'type': 'STREAM-END'. */
 161  
 162        key = yaml_document_add_scalar(&output_document, NULL,
 163                                       (yaml_char_t *)"type", -1,
 164                                       YAML_PLAIN_SCALAR_STYLE);
 165        if (!key)
 166          goto error;
 167        value = yaml_document_add_scalar(&output_document, NULL,
 168                                         (yaml_char_t *)"STREAM-END", -1,
 169                                         YAML_PLAIN_SCALAR_STYLE);
 170        if (!value)
 171          goto error;
 172        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 173                                               value))
 174          goto error;
 175  
 176        break;
 177  
 178      case YAML_DOCUMENT_START_EVENT:
 179  
 180        /* Add 'type': 'DOCUMENT-START'. */
 181  
 182        key = yaml_document_add_scalar(&output_document, NULL,
 183                                       (yaml_char_t *)"type", -1,
 184                                       YAML_PLAIN_SCALAR_STYLE);
 185        if (!key)
 186          goto error;
 187        value = yaml_document_add_scalar(&output_document, NULL,
 188                                         (yaml_char_t *)"DOCUMENT-START", -1,
 189                                         YAML_PLAIN_SCALAR_STYLE);
 190        if (!value)
 191          goto error;
 192        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 193                                               value))
 194          goto error;
 195  
 196        /* Display the output_document version numbers. */
 197  
 198        if (input_event.data.document_start.version_directive) {
 199          yaml_version_directive_t *version =
 200              input_event.data.document_start.version_directive;
 201          char number[64];
 202  
 203          /* Add 'version': {}. */
 204  
 205          key = yaml_document_add_scalar(&output_document, NULL,
 206                                         (yaml_char_t *)"version", -1,
 207                                         YAML_PLAIN_SCALAR_STYLE);
 208          if (!key)
 209            goto error;
 210          map = yaml_document_add_mapping(&output_document, NULL,
 211                                          YAML_FLOW_MAPPING_STYLE);
 212          if (!map)
 213            goto error;
 214          if (!yaml_document_append_mapping_pair(&output_document, properties,
 215                                                 key, map))
 216            goto error;
 217  
 218          /* Add 'major': <number>. */
 219  
 220          key = yaml_document_add_scalar(&output_document, NULL,
 221                                         (yaml_char_t *)"major", -1,
 222                                         YAML_PLAIN_SCALAR_STYLE);
 223          if (!key)
 224            goto error;
 225          sprintf(number, "%d", version->major);
 226          value = yaml_document_add_scalar(
 227              &output_document, (yaml_char_t *)YAML_INT_TAG,
 228              (yaml_char_t *)number, -1, YAML_PLAIN_SCALAR_STYLE);
 229          if (!value)
 230            goto error;
 231          if (!yaml_document_append_mapping_pair(&output_document, map, key,
 232                                                 value))
 233            goto error;
 234  
 235          /* Add 'minor': <number>. */
 236  
 237          key = yaml_document_add_scalar(&output_document, NULL,
 238                                         (yaml_char_t *)"minor", -1,
 239                                         YAML_PLAIN_SCALAR_STYLE);
 240          if (!key)
 241            goto error;
 242          sprintf(number, "%d", version->minor);
 243          value = yaml_document_add_scalar(
 244              &output_document, (yaml_char_t *)YAML_INT_TAG,
 245              (yaml_char_t *)number, -1, YAML_PLAIN_SCALAR_STYLE);
 246          if (!value)
 247            goto error;
 248          if (!yaml_document_append_mapping_pair(&output_document, map, key,
 249                                                 value))
 250            goto error;
 251        }
 252  
 253        /* Display the output_document tag directives. */
 254  
 255        if (input_event.data.document_start.tag_directives.start !=
 256            input_event.data.document_start.tag_directives.end) {
 257          yaml_tag_directive_t *tag;
 258  
 259          /* Add 'tags': []. */
 260  
 261          key = yaml_document_add_scalar(&output_document, NULL,
 262                                         (yaml_char_t *)"tags", -1,
 263                                         YAML_PLAIN_SCALAR_STYLE);
 264          if (!key)
 265            goto error;
 266          seq = yaml_document_add_sequence(&output_document, NULL,
 267                                           YAML_BLOCK_SEQUENCE_STYLE);
 268          if (!seq)
 269            goto error;
 270          if (!yaml_document_append_mapping_pair(&output_document, properties,
 271                                                 key, seq))
 272            goto error;
 273  
 274          for (tag = input_event.data.document_start.tag_directives.start;
 275               tag != input_event.data.document_start.tag_directives.end; tag++) {
 276            /* Add {}. */
 277  
 278            map = yaml_document_add_mapping(&output_document, NULL,
 279                                            YAML_FLOW_MAPPING_STYLE);
 280            if (!map)
 281              goto error;
 282            if (!yaml_document_append_sequence_item(&output_document, seq, map))
 283              goto error;
 284  
 285            /* Add 'handle': <handle>. */
 286  
 287            key = yaml_document_add_scalar(&output_document, NULL,
 288                                           (yaml_char_t *)"handle", -1,
 289                                           YAML_PLAIN_SCALAR_STYLE);
 290            if (!key)
 291              goto error;
 292            value = yaml_document_add_scalar(&output_document, NULL, tag->handle,
 293                                             -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 294            if (!value)
 295              goto error;
 296            if (!yaml_document_append_mapping_pair(&output_document, map, key,
 297                                                   value))
 298              goto error;
 299  
 300            /* Add 'prefix': <prefix>. */
 301  
 302            key = yaml_document_add_scalar(&output_document, NULL,
 303                                           (yaml_char_t *)"prefix", -1,
 304                                           YAML_PLAIN_SCALAR_STYLE);
 305            if (!key)
 306              goto error;
 307            value = yaml_document_add_scalar(&output_document, NULL, tag->prefix,
 308                                             -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 309            if (!value)
 310              goto error;
 311            if (!yaml_document_append_mapping_pair(&output_document, map, key,
 312                                                   value))
 313              goto error;
 314          }
 315        }
 316  
 317        /* Add 'implicit': <flag>. */
 318  
 319        key = yaml_document_add_scalar(&output_document, NULL,
 320                                       (yaml_char_t *)"implicit", -1,
 321                                       YAML_PLAIN_SCALAR_STYLE);
 322        if (!key)
 323          goto error;
 324        value = yaml_document_add_scalar(
 325            &output_document, (yaml_char_t *)YAML_BOOL_TAG,
 326            (input_event.data.document_start.implicit ? (yaml_char_t *)"true"
 327                                                      : (yaml_char_t *)"false"),
 328            -1, YAML_PLAIN_SCALAR_STYLE);
 329        if (!value)
 330          goto error;
 331        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 332                                               value))
 333          goto error;
 334  
 335        break;
 336  
 337      case YAML_DOCUMENT_END_EVENT:
 338  
 339        /* Add 'type': 'DOCUMENT-END'. */
 340  
 341        key = yaml_document_add_scalar(&output_document, NULL,
 342                                       (yaml_char_t *)"type", -1,
 343                                       YAML_PLAIN_SCALAR_STYLE);
 344        if (!key)
 345          goto error;
 346        value = yaml_document_add_scalar(&output_document, NULL,
 347                                         (yaml_char_t *)"DOCUMENT-END", -1,
 348                                         YAML_PLAIN_SCALAR_STYLE);
 349        if (!value)
 350          goto error;
 351        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 352                                               value))
 353          goto error;
 354  
 355        /* Add 'implicit': <flag>. */
 356  
 357        key = yaml_document_add_scalar(&output_document, NULL,
 358                                       (yaml_char_t *)"implicit", -1,
 359                                       YAML_PLAIN_SCALAR_STYLE);
 360        if (!key)
 361          goto error;
 362        value = yaml_document_add_scalar(
 363            &output_document, (yaml_char_t *)YAML_BOOL_TAG,
 364            (input_event.data.document_end.implicit ? (yaml_char_t *)"true"
 365                                                    : (yaml_char_t *)"false"),
 366            -1, YAML_PLAIN_SCALAR_STYLE);
 367        if (!value)
 368          goto error;
 369        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 370                                               value))
 371          goto error;
 372  
 373        break;
 374  
 375      case YAML_ALIAS_EVENT:
 376  
 377        /* Add 'type': 'ALIAS'. */
 378  
 379        key = yaml_document_add_scalar(&output_document, NULL,
 380                                       (yaml_char_t *)"type", -1,
 381                                       YAML_PLAIN_SCALAR_STYLE);
 382        if (!key)
 383          goto error;
 384        value = yaml_document_add_scalar(&output_document, NULL,
 385                                         (yaml_char_t *)"ALIAS", -1,
 386                                         YAML_PLAIN_SCALAR_STYLE);
 387        if (!value)
 388          goto error;
 389        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 390                                               value))
 391          goto error;
 392  
 393        /* Add 'anchor': <anchor>. */
 394  
 395        key = yaml_document_add_scalar(&output_document, NULL,
 396                                       (yaml_char_t *)"anchor", -1,
 397                                       YAML_PLAIN_SCALAR_STYLE);
 398        if (!key)
 399          goto error;
 400        value = yaml_document_add_scalar(&output_document, NULL,
 401                                         input_event.data.alias.anchor, -1,
 402                                         YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 403        if (!value)
 404          goto error;
 405        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 406                                               value))
 407          goto error;
 408  
 409        break;
 410  
 411      case YAML_SCALAR_EVENT:
 412  
 413        /* Add 'type': 'SCALAR'. */
 414  
 415        key = yaml_document_add_scalar(&output_document, NULL,
 416                                       (yaml_char_t *)"type", -1,
 417                                       YAML_PLAIN_SCALAR_STYLE);
 418        if (!key)
 419          goto error;
 420        value = yaml_document_add_scalar(&output_document, NULL,
 421                                         (yaml_char_t *)"SCALAR", -1,
 422                                         YAML_PLAIN_SCALAR_STYLE);
 423        if (!value)
 424          goto error;
 425        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 426                                               value))
 427          goto error;
 428  
 429        /* Add 'anchor': <anchor>. */
 430  
 431        if (input_event.data.scalar.anchor) {
 432          key = yaml_document_add_scalar(&output_document, NULL,
 433                                         (yaml_char_t *)"anchor", -1,
 434                                         YAML_PLAIN_SCALAR_STYLE);
 435          if (!key)
 436            goto error;
 437          value = yaml_document_add_scalar(&output_document, NULL,
 438                                           input_event.data.scalar.anchor, -1,
 439                                           YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 440          if (!value)
 441            goto error;
 442          if (!yaml_document_append_mapping_pair(&output_document, properties,
 443                                                 key, value))
 444            goto error;
 445        }
 446  
 447        /* Add 'tag': <tag>. */
 448  
 449        if (input_event.data.scalar.tag) {
 450          key = yaml_document_add_scalar(&output_document, NULL,
 451                                         (yaml_char_t *)"tag", -1,
 452                                         YAML_PLAIN_SCALAR_STYLE);
 453          if (!key)
 454            goto error;
 455          value = yaml_document_add_scalar(&output_document, NULL,
 456                                           input_event.data.scalar.tag, -1,
 457                                           YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 458          if (!value)
 459            goto error;
 460          if (!yaml_document_append_mapping_pair(&output_document, properties,
 461                                                 key, value))
 462            goto error;
 463        }
 464  
 465        /* Add 'value': <value>. */
 466  
 467        key = yaml_document_add_scalar(&output_document, NULL,
 468                                       (yaml_char_t *)"value", -1,
 469                                       YAML_PLAIN_SCALAR_STYLE);
 470        if (!key)
 471          goto error;
 472        value = yaml_document_add_scalar(
 473            &output_document, NULL, input_event.data.scalar.value,
 474            input_event.data.scalar.length, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 475        if (!value)
 476          goto error;
 477        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 478                                               value))
 479          goto error;
 480  
 481        /* Display if the scalar tag is implicit. */
 482  
 483        /* Add 'implicit': {} */
 484  
 485        key = yaml_document_add_scalar(&output_document, NULL,
 486                                       (yaml_char_t *)"version", -1,
 487                                       YAML_PLAIN_SCALAR_STYLE);
 488        if (!key)
 489          goto error;
 490        map = yaml_document_add_mapping(&output_document, NULL,
 491                                        YAML_FLOW_MAPPING_STYLE);
 492        if (!map)
 493          goto error;
 494        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 495                                               map))
 496          goto error;
 497  
 498        /* Add 'plain': <flag>. */
 499  
 500        key = yaml_document_add_scalar(&output_document, NULL,
 501                                       (yaml_char_t *)"plain", -1,
 502                                       YAML_PLAIN_SCALAR_STYLE);
 503        if (!key)
 504          goto error;
 505        value = yaml_document_add_scalar(
 506            &output_document, (yaml_char_t *)YAML_BOOL_TAG,
 507            (input_event.data.scalar.plain_implicit ? (yaml_char_t *)"true"
 508                                                    : (yaml_char_t *)"false"),
 509            -1, YAML_PLAIN_SCALAR_STYLE);
 510        if (!value)
 511          goto error;
 512        if (!yaml_document_append_mapping_pair(&output_document, map, key, value))
 513          goto error;
 514  
 515        /* Add 'quoted': <flag>. */
 516  
 517        key = yaml_document_add_scalar(&output_document, NULL,
 518                                       (yaml_char_t *)"quoted", -1,
 519                                       YAML_PLAIN_SCALAR_STYLE);
 520        if (!key)
 521          goto error;
 522        value = yaml_document_add_scalar(
 523            &output_document, (yaml_char_t *)YAML_BOOL_TAG,
 524            (input_event.data.scalar.quoted_implicit ? (yaml_char_t *)"true"
 525                                                     : (yaml_char_t *)"false"),
 526            -1, YAML_PLAIN_SCALAR_STYLE);
 527        if (!value)
 528          goto error;
 529        if (!yaml_document_append_mapping_pair(&output_document, map, key, value))
 530          goto error;
 531  
 532        /* Display the style information. */
 533  
 534        if (input_event.data.scalar.style) {
 535          yaml_scalar_style_t style = input_event.data.scalar.style;
 536  
 537          /* Add 'style': <style>. */
 538  
 539          key = yaml_document_add_scalar(&output_document, NULL,
 540                                         (yaml_char_t *)"style", -1,
 541                                         YAML_PLAIN_SCALAR_STYLE);
 542          if (!key)
 543            goto error;
 544          value = yaml_document_add_scalar(
 545              &output_document, NULL,
 546              (yaml_char_t
 547                   *)(style == YAML_PLAIN_SCALAR_STYLE
 548                          ? "plain"
 549                          : style == YAML_SINGLE_QUOTED_SCALAR_STYLE
 550                                ? "single-quoted"
 551                                : style == YAML_DOUBLE_QUOTED_SCALAR_STYLE
 552                                      ? "double-quoted"
 553                                      : style == YAML_LITERAL_SCALAR_STYLE
 554                                            ? "literal"
 555                                            : style == YAML_FOLDED_SCALAR_STYLE
 556                                                  ? "folded"
 557                                                  : "unknown"),
 558              -1, YAML_PLAIN_SCALAR_STYLE);
 559          if (!value)
 560            goto error;
 561          if (!yaml_document_append_mapping_pair(&output_document, properties,
 562                                                 key, value))
 563            goto error;
 564        }
 565  
 566        break;
 567  
 568      case YAML_SEQUENCE_START_EVENT:
 569  
 570        /* Add 'type': 'SEQUENCE-START'. */
 571  
 572        key = yaml_document_add_scalar(&output_document, NULL,
 573                                       (yaml_char_t *)"type", -1,
 574                                       YAML_PLAIN_SCALAR_STYLE);
 575        if (!key)
 576          goto error;
 577        value = yaml_document_add_scalar(&output_document, NULL,
 578                                         (yaml_char_t *)"SEQUENCE-START", -1,
 579                                         YAML_PLAIN_SCALAR_STYLE);
 580        if (!value)
 581          goto error;
 582        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 583                                               value))
 584          goto error;
 585  
 586        /* Add 'anchor': <anchor>. */
 587  
 588        if (input_event.data.sequence_start.anchor) {
 589          key = yaml_document_add_scalar(&output_document, NULL,
 590                                         (yaml_char_t *)"anchor", -1,
 591                                         YAML_PLAIN_SCALAR_STYLE);
 592          if (!key)
 593            goto error;
 594          value = yaml_document_add_scalar(&output_document, NULL,
 595                                           input_event.data.sequence_start.anchor,
 596                                           -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 597          if (!value)
 598            goto error;
 599          if (!yaml_document_append_mapping_pair(&output_document, properties,
 600                                                 key, value))
 601            goto error;
 602        }
 603  
 604        /* Add 'tag': <tag>. */
 605  
 606        if (input_event.data.sequence_start.tag) {
 607          key = yaml_document_add_scalar(&output_document, NULL,
 608                                         (yaml_char_t *)"tag", -1,
 609                                         YAML_PLAIN_SCALAR_STYLE);
 610          if (!key)
 611            goto error;
 612          value = yaml_document_add_scalar(&output_document, NULL,
 613                                           input_event.data.sequence_start.tag,
 614                                           -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 615          if (!value)
 616            goto error;
 617          if (!yaml_document_append_mapping_pair(&output_document, properties,
 618                                                 key, value))
 619            goto error;
 620        }
 621  
 622        /* Add 'implicit': <flag>. */
 623  
 624        key = yaml_document_add_scalar(&output_document, NULL,
 625                                       (yaml_char_t *)"implicit", -1,
 626                                       YAML_PLAIN_SCALAR_STYLE);
 627        if (!key)
 628          goto error;
 629        value = yaml_document_add_scalar(
 630            &output_document, (yaml_char_t *)YAML_BOOL_TAG,
 631            (input_event.data.sequence_start.implicit ? (yaml_char_t *)"true"
 632                                                      : (yaml_char_t *)"false"),
 633            -1, YAML_PLAIN_SCALAR_STYLE);
 634        if (!value)
 635          goto error;
 636        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 637                                               value))
 638          goto error;
 639  
 640        /* Display the style information. */
 641  
 642        if (input_event.data.sequence_start.style) {
 643          yaml_sequence_style_t style = input_event.data.sequence_start.style;
 644  
 645          /* Add 'style': <style>. */
 646  
 647          key = yaml_document_add_scalar(&output_document, NULL,
 648                                         (yaml_char_t *)"style", -1,
 649                                         YAML_PLAIN_SCALAR_STYLE);
 650          if (!key)
 651            goto error;
 652          value = yaml_document_add_scalar(
 653              &output_document, NULL,
 654              (yaml_char_t *)(style == YAML_BLOCK_SEQUENCE_STYLE
 655                                  ? "block"
 656                                  : style == YAML_FLOW_SEQUENCE_STYLE
 657                                        ? "flow"
 658                                        : "unknown"),
 659              -1, YAML_PLAIN_SCALAR_STYLE);
 660          if (!value)
 661            goto error;
 662          if (!yaml_document_append_mapping_pair(&output_document, properties,
 663                                                 key, value))
 664            goto error;
 665        }
 666  
 667        break;
 668  
 669      case YAML_SEQUENCE_END_EVENT:
 670  
 671        /* Add 'type': 'SEQUENCE-END'. */
 672  
 673        key = yaml_document_add_scalar(&output_document, NULL,
 674                                       (yaml_char_t *)"type", -1,
 675                                       YAML_PLAIN_SCALAR_STYLE);
 676        if (!key)
 677          goto error;
 678        value = yaml_document_add_scalar(&output_document, NULL,
 679                                         (yaml_char_t *)"SEQUENCE-END", -1,
 680                                         YAML_PLAIN_SCALAR_STYLE);
 681        if (!value)
 682          goto error;
 683        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 684                                               value))
 685          goto error;
 686  
 687        break;
 688  
 689      case YAML_MAPPING_START_EVENT:
 690  
 691        /* Add 'type': 'MAPPING-START'. */
 692  
 693        key = yaml_document_add_scalar(&output_document, NULL,
 694                                       (yaml_char_t *)"type", -1,
 695                                       YAML_PLAIN_SCALAR_STYLE);
 696        if (!key)
 697          goto error;
 698        value = yaml_document_add_scalar(&output_document, NULL,
 699                                         (yaml_char_t *)"MAPPING-START", -1,
 700                                         YAML_PLAIN_SCALAR_STYLE);
 701        if (!value)
 702          goto error;
 703        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 704                                               value))
 705          goto error;
 706  
 707        /* Add 'anchor': <anchor>. */
 708  
 709        if (input_event.data.mapping_start.anchor) {
 710          key = yaml_document_add_scalar(&output_document, NULL,
 711                                         (yaml_char_t *)"anchor", -1,
 712                                         YAML_PLAIN_SCALAR_STYLE);
 713          if (!key)
 714            goto error;
 715          value = yaml_document_add_scalar(&output_document, NULL,
 716                                           input_event.data.mapping_start.anchor,
 717                                           -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 718          if (!value)
 719            goto error;
 720          if (!yaml_document_append_mapping_pair(&output_document, properties,
 721                                                 key, value))
 722            goto error;
 723        }
 724  
 725        /* Add 'tag': <tag>. */
 726  
 727        if (input_event.data.mapping_start.tag) {
 728          key = yaml_document_add_scalar(&output_document, NULL,
 729                                         (yaml_char_t *)"tag", -1,
 730                                         YAML_PLAIN_SCALAR_STYLE);
 731          if (!key)
 732            goto error;
 733          value = yaml_document_add_scalar(&output_document, NULL,
 734                                           input_event.data.mapping_start.tag, -1,
 735                                           YAML_DOUBLE_QUOTED_SCALAR_STYLE);
 736          if (!value)
 737            goto error;
 738          if (!yaml_document_append_mapping_pair(&output_document, properties,
 739                                                 key, value))
 740            goto error;
 741        }
 742  
 743        /* Add 'implicit': <flag>. */
 744  
 745        key = yaml_document_add_scalar(&output_document, NULL,
 746                                       (yaml_char_t *)"implicit", -1,
 747                                       YAML_PLAIN_SCALAR_STYLE);
 748        if (!key)
 749          goto error;
 750        value = yaml_document_add_scalar(
 751            &output_document, (yaml_char_t *)YAML_BOOL_TAG,
 752            (yaml_char_t *)(input_event.data.mapping_start.implicit ? "true"
 753                                                                    : "false"),
 754            -1, YAML_PLAIN_SCALAR_STYLE);
 755        if (!value)
 756          goto error;
 757        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 758                                               value))
 759          goto error;
 760  
 761        /* Display the style information. */
 762  
 763        if (input_event.data.sequence_start.style) {
 764          yaml_sequence_style_t style = input_event.data.sequence_start.style;
 765  
 766          /* Add 'style': <style>. */
 767  
 768          key = yaml_document_add_scalar(&output_document, NULL,
 769                                         (yaml_char_t *)"style", -1,
 770                                         YAML_PLAIN_SCALAR_STYLE);
 771          if (!key)
 772            goto error;
 773          value = yaml_document_add_scalar(
 774              &output_document, NULL,
 775              (yaml_char_t *)(style == YAML_BLOCK_MAPPING_STYLE
 776                                  ? "block"
 777                                  : style == YAML_FLOW_MAPPING_STYLE ? "flow"
 778                                                                     : "unknown"),
 779              -1, YAML_PLAIN_SCALAR_STYLE);
 780          if (!value)
 781            goto error;
 782          if (!yaml_document_append_mapping_pair(&output_document, properties,
 783                                                 key, value))
 784            goto error;
 785        }
 786  
 787        break;
 788  
 789      case YAML_MAPPING_END_EVENT:
 790  
 791        /* Add 'type': 'MAPPING-END'. */
 792  
 793        key = yaml_document_add_scalar(&output_document, NULL,
 794                                       (yaml_char_t *)"type", -1,
 795                                       YAML_PLAIN_SCALAR_STYLE);
 796        if (!key)
 797          goto error;
 798        value = yaml_document_add_scalar(&output_document, NULL,
 799                                         (yaml_char_t *)"MAPPING-END", -1,
 800                                         YAML_PLAIN_SCALAR_STYLE);
 801        if (!value)
 802          goto error;
 803        if (!yaml_document_append_mapping_pair(&output_document, properties, key,
 804                                               value))
 805          goto error;
 806  
 807        break;
 808  
 809      default:
 810        /* It couldn't really happen. */
 811        break;
 812      }
 813  
 814      /* Delete the event object. */
 815  
 816      yaml_event_delete(&input_event);
 817    }
 818  
 819    if (!yaml_emitter_dump(&emitter, &output_document))
 820      goto error;
 821  
 822    yaml_emitter_close(&emitter);
 823  
 824  error:
 825  
 826    free(out.buf);
 827  
 828    yaml_event_delete(&input_event);
 829    yaml_document_delete(&output_document);
 830    yaml_parser_delete(&parser);
 831    yaml_emitter_delete(&emitter);
 832  
 833    return 0;
 834  }
```