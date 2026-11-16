# LLM 하네스 수정 — http-parser/official, 제안 1,2

- 모델: `claude-sonnet-5-5`
- 제안: `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)`의 1번째 인자 `parser`를 하네스가 고정합니다(24행에서 항상 같은 객체 `&parser`) → 퍼저 입력으로 바꾸세요
- 제안: `http_parser_init(http_parser *, enum http_parser_type)`의 2번째 인자 `type`를 하네스가 고정합니다(23행에서 항상 `HTTP_BOTH`) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 59개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 컴파일 실패 | -/- | - | - | 3423/1011 |
| 2 | 통과 | 33/59 | 1: 31/57, 2: 2/2 | ASSERT(강), ASSERT(강) | 4551/2422 |
| 3 | 통과 | 29/59 | 1: 27/57, 2: 2/2 | ASSERT(강), ASSERT(강) | 7019/3131 |

**채택 후보: 시도 2** (`harnesses/http-parser/llm/official_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -19,8 +19,26 @@
     ,.on_chunk_complete = 0
   };
 
+  // 앞쪽 2바이트를 제어용으로 사용: [0]=파서 타입, [1]=파서 상태 선택
+  uint8_t type_sel = 0;
+  uint8_t state_sel = 0;
+  if (size >= 2) {
+    type_sel = data[0];
+    state_sel = data[1];
+    data += 2;
+    size -= 2;
+  }
+
   http_parser parser;
-  http_parser_init(&parser, HTTP_BOTH);
+  enum http_parser_type type = (enum http_parser_type)(type_sel % 3); // 요청/응답/둘 다를 모두 시도하도록 입력에서 타입 선택 (HTTP_BOTH 포함)
+  http_parser_init(&parser, type);
+
+  // 0~3은 init 상태 그대로 두어 원래 동작도 계속 나오게 함
+  if (state_sel >= 4) {
+    // s_message_done은 http_parser.c 내부 enum이라 헤더에서 보이지 않으므로 상한을 직접 지정 (상한 초과 값은 라이브러리의 default 분기가 에러로 처리)
+    parser.state = (unsigned int)(1 + (state_sel % 66)); // 파서 객체 상태를 퍼저 입력으로 변경
+  }
+
   http_parser_execute(&parser, &settings_null, (char*)data, size);
 
   return 0;
```
