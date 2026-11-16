# LLM 하네스 수정 — libyaml/official_deconstructor_alt, 제안 1,2,3,4,5,6,8,9

- 모델: `claude-sonnet-5-5`
- 제안: `yaml_emitter_open(yaml_emitter_t *)`의 1번째 인자 `emitter`를 하네스가 고정합니다(70행에서 항상 같은 객체 `&emitter`) (라이브러리 내부 `yaml_emitter_emit` → `yaml_emitter_state_machine` → `yaml_emitter_emit_flow_mapping_key` → `yaml_emitter_check_simple_key`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_add_sequence(yaml_document_t *, const yaml_char_t *, yaml_sequence_style_t)`의 2번째 인자 `tag`를 하네스가 고정합니다(80행에서 항상 `0`, 266행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_add_mapping(yaml_document_t *, const yaml_char_t *, yaml_mapping_style_t)`의 2번째 인자 `tag`를 하네스가 고정합니다(101행에서 항상 `0`, 210행에서 항상 `0`, 278행에서 항상 `0`, 490행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_emitter_dump(yaml_emitter_t *, yaml_document_t *)`의 1번째 인자 `emitter`를 하네스가 고정합니다(819행에서 항상 같은 객체 `&emitter`) (라이브러리 내부 `yaml_emitter_dump_node`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)`의 2번째 인자 `version_directive`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_initialize(yaml_document_t *, yaml_version_directive_t *, yaml_tag_directive_t *, yaml_tag_directive_t *, int, int)`의 3번째 인자 `tag_directives_start`를 하네스가 고정합니다(75행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_delete(yaml_document_t *)`의 1번째 인자 `document`를 하네스가 고정합니다(829행에서 항상 같은 객체 `&output_document`) → 퍼저 입력으로 바꾸세요
- 제안: `yaml_document_add_scalar(yaml_document_t *, const yaml_char_t *, const yaml_char_t *, int, yaml_scalar_style_t)`의 2번째 인자 `tag`를 하네스가 `0`, `"tag:yaml.org,2002:int"`, `"tag:yaml.org,2002:bool"` 중에서만 고릅니다(115행, 120행, 134행, 139행, 162행, 167행, 182행, 187행, 205행, 220행, 226행, 237행, 243행, 261행, 287행, 292행, 302행, 307행, 319행, 324행, 341행, 346행, 357행, 362행, 379행, 384행, 395행, 400행, 415행, 420행, 432행, 437행, 450행, 455행, 467행, 472행, 485행, 500행, 505행, 517행, 522행, 539행, 544행, 572행, 577행, 589행, 594행, 607행, 612행, 624행, 629행, 647행, 652행, 673행, 678행, 693행, 698행, 710행, 715행, 728행, 733행, 745행, 750행, 768행, 773행, 793행, 798행) (라이브러리 내부 `yaml_strdup`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 17개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 컴파일 실패 | -/- | - | - | 19993/19842 |
| 2 | 실패 | 8/17 | 1: 0/5, 2: 2/2, 3: 2/2, 4: 0/2, 5: 1/1, 6: 1/1, 8: 0/1, 9: 2/3 | LIBRARY(강) | 34901/15702 |
| 3 | 통과 | 11/17 | 1: 2/5, 2: 2/2, 3: 2/2, 4: 1/2, 5: 1/1, 6: 1/1, 8: 0/1, 9: 2/3 | - | 51294/18580 |

**채택 후보: 시도 3** (`harnesses/libyaml/llm/official_deconstructor_alt_combined/try3.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 3
@@ -14,7 +14,6 @@
 // limitations under the License.
 
 #include "yaml.h"
-#include "yaml_write_handler.h"
 #include <assert.h>
 #include <stdbool.h>
 #include <stdint.h>
@@ -26,22 +25,115 @@
 #undef NDEBUG
 #endif
 
+typedef struct yaml_output_buffer { // [gapfuzz-llm] yaml_write_handler.h가 빌드 환경에 없어 같은 역할의 타입을 하네스에 직접 정의
+  unsigned char *buf;
+  size_t size;
+  size_t capacity;
+} yaml_output_buffer_t;
+
+static int yaml_write_handler(void *data, unsigned char *buffer, size_t size) { // [gapfuzz-llm] 헤더 대신 쓰기 핸들러를 하네스에 직접 구현 (용량 초과 시 실패 반환)
+  yaml_output_buffer_t *out = (yaml_output_buffer_t *)data;
+  if (size > out->capacity || out->size > out->capacity - size)
+    return 0;
+  if (size == 0)
+    return 1;
+  unsigned char *nb = (unsigned char *)realloc(out->buf, out->size + size);
+  if (!nb)
+    return 0;
+  out->buf = nb;
+  memcpy(out->buf + out->size, buffer, size);
+  out->size += size;
+  return 1;
+}
+
+/* 태그 선택용 상태: 입력 바이트로 시드되고 호출마다 갱신된다. */
+static uint8_t g_tag_state; // [gapfuzz-llm] 태그를 퍼저 입력에서 고르기 위한 상태 변수 추가
+static bool g_pick_enabled; // [gapfuzz-llm] 대체 문서를 만들 때는 태그 변경을 끄기 위한 플래그
+static unsigned g_calls; // [gapfuzz-llm] 태그 선택 호출 횟수
+static int g_bad_at; // [gapfuzz-llm] 잘못된 UTF-8 태그를 낼 호출 번호 (-1이면 사용 안 함)
+
+static const yaml_char_t *pick_tag(const yaml_char_t *orig) { // [gapfuzz-llm] 원래 태그(NULL/INT/BOOL)와 다른 태그 값을 입력에서 고름
+  static const yaml_char_t *const alt_tags[] = {
+      (const yaml_char_t *)"tag:yaml.org,2002:int",
+      (const yaml_char_t *)"tag:yaml.org,2002:bool",
+      (const yaml_char_t *)"!custom",
+  };
+  static const yaml_char_t *const bad_tags[] = {
+      (const yaml_char_t *)"\xff\xfe", /* 잘못된 UTF-8 */
+      (const yaml_char_t *)"\xE3\x81", /* 잘린 UTF-8 */
+  };
+  if (!g_pick_enabled)
+    return orig;
+  unsigned n = g_calls++;
+  if (g_bad_at >= 0 && n == (unsigned)g_bad_at) // [gapfuzz-llm] 잘못된 태그는 실행당 최대 1번만 내서 이후 흐름(dump)이 막히지 않게 함
+    return bad_tags[g_tag_state & 1];
+  g_tag_state = (uint8_t)(g_tag_state * 167u + 13u);
+  unsigned idx = (g_tag_state >> 5) % 6u;
+  if (idx < 3)
+    return orig; /* 원래 값도 계속 나오게 함 */
+  return alt_tags[idx - 3];
+}
+
+static int harness_add_scalar(yaml_document_t *d, const yaml_char_t *tag,
+                              const yaml_char_t *value, int length,
+                              yaml_scalar_style_t style) {
+  return yaml_document_add_scalar(d, pick_tag(tag), value, length, style);
+}
+
+static int harness_add_sequence(yaml_document_t *d, const yaml_char_t *tag,
+                                yaml_sequence_style_t style) {
+  return yaml_document_add_sequence(d, pick_tag(tag), style);
+}
+
+static int harness_add_mapping(yaml_document_t *d, const yaml_char_t *tag,
+                               yaml_mapping_style_t style) {
+  return yaml_document_add_mapping(d, pick_tag(tag), style);
+}
+
+#define yaml_document_add_scalar(d, t, v, l, s) harness_add_scalar(d, t, v, l, s) // [gapfuzz-llm] scalar tag를 입력으로 선택하는 래퍼로 교체
+#define yaml_document_add_sequence(d, t, s) harness_add_sequence(d, t, s) // [gapfuzz-llm] sequence tag를 입력으로 선택하는 래퍼로 교체
+#define yaml_document_add_mapping(d, t, s) harness_add_mapping(d, t, s) // [gapfuzz-llm] mapping tag를 입력으로 선택하는 래퍼로 교체
+
 int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
   if (size < 2)
     return 0;
 
   bool done = false;
-  bool is_canonical = data[0] & 1;
-  bool is_unicode = data[1] & 1;
-  data += 2;
-  size -= 2;
+  uint8_t hb[8] = {0}; // [gapfuzz-llm] 앞쪽 헤더 바이트를 순서대로 배분해 겹치지 않게 사용
+  size_t hn = size < 8 ? size : 8; // [gapfuzz-llm] 헤더 길이 (최대 8바이트)
+  memcpy(hb, data, hn); // [gapfuzz-llm] 헤더 바이트 복사
+  bool is_canonical = hb[0] & 1;
+  bool is_unicode = hb[1] & 1;
+  data += hn; // [gapfuzz-llm] 사용한 헤더 바이트만큼 건너뜀
+  size -= hn; // [gapfuzz-llm] 나머지는 원래대로 파서 입력으로 사용
+
+  g_tag_state = hb[5]; // [gapfuzz-llm] 태그 선택 상태를 입력으로 시드
+  g_calls = 0; // [gapfuzz-llm] 호출 카운터 초기화
+  g_bad_at = (hb[5] & 0x80) ? (int)((hb[5] >> 1) & 0x3F) : -1; // [gapfuzz-llm] 잘못된 태그를 낼 호출 번호를 입력으로 결정
+  g_pick_enabled = true; // [gapfuzz-llm] 태그 변경 켬
 
   yaml_parser_t parser;
   yaml_emitter_t emitter;
   yaml_event_t input_event;
   yaml_document_t output_document;
+  yaml_document_t alt_document; // [gapfuzz-llm] 앵커/별칭이 생기는 대체 문서
+  yaml_document_t *dump_doc = &output_document; // [gapfuzz-llm] dump 대상 문서를 입력으로 선택
+  yaml_document_t *other_doc = &alt_document; // [gapfuzz-llm] 선택되지 않은 문서
+  bool dumped = false; // [gapfuzz-llm] yaml_emitter_dump가 문서 소유권을 가져갔는지 표시 (이중 해제 방지)
+  yaml_version_directive_t ver = {1, 1 + ((hb[6] >> 3) & 1)}; // [gapfuzz-llm] 입력으로 정하는 버전 지시자
+  yaml_tag_directive_t tds[2] = {
+      {(yaml_char_t *)"!e!", (yaml_char_t *)"tag:example.com,2000:app/"},
+      {(yaml_char_t *)"!f!", (yaml_char_t *)"tag:example.org,2001:"}}; // [gapfuzz-llm] 유효한 태그 지시자 후보
+  int td_n = (hb[6] >> 1) & 3; // [gapfuzz-llm] 태그 지시자 개수를 입력으로 선택
+  if (td_n > 2)
+    td_n = 2;
 
   int root;
+  int a_root, a_item, a_map, a_val; // [gapfuzz-llm] 대체 문서 노드 ID
+
+  memset(&input_event, 0, sizeof(input_event)); // [gapfuzz-llm] 조기 error 경로에서 안전한 해제를 위해 0 초기화
+  memset(&output_document, 0, sizeof(output_document)); // [gapfuzz-llm] 조기 error 경로에서 안전한 해제를 위해 0 초기화
+  memset(&alt_document, 0, sizeof(alt_document)); // [gapfuzz-llm] 조기 error 경로에서 안전한 해제를 위해 0 초기화
 
   /* Initialize the parser and emitter objects. */
 
@@ -64,6 +156,11 @@
 
   yaml_emitter_set_canonical(&emitter, is_canonical);
   yaml_emitter_set_unicode(&emitter, is_unicode);
+  if (hb[2] % 4 != 0) // [gapfuzz-llm] emitter 폭 설정을 입력으로 변경 (0이면 기본값 유지)
+    yaml_emitter_set_width(&emitter, (int)(hb[2] % 100) - 1);
+  if (hb[3] & 0x80) // [gapfuzz-llm] emitter 들여쓰기를 입력으로 변경
+    yaml_emitter_set_indent(&emitter, hb[3] & 0x0F);
+  yaml_emitter_set_break(&emitter, (yaml_break_t)(hb[4] % 4)); // [gapfuzz-llm] emitter 줄바꿈 종류를 입력으로 변경
 
   /* Create and emit the STREAM-START event. */
 
@@ -72,8 +169,47 @@
 
   /* Create a output_document object. */
 
-  if (!yaml_document_initialize(&output_document, NULL, NULL, NULL, 0, 0))
+  if (!yaml_document_initialize(&output_document,
+                                (hb[6] & 1) ? &ver : NULL,
+                                td_n ? tds : NULL, td_n ? tds + td_n : NULL, 0,
+                                0)) // [gapfuzz-llm] 버전/태그 지시자를 입력에 따라 전달
     goto error;
+
+  /* Build the alternative document (shared nodes -> anchors/aliases). */
+
+  if (hb[7] & 1) { // [gapfuzz-llm] 대체 문서 사용 여부를 입력으로 선택
+    g_pick_enabled = false; // [gapfuzz-llm] 대체 문서는 항상 유효한 기본 태그로 만들어 anchor/alias 경로가 막히지 않게 함
+    if (!yaml_document_initialize(&alt_document, NULL, NULL, NULL, 1, 1))
+      goto error;
+    a_root = yaml_document_add_sequence(
+        &alt_document, NULL,
+        (hb[7] & 2) ? YAML_FLOW_SEQUENCE_STYLE : YAML_BLOCK_SEQUENCE_STYLE);
+    if (!a_root)
+      goto error;
+    a_item = yaml_document_add_scalar(&alt_document, NULL, (yaml_char_t *)"a",
+                                      -1, YAML_PLAIN_SCALAR_STYLE);
+    if (!a_item)
+      goto error;
+    if (!yaml_document_append_sequence_item(&alt_document, a_root, a_item))
+      goto error;
+    if (!yaml_document_append_sequence_item(&alt_document, a_root, a_item))
+      goto error;
+    a_map = yaml_document_add_mapping(&alt_document, NULL,
+                                      YAML_FLOW_MAPPING_STYLE);
+    if (!a_map)
+      goto error;
+    a_val = yaml_document_add_scalar(&alt_document, NULL, (yaml_char_t *)"b",
+                                     -1, YAML_PLAIN_SCALAR_STYLE);
+    if (!a_val)
+      goto error;
+    if (!yaml_document_append_mapping_pair(&alt_document, a_map, a_item, a_val))
+      goto error;
+    if (!yaml_document_append_sequence_item(&alt_document, a_root, a_map))
+      goto error;
+    g_pick_enabled = true; // [gapfuzz-llm] 이후 output_document 구성에서는 태그 변경 다시 켬
+    dump_doc = &alt_document; // [gapfuzz-llm] 대체 문서를 dump 대상으로 선택
+    other_doc = &output_document; // [gapfuzz-llm] 나머지 문서도 마지막에 해제
+  }
 
   /* Create the root sequence. */
 
@@ -816,7 +952,8 @@
     yaml_event_delete(&input_event);
   }
 
-  if (!yaml_emitter_dump(&emitter, &output_document))
+  dumped = true; // [gapfuzz-llm] yaml_emitter_dump는 성공/실패와 무관하게 문서를 해제하므로 이후 직접 해제하지 않음
+  if (!yaml_emitter_dump(&emitter, dump_doc)) // [gapfuzz-llm] 입력으로 고른 문서를 dump
     goto error;
 
   yaml_emitter_close(&emitter);
@@ -826,7 +963,9 @@
   free(out.buf);
 
   yaml_event_delete(&input_event);
-  yaml_document_delete(&output_document);
+  if (!dumped) // [gapfuzz-llm] dump가 소유권을 가져간 문서는 이중 해제(double free)를 피하려고 직접 해제하지 않음
+    yaml_document_delete(dump_doc);
+  yaml_document_delete(other_doc); // [gapfuzz-llm] dump 대상이 아닌 문서는 직접 해제 (0 초기화되어 안전)
   yaml_parser_delete(&parser);
   yaml_emitter_delete(&emitter);
```
