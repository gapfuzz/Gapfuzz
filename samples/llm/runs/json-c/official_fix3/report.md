# LLM 하네스 수정 — json-c/official, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `json_tokener_new_ex(int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`json_tokener_new`)에서만 불립니다. 내부 호출은 1번째 인자 `depth`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1334/1591 |

**채택 후보: 시도 1** (`harnesses/json-c/llm/official_fix3/try1.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -4,8 +4,16 @@
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
 {
+	int depth = JSON_TOKENER_DEFAULT_DEPTH; // [gapfuzz-llm] 입력이 비어 있으면 기존 기본 depth(32)를 그대로 사용
+	if (size >= 1) {
+		depth = static_cast<int>(data[0] % 70) - 5; // [gapfuzz-llm] 첫 바이트로 depth를 -5~64에서 고르게 선택(기본값 32와 depth < 1 모두 가능)
+		data += 1; // [gapfuzz-llm] depth 선택에 쓴 첫 바이트는 JSON 입력에서 제외
+		size -= 1; // [gapfuzz-llm] 소비한 바이트만큼 길이 감소
+	}
 	const char *data1 = reinterpret_cast<const char *>(data);
-	json_tokener *tok = json_tokener_new();
+	json_tokener *tok = json_tokener_new_ex(depth); // [gapfuzz-llm] depth < 1 분기를 타도록 json_tokener_new_ex를 직접 호출
+	if (tok == NULL) // [gapfuzz-llm] depth < 1이면 NULL이 반환되며 parse_ex에 NULL을 넘기면 안 되므로 종료
+		return 0;
 	json_object *obj = json_tokener_parse_ex(tok, data1, size);
 	
 	if (json_object_is_type(obj, json_type_object)) {
```
