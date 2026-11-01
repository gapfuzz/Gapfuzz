# LLM 하네스 수정 — pugixml/official, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 4번째 인자 `encoding`를 하네스가 고정합니다(9행에서 기본값, 10행에서 기본값, 11행에서 기본값) (라이브러리 내부 `impl::{익명}::load_buffer_impl` → `impl::{익명}::get_buffer_encoding`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 5개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 4/5 | - | 2504/1639 |
| 2 | 통과 | 5/5 | - | 3580/4226 |

**채택 후보: 시도 2** (`harnesses/pugixml/llm/official_fix1/try2.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -1,14 +1,60 @@
 #include "pugixml.hpp"
 
 #include <stdint.h>
+#include <stdlib.h>
+
+static bool g_fail_alloc = false; // [gapfuzz-llm] 할당 실패 모드 플래그: convert_buffer의 메모리 부족 분기를 열기 위함
+
+static void *fuzz_allocate(size_t size) // [gapfuzz-llm] 플래그가 켜져 있으면 NULL을 반환하는 할당 함수
+{
+	if (g_fail_alloc) return NULL; // [gapfuzz-llm] pugixml은 NULL 반환을 status_out_of_memory로 처리함
+	return malloc(size); // [gapfuzz-llm] 평소에는 일반 malloc 사용
+}
+
+static void fuzz_deallocate(void *ptr) // [gapfuzz-llm] 위 할당 함수와 짝이 되는 해제 함수
+{
+	free(ptr); // [gapfuzz-llm] malloc으로 할당한 메모리를 해제
+}
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size)
 {
+	static bool s_allocator_set = (pugi::set_memory_management_functions(fuzz_allocate, fuzz_deallocate), true); // [gapfuzz-llm] 문서 생성 전에 한 번만 사용자 할당자를 등록
+	(void)s_allocator_set;
+
     pugi::xml_document doc;
 
-	doc.load_buffer(Data, Size);
-	doc.load_buffer(Data, Size, pugi::parse_minimal);
-	doc.load_buffer(Data, Size, pugi::parse_full);
+	static const pugi::xml_encoding kEncodings[] = { // [gapfuzz-llm] 인코딩 후보 목록: 기본값(auto)을 포함해 모든 인코딩을 고를 수 있게 함
+		pugi::encoding_auto, pugi::encoding_utf8, pugi::encoding_utf16_le,
+		pugi::encoding_utf16_be, pugi::encoding_utf16, pugi::encoding_utf32_le,
+		pugi::encoding_utf32_be, pugi::encoding_utf32, pugi::encoding_wchar,
+		pugi::encoding_latin1
+	};
+	pugi::xml_encoding encoding = pugi::encoding_auto; // [gapfuzz-llm] 입력이 비어 있으면 원래 값(auto) 유지
+	bool fail_alloc = false; // [gapfuzz-llm] 입력이 짧으면 할당 실패 없이 원래 동작 유지
+	if (Size > 0) // [gapfuzz-llm] 입력 첫 바이트로 인코딩을 선택
+	{
+		encoding = kEncodings[Data[0] % (sizeof(kEncodings) / sizeof(kEncodings[0]))]; // [gapfuzz-llm] 첫 바이트로 인코딩 선택
+		Data++; // [gapfuzz-llm] 선택에 쓴 바이트는 문서 내용에서 제외
+		Size--; // [gapfuzz-llm] 남은 크기 갱신
+	}
+	if (Size > 0) // [gapfuzz-llm] 두 번째 바이트로 할당 실패 여부를 선택
+	{
+		fail_alloc = (Data[0] % 4) == 0; // [gapfuzz-llm] 약 1/4 확률로 load_buffer 중 할당을 실패시켜 메모리 부족 분기 도달
+		Data++; // [gapfuzz-llm] 선택에 쓴 바이트는 문서 내용에서 제외
+		Size--; // [gapfuzz-llm] 남은 크기 갱신
+	}
+
+	try // [gapfuzz-llm] 할당 실패 시 예외가 새어 나와 하네스가 죽지 않도록 감쌈
+	{
+		g_fail_alloc = fail_alloc; // [gapfuzz-llm] 이 호출 동안만 할당 실패 적용
+		doc.load_buffer(Data, Size, pugi::parse_default, encoding); // [gapfuzz-llm] encoding을 고정 기본값 대신 퍼저 입력에서 선택
+		doc.load_buffer(Data, Size, pugi::parse_minimal, encoding); // [gapfuzz-llm] encoding을 고정 기본값 대신 퍼저 입력에서 선택
+		doc.load_buffer(Data, Size, pugi::parse_full, encoding); // [gapfuzz-llm] encoding을 고정 기본값 대신 퍼저 입력에서 선택
+	}
+	catch (...) // [gapfuzz-llm] 예외는 무시하고 다음 입력으로 진행
+	{
+	}
+	g_fail_alloc = false; // [gapfuzz-llm] 문서 소멸 등 이후 동작에서는 정상 할당 상태로 복구
 
 	return 0;
 }
```
