# LLM 하네스 수정 — libyaml/official_deconstructor, 제안 2,3,4,5,6,10

- 모델: `claude-sonnet-5-5`
- 제안: `yaml_scalar_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, const yaml_char_t *, int, int, int, yaml_scalar_style_t)`의 2번째 인자 `anchor`를 하네스가 고정합니다(117행에서 항상 `0`, 126행에서 항상 `0`, 140행에서 항상 `0`, 149행에서 항상 `0`, 170행에서 항상 `0`, 179행에서 항상 `0`, 192행에서 항상 `0`, 201행에서 항상 `0`, 217행에서 항상 `0`, 235행에서 항상 `0`, 245행에서 항상 `0`, 254행에서 항상 `0`, 264행에서 항상 `0`, 286행에서 항상 `0`, 315행에서 항상 `0`, 324행에서 항상 `0`, 334행에서 항상 `0`, 343행에서 항상 `0`, 369행에서 항상 `0`, 378행에서 항상 `0`, 394행에서 항상 `0`, 403행에서 항상 `0`, 412행에서 항상 `0`, 421행에서 항상 `0`, 436행에서 항상 `0`, 445행에서 항상 `0`, 454행에서 항상 `0`, 463행에서 항상 `0`, 477행에서 항상 `0`, 486행에서 항상 `0`, 498행에서 항상 `0`, 507행에서 항상 `0`, 521행에서 항상 `0`, 530행에서 항상 `0`, 543행에서 항상 `0`, 552행에서 항상 `0`, 564행에서 항상 `0`, 582행에서 항상 `0`, 591행에서 항상 `0`, 602행에서 항상 `0`, 611행에서 항상 `0`, 635행에서 항상 `0`, 644행에서 항상 `0`, 671행에서 항상 `0`, 680행에서 항상 `0`, 693행에서 항상 `0`, 702행에서 항상 `0`, 716행에서 항상 `0`, 725행에서 항상 `0`, 736행에서 항상 `0`, 745행에서 항상 `0`, 762행에서 항상 `0`, 771행에서 항상 `0`, 790행에서 항상 `0`, 799행에서 항상 `0`, 812행에서 항상 `0`, 821행에서 항상 `0`, 834행에서 항상 `0`, 843행에서 항상 `0`, 857행에서 항상 `0`, 866행에서 항상 `0`, 877행에서 항상 `0`, 886행에서 항상 `0`, 903행에서 항상 `0`, 912행에서 항상 `0`, 931행에서 항상 `0`, 940행에서 항상 `0`) (라이브러리 내부 `yaml_strdup`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_sequence_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_sequence_style_t)`의 3번째 인자 `tag`를 하네스가 고정합니다(82행에서 항상 `"tag:yaml.org,2002:seq"`, 295행에서 항상 `"tag:yaml.org,2002:seq"`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_mapping_start_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_mapping_style_t)`의 3번째 인자 `tag`를 하네스가 고정합니다(103행에서 항상 `"tag:yaml.org,2002:map"`, 226행에서 항상 `"tag:yaml.org,2002:map"`, 306행에서 항상 `"tag:yaml.org,2002:map"`, 573행에서 항상 `"tag:yaml.org,2002:map"`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)`의 2번째 인자 `version_directive`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_start_event_initialize(yaml_event_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int)`의 3번째 인자 `tag_directives_start`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_scalar_event_initialize(yaml_event_t *, const yaml_char_t *, const yaml_char_t *, const yaml_char_t *, int, int, int, yaml_scalar_style_t)`의 3번째 인자 `tag`를 하네스가 `"tag:yaml.org,2002:str"`, `"tag:yaml.org,2002:int"`, `"tag:yaml.org,2002:bool"` 중에서만 고릅니다(117행, 126행, 140행, 149행, 170행, 179행, 192행, 201행, 217행, 235행, 245행, 254행, 264행, 286행, 315행, 324행, 334행, 343행, 369행, 378행, 394행, 403행, 412행, 421행, 436행, 445행, 454행, 463행, 477행, 486행, 498행, 507행, 521행, 530행, 543행, 552행, 564행, 582행, 591행, 602행, 611행, 635행, 644행, 671행, 680행, 693행, 702행, 716행, 725행, 736행, 745행, 762행, 771행, 790행, 799행, 812행, 821행, 834행, 843행, 857행, 866행, 877행, 886행, 903행, 912행, 931행, 940행) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 11개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 컴파일 실패 | -/- | - | - | 23409/19972 |
| 2 | 통과 | 10/11 | 2: 2/3, 3: 2/2, 4: 2/2, 5: 1/1, 6: 1/1, 10: 2/2 | - | 41531/19096 |
| 3 | 통과 | 10/11 | 2: 2/3, 3: 2/2, 4: 2/2, 5: 1/1, 6: 1/1, 10: 2/2 | - | 60076/19294 |

**채택 후보: 시도 2** (`harnesses/libyaml/llm/official_deconstructor_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -14,7 +14,6 @@
 // limitations under the License.
 
 #include "yaml.h"
-#include "yaml_write_handler.h"
 #include <assert.h>
 #include <stdbool.h>
 #include <stdint.h>
@@ -26,6 +25,37 @@
 #undef NDEBUG
 #endif
 
+/* [gapfuzz-llm] 빌드 환경에 yaml_write_handler.h가 없어 같은 역할의 버퍼 타입과 쓰기 핸들러를 하네스에 직접 정의 */
+typedef struct yaml_output_buffer {
+  unsigned char *buf;
+  size_t size;
+  size_t capacity;
+} yaml_output_buffer_t;
+
+static int yaml_write_handler(void *data, unsigned char *buffer, size_t size) {
+  yaml_output_buffer_t *out = (yaml_output_buffer_t *)data;
+  if (out->capacity == 0)
+    out->capacity = 1000;
+  if (out->buf == NULL) {
+    out->buf = (unsigned char *)malloc(out->capacity);
+    if (out->buf == NULL)
+      return 0;
+  }
+  if (size > out->capacity - out->size) {
+    size_t new_capacity = out->capacity;
+    while (size > new_capacity - out->size)
+      new_capacity *= 2;
+    unsigned char *new_buf = (unsigned char *)realloc(out->buf, new_capacity);
+    if (new_buf == NULL)
+      return 0;
+    out->buf = new_buf;
+    out->capacity = new_capacity;
+  }
+  memcpy(out->buf + out->size, buffer, size);
+  out->size += size;
+  return 1;
+}
+
 int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   if (size < 2)
     return 0;
@@ -36,6 +66,65 @@
   data += 2;
   size -= 2;
 
+  /* [gapfuzz-llm] 입력 앞쪽 바이트를 순서대로 배분해 서로 겹치지 않게 선택값으로 사용 */
+  uint8_t sel[6] = {0, 0, 0, 0, 0, 0};
+  size_t nsel = size < 6 ? size : 6;
+  memcpy(sel, data, nsel);
+  data += nsel;
+  size -= nsel;
+
+  /* 스칼라 anchor 후보: NULL이 자주 나오도록 하고, 유효/잘린 UTF-8도 포함 */
+  const yaml_char_t *scalar_anchor = NULL;
+  switch (sel[0] % 6) {
+  case 1: scalar_anchor = (const yaml_char_t *)"a"; break;
+  case 2: scalar_anchor = (const yaml_char_t *)"anchor1"; break;
+  case 3: scalar_anchor = (const yaml_char_t *)"\xc3\xa9"; break;
+  case 4: scalar_anchor = (const yaml_char_t *)"\xe3\x81"; break; /* 잘린 UTF-8 */
+  default: scalar_anchor = NULL; break;
+  }
+
+  /* 스칼라 tag 후보: 원래 값 3개 + NULL + 사용자 정의 + 잘린 UTF-8 */
+  const yaml_char_t *scalar_tag = NULL;
+  switch (sel[1] % 7) {
+  case 0: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:str"; break;
+  case 1: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:int"; break;
+  case 2: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:bool"; break;
+  case 3: scalar_tag = NULL; break;
+  case 4: scalar_tag = (const yaml_char_t *)"!custom"; break;
+  case 5: scalar_tag = (const yaml_char_t *)"\xe3\x81"; break;
+  default: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:str"; break;
+  }
+
+  /* 시퀀스 tag 후보 */
+  const yaml_char_t *seq_tag = NULL;
+  switch (sel[2] % 5) {
+  case 0: seq_tag = (const yaml_char_t *)"tag:yaml.org,2002:seq"; break;
+  case 1: seq_tag = NULL; break;
+  case 2: seq_tag = (const yaml_char_t *)"!myseq"; break;
+  case 3: seq_tag = (const yaml_char_t *)"\xc3\xa9"; break;
+  default: seq_tag = (const yaml_char_t *)"\xe3\x81"; break;
+  }
+
+  /* 매핑 tag 후보 */
+  const yaml_char_t *map_tag = NULL;
+  switch (sel[3] % 5) {
+  case 0: map_tag = (const yaml_char_t *)"tag:yaml.org,2002:map"; break;
+  case 1: map_tag = NULL; break;
+  case 2: map_tag = (const yaml_char_t *)"!mymap"; break;
+  case 3: map_tag = (const yaml_char_t *)"\xc3\xa9"; break;
+  default: map_tag = (const yaml_char_t *)"\xe3\x81"; break;
+  }
+
+  /* 문서 시작의 version_directive 후보 */
+  yaml_version_directive_t doc_version = {1, (sel[4] >> 4) & 1 ? 2 : 1};
+  yaml_version_directive_t *doc_version_ptr = (sel[4] & 1) ? &doc_version : NULL;
+
+  /* 문서 시작의 tag_directives 후보 */
+  yaml_tag_directive_t doc_tag_directive = {
+      (yaml_char_t *)"!e!", (yaml_char_t *)"tag:example.com,2000:"};
+  yaml_tag_directive_t *doc_tags_start = (sel[5] & 1) ? &doc_tag_directive : NULL;
+  yaml_tag_directive_t *doc_tags_end = (sel[5] & 1) ? &doc_tag_directive + 1 : NULL;
+
   yaml_parser_t parser;
   yaml_emitter_t emitter;
   yaml_event_t input_event;
@@ -72,7 +161,7 @@
 
   /* Create and emit the DOCUMENT-START event. */
 
-  if (!yaml_document_start_event_initialize(&output_event, NULL, NULL, NULL, 0))
+  if (!yaml_document_start_event_initialize(&output_event, doc_version_ptr, doc_tags_start, doc_tags_end, 0)) // [gapfuzz-llm] version_directive와 tag_directives를 퍼저 입력으로 선택
     goto error;
   if (!yaml_emitter_emit(&emitter, &output_event))
     goto error;
@@ -80,7 +169,7 @@
   /* Create and emit the SEQUENCE-START event. */
 
   if (!yaml_sequence_start_event_initialize(
-          &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:seq", 1,
+          &output_event, NULL, seq_tag, 1, // [gapfuzz-llm] 시퀀스 tag를 퍼저 입력으로 선택
           YAML_BLOCK_SEQUENCE_STYLE))
     goto error;
   if (!yaml_emitter_emit(&emitter, &output_event))
@@ -101,7 +190,7 @@
     /* Create and emit a MAPPING-START event. */
 
     if (!yaml_mapping_start_event_initialize(
-            &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map", 1,
+            &output_event, NULL, map_tag, 1, // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
             YAML_BLOCK_MAPPING_STYLE))
       goto error;
     if (!yaml_emitter_emit(&emitter, &output_event))
@@ -115,7 +204,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -124,7 +213,7 @@
       /* Write 'STREAM-START'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"STREAM-START", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -138,7 +227,7 @@
         /* Write 'encoding'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"encoding", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -147,7 +236,7 @@
         /* Write the stream encoding. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)(encoding == YAML_UTF8_ENCODING
                                     ? "utf-8"
                                     : encoding == YAML_UTF16LE_ENCODING
@@ -168,7 +257,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -177,7 +266,7 @@
       /* Write 'STREAM-END'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"STREAM-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -190,7 +279,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -198,8 +287,7 @@
 
       /* Write 'DOCUMENT-START'. */
 
-      if (!yaml_scalar_event_initialize(&output_event, NULL,
-                                        (yaml_char_t *)"tag:yaml.org,2002:str",
+      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                         (yaml_char_t *)"DOCUMENT-START", -1, 1,
                                         1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
@@ -215,7 +303,7 @@
 
         /* Write 'version'. */
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"version", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -224,7 +312,7 @@
         /* Write '{'. */
 
         if (!yaml_mapping_start_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map", 1,
+                &output_event, NULL, map_tag, 1, // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
                 YAML_FLOW_MAPPING_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -233,7 +321,7 @@
         /* Write 'major'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"major", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -243,7 +331,7 @@
 
         sprintf(number, "%d", version->major);
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:int",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)number, -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -252,7 +340,7 @@
         /* Write 'minor'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"minor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -262,7 +350,7 @@
 
         sprintf(number, "%d", version->minor);
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:int",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)number, -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -284,7 +372,7 @@
 
         /* Write 'tags'. */
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"tags", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -293,7 +381,7 @@
         /* Start a block sequence. */
 
         if (!yaml_sequence_start_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:seq", 1,
+                &output_event, NULL, seq_tag, 1, // [gapfuzz-llm] 시퀀스 tag를 퍼저 입력으로 선택
                 YAML_BLOCK_SEQUENCE_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -304,8 +392,8 @@
           /* Write '{'. */
 
           if (!yaml_mapping_start_event_initialize(
-                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map",
-                  1, YAML_FLOW_MAPPING_STYLE))
+                  &output_event, NULL, map_tag,
+                  1, YAML_FLOW_MAPPING_STYLE)) // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
             goto error;
           if (!yaml_emitter_emit(&emitter, &output_event))
             goto error;
@@ -313,7 +401,7 @@
           /* Write 'handle'. */
 
           if (!yaml_scalar_event_initialize(
-                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                   (yaml_char_t *)"handle", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
             goto error;
           if (!yaml_emitter_emit(&emitter, &output_event))
@@ -322,7 +410,7 @@
           /* Write the tag directive handle. */
 
           if (!yaml_scalar_event_initialize(
-                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                   (yaml_char_t *)tag->handle, -1, 0, 1,
                   YAML_DOUBLE_QUOTED_SCALAR_STYLE))
             goto error;
@@ -332,7 +420,7 @@
           /* Write 'prefix'. */
 
           if (!yaml_scalar_event_initialize(
-                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                   (yaml_char_t *)"prefix", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
             goto error;
           if (!yaml_emitter_emit(&emitter, &output_event))
@@ -341,7 +429,7 @@
           /* Write the tag directive prefix. */
 
           if (!yaml_scalar_event_initialize(
-                  &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                   (yaml_char_t *)tag->prefix, -1, 0, 1,
                   YAML_DOUBLE_QUOTED_SCALAR_STYLE))
             goto error;
@@ -367,7 +455,7 @@
       /* Write 'implicit'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -376,7 +464,7 @@
       /* Write if the document is implicit. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)(input_event.data.document_start.implicit
                                   ? "true"
                                   : "false"),
@@ -392,7 +480,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -401,7 +489,7 @@
       /* Write 'DOCUMENT-END'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"DOCUMENT-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -410,7 +498,7 @@
       /* Write 'implicit'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -419,7 +507,7 @@
       /* Write if the document is implicit. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)(input_event.data.document_end.implicit ? "true"
                                                                      : "false"),
               -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
@@ -434,7 +522,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -443,7 +531,7 @@
       /* Write 'ALIAS'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"ALIAS", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -452,7 +540,7 @@
       /* Write 'anchor'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -460,8 +548,7 @@
 
       /* Write the alias anchor. */
 
-      if (!yaml_scalar_event_initialize(&output_event, NULL,
-                                        (yaml_char_t *)"tag:yaml.org,2002:str",
+      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                         input_event.data.alias.anchor, -1, 0, 1,
                                         YAML_DOUBLE_QUOTED_SCALAR_STYLE))
         goto error;
@@ -475,7 +562,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -484,7 +571,7 @@
       /* Write 'SCALAR'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"SCALAR", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -496,7 +583,7 @@
         /* Write 'anchor'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -505,7 +592,7 @@
         /* Write the scalar anchor. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 input_event.data.scalar.anchor, -1, 0, 1,
                 YAML_DOUBLE_QUOTED_SCALAR_STYLE))
           goto error;
@@ -519,7 +606,7 @@
         /* Write 'tag'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -528,7 +615,7 @@
         /* Write the scalar tag. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 input_event.data.scalar.tag, -1, 0, 1,
                 YAML_DOUBLE_QUOTED_SCALAR_STYLE))
           goto error;
@@ -541,7 +628,7 @@
       /* Write 'value'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"value", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -550,7 +637,7 @@
       /* Write the scalar value. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               input_event.data.scalar.value, input_event.data.scalar.length, 0,
               1, YAML_DOUBLE_QUOTED_SCALAR_STYLE))
         goto error;
@@ -562,7 +649,7 @@
       /* Write 'implicit'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -571,7 +658,7 @@
       /* Write '{'. */
 
       if (!yaml_mapping_start_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:map", 1,
+              &output_event, NULL, map_tag, 1, // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
               YAML_FLOW_MAPPING_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -580,7 +667,7 @@
       /* Write 'plain'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"plain", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -589,7 +676,7 @@
       /* Write if the scalar is implicit in the plain style. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)(input_event.data.scalar.plain_implicit ? "true"
                                                                      : "false"),
               -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
@@ -600,7 +687,7 @@
       /* Write 'quoted'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"non-plain", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -609,7 +696,7 @@
       /* Write if the scalar is implicit in a non-plain style. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)(input_event.data.scalar.quoted_implicit
                                   ? "true"
                                   : "false"),
@@ -633,7 +720,7 @@
         /* Write 'style'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -642,7 +729,7 @@
         /* Write the scalar style. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t
                      *)(style == YAML_PLAIN_SCALAR_STYLE
                             ? "plain"
@@ -669,7 +756,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -677,8 +764,7 @@
 
       /* Write 'SEQUENCE-START'. */
 
-      if (!yaml_scalar_event_initialize(&output_event, NULL,
-                                        (yaml_char_t *)"tag:yaml.org,2002:str",
+      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                         (yaml_char_t *)"SEQUENCE-START", -1, 1,
                                         1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
@@ -691,7 +777,7 @@
         /* Write 'anchor'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -700,7 +786,7 @@
         /* Write the sequence anchor. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 input_event.data.sequence_start.anchor, -1, 0, 1,
                 YAML_DOUBLE_QUOTED_SCALAR_STYLE))
           goto error;
@@ -714,7 +800,7 @@
         /* Write 'tag'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -723,7 +809,7 @@
         /* Write the sequence tag. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 input_event.data.sequence_start.tag, -1, 0, 1,
                 YAML_DOUBLE_QUOTED_SCALAR_STYLE))
           goto error;
@@ -734,7 +820,7 @@
       /* Write 'implicit'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -743,7 +829,7 @@
       /* Write if the sequence tag is implicit. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)(input_event.data.sequence_start.implicit
                                   ? "true"
                                   : "false"),
@@ -760,7 +846,7 @@
         /* Write 'style'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -769,7 +855,7 @@
         /* Write the scalar style. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)(style == YAML_BLOCK_SEQUENCE_STYLE
                                     ? "block"
                                     : style == YAML_FLOW_SEQUENCE_STYLE
@@ -788,7 +874,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -797,7 +883,7 @@
       /* Write 'SEQUENCE-END'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"SEQUENCE-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -810,7 +896,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -818,8 +904,7 @@
 
       /* Write 'MAPPING-START'. */
 
-      if (!yaml_scalar_event_initialize(&output_event, NULL,
-                                        (yaml_char_t *)"tag:yaml.org,2002:str",
+      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                         (yaml_char_t *)"MAPPING-START", -1, 1,
                                         1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
@@ -832,7 +917,7 @@
         /* Write 'anchor'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -841,7 +926,7 @@
         /* Write the mapping anchor. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 input_event.data.mapping_start.anchor, -1, 0, 1,
                 YAML_DOUBLE_QUOTED_SCALAR_STYLE))
           goto error;
@@ -855,7 +940,7 @@
         /* Write 'tag'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -864,7 +949,7 @@
         /* Write the mapping tag. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 input_event.data.mapping_start.tag, -1, 0, 1,
                 YAML_DOUBLE_QUOTED_SCALAR_STYLE))
           goto error;
@@ -875,7 +960,7 @@
       /* Write 'implicit'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -884,7 +969,7 @@
       /* Write if the mapping tag is implicit. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:bool",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)(input_event.data.mapping_start.implicit
                                   ? "true"
                                   : "false"),
@@ -901,7 +986,7 @@
         /* Write 'style'. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
           goto error;
         if (!yaml_emitter_emit(&emitter, &output_event))
@@ -910,7 +995,7 @@
         /* Write the scalar style. */
 
         if (!yaml_scalar_event_initialize(
-                &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                 (yaml_char_t *)(style == YAML_BLOCK_MAPPING_STYLE
                                     ? "block"
                                     : style == YAML_FLOW_MAPPING_STYLE
@@ -929,7 +1014,7 @@
       /* Write 'type'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
@@ -938,7 +1023,7 @@
       /* Write 'MAPPING-END'. */
 
       if (!yaml_scalar_event_initialize(
-              &output_event, NULL, (yaml_char_t *)"tag:yaml.org,2002:str",
+              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
               (yaml_char_t *)"MAPPING-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
         goto error;
       if (!yaml_emitter_emit(&emitter, &output_event))
```
