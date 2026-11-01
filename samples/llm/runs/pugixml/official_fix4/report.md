# LLM 하네스 수정 — pugixml/official, 제안 4

- 모델: `claude-sonnet-5-5`
- 제안: `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 1번째 인자 `contents`에 하네스가 null을 넘긴 적이 없습니다(9행, 10행, 11행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/2 | - | 1467/1528 |
| 2 | 통과 | 1/2 | - | 2295/2995 |

**채택 후보: 시도 1** (`harnesses/pugixml/llm/official_fix4/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -6,9 +6,14 @@
 {
     pugi::xml_document doc;
 
-	doc.load_buffer(Data, Size);
-	doc.load_buffer(Data, Size, pugi::parse_minimal);
-	doc.load_buffer(Data, Size, pugi::parse_full);
+	bool use_null = Size > 0 && (Data[0] & 1); // [gapfuzz-llm] 입력 첫 바이트로 contents에 nullptr을 넘길지 고르기 위함
+	bool zero_len = Size > 0 && (Data[0] & 2); // [gapfuzz-llm] nullptr일 때 길이 0 경로(2138행 거짓)와 길이>0 경로(4844행 참)를 모두 타기 위함
+	const void *contents = use_null ? nullptr : static_cast<const void *>(Data); // [gapfuzz-llm] 원래 Data도 계속 전달하면서 nullptr도 입력에 따라 전달
+	size_t length = (use_null && zero_len) ? 0 : Size; // [gapfuzz-llm] 원래 Size도 계속 나오게 두고 nullptr+0 조합도 생성
+
+	doc.load_buffer(contents, length); // [gapfuzz-llm] contents가 nullptr일 수 있도록 변경
+	doc.load_buffer(contents, length, pugi::parse_minimal); // [gapfuzz-llm] contents가 nullptr일 수 있도록 변경
+	doc.load_buffer(contents, length, pugi::parse_full); // [gapfuzz-llm] contents가 nullptr일 수 있도록 변경
 
 	return 0;
 }
```
