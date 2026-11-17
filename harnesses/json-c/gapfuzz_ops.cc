// [gapfuzz-ops] 이 파일은 Claude(claude-sonnet-5-5)가 새로 쓴 하네스입니다. OSS-Fuzz 하네스 전체를 합쳐도 불리지 않던 API 9개를 부릅니다.
// [gapfuzz-ops] gapfuzz가 검사해 통과했습니다 (python3 -m gapfuzz llmops json-c --union, 기록: evaluation/artifacts/llm/ops/json-c/_union/).
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <json.h>

// 입력 상한 및 반복 상한
static const size_t kMaxInput = 64 * 1024;
static const int kMaxSteps = 8;
static const int kMaxIter = 64;

// 영역(포인터, 길이)에서 8바이트를 읽어 부족하면 0으로 채운다.
static uint64_t read_u64(const uint8_t *p, size_t n, size_t off)
{
	uint64_t v = 0;
	for (size_t i = 0; i < 8; i++) {
		uint8_t b = (off + i < n) ? p[off + i] : 0;
		v = (v << 8) | b;
	}
	return v;
}

// 깊이를 제한해서 파싱한다. 실패하면 NULL.
static json_object *parse_region(const uint8_t *p, size_t n)
{
	if (n == 0)
		return NULL;
	json_tokener *tok = json_tokener_new_ex(16);
	if (!tok)
		return NULL;
	json_object *obj = json_tokener_parse_ex(tok, reinterpret_cast<const char *>(p), (int)n);
	if (json_tokener_get_error(tok) != json_tokener_success) {
		if (obj)
			json_object_put(obj);
		obj = NULL;
	}
	json_tokener_free(tok);
	return obj;
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
	if (size > kMaxInput)
		size = kMaxInput;
	if (size < 12)
		return 0;

	// 헤더: [0]=단계 수, [1..8]=연산 선택 바이트, [9],[10]=영역 분할, [11]=옵션
	int nsteps = 1 + data[0] % kMaxSteps;
	const uint8_t *ops = data + 1;
	uint8_t split1 = data[9];
	uint8_t split2 = data[10];
	uint8_t opt = data[11];

	const uint8_t *rest = data + 12;
	size_t restlen = size - 12;
	size_t doclen = restlen * split1 / 256;
	const uint8_t *docp = rest;
	const uint8_t *r2 = rest + doclen;
	size_t r2len = restlen - doclen;
	size_t patchlen = r2len * split2 / 256;
	const uint8_t *patchp = r2;
	const uint8_t *scalp = r2 + patchlen; // 숫자 값에 쓰는 영역
	size_t scallen = r2len - patchlen;

	json_object *doc = parse_region(docp, doclen);
	json_object *patch = parse_region(patchp, patchlen);
	json_object *work = NULL; // 변경해도 되는 deep copy
	if (doc) {
		if (json_object_deep_copy(doc, &work, NULL) != 0)
			work = NULL;
	}

	for (int step = 0; step < nsteps; step++) {
		uint8_t op = ops[step];
		switch (op % 6) {
		case 0: {
			// [gapfuzz-ops] json_patch_apply
			if (!doc || !patch)
				break;
			struct json_patch_error perr;
			memset(&perr, 0, sizeof(perr));
			json_object *base = NULL;
			if (opt & 1) {
				// base가 NULL이면 copy_from을 복사한다.
				(void)json_patch_apply(doc, patch, &base, &perr);
			} else {
				// base를 직접 만들어서 제자리에서 수정한다. copy_from은 NULL.
				if (json_object_deep_copy(doc, &base, NULL) != 0)
					break;
				(void)json_patch_apply(NULL, patch, &base, &perr);
			}
			// 실패해도 base는 반드시 json_object_put으로 해제한다.
			if (base) {
				(void)json_object_to_json_string(base);
				json_object_put(base);
			}
			break;
		}
		case 1: {
			// [gapfuzz-ops] json_object_int_inc
			int64_t v0 = (int64_t)read_u64(scalp, scallen, 0);
			int64_t v1 = (int64_t)read_u64(scalp, scallen, 8);
			json_object *num = json_object_new_int64(v0);
			if (!num)
				break;
			(void)json_object_int_inc(num, v1);
			(void)json_object_int_inc(num, -v1);
			(void)json_object_get_int64(num);
			// int가 아닌 객체에는 아무 일도 하지 않고 0을 반환한다.
			if (work)
				(void)json_object_int_inc(work, v1);
			json_object_put(num);
			break;
		}
		case 2: {
			// [gapfuzz-ops] json_object_double_to_json_string
			// (전역 상태를 바꾸는 json_c_set_serialization_double_format 대신
			//  객체별 serializer로 같은 직렬화 경로를 부른다.)
			double d;
			uint64_t bits = read_u64(scalp, scallen, 0);
			memcpy(&d, &bits, sizeof(d));
			char fmt[16];
			snprintf(fmt, sizeof(fmt), "%%.%dg", 1 + (int)(opt % 17));
			json_object *jd = json_object_new_double(d);
			if (!jd)
				break;
			char *fmtcopy = strdup(fmt);
			if (fmtcopy) {
				json_object_set_serializer(jd, json_object_double_to_json_string, fmtcopy,
				                           json_object_free_userdata);
			}
			const char *s = json_object_to_json_string_ext(jd, (opt & 2) ? JSON_C_TO_STRING_PRETTY
			                                                              : JSON_C_TO_STRING_PLAIN);
			if (s)
				(void)strlen(s);
			json_object_put(jd);
			break;
		}
		case 3: {
			// [gapfuzz-ops] json_object_array_put_with_idx_limit_cb
			// 콜백을 직접 호출한다. 부모는 배열이어야 하므로 전용 배열을 만든다.
			json_object *arr = json_object_new_array();
			if (!arr)
				break;
			size_t limit = (size_t)(read_u64(scalp, scallen, 8) % 1025);
			size_t *limit_ptr = &limit;
			int ncalls = 1 + (int)(opt % 4);
			for (int i = 0; i < ncalls; i++) {
				json_object *v = json_object_new_int64((int64_t)read_u64(scalp, scallen, 16 + i));
				if (!v)
					break;
				size_t idx = (size_t)(read_u64(scalp, scallen, 24 + i * 2) % 2048);
				// priv가 NULL인 경우는 문서상 음수를 반환한다.
				void *priv = (opt & 8) ? NULL : (void *)limit_ptr;
				// 콜백이 성공하면 참조를 가져가므로, 실패 시에만 직접 해제한다.
				int rc = json_object_array_put_with_idx_limit_cb(arr, NULL, idx, v, priv);
				if (rc < 0)
					json_object_put(v);
			}
			(void)json_object_array_length(arr);
			(void)json_object_to_json_string(arr);
			json_object_put(arr);
			break;
		}
		case 4: {
			// [gapfuzz-ops] json_object_iter_end
			// [gapfuzz-ops] json_object_iter_equal
			// [gapfuzz-ops] json_object_iter_peek_name
			// [gapfuzz-ops] json_object_iter_peek_value
			// [gapfuzz-ops] json_object_iter_next
			// [gapfuzz-ops] json_type_to_name
			json_object *target = (opt & 16) ? doc : work;
			if (!target || !json_object_is_type(target, json_type_object))
				break;
			struct json_object_iterator it = json_object_iter_begin(target);
			struct json_object_iterator end = json_object_iter_end(target);
			int n = 0;
			// 순회 중에는 객체를 수정하지 않는다.
			while (!json_object_iter_equal(&it, &end) && n < kMaxIter) {
				const char *name = json_object_iter_peek_name(&it);
				json_object *v = json_object_iter_peek_value(&it);
				if (name)
					(void)strlen(name);
				// JSON null은 NULL 포인터로 표현된다.
				const char *tn = json_type_to_name(json_object_get_type(v));
				if (tn)
					(void)strlen(tn);
				json_object_iter_next(&it);
				n++;
			}
			break;
		}
		case 5: {
			// [gapfuzz-ops] json_type_to_name
			// 유효한 enum 범위(null..string)만 사용한다.
			for (int i = 0; i < 8; i++) {
				uint8_t b = (size_t)i < scallen ? scalp[i] : (uint8_t)i;
				const char *tn = json_type_to_name((enum json_type)(b % 7));
				if (tn)
					(void)strlen(tn);
			}
			break;
		}
		}
	}

	if (work)
		json_object_put(work);
	if (patch)
		json_object_put(patch);
	if (doc)
		json_object_put(doc);
	return 0;
}
