# LLM 하네스 수정 — pugixml/official, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 3번째 인자 `options`를 하네스가 `기본값`, `parse_minimal`, `parse_full` 중에서만 고릅니다(9행, 10행, 11행) (라이브러리 내부 `impl::{익명}::load_buffer_impl` → `impl::{익명}::xml_parser::parse` → `impl::{익명}::xml_parser::parse_tree` → `impl::{익명}::get_strconv_pcdata`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 26개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 23/26 | - | 4161/1476 |
| 2 | 통과 | 24/26 | - | 5026/2152 |
| 3 | 통과 | 24/26 | - | 6010/1450 |

**채택 후보: 시도 2** (`harnesses/pugixml/llm/official_fix3/try2.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -6,8 +6,13 @@
 {
     pugi::xml_document doc;
 
+	// 입력 앞 2바이트로 options 비트 조합을 만들고, 첫 바이트의 최하위 비트가 0이면 원래 값(parse_minimal)을 쓴다
+	unsigned int fuzz_options = pugi::parse_minimal; // [gapfuzz-llm] options를 퍼저 입력에서 고르기 위한 변수, 기본은 원래 값
+	if (Size >= 2 && (Data[0] & 1)) fuzz_options = ((unsigned int)Data[0] << 8) | Data[1]; // [gapfuzz-llm] 입력 앞 2바이트로 임의의 options 비트 조합(escapes, eol, wconv, wnorm, fragment 등)을 만듦
+
 	doc.load_buffer(Data, Size);
-	doc.load_buffer(Data, Size, pugi::parse_minimal);
+	doc.load_buffer(Data, Size, fuzz_options); // [gapfuzz-llm] parse_minimal만 쓰면 pcdata/attribute 변환 분기가 막히므로 입력에서 고른 options 사용
+	doc.load_buffer(Data, 0, fuzz_options); // [gapfuzz-llm] 길이 0 버퍼에서 parse_fragment 옵션을 확인하는 분기는 빈 입력과 options가 함께 있어야 열리므로 추가
 	doc.load_buffer(Data, Size, pugi::parse_full);
 
 	return 0;
```
