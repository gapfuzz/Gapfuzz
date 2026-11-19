# 호출 안 함 API 추가 — http-parser/_union

- 모델: `claude-sonnet-5-5`
- 수정 전: 공개 API 14개 중 호출 안 함 10개, 라인 66.58% · 분기 61.33%
- 추가를 요청한 API 10개: `http_status_str`, `http_parser_pause`, `http_should_keep_alive`, `http_method_str`, `http_parser_version`, `http_errno_name`, `http_errno_description`, `http_parser_settings_init`, `http_parser_set_max_header_size`, `http_body_is_final`

| 시도 | 결과 | 실행된 API | 호출 안 함 | 라인 | 분기 | 사라진 API | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | 통과 | 9/10 | 3 | 48.5% | 48.5% | 0 | - | 2961/5314 |
| 2 | 통과 | 10/10 | 2 | 39.78% | 41.71% | 0 | - | 6330/4406 |

수정 전 수치는 진단 때(기본 120초 × 1회), 시도별 수치는 검사 퍼징(짧음)의 중앙값이라 길이가 다릅니다. 정식 비교는 같은 조건의 긴 실험으로 하세요.

**채택: 시도 2** → `harnesses/http-parser/gapfuzz_ops.c`. 사람이 읽고 쓰세요.

```diff
--- 수정 전
+++ 시도 2
@@ -0,0 +1,183 @@
+// http-parser 미호출 API 하네스: 문자열 변환 함수, 버전, 파서 일시정지, keep-alive 판정, 헤더 크기 상한 등
+#include <stdint.h>
+#include <stdlib.h>
+#include <string.h>
+#include "http_parser.h"
+
+#define MAX_INPUT  65536
+#define MAX_ITERS  64
+
+typedef struct {
+  unsigned pause_mask;  // 어떤 콜백에서 일시정지할지 고르는 비트마스크
+  unsigned pause_count; // 콜백 안 일시정지 횟수 상한용
+} ctx_t;
+
+// 콜백 안에서 입력으로 정해진 조건에 따라 파서를 멈춘다
+static void maybe_pause(http_parser *p, unsigned bit) {
+  ctx_t *c = (ctx_t *)p->data;
+  if (c && (c->pause_mask & bit) && c->pause_count < MAX_ITERS) {
+    c->pause_count++;
+    http_parser_pause(p, 1);
+  }
+}
+
+static int cb_begin(http_parser *p) { maybe_pause(p, 1); return 0; }
+static int cb_headers_done(http_parser *p) { maybe_pause(p, 2); return 0; }
+static int cb_msg_done(http_parser *p) { maybe_pause(p, 4); return 0; }
+static int cb_body(http_parser *p, const char *at, size_t len) {
+  (void)at; (void)len;
+  maybe_pause(p, 8);
+  return 0;
+}
+
+// 반환된 문자열이 유효한지 읽어서 확인
+static size_t touch(const char *s) {
+  return s ? strlen(s) : 0;
+}
+
+int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
+{
+  // 헤더: 타입, 청크 분할 선택, 일시정지 마스크/연산 개수, 임의값 2개(각 2바이트)
+  if (size < 8) return 0;
+  if (size > MAX_INPUT) size = MAX_INPUT;
+
+  static const enum http_parser_type types[3] = {HTTP_REQUEST, HTTP_RESPONSE, HTTP_BOTH};
+  enum http_parser_type type = types[data[0] % 3];
+  unsigned chunk_sel = data[1];
+  unsigned pause_mask = data[2] & 0x0F;
+  size_t nops = 1 + (data[2] >> 4) % 8;
+  unsigned v1 = (unsigned)data[3] | ((unsigned)data[4] << 8);
+  unsigned v2 = (unsigned)data[5] | ((unsigned)data[6] << 8);
+  size_t off = 7;
+
+  if (size < off + nops) return 0;
+  const uint8_t *ops = data + off;
+  off += nops;
+  const char *body = (const char *)data + off;
+  size_t blen = size - off;
+
+  // 반복이 64회를 넘지 않도록 청크 크기의 하한을 정한다
+  size_t chunk = 1 + (size_t)chunk_sel;
+  size_t min_chunk = blen / (MAX_ITERS - 4) + 1;
+  if (chunk < min_chunk) chunk = min_chunk;
+
+  volatile size_t sink = 0;
+
+  // [gapfuzz-ops] http_parser_version
+  unsigned long ver = http_parser_version();
+  sink += (ver >> 16) & 255;
+
+  // [gapfuzz-ops] http_parser_settings_init
+  http_parser_settings settings;
+  http_parser_settings_init(&settings);
+  settings.on_message_begin = cb_begin;
+  settings.on_headers_complete = cb_headers_done;
+  settings.on_message_complete = cb_msg_done;
+  settings.on_body = cb_body;
+
+  // [gapfuzz-ops] http_parser_set_max_header_size
+  // 헤더 크기 상한을 입력값으로 바꿔서 파싱한다. 이 값은 라이브러리 전역 변수이므로
+  // 함수 끝에서 반드시 기본값으로 되돌린다. 이 구간에는 early return이 없다.
+  http_parser_set_max_header_size((uint32_t)v2 % (MAX_INPUT + 1));
+
+  ctx_t ctx = {pause_mask, 0};
+  http_parser parser;
+  http_parser_init(&parser, type);
+  parser.data = &ctx;
+
+  size_t pos = 0;
+  for (unsigned i = 0; i < MAX_ITERS; i++) {
+    uint8_t op = ops[i % nops];
+
+    switch (op & 7) {
+    case 0: {
+      // [gapfuzz-ops] http_should_keep_alive
+      sink += (size_t)http_should_keep_alive(&parser);
+      break;
+    }
+    case 1: {
+      // [gapfuzz-ops] http_body_is_final
+      sink += (size_t)http_body_is_final(&parser);
+      break;
+    }
+    case 2: {
+      // [gapfuzz-ops] http_parser_pause
+      // 오류 상태에서 부르면 assert가 걸리므로 OK/PAUSED일 때만 부른다
+      enum http_errno e = HTTP_PARSER_ERRNO(&parser);
+      if (e == HPE_OK || e == HPE_PAUSED) {
+        http_parser_pause(&parser, (op >> 3) & 1);
+      }
+      break;
+    }
+    case 3: {
+      // [gapfuzz-ops] http_method_str
+      sink += touch(http_method_str((enum http_method)((v1 + i + op) & 0xFF)));
+      break;
+    }
+    case 4: {
+      // [gapfuzz-ops] http_status_str
+      sink += touch(http_status_str((enum http_status)((v2 + i * 7 + op) & 0x3FF)));
+      break;
+    }
+    case 5: {
+      // [gapfuzz-ops] http_errno_name
+      // 범위를 벗어나면 assert가 걸리므로 유효한 범위로 제한한다
+      enum http_errno e = (enum http_errno)((v1 + i + op) % (HPE_UNKNOWN + 1));
+      sink += touch(http_errno_name(e));
+      break;
+    }
+    case 6: {
+      // [gapfuzz-ops] http_errno_description
+      enum http_errno e = (enum http_errno)((v2 + i + op) % (HPE_UNKNOWN + 1));
+      sink += touch(http_errno_description(e));
+      break;
+    }
+    default: {
+      // [gapfuzz-ops] http_parser_set_max_header_size
+      // 실행 도중에도 상한을 바꿔 본다 (끝에서 기본값으로 복원됨)
+      http_parser_set_max_header_size((uint32_t)((v1 * 31u + i * 977u + op) % (MAX_INPUT + 1)));
+      break;
+    }
+    }
+
+    // 파서 진행: 일시정지 상태면 풀고, 다른 오류면 중단한다
+    if (pos < blen) {
+      enum http_errno e = HTTP_PARSER_ERRNO(&parser);
+      if (e == HPE_PAUSED) {
+        // [gapfuzz-ops] http_parser_pause
+        http_parser_pause(&parser, 0);
+        e = HTTP_PARSER_ERRNO(&parser);
+      }
+      if (e != HPE_OK) break;
+      size_t n = blen - pos;
+      if (n > chunk) n = chunk;
+      size_t used = http_parser_execute(&parser, &settings, body + pos, n);
+      pos += used;
+    } else if (i >= nops) {
+      break;
+    }
+  }
+
+  // 마지막 상태에 대한 조회
+  enum http_errno last = HTTP_PARSER_ERRNO(&parser);
+  // [gapfuzz-ops] http_errno_name
+  sink += touch(http_errno_name(last));
+  // [gapfuzz-ops] http_errno_description
+  sink += touch(http_errno_description(last));
+  // [gapfuzz-ops] http_should_keep_alive
+  sink += (size_t)http_should_keep_alive(&parser);
+  // [gapfuzz-ops] http_body_is_final
+  sink += (size_t)http_body_is_final(&parser);
+
+  // 입력이 끝났음을 파서에 알린다 (EOF)
+  if (HTTP_PARSER_ERRNO(&parser) == HPE_OK) {
+    http_parser_execute(&parser, &settings, body, 0);
+  }
+
+  // [gapfuzz-ops] http_parser_set_max_header_size
+  // 전역 상한을 컴파일 시점 기본값으로 복원해 다음 실행에 영향을 남기지 않는다
+  http_parser_set_max_header_size((uint32_t)HTTP_MAX_HEADER_SIZE);
+
+  (void)sink;
+  return 0;
+}
```
