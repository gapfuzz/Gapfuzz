// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,3,4를 공식 하네스에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness.py, 기록: samples/llm/combined/pugixml/).
#include "pugixml.hpp"

#include <stdint.h>
#include <stdlib.h>

static bool g_fail_alloc = false; // [gapfuzz-llm] 할당 실패 모드 플래그: convert_buffer의 메모리 부족 분기(4864행)를 열기 위함

static void *fuzz_allocate(size_t size) // [gapfuzz-llm] 플래그가 켜져 있으면 NULL을 반환하는 할당 함수
{
	if (g_fail_alloc) return NULL; // [gapfuzz-llm] pugixml은 NULL 반환을 status_out_of_memory로 처리함
	return malloc(size); // [gapfuzz-llm] 평소에는 일반 malloc 사용
}

static void fuzz_deallocate(void *ptr) // [gapfuzz-llm] 위 할당 함수와 짝이 되는 해제 함수
{
	free(ptr); // [gapfuzz-llm] malloc으로 할당한 메모리를 해제
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size)
{
	static bool s_allocator_set = (pugi::set_memory_management_functions(fuzz_allocate, fuzz_deallocate), true); // [gapfuzz-llm] 문서 생성 전에 한 번만 사용자 할당자를 등록
	(void)s_allocator_set; // [gapfuzz-llm] 미사용 변수 경고 방지

    pugi::xml_document doc;

	static const pugi::xml_encoding kEncodings[] = { // [gapfuzz-llm] 인코딩 후보 목록: 원래 값(auto)을 포함해 모든 인코딩을 고를 수 있게 함
		pugi::encoding_auto, pugi::encoding_utf8, pugi::encoding_utf16_le,
		pugi::encoding_utf16_be, pugi::encoding_utf16, pugi::encoding_utf32_le,
		pugi::encoding_utf32_be, pugi::encoding_utf32, pugi::encoding_wchar,
		pugi::encoding_latin1
	};

	pugi::xml_encoding encoding = pugi::encoding_auto; // [gapfuzz-llm] 입력이 짧으면 원래 값(auto) 유지
	unsigned int fuzz_options = pugi::parse_minimal; // [gapfuzz-llm] options를 퍼저 입력에서 고르기 위한 변수, 기본은 원래 값
	bool use_null = false; // [gapfuzz-llm] contents에 nullptr을 넘길지 여부, 기본은 원래대로 Data 전달
	bool zero_len = false; // [gapfuzz-llm] nullptr일 때 길이 0 경로와 길이>0 경로를 모두 타기 위한 플래그
	bool fuzz_opt2 = false; // [gapfuzz-llm] 두 번째 호출에 입력에서 고른 options를 쓸지 여부
	bool fuzz_opt3 = false; // [gapfuzz-llm] 세 번째 호출에 입력에서 고른 options를 쓸지 여부
	unsigned int fail_calls = 0; // [gapfuzz-llm] 호출별 할당 실패 여부 비트 마스크(기본은 실패 없음)

	if (Size >= 5) // [gapfuzz-llm] 앞 5바이트를 서로 겹치지 않게 순서대로 배분
	{
		encoding = kEncodings[Data[0] % (sizeof(kEncodings) / sizeof(kEncodings[0]))]; // [gapfuzz-llm] 0번 바이트: 인코딩 선택
		fuzz_options = ((unsigned int)Data[1] << 8) | Data[2]; // [gapfuzz-llm] 1~2번 바이트: options 비트 조합 생성
		use_null = (Data[3] & 1) != 0; // [gapfuzz-llm] 3번 바이트 bit0: contents에 nullptr 전달 여부
		zero_len = (Data[3] & 2) != 0; // [gapfuzz-llm] 3번 바이트 bit1: nullptr과 함께 길이 0 사용 여부
		fuzz_opt2 = (Data[3] & 4) != 0; // [gapfuzz-llm] 3번 바이트 bit2: 두 번째 호출 options 선택
		fuzz_opt3 = (Data[3] & 8) != 0; // [gapfuzz-llm] 3번 바이트 bit3: 세 번째 호출 options 선택
		if (use_null && zero_len) // [gapfuzz-llm] nullptr+길이 0은 utf8 빠른 경로(get_mutable_buffer, 2138행)에서만 contents 거짓 분기에 닿으므로 항상 그 경로로 유도
			encoding = (Data[0] & 1) ? pugi::encoding_utf8 : pugi::encoding_auto; // [gapfuzz-llm] 길이 0이면 auto도 utf8로 판정됨
		fail_calls = (Data[4] & 8) ? (unsigned int)(Data[4] & 7) : 0u; // [gapfuzz-llm] 4번 바이트: 절반은 실패 없음, 나머지는 호출별 할당 실패 선택
		Data += 5; // [gapfuzz-llm] 설정에 쓴 바이트는 문서 내용에서 제외하고 나머지는 계속 사용
		Size -= 5; // [gapfuzz-llm] 남은 크기 갱신
	}

	const void *contents = use_null ? nullptr : static_cast<const void *>(Data); // [gapfuzz-llm] 원래 Data도 계속 전달하면서 nullptr도 입력에 따라 전달
	size_t length = (use_null && zero_len) ? 0 : Size; // [gapfuzz-llm] nullptr+0 조합도 만들고, 원래 Size도 계속 나오게 함

	unsigned int options2 = fuzz_opt2 ? fuzz_options : (unsigned int)pugi::parse_minimal; // [gapfuzz-llm] 원래 parse_minimal 또는 입력에서 고른 options
	unsigned int options3 = fuzz_opt3 ? fuzz_options : (unsigned int)pugi::parse_full; // [gapfuzz-llm] 원래 parse_full 또는 입력에서 고른 options

	try // [gapfuzz-llm] 라이브러리 예외(예: bad_alloc)로 하네스가 죽지 않도록 감쌈
	{
		g_fail_alloc = (fail_calls & 1) != 0; // [gapfuzz-llm] 첫 번째 호출 동안만 할당 실패 적용
		doc.load_buffer(contents, length, pugi::parse_default, encoding); // [gapfuzz-llm] contents/encoding을 퍼저 입력에서 선택
		g_fail_alloc = (fail_calls & 2) != 0; // [gapfuzz-llm] 두 번째 호출의 할당 실패 여부 설정
		doc.load_buffer(contents, length, options2, encoding); // [gapfuzz-llm] contents/options/encoding을 퍼저 입력에서 선택
		g_fail_alloc = (fail_calls & 4) != 0; // [gapfuzz-llm] 세 번째 호출의 할당 실패 여부 설정
		doc.load_buffer(contents, length, options3, encoding); // [gapfuzz-llm] contents/options/encoding을 퍼저 입력에서 선택
	}
	catch (...) // [gapfuzz-llm] 예외는 무시하고 다음 입력으로 진행
	{
	}
	g_fail_alloc = false; // [gapfuzz-llm] 문서 소멸 등 이후 동작은 정상 할당 상태로 복구

	return 0;
}
