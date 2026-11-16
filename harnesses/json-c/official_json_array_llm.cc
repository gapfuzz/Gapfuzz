// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 2,3,4,7를 OSS-Fuzz 하네스 official_json_array에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: samples/llm/combined/json-c/official_json_array/).
// OSS-Fuzz 하네스: json-c 저장소 fuzz/json_array_fuzzer.cc (커밋 d9b375f) 그대로.
#include <fuzzer/FuzzedDataProvider.h>

#include <string> // [gapfuzz-llm] 토크나이저 입력 문자열 보관용

#include "json.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	FuzzedDataProvider fdp(data, size);
	uint8_t ctl = fdp.ConsumeIntegral<uint8_t>(); // [gapfuzz-llm] 토크나이저 직접 호출 모드를 입력 바이트에서 선택
	uint8_t ctl2 = fdp.ConsumeIntegral<uint8_t>(); // [gapfuzz-llm] UTF8 검증 플래그와 최대 깊이를 고르는 두 번째 바이트(ctl과 겹치지 않음)
	std::string tok_str = fdp.ConsumeRandomLengthString(64); // [gapfuzz-llm] 토크나이저에 직접 넘길 문자열(길이 확대)
	switch ((ctl >> 6) & 3) { // [gapfuzz-llm] 앞쪽 공백/부호를 붙여 eatws 및 숫자 분기 도달 유도(0이면 원래 문자열 그대로)
	case 1: tok_str = " " + tok_str; break; // [gapfuzz-llm] 선행 공백
	case 2: tok_str = "\t\n /" + tok_str; break; // [gapfuzz-llm] 공백 뒤 주석 시작
	case 3: tok_str = "-" + tok_str; break; // [gapfuzz-llm] 음수 부호 숫자 경로
	default: break;
	}
	{ // [gapfuzz-llm] json_tokener_parse_ex/free/reset 직접 호출 블록 시작
		int tok_flags = (ctl & 1) ? JSON_TOKENER_STRICT : 0; // [gapfuzz-llm] STRICT 플래그 유무를 퍼저가 선택(0도 가능)
		if (ctl2 & 1) tok_flags |= JSON_TOKENER_VALIDATE_UTF8; // [gapfuzz-llm] UTF8 검증 플래그도 퍼저가 선택
		int depth_sel = ctl2 >> 1; // [gapfuzz-llm] 최대 깊이 선택값
		int max_depth = (depth_sel % 8 == 0) ? JSON_TOKENER_DEFAULT_DEPTH : (1 + depth_sel % 8); // [gapfuzz-llm] 작은 깊이로 깊이 초과 분기 유도, 기본값도 유지
		int len_mode = (ctl >> 1) & 3; // [gapfuzz-llm] len 선택 방식
		int state_mode = (ctl >> 3) & 3; // [gapfuzz-llm] tok 상태 선택 방식
		int len;
		switch (len_mode) { // [gapfuzz-llm] len을 정상/-1/-2/부분 길이로 다양화
		case 0: len = (int)tok_str.size(); break; // [gapfuzz-llm] 원래처럼 전체 길이
		case 1: len = -1; break; // [gapfuzz-llm] -1: c_str()은 NUL 종료이므로 안전
		case 2: len = -2; break; // [gapfuzz-llm] len < -1 크기 오류 분기 도달
		default: len = (int)fdp.ConsumeIntegralInRange<size_t>(0, tok_str.size()); break; // [gapfuzz-llm] 입력 끝 이전에 잘린 부분 입력(버퍼 범위 내)
		}
		json_tokener_reset(NULL); // [gapfuzz-llm] reset의 null 분기 (null 허용 API)
		json_tokener_free(NULL); // [gapfuzz-llm] free의 null 분기 (null 허용 API)
		if (ctl & 0x20) { // [gapfuzz-llm] pb가 NULL인 tok을 free에 넘겨 tok->pb 거짓 분기 도달
			struct json_tokener *tok0 = json_tokener_new(); // [gapfuzz-llm] 유효한 tok 생성
			if (tok0 != NULL) {
				if (tok0->pb != NULL) printbuf_free(tok0->pb); // [gapfuzz-llm] pb를 직접 해제(이중 해제 방지 위해 곧바로 NULL 대입)
				tok0->pb = NULL; // [gapfuzz-llm] free가 pb==NULL을 다루게 함
				json_tokener_free(tok0); // [gapfuzz-llm] tok 해제
			}
		}
		if (state_mode != 3) { // [gapfuzz-llm] 3이면 null만 전달하고 parse_ex는 호출하지 않음(parse_ex는 null 금지)
			struct json_tokener *tok = json_tokener_new_ex(max_depth); // [gapfuzz-llm] 깊이를 퍼저가 고른 tok 객체 생성
			if (tok != NULL) {
				json_tokener_set_flags(tok, tok_flags); // [gapfuzz-llm] 플래그를 퍼저 입력으로 설정
				if (state_mode == 1) { // [gapfuzz-llm] 불완전하게 파싱한 뒤 reset 없이 재사용하는 상태
					size_t half = tok_str.size() / 2; // [gapfuzz-llm] 절반만 먼저 넘김
					json_object *part = json_tokener_parse_ex(tok, tok_str.c_str(), (int)half); // [gapfuzz-llm] 중간 상태 tok 만들기
					if (part != NULL) json_object_put(part); // [gapfuzz-llm] 반환 객체 해제
				} else if (state_mode == 2) {
					json_tokener_reset(tok); // [gapfuzz-llm] 명시적 reset 후 파싱
				}
				json_object *res = json_tokener_parse_ex(tok, tok_str.c_str(), len); // [gapfuzz-llm] 하네스가 직접 parse_ex 호출
				if (res != NULL) json_object_put(res); // [gapfuzz-llm] 반환 객체 해제
				json_tokener_free(tok); // [gapfuzz-llm] 할당한 tok 해제
			}
		}
	} // [gapfuzz-llm] 직접 호출 블록 끝
	json_object *my_array = json_object_new_array();
	for (int i = 0; i < 3; ++i) {
		json_object *jso = json_tokener_parse(fdp.ConsumeRandomLengthString(10).c_str());
		if (jso == NULL) {
			continue;
		}
		json_object_array_add(my_array, jso);
	}
	json_object_array_insert_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10),
	                             json_object_new_int(fdp.ConsumeIntegral<int>()));
	json_object_array_get_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10));
	json_object_array_put_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10),
	                          json_object_new_int(fdp.ConsumeIntegral<int>()));
	json_object_array_del_idx(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10),
	                          fdp.ConsumeIntegralInRange<size_t>(0, 10));
	json_object_array_shrink(my_array, fdp.ConsumeIntegralInRange<size_t>(0, 10));
	json_object_array_sort(my_array, [](const void *a, const void *b) { return 0; });
	json_object_array_length(my_array);
	json_object_put(my_array);
	return 0;
}
