# LLM 하네스 수정 — libucl/official_msgpack, 제안 1,3,10

- 모델: `claude-sonnet-5-5`
- 제안: `ucl_parser_add_chunk_full(struct ucl_parser *, const unsigned char *, size_t, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)`의 6번째 인자 `parse_type`를 하네스가 고정합니다(17행에서 항상 `UCL_PARSE_MSGPACK`) → 퍼저 입력으로 바꾸세요
- 제안: `ucl_object_unref(ucl_object_t *)`의 1번째 인자 `obj`에 하네스가 null을 넘긴 적이 없습니다(21행) → nullptr도 넘겨 보세요
- 제안: `ucl_parser_set_filevars(struct ucl_parser *, const char *, bool)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`ucl_parser_new`)에서만 불립니다. 내부 호출은 2번째 인자 `filename`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 겨냥한 분기: 9개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 7/9 | 1: 5/6, 3: 1/2, 10: 1/1 | LIBRARY(약) | 4065/1437 |
| 2 | 통과 | 9/9 | 1: 6/6, 3: 2/2, 10: 1/1 | - | 5725/3399 |

**채택 후보: 시도 2** (`harnesses/libucl/llm/official_msgpack_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -9,19 +9,57 @@
 		return 0;
 	}
 
+	/* 앞쪽 바이트 3개는 옵션용, 나머지는 원래대로 파서 입력으로 쓴다 */
+	uint8_t type_sel = data[0];   // [gapfuzz-llm] parse_type을 퍼저 입력으로 선택하기 위한 바이트
+	uint8_t fname_sel = data[1];  // [gapfuzz-llm] set_filevars의 filename/need_expand 선택용 바이트
+	uint8_t unref_sel = data[2];  // [gapfuzz-llm] ucl_object_unref/free에 null을 넘길지 선택용 바이트
+
 	struct ucl_parser *parser = ucl_parser_new(UCL_PARSER_KEY_LOWERCASE);
 	if (parser == NULL) {
 		return 0;
 	}
 
+	/* 원래 값(MSGPACK)도 계속 나오도록 여러 값 중 고름 */
+	enum ucl_parse_type parse_type;  // [gapfuzz-llm] 고정값 대신 입력으로 parse_type 선택
+	switch (type_sel % 6) {          // [gapfuzz-llm] AUTO/UCL/CBOR/CSEXP/MSGPACK 및 범위 밖 값 모두 도달
+	case 0: parse_type = UCL_PARSE_AUTO; break;
+	case 1: parse_type = UCL_PARSE_UCL; break;
+	case 2: parse_type = UCL_PARSE_CBOR; break;
+	case 3: parse_type = UCL_PARSE_CSEXP; break;
+	case 4: parse_type = (enum ucl_parse_type)(100 + (type_sel % 100)); break;  // [gapfuzz-llm] 정의되지 않은 enum 값으로 switch의 default 분기 도달
+	default: parse_type = UCL_PARSE_MSGPACK; break;
+	}
+
+	/* filename이 null/비null, need_expand 참/거짓 모두 시도 */
+	switch (fname_sel % 4) {  // [gapfuzz-llm] ucl_parser_set_filevars를 직접 호출해 filename 분기 탐색
+	case 0:
+		ucl_parser_set_filevars(parser, NULL, false);  // [gapfuzz-llm] filename == NULL 경로
+		break;
+	case 1:
+		ucl_parser_set_filevars(parser, "/tmp/test.conf", false);  // [gapfuzz-llm] filename != NULL, 확장 없음
+		break;
+	case 2:
+		ucl_parser_set_filevars(parser, ".", true);  // [gapfuzz-llm] filename != NULL, realpath 확장 경로
+		break;
+	default:
+		break;  // [gapfuzz-llm] 호출하지 않는 원래 동작도 유지
+	}
+
 	if (ucl_parser_add_chunk_full(parser, (const unsigned char *)data, size,
-			0, UCL_DUPLICATE_APPEND, UCL_PARSE_MSGPACK)) {
+			0, UCL_DUPLICATE_APPEND, parse_type)) {  // [gapfuzz-llm] 선택된 parse_type 전달
 		ucl_object_t *obj = ucl_parser_get_object(parser);
 		if (obj != NULL) {
 			ucl_object_unref(obj);
 		}
 	}
 
+	if (unref_sel % 4 == 0) {
+		ucl_object_unref(NULL);  // [gapfuzz-llm] unref의 obj == NULL 경로 (null 허용)
+	}
+	else if (unref_sel % 4 == 1) {
+		ucl_object_free(NULL);  // [gapfuzz-llm] 해제 내부 함수의 302행 obj == NULL 분기는 ucl_object_free로 직접 도달 (null이면 즉시 반환)
+	}
+
 	ucl_parser_free(parser);
 	return 0;
 }
```
