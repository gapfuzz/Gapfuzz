라이브러리: pugixml
하네스 파일: official.cpp

아래 제안 3개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 4번째 인자 `encoding`를 하네스가 고정합니다(9행에서 기본값, 10행에서 기본값, 11행에서 기본값) (라이브러리 내부 `impl::{익명}::load_buffer_impl` → `impl::{익명}::get_buffer_encoding`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (5개)
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2106행, 조건 `encoding == encoding_wchar`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2102  
 2103  	PUGI_IMPL_FN xml_encoding get_buffer_encoding(xml_encoding encoding, const void* contents, size_t size)
 2104  	{
 2105  		// replace wchar encoding with utf implementation
 2106> 		if (encoding == encoding_wchar) return get_wchar_encoding();
 2107  
 2108  		// replace utf16 encoding with utf16 with specific endianness
 2109  		if (encoding == encoding_utf16) return is_little_endian() ? encoding_utf16_le : encoding_utf16_be;
 2110  
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2109행, 조건 `encoding == encoding_utf16`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2105  		// replace wchar encoding with utf implementation
 2106  		if (encoding == encoding_wchar) return get_wchar_encoding();
 2107  
 2108  		// replace utf16 encoding with utf16 with specific endianness
 2109> 		if (encoding == encoding_utf16) return is_little_endian() ? encoding_utf16_le : encoding_utf16_be;
 2110  
 2111  		// replace utf32 encoding with utf32 with specific endianness
 2112  		if (encoding == encoding_utf32) return is_little_endian() ? encoding_utf32_le : encoding_utf32_be;
 2113  
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2112행, 조건 `encoding == encoding_utf32`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2108  		// replace utf16 encoding with utf16 with specific endianness
 2109  		if (encoding == encoding_utf16) return is_little_endian() ? encoding_utf16_le : encoding_utf16_be;
 2110  
 2111  		// replace utf32 encoding with utf32 with specific endianness
 2112> 		if (encoding == encoding_utf32) return is_little_endian() ? encoding_utf32_le : encoding_utf32_be;
 2113  
 2114  		// only do autodetection if no explicit encoding is requested
 2115  		if (encoding != encoding_auto) return encoding;
 2116  
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2115행, 조건 `encoding != encoding_auto`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2111  		// replace utf32 encoding with utf32 with specific endianness
 2112  		if (encoding == encoding_utf32) return is_little_endian() ? encoding_utf32_le : encoding_utf32_be;
 2113  
 2114  		// only do autodetection if no explicit encoding is requested
 2115> 		if (encoding != encoding_auto) return encoding;
 2116  
 2117  		// try to guess encoding (based on XML specification, Appendix F.1)
 2118  		const uint8_t* data = static_cast<const uint8_t*>(contents);
 2119  
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 4864행, 조건 `!impl::convert_buffer(buffer, length, buffer_encoding, contents, size, is_mutable)`가 퍼징 중 한 번도 '참'이 되지 않음
```
 4860  		// get private buffer
 4861  		char_t* buffer = NULL;
 4862  		size_t length = 0;
 4863  
 4864> 		if (!impl::convert_buffer(buffer, length, buffer_encoding, contents, size, is_mutable)) return impl::make_parse_result(status_out_of_memory);
 4865  
 4866  		// after this we either deallocate contents (below) or hold on to it via doc->buffer, so we don't need to guard it
 4867  		contents_guard.release();
 4868  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 제안 3
`xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 3번째 인자 `options`를 하네스가 `기본값`, `parse_minimal`, `parse_full` 중에서만 고릅니다(9행, 10행, 11행) (라이브러리 내부 `impl::{익명}::load_buffer_impl` → `impl::{익명}::xml_parser::parse` → `impl::{익명}::xml_parser::parse_tree` → `impl::{익명}::get_strconv_pcdata`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (26개)
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2800행, 조건 `case 1`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2796  
 2797  		switch (((optmask >> 4) & 3) | ((optmask >> 9) & 4)) // get bitmask for flags (trim eol escapes); this simultaneously checks 3 options from assertion above
 2798  		{
 2799  		case 0: return strconv_pcdata_impl<opt_false, opt_false, opt_false>::parse;
 2800> 		case 1: return strconv_pcdata_impl<opt_false, opt_false, opt_true>::parse;
 2801  		case 2: return strconv_pcdata_impl<opt_false, opt_true, opt_false>::parse;
 2802  		case 3: return strconv_pcdata_impl<opt_false, opt_true, opt_true>::parse;
 2803  		case 4: return strconv_pcdata_impl<opt_true, opt_false, opt_false>::parse;
 2804  		case 5: return strconv_pcdata_impl<opt_true, opt_false, opt_true>::parse;
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2801행, 조건 `case 2`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2797  		switch (((optmask >> 4) & 3) | ((optmask >> 9) & 4)) // get bitmask for flags (trim eol escapes); this simultaneously checks 3 options from assertion above
 2798  		{
 2799  		case 0: return strconv_pcdata_impl<opt_false, opt_false, opt_false>::parse;
 2800  		case 1: return strconv_pcdata_impl<opt_false, opt_false, opt_true>::parse;
 2801> 		case 2: return strconv_pcdata_impl<opt_false, opt_true, opt_false>::parse;
 2802  		case 3: return strconv_pcdata_impl<opt_false, opt_true, opt_true>::parse;
 2803  		case 4: return strconv_pcdata_impl<opt_true, opt_false, opt_false>::parse;
 2804  		case 5: return strconv_pcdata_impl<opt_true, opt_false, opt_true>::parse;
 2805  		case 6: return strconv_pcdata_impl<opt_true, opt_true, opt_false>::parse;
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2803행, 조건 `case 4`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2799  		case 0: return strconv_pcdata_impl<opt_false, opt_false, opt_false>::parse;
 2800  		case 1: return strconv_pcdata_impl<opt_false, opt_false, opt_true>::parse;
 2801  		case 2: return strconv_pcdata_impl<opt_false, opt_true, opt_false>::parse;
 2802  		case 3: return strconv_pcdata_impl<opt_false, opt_true, opt_true>::parse;
 2803> 		case 4: return strconv_pcdata_impl<opt_true, opt_false, opt_false>::parse;
 2804  		case 5: return strconv_pcdata_impl<opt_true, opt_false, opt_true>::parse;
 2805  		case 6: return strconv_pcdata_impl<opt_true, opt_true, opt_false>::parse;
 2806  		case 7: return strconv_pcdata_impl<opt_true, opt_true, opt_true>::parse;
 2807  		default: assert(false); return NULL; // unreachable
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2804행, 조건 `case 5`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2800  		case 1: return strconv_pcdata_impl<opt_false, opt_false, opt_true>::parse;
 2801  		case 2: return strconv_pcdata_impl<opt_false, opt_true, opt_false>::parse;
 2802  		case 3: return strconv_pcdata_impl<opt_false, opt_true, opt_true>::parse;
 2803  		case 4: return strconv_pcdata_impl<opt_true, opt_false, opt_false>::parse;
 2804> 		case 5: return strconv_pcdata_impl<opt_true, opt_false, opt_true>::parse;
 2805  		case 6: return strconv_pcdata_impl<opt_true, opt_true, opt_false>::parse;
 2806  		case 7: return strconv_pcdata_impl<opt_true, opt_true, opt_true>::parse;
 2807  		default: assert(false); return NULL; // unreachable
 2808  		}
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2805행, 조건 `case 6`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2801  		case 2: return strconv_pcdata_impl<opt_false, opt_true, opt_false>::parse;
 2802  		case 3: return strconv_pcdata_impl<opt_false, opt_true, opt_true>::parse;
 2803  		case 4: return strconv_pcdata_impl<opt_true, opt_false, opt_false>::parse;
 2804  		case 5: return strconv_pcdata_impl<opt_true, opt_false, opt_true>::parse;
 2805> 		case 6: return strconv_pcdata_impl<opt_true, opt_true, opt_false>::parse;
 2806  		case 7: return strconv_pcdata_impl<opt_true, opt_true, opt_true>::parse;
 2807  		default: assert(false); return NULL; // unreachable
 2808  		}
 2809  	}
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2806행, 조건 `case 7`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2802  		case 3: return strconv_pcdata_impl<opt_false, opt_true, opt_true>::parse;
 2803  		case 4: return strconv_pcdata_impl<opt_true, opt_false, opt_false>::parse;
 2804  		case 5: return strconv_pcdata_impl<opt_true, opt_false, opt_true>::parse;
 2805  		case 6: return strconv_pcdata_impl<opt_true, opt_true, opt_false>::parse;
 2806> 		case 7: return strconv_pcdata_impl<opt_true, opt_true, opt_true>::parse;
 2807  		default: assert(false); return NULL; // unreachable
 2808  		}
 2809  	}
 2810  
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2807행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2803  		case 4: return strconv_pcdata_impl<opt_true, opt_false, opt_false>::parse;
 2804  		case 5: return strconv_pcdata_impl<opt_true, opt_false, opt_true>::parse;
 2805  		case 6: return strconv_pcdata_impl<opt_true, opt_true, opt_false>::parse;
 2806  		case 7: return strconv_pcdata_impl<opt_true, opt_true, opt_true>::parse;
 2807> 		default: assert(false); return NULL; // unreachable
 2808  		}
 2809  	}
 2810  
 2811  	typedef char_t* (*strconv_attribute_t)(char_t*, char_t);
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2969행, 조건 `case 1`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2965  
 2966  		switch ((optmask >> 4) & 15) // get bitmask for flags (wnorm wconv eol escapes); this simultaneously checks 4 options from assertion above
 2967  		{
 2968  		case 0:  return strconv_attribute_impl<opt_false>::parse_simple;
 2969> 		case 1:  return strconv_attribute_impl<opt_true>::parse_simple;
 2970  		case 2:  return strconv_attribute_impl<opt_false>::parse_eol;
 2971  		case 3:  return strconv_attribute_impl<opt_true>::parse_eol;
 2972  		case 4:  return strconv_attribute_impl<opt_false>::parse_wconv;
 2973  		case 5:  return strconv_attribute_impl<opt_true>::parse_wconv;
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 제안 4
`xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 1번째 인자 `contents`에 하네스가 null을 넘긴 적이 없습니다(9행, 10행, 11행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2138행, 조건 `contents`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 2134  		{
 2135  			char_t* buffer = static_cast<char_t*>(xml_memory::allocate((length + 1) * sizeof(char_t)));
 2136  			if (!buffer) return false;
 2137  
 2138> 			if (contents)
 2139  				memcpy(buffer, contents, length * sizeof(char_t));
 2140  
 2141  			buffer[length] = 0;
 2142  
```
- `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 4844행, 조건 `!contents`가 퍼징 중 한 번도 '참'이 되지 않음
```
 4840  
 4841  	PUGI_IMPL_FN xml_parse_result load_buffer_impl(xml_document_struct* doc, xml_node_struct* root, void* contents, size_t size, unsigned int options, xml_encoding encoding, bool is_mutable, bool own, char_t** out_buffer)
 4842  	{
 4843  		// check input buffer
 4844> 		if (!contents && size) return make_parse_result(status_io_error);
 4845  
 4846  		// get actual encoding
 4847  		xml_encoding buffer_encoding = impl::get_buffer_encoding(encoding, contents, size);
 4848  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  #include "pugixml.hpp"
   2  
   3  #include <stdint.h>
   4  
   5  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size)
   6  {
   7      pugi::xml_document doc;
   8  
   9  	doc.load_buffer(Data, Size);
  10  	doc.load_buffer(Data, Size, pugi::parse_minimal);
  11  	doc.load_buffer(Data, Size, pugi::parse_full);
  12  
  13  	return 0;
  14  }
```