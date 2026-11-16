# 호출 안 함 API 우선순위 — json-c/_union

'호출 안 함' API 34개. 추가 가능 28개, 제외 6개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `json_patch_apply(struct json_object *, struct json_object *, struct json_object **, struct json_patch_error *)` | 17 | 294 | 294 | 이번에 추가 |
| 2 | `json_object_int_inc(struct json_object *, int64_t)` | 4 | 37 | 37 | 이번에 추가 |
| 3 | `json_c_set_serialization_double_format(const char *, int)` | 7 | 29 | 29 | 이번에 추가 |
| 4 | `json_object_array_put_with_idx_limit_cb(struct json_object *, const char *, size_t, struct json_object *, void *)` | 2 | 10 | 10 | 이번에 추가 |
| 5 | `json_type_to_name(enum json_type)` | 5 | 9 | 8 | 이번에 추가 |
| 6 | `json_object_iter_peek_value(const struct json_object_iterator *)` | 1 | 7 | 7 | 이번에 추가 |
| 7 | `json_object_iter_peek_name(const struct json_object_iterator *)` | 1 | 7 | 7 | 이번에 추가 |
| 8 | `json_object_iter_next(struct json_object_iterator *)` | 1 | 7 | 7 | 이번에 추가 |
| 9 | `json_object_iter_equal(const struct json_object_iterator *, const struct json_object_iterator *)` | 1 | 7 | 7 | 이번에 추가 |
| 10 | `json_object_iter_end(const struct json_object *)` | 1 | 7 | 7 | 이번에 추가 |
| 11 | `json_tokener_error_desc(enum json_tokener_error)` | 1 | 6 | 6 |  |
| 12 | `json_object_array_bsearch(const struct json_object *, const struct json_object *, int (*)(const void *, const void *))` | 4 | 6 | 6 |  |
| 13 | `json_util_get_last_err(void)` | 1 | 4 | 4 |  |
| 14 | `json_pointer_set_with_limit_index(struct json_object **, const char *, struct json_object *, size_t)` | 1 | 4 | 4 |  |
| 15 | `json_parse_double(const char *, double *)` | 2 | 4 | 4 |  |
| 16 | `json_object_iter_begin(struct json_object *)` | 1 | 4 | 4 |  |
| 17 | `json_object_get_userdata(json_object *)` | 1 | 3 | 3 |  |
| 18 | `json_tokener_get_parse_end(struct json_tokener *)` | 2 | 2 | 2 |  |
| 19 | `json_object_object_length(const struct json_object *)` | 2 | 2 | 2 |  |
| 20 | `json_tokener_get_error(struct json_tokener *)` | 1 | 1 | 1 |  |
| 21 | `json_object_object_get(const struct json_object *, const char *)` | 1 | 1 | 1 |  |
| 22 | `json_object_new_string(const char *)` | 2 | 1 | 1 |  |
| 23 | `json_object_new_null(void)` | 1 | 1 | 1 |  |
| 24 | `json_object_iter_init_default(void)` | 1 | 1 | 1 |  |
| 25 | `json_object_double_to_json_string(struct json_object *, struct printbuf *, int, int)` | 1 | 1 | 1 |  |
| 26 | `json_c_object_sizeof(void)` | 1 | 1 | 1 |  |
| 27 | `json_object_equal(struct json_object *, struct json_object *)` | 5 | 73 | 0 |  |
| 28 | `json_object_object_del(struct json_object *, const char *)` | 3 | 6 | 0 |  |
| 29 | `json_object_from_file(const char *)` | 16 | 71 | 0 | 파일 입출력 |
| 30 | `json_object_from_fd(int)` | 13 | 66 | 0 | 파일 입출력 |
| 31 | `json_object_from_fd_ex(int, int)` | 12 | 65 | 0 | 파일 입출력 |
| 32 | `json_object_to_file(const char *, struct json_object *)` | 15 | 57 | 0 | 파일 입출력 |
| 33 | `json_object_to_file_ext(const char *, struct json_object *, int)` | 14 | 55 | 0 | 파일 입출력 |
| 34 | `json_object_to_fd(int, struct json_object *, int)` | 12 | 51 | 0 | 파일 입출력 |
