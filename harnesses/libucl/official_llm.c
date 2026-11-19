// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,3,4,5,6,7,8,9를 OSS-Fuzz 하네스 official에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/libucl/official/).
// OSS-Fuzz 하네스: libucl 저장소 tests/fuzzers/ucl_add_string_fuzzer.c (0.10.0, 커밋 d6659c1) 그대로.
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include "ucl.h"

// 하네스가 직접 등록하는 더미 매크로 핸들러
static bool fuzz_macro_handler(const unsigned char *data, size_t len,
		const ucl_object_t *arguments, void *ud) { // [gapfuzz-llm] register_macro에 넘길 null 아닌 핸들러
	(void)data; (void)len; (void)arguments; (void)ud;
	return true;
}

static bool fuzz_context_macro_handler(const unsigned char *data, size_t len,
		const ucl_object_t *arguments, const ucl_object_t *ctx, void *ud) { // [gapfuzz-llm] register_context_macro에 넘길 null 아닌 핸들러
	(void)data; (void)len; (void)arguments; (void)ctx; (void)ud;
	return true;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	// If size is 0 we need a null-terminated string.
	// We dont null-terminate the string and by the design
	// of the API passing 0 as size with non null-terminated string
	// gives undefined behavior. 	
	if(size==0){
		return 0;
	}
	// 입력 앞쪽 5바이트를 제어용으로 차례로 배분 (겹치지 않게), 나머지는 원래대로 문자열로 사용
	uint8_t hdr[5] = {0, 0, 0, 0, 0}; // [gapfuzz-llm] 제어 바이트 (입력이 짧으면 0 = 기존 동작)
	if (size > sizeof(hdr)) { // [gapfuzz-llm] 문자열이 최소 1바이트 남을 때만 헤더 소비
		memcpy(hdr, data, sizeof(hdr));
		data += sizeof(hdr);
		size -= sizeof(hdr);
	}

	// 변수/매크로 이름용 null 종료 버퍼 (입력 일부 복사)
	char namebuf[16]; // [gapfuzz-llm] 입력에서 만든 이름 문자열용
	size_t nlen = size < sizeof(namebuf) - 1 ? size : sizeof(namebuf) - 1;
	memcpy(namebuf, data, nlen);
	namebuf[nlen] = '\0';

	struct ucl_parser *parser;
	int flags = hdr[0] & 0x7F; // [gapfuzz-llm] flags를 퍼저 입력에서 선택 (SAVE_COMMENTS, NO_FILEVARS 등 포함, 0도 가능)
       	parser = ucl_parser_new(flags);

	if (parser != NULL) { // [gapfuzz-llm] 직접 호출하는 API는 null이 아닌 parser에만 사용
		// 제안 6: register_variable 직접 호출 (null / 기존 변수 / 새 변수)
		const char *var = NULL;
		switch (hdr[1] & 3) {
		case 0: var = NULL; break;
		case 1: var = "CURDIR"; break;
		case 2: var = "FILENAME"; break;
		default: var = namebuf; break;
		}
		ucl_parser_register_variable(parser, var, "value"); // [gapfuzz-llm] var에 null/기존/새 이름 전달
		if ((hdr[1] & 3) == 3) {
			ucl_parser_register_variable(parser, var, "value2"); // [gapfuzz-llm] 같은 이름 재등록으로 중복 분기 확인
		}

		// 제안 8: register_macro 직접 호출 (macro null 포함, handler는 non-null)
		const char *macro = NULL;
		switch ((hdr[2]) & 3) {
		case 0: macro = NULL; break;
		case 1: macro = "fuzz_macro"; break;
		case 2: macro = namebuf; break;
		default: macro = "include"; break;
		}
		ucl_parser_register_macro(parser, macro, fuzz_macro_handler, NULL); // [gapfuzz-llm] macro에 null 포함 다양한 값 전달

		// 제안 9: register_context_macro 직접 호출
		const char *cmacro = NULL;
		switch ((hdr[2] >> 2) & 3) {
		case 0: cmacro = NULL; break;
		case 1: cmacro = "fuzz_ctx_macro"; break;
		case 2: cmacro = namebuf; break;
		default: cmacro = "include_ctx"; break;
		}
		ucl_parser_register_context_macro(parser, cmacro, fuzz_context_macro_handler, NULL); // [gapfuzz-llm] macro에 null 포함 다양한 값 전달
	}

	// 제안 2, 3: add_string은 null이면 내부에서 먼저 반환하므로 add_chunk 계열을 직접 호출해 깊은 null 분기에 도달
	if (hdr[3] & 4) {
		ucl_parser_add_chunk_priority(NULL, data, size, 0); // [gapfuzz-llm] add_chunk_priority의 parser == NULL 분기 직접 도달
	}
	if (hdr[3] & 8) {
		ucl_parser_add_chunk_full(NULL, data, size, 0, UCL_DUPLICATE_APPEND, UCL_PARSE_UCL); // [gapfuzz-llm] add_chunk_full의 parser == NULL 분기 직접 도달
	}
	if ((hdr[3] & 16) && parser != NULL) {
		ucl_parser_add_chunk_full(parser, NULL, size, 0, UCL_DUPLICATE_APPEND, UCL_PARSE_UCL); // [gapfuzz-llm] add_chunk_full의 data == NULL && len != 0 분기 직접 도달 (size는 항상 1 이상)
	}

	// 제안 2, 3: parser / data 에 null도 전달
	struct ucl_parser *add_parser = (hdr[3] & 1) ? NULL : parser; // [gapfuzz-llm] parser null 입력도 시도
	const char *add_data = (hdr[3] & 2) ? NULL : (const char *)data; // [gapfuzz-llm] data null 입력도 시도
	ucl_parser_add_string(add_parser, add_data, size); // [gapfuzz-llm] parser/data에 null 가능

	// 제안 7: iterate_with_error 직접 호출 (expand_values 다양화)
	if (parser != NULL) {
		ucl_object_t *top = ucl_parser_get_object(parser); // [gapfuzz-llm] 파싱 결과 객체 획득 (참조 증가)
		if (top != NULL) {
			ucl_object_iter_t it = NULL;
			int ep = 0;
			bool expand = (hdr[4] & 1) != 0; // [gapfuzz-llm] expand_values를 true/false 모두 시도
			const ucl_object_t *cur;
			int guard = 0;
			while ((cur = ucl_object_iterate_with_error(top, &it, expand, &ep)) != NULL && guard < 1000) { // [gapfuzz-llm] 직접 순회 호출
				guard++;
			}
			ucl_object_unref(top); // [gapfuzz-llm] 획득한 참조 해제
		}
	}

	// 제안 4: get_error에 null도 전달
	struct ucl_parser *err_parser = (hdr[4] & 2) ? NULL : parser; // [gapfuzz-llm] parser null 입력도 시도
	if (ucl_parser_get_error(err_parser) != NULL) { // [gapfuzz-llm] null parser 가능
		if (hdr[4] & 4) {
			ucl_parser_free (NULL); // [gapfuzz-llm] free에 null 전달 분기 확인
		}
		ucl_parser_free (parser);
		return 0;
	}

	if (hdr[4] & 4) {
		ucl_parser_free (NULL); // [gapfuzz-llm] free에 null 전달 분기 확인
	}
	ucl_parser_free (parser);
        return 0;
}
