# LLM 하네스 수정 — http-parser/official, 제안 1,2

- 모델: `claude-sonnet-5-5`
- 제안: `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)`의 1번째 인자 `parser`를 하네스가 고정합니다(24행에서 항상 같은 객체 `&parser`) → 퍼저 입력으로 바꾸세요
- 제안: `http_parser_init(http_parser *, enum http_parser_type)`의 2번째 인자 `type`를 하네스가 고정합니다(23행에서 항상 `HTTP_BOTH`) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 59개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 20/59 | 1: 18/57, 2: 2/2 | - | 3423/1043 |
| 2 | 통과 | 44/59 | 1: 42/57, 2: 2/2 | - | 6818/2578 |
| 3 | 통과 | 26/59 | 1: 24/57, 2: 2/2 | - | 9106/3881 |

**채택 후보: 시도 2** (`harnesses/http-parser/llm/official_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -19,9 +19,35 @@
     ,.on_chunk_complete = 0
   };
 
+  // 앞 4바이트를 하네스 설정용으로 소비(서로 겹치지 않게 순서대로 배분)하고 나머지를 파서 입력으로 사용
+  uint8_t type_sel = 0, split_a = 0, split_b = 0, opt_sel = 0;
+  if (size >= 4) {
+    type_sel = data[0];
+    split_a = data[1];
+    split_b = data[2];
+    opt_sel = data[3];
+    data += 4;
+    size -= 4;
+  }
+
   http_parser parser;
-  http_parser_init(&parser, HTTP_BOTH);
-  http_parser_execute(&parser, &settings_null, (char*)data, size);
+  enum http_parser_type type = (enum http_parser_type)(type_sel % 3); // HTTP_REQUEST/RESPONSE/HTTP_BOTH 모두 나오도록 입력에서 선택
+  http_parser_init(&parser, type);
+  parser.lenient_http_headers = (opt_sel >> 1) & 1; // init이 0으로 초기화하므로 이후 입력으로 lenient 모드 선택(!lenient 분기 도달)
+
+  if ((opt_sel & 1) == 0 && split_a % 4 == 0) { // 일부 입력은 원래처럼 한 번에 실행
+    http_parser_execute(&parser, &settings_null, (char*)data, size);
+  } else {
+    // 입력을 세 조각으로 나눠 이어서 실행: 헤더/청크/본문 중간 상태에서 다음 호출이 시작되게 함
+    size_t p1 = ((size_t)split_a * size) / 256;
+    size_t p2 = p1 + ((size_t)split_b * (size - p1)) / 256;
+    http_parser_execute(&parser, &settings_null, (char*)data, p1); // 파서 상태를 다양하게 만들기 위해 앞부분만 먼저 실행
+    http_parser_execute(&parser, &settings_null, (char*)data + p1, p2 - p1); // 중간 조각을 이어서 실행
+    http_parser_execute(&parser, &settings_null, (char*)data + p2, size - p2); // 나머지 조각 실행
+    if (opt_sel & 4) {
+      http_parser_execute(&parser, &settings_null, (char*)data + size, 0); // 길이 0 호출로 EOF 상태 분기(body_identity_eof, dead 등) 도달
+    }
+  }
 
   return 0;
 }
```
