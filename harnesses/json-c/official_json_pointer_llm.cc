// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,3,4,5,8,9를 OSS-Fuzz 하네스 official_json_pointer에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/json-c/official_json_pointer/).
// OSS-Fuzz 하네스: json-c 저장소 fuzz/json_pointer_fuzzer.cc (커밋 d9b375f) 그대로.
#include <fuzzer/FuzzedDataProvider.h>

#include <string>

#include "json.h"

// 경로가 "" 이거나 "/키" 형태(슬래시가 맨 앞 하나뿐)인지 확인한다.
static bool IsSingleLevelPath(const char *p) {  // [gapfuzz-llm] 자기 자신 추가 시 순환/누수가 생기지 않는 경로만 허용하는 헬퍼
	if (p == nullptr) {
		return false;
	}
	if (p[0] == '\0') {
		return true;
	}
	if (p[0] != '/') {
		return false;
	}
	for (const char *c = p + 1; *c; ++c) {
		if (*c == '/') {
			return false;
		}
	}
	return true;
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	FuzzedDataProvider fdp(data, size);

	// 입력 앞쪽 바이트에서 차례로 꺼내 쓰는 선택값들 (기존 입력 소비와 겹치지 않게 가장 먼저 소비)
	bool get_res_null = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;   // [gapfuzz-llm] json_pointer_get의 res를 가끔 NULL로 전달
	bool getf_res_null = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;  // [gapfuzz-llm] json_pointer_getf의 res를 가끔 NULL로 전달
	bool get_path_null = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;  // [gapfuzz-llm] json_pointer_get의 path를 가끔 nullptr로 전달
	bool set_path_null = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;  // [gapfuzz-llm] json_pointer_set의 path를 가끔 nullptr로 전달
	bool set_obj_null = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;   // [gapfuzz-llm] json_pointer_set의 obj를 가끔 NULL로 전달
	bool setf_obj_null = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;  // [gapfuzz-llm] json_pointer_setf의 obj를 가끔 NULL로 전달
	int getf_fmt_sel = fdp.ConsumeIntegralInRange<int>(0, 4);         // [gapfuzz-llm] getf의 path_fmt를 입력으로 선택
	int setf_fmt_sel = fdp.ConsumeIntegralInRange<int>(0, 4);         // [gapfuzz-llm] setf의 path_fmt를 입력으로 선택
	bool jo1_null_sel = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;   // [gapfuzz-llm] *obj가 NULL인 상태(json_object_get_type의 !jso)를 만들기 위한 선택값
	bool alias_sel = fdp.ConsumeIntegralInRange<int>(0, 3) == 0;      // [gapfuzz-llm] 설정할 값을 대상 객체 자신으로 쓰는(jso == val) 선택값
	// 포맷 문자열은 인자 1개(%s)만 소비하는 안전한 후보 또는 NULL 중에서만 고른다
	const char *fmt_table[5] = {"%s", "%s", "/%s", nullptr, "%s"};    // [gapfuzz-llm] 안전한 포맷 후보 표 (NULL 포함)

	struct json_tokener *tokener =
	    json_tokener_new_ex(fdp.ConsumeIntegralInRange<int>(1, JSON_TOKENER_DEFAULT_DEPTH));
	int flags = 0;
	if (fdp.ConsumeBool()) {
		flags |= JSON_TOKENER_VALIDATE_UTF8;
	}
	if (fdp.ConsumeBool()) {
		flags |= JSON_TOKENER_ALLOW_TRAILING_CHARS;
	}
	if (fdp.ConsumeBool()) {
		flags |= JSON_TOKENER_STRICT;
	}
	json_tokener_set_flags(tokener, flags);

	std::string path = fdp.ConsumeRandomLengthString(5);
	std::string sub_json_str = fdp.ConsumeRandomLengthString(10);
	bool use_format_string = fdp.ConsumeBool();
	std::string json_str = fdp.ConsumeRemainingBytesAsString();

	struct json_object *jo1 = json_tokener_parse_ex(tokener, json_str.c_str(), json_str.size());

	if (jo1_null_sel) {  // [gapfuzz-llm] 파싱 결과를 버리고 jo1을 NULL로 만들어 *obj == NULL 경로를 확실히 실행
		json_object_put(jo1);
		jo1 = NULL;
	}

	struct json_object *sub_json = json_tokener_parse(sub_json_str.c_str());
	if (sub_json == NULL) {
		sub_json = json_object_new_object();
	}

	struct json_object *jo2 = NULL;
	if (use_format_string) {
		json_pointer_getf(jo1, getf_res_null ? NULL : &jo2, fmt_table[getf_fmt_sel], path.c_str());  // [gapfuzz-llm] res와 path_fmt를 입력에 따라 변경
		const char *sf = fmt_table[setf_fmt_sel];
		std::string eff = (sf != nullptr && sf[0] == '/') ? "/" + path : path;
		if (alias_sel && !setf_obj_null && jo1 != NULL && json_object_is_type(jo1, json_type_object) &&
		    IsSingleLevelPath(eff.c_str())) {  // [gapfuzz-llm] 값을 jo1 자신(참조 하나 추가)으로 바꿔 jso == val 분기 유도
			json_object_put(sub_json);
			sub_json = json_object_get(jo1);
		}
		if (json_pointer_setf(setf_obj_null ? NULL : &jo1, sub_json, sf, path.c_str()))  // [gapfuzz-llm] obj와 path_fmt를 입력에 따라 변경
		{
			json_object_put(sub_json);
		}
	} else {
		json_pointer_get(jo1, get_path_null ? nullptr : path.c_str(), get_res_null ? NULL : &jo2);  // [gapfuzz-llm] path와 res를 입력에 따라 nullptr/NULL로 변경
		if (alias_sel && !set_obj_null && !set_path_null && jo1 != NULL &&
		    json_object_is_type(jo1, json_type_object) && IsSingleLevelPath(path.c_str())) {  // [gapfuzz-llm] 값을 jo1 자신(참조 하나 추가)으로 바꿔 jso == val 분기 유도
			json_object_put(sub_json);
			sub_json = json_object_get(jo1);
		}
		if (json_pointer_set(set_obj_null ? NULL : &jo1, set_path_null ? nullptr : path.c_str(), sub_json))  // [gapfuzz-llm] obj와 path를 입력에 따라 NULL/nullptr로 변경
		{
			json_object_put(sub_json);
		}
	}

	// Clean up the main JSON object
	json_object_put(jo1);
	json_tokener_free(tokener);
	return 0;
}
