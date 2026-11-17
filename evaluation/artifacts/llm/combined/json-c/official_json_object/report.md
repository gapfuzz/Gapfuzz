# LLM 하네스 수정 — json-c/official_json_object, 제안 1,2,3,4

- 모델: `claude-sonnet-5-5`
- 제안: `json_c_visit(json_object *, int, json_c_visit_userfunc *, void *)`의 4번째 인자 `userarg`를 하네스가 고정합니다(28행에서 항상 `NULL`) → 퍼저 입력으로 바꾸세요
- 제안: `json_object_deep_copy(struct json_object *, struct json_object **, json_c_shallow_copy_fn *)`의 2번째 인자 `dst`를 하네스가 고정합니다(40행에서 항상 같은 객체 `&dst`) (라이브러리 내부 `json_object_deep_copy_recursive` → `json_object_object_add` → `json_object_object_add_ex`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `json_object_deep_copy(struct json_object *, struct json_object **, json_c_shallow_copy_fn *)`의 3번째 인자 `shallow_copy`에 하네스가 null을 넘긴 적이 없습니다(40행) → nullptr도 넘겨 보세요
- 제안: `json_tokener_parse_ex(struct json_tokener *, const char *, int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_parse_verbose`)에서만 불립니다. 내부 호출은 1번째 인자 `tok`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 겨냥한 분기: 81개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 44/81 | 1: 11/25, 2: 2/3, 3: 1/1, 4: 30/52 | - | 7500/3744 |
| 2 | 통과 | 60/81 | 1: 25/25, 2: 2/3, 3: 1/1, 4: 32/52 | - | 12231/5539 |
| 3 | 통과 | 60/81 | 1: 25/25, 2: 2/3, 3: 1/1, 4: 32/52 | - | 17026/5793 |

**채택 후보: 시도 2** (`harnesses/json-c/llm/official_json_object_combined/try2.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -1,13 +1,26 @@
-// OSS-Fuzz 하네스: json-c 저장소 fuzz/json_object_fuzzer.cc (커밋 d9b375f) 그대로.
+// OSS-Fuzz 하네스: json-c 저장소 fuzz/json_object_fuzzer.cc (커밋 d9b375f) 기반.
 #include <fuzzer/FuzzedDataProvider.h>
 
 #include "json.h"
 #include "json_visit.h"
 
+struct VisitCtx {  // [gapfuzz-llm] 루트/자식/컨테이너 종료 호출별로 반환값을 따로 정하는 userarg
+	int root_ret;
+	int child_ret;
+	int second_ret;
+};
+
 // Function to test json_c_visit
 static int emit_object(json_object *jso, int flags, json_object *parent_jso, const char *jso_key,
                        size_t *jso_index, void *userarg) {
-	return JSON_C_VISIT_RETURN_CONTINUE;
+	if (userarg == NULL)  // [gapfuzz-llm] userarg가 NULL인 원래 경로도 유지
+		return JSON_C_VISIT_RETURN_CONTINUE;
+	VisitCtx *ctx = (VisitCtx *)userarg;  // [gapfuzz-llm] 퍼저가 고른 반환값 사용
+	if (flags & JSON_C_VISIT_SECOND)
+		return ctx->second_ret;  // [gapfuzz-llm] 컨테이너 종료 시점 호출의 반환 분기(switch) 탐색
+	if (parent_jso == NULL)
+		return ctx->root_ret;  // [gapfuzz-llm] 루트는 CONTINUE로 두어야 자식 순회 분기에 도달 가능
+	return ctx->child_ret;  // [gapfuzz-llm] 자식 노드에서 SKIP/POP/STOP/ERROR/무효 값 반환
 }
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
@@ -25,7 +38,15 @@
 	json_object_get_array(jso);
 	json_object_get_type(jso);
 
-	json_c_visit(jso, 0, emit_object, NULL);
+	const int visit_rets[] = {JSON_C_VISIT_RETURN_CONTINUE, JSON_C_VISIT_RETURN_SKIP,
+	                          JSON_C_VISIT_RETURN_POP,      JSON_C_VISIT_RETURN_STOP,
+	                          JSON_C_VISIT_RETURN_ERROR,    12345};  // [gapfuzz-llm] 유효/무효 반환 코드 후보 목록
+	VisitCtx vctx;  // [gapfuzz-llm] 호출 종류별 반환값을 퍼저 입력으로 선택
+	vctx.root_ret = visit_rets[fdp.ConsumeIntegralInRange<int>(0, 5)];  // [gapfuzz-llm] 루트 반환값
+	vctx.child_ret = visit_rets[fdp.ConsumeIntegralInRange<int>(0, 5)];  // [gapfuzz-llm] 자식 반환값
+	vctx.second_ret = visit_rets[fdp.ConsumeIntegralInRange<int>(0, 5)];  // [gapfuzz-llm] 종료 호출 반환값
+	void *visit_arg = fdp.ConsumeBool() ? (void *)&vctx : NULL;  // [gapfuzz-llm] 고정 NULL 대신 퍼저가 고른 userarg (NULL도 가능)
+	json_c_visit(jso, 0, emit_object, visit_arg);  // [gapfuzz-llm] 퍼저가 고른 userarg 전달
 
 	json_object_set_int(jso, fdp.ConsumeIntegral<int>());
 	json_object_set_int64(jso, fdp.ConsumeIntegral<int64_t>());
@@ -37,8 +58,52 @@
 	json_object_set_string_len(jso, str.c_str(), str.size());
 
 	json_object *dst = NULL;
-	json_object_deep_copy(jso, &dst, json_c_shallow_copy_default);
+	json_object *pre = NULL;
+	json_object **dst_arg = &dst;
+	int dst_mode = fdp.ConsumeIntegralInRange<int>(0, 2);  // [gapfuzz-llm] dst 인자 종류를 퍼저 입력으로 선택
+	if (dst_mode == 1) {
+		dst_arg = NULL;  // [gapfuzz-llm] dst 포인터 자체가 null인 경우 (!dst 분기)
+	} else if (dst_mode == 2) {
+		pre = json_object_new_string("x");
+		dst_arg = &pre;  // [gapfuzz-llm] *dst가 이미 non-null인 경우 (*dst 분기)
+	}
+	json_c_shallow_copy_fn *shallow = fdp.ConsumeBool() ? json_c_shallow_copy_default : nullptr;  // [gapfuzz-llm] shallow_copy에 nullptr도 전달
+	json_object_deep_copy(jso, dst_arg, shallow);  // [gapfuzz-llm] 퍼저가 고른 dst, shallow_copy 사용
 	json_object_put(dst);
+	if (dst_mode == 2)
+		json_object_put(pre);  // [gapfuzz-llm] 사전 할당한 객체 해제
+
+	// [gapfuzz-llm] json_tokener_parse_ex를 직접 호출: tok 플래그/깊이/입력 분할을 다양하게 시도
+	{
+		int depth = fdp.ConsumeBool() ? JSON_TOKENER_DEFAULT_DEPTH
+		                              : fdp.ConsumeIntegralInRange<int>(1, 4);  // [gapfuzz-llm] 얕은 깊이로 depth 관련 분기 탐색 (1 이상만 사용)
+		struct json_tokener *tok = json_tokener_new_ex(depth);  // [gapfuzz-llm] null tok은 문서상 금지이므로 유효한 tok만 사용
+		if (tok != NULL) {
+			int flag_sel = fdp.ConsumeIntegralInRange<int>(0, 3);  // [gapfuzz-llm] 플래그 조합 선택
+			int flags = 0;
+			if (flag_sel & 1)
+				flags |= JSON_TOKENER_STRICT;  // [gapfuzz-llm] STRICT 켠 상태
+			if (flag_sel & 2)
+				flags |= JSON_TOKENER_VALIDATE_UTF8;  // [gapfuzz-llm] UTF-8 검증 켠 상태
+			json_tokener_set_flags(tok, flags);  // [gapfuzz-llm] 선택한 플래그 적용
+
+			std::string tstr = fdp.ConsumeRandomLengthString(80);  // [gapfuzz-llm] 파서 직접 입력(숫자/이스케이프 등 도달용으로 길이 확대)
+			int total = (int)tstr.size();
+			int cut = total;
+			if (total > 0 && fdp.ConsumeBool())
+				cut = fdp.ConsumeIntegralInRange<int>(0, total);  // [gapfuzz-llm] 입력을 두 조각으로 나눠 입력 소진/재개 분기 탐색
+			int first_len = cut;
+			if (fdp.ConsumeBool())
+				first_len = cut + (cut < total ? 0 : 1);  // [gapfuzz-llm] 끝에 NUL 문자를 포함해 넘기는 경우 (c_str은 NUL 종료라 안전)
+			json_object *parsed = json_tokener_parse_ex(tok, tstr.c_str(), first_len);  // [gapfuzz-llm] 첫 조각 직접 호출
+			json_object_put(parsed);  // [gapfuzz-llm] 결과 해제
+			if (parsed == NULL && json_tokener_get_error(tok) == json_tokener_continue && cut < total) {
+				json_object *parsed2 = json_tokener_parse_ex(tok, tstr.c_str() + cut, total - cut);  // [gapfuzz-llm] 같은 tok으로 나머지 조각 이어서 파싱
+				json_object_put(parsed2);  // [gapfuzz-llm] 결과 해제
+			}
+			json_tokener_free(tok);  // [gapfuzz-llm] tok 해제
+		}
+	}
 
 	json_object_put(jso);
 	return 0;
```
