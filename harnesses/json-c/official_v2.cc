// json-c 공식 하네스(tokener_parse_ex_fuzzer.cc)에 gapfuzz 제안을 적용한 버전.
//
// 입력 앞 3바이트를 설정으로 쓰고(있을 때만), 나머지는 공식 하네스처럼 JSON으로 파싱한다.
//   제안 3 (DIRECT_CALL) json_tokener_new_ex의 depth   → 0·음수를 포함한 값으로 직접 부름
//   제안 2 (DIRECT_CALL) json_object_object_add_ex의 opts → 플래그 조합을 입력으로 고름
//   제안 4 (DIRECT_CALL) json_object_to_json_string_length의 length → 포인터 또는 NULL
//   제안 5 (DIRECT_CALL) json_object_array_shrink의 empty_slots → 0 이상 값만
//     (음수는 라이브러리가 json_abort로 거부하는 인자라 넘기면 가짜 크래시가 남: 처음엔 음수도 넘겼다가
//      gapfuzz 크래시 귀속이 '하네스 버그'로 판정해 고침. 그래서 이 제안이 겨냥한 `empty_slots < 0` 분기는 열 수 없음)
//   제안 1 (NARROW, json_tokener_free에 NULL)은 대조군으로 일부러 적용하지 않음
#include <stdint.h>

#include <json.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
	int depth = JSON_TOKENER_DEFAULT_DEPTH;
	unsigned add_opts = 0;
	int shrink = 0;
	int len_null = 0;
	if (size >= 3) {
		depth = (int)(int8_t)data[0];                 // -128..127, 0·음수 포함
		add_opts = data[1] & 0x3;                      // 비트 0: KEY_IS_NEW, 비트 1: CONSTANT_KEY
		len_null = (data[1] >> 2) & 1;
		shrink = (int)data[2];                         // 0..255 (음수 금지)
		data += 3;
		size -= 3;
	}

	const char *data1 = reinterpret_cast<const char *>(data);
	json_tokener *tok = json_tokener_new_ex(depth);
	if (!tok)                                          // depth < 1이면 NULL: 기본 깊이로 이어서 파싱
		tok = json_tokener_new();
	if (!tok)
		return 0;
	json_object *obj = json_tokener_parse_ex(tok, data1, size);

	if (json_object_is_type(obj, json_type_object)) {
		json_object_object_foreach(obj, key, val) {
			(void)json_object_get_type(val);
			(void)json_object_get_string(val);
		}
		unsigned opts = ((add_opts & 1) ? JSON_C_OBJECT_ADD_KEY_IS_NEW : 0) |
		                ((add_opts & 2) ? JSON_C_OBJECT_ADD_CONSTANT_KEY : 0);
		// CONSTANT_KEY는 키 문자열이 객체보다 오래 살아야 하므로 문자열 상수를 쓴다.
		// KEY_IS_NEW는 키가 없다는 약속이므로, 이미 있으면 부르지 않는다(하네스 오사용 방지).
		static const char kKey[] = "gapfuzz_added";
		if (!(opts & JSON_C_OBJECT_ADD_KEY_IS_NEW) || !json_object_object_get_ex(obj, kKey, NULL))
			json_object_object_add_ex(obj, kKey, json_object_new_int(depth), opts);
	}
	if (json_object_is_type(obj, json_type_array))
		(void)json_object_array_shrink(obj, shrink);

	size_t out_len = 0;
	(void)json_object_to_json_string_length(obj, JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED,
	                                        len_null ? NULL : &out_len);

	json_object_put(obj);
	json_tokener_free(tok);
	return 0;
}
