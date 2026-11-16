# 호출 안 함 API 우선순위 — libucl/_union

'호출 안 함' API 82개. 추가 가능 72개, 제외 10개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `ucl_object_validate_root(const ucl_object_t *, const ucl_object_t *, const ucl_object_t *, struct ucl_schema_error *)` | 73 | 1101 | 1101 | 이번에 추가 |
| 2 | `ucl_object_merge(ucl_object_t *, ucl_object_t *, bool)` | 15 | 380 | 233 | 이번에 추가 |
| 3 | `ucl_object_sort_keys(ucl_object_t *, enum ucl_object_keys_sort_flags)` | 7 | 150 | 150 | 이번에 추가 |
| 4 | `ucl_comments_add(ucl_object_t *, const ucl_object_t *, const char *)` | 12 | 224 | 94 | 이번에 추가 |
| 5 | `ucl_object_pop_key(ucl_object_t *, const char *)` | 9 | 92 | 84 | 이번에 추가 |
| 6 | `ucl_parser_insert_chunk(struct ucl_parser *, const unsigned char *, size_t)` | 2 | 64 | 64 | 이번에 추가 |
| 7 | `ucl_object_reserve(ucl_object_t *, size_t)` | 4 | 61 | 61 | 이번에 추가 |
| 8 | `ucl_array_prepend(ucl_object_t *, ucl_object_t *)` | 4 | 59 | 59 | 이번에 추가 |
| 9 | `ucl_object_emit(const ucl_object_t *, enum ucl_emitter)` | 11 | 49 | 49 | 이번에 추가 |
| 10 | `ucl_object_lookup_path(const ucl_object_t *, const char *)` | 5 | 59 | 36 | 이번에 추가 |
| 11 | `ucl_object_emit_streamline_new(const ucl_object_t *, enum ucl_emitter, struct ucl_emitter_functions *)` | 7 | 39 | 33 |  |
| 12 | `ucl_parser_get_current_stack_object(struct ucl_parser *, unsigned int)` | 2 | 31 | 27 |  |
| 13 | `ucl_parser_chunk_skip(struct ucl_parser *)` | 1 | 24 | 24 |  |
| 14 | `ucl_array_delete(ucl_object_t *, ucl_object_t *)` | 2 | 21 | 21 |  |
| 15 | `ucl_array_pop_last(ucl_object_t *)` | 2 | 17 | 17 |  |
| 16 | `ucl_array_pop_first(ucl_object_t *)` | 2 | 17 | 17 |  |
| 17 | `ucl_array_index_of(ucl_object_t *, ucl_object_t *)` | 1 | 17 | 17 |  |
| 18 | `ucl_array_replace_index(ucl_object_t *, ucl_object_t *, unsigned int)` | 1 | 15 | 15 |  |
| 19 | `ucl_object_lookup_any(const ucl_object_t *, const char *, ...)` | 5 | 21 | 13 |  |
| 20 | `ucl_array_tail(const ucl_object_t *)` | 1 | 13 | 13 |  |
| 21 | `ucl_array_size(const ucl_object_t *)` | 1 | 13 | 13 |  |
| 22 | `ucl_parser_chunk_peek(struct ucl_parser *)` | 1 | 12 | 12 |  |
| 23 | `ucl_object_tolstring(const ucl_object_t *, size_t *)` | 2 | 12 | 12 |  |
| 24 | `ucl_object_delete_key(ucl_object_t *, const char *)` | 9 | 92 | 11 |  |
| 25 | `ucl_object_iterate_reset(ucl_object_iter_t, const ucl_object_t *)` | 4 | 12 | 11 |  |
| 26 | `ucl_parser_add_special_handler(struct ucl_parser *, struct ucl_parser_special_handler *)` | 1 | 11 | 11 |  |
| 27 | `ucl_object_emit_streamline_finish(struct ucl_emitter_context *)` | 3 | 11 | 11 |  |
| 28 | `ucl_object_array_sort(ucl_object_t *, int (*)(const ucl_object_t **, const ucl_object_t **))` | 2 | 11 | 11 |  |
| 29 | `ucl_parser_set_limits(struct ucl_parser *, const struct ucl_parser_limits *)` | 3 | 8 | 8 |  |
| 30 | `ucl_object_emit_streamline_add_object(struct ucl_emitter_context *, const ucl_object_t *)` | 1 | 8 | 8 |  |
| 31 | `ucl_object_iter_chk_excpn(ucl_object_iter_t)` | 3 | 7 | 7 |  |
| 32 | `ucl_elt_append(ucl_object_t *, ucl_object_t *)` | 1 | 7 | 7 |  |
| 33 | `ucl_comments_find(const ucl_object_t *, const ucl_object_t *)` | 2 | 14 | 6 |  |
| 34 | `ucl_parser_get_linenum(struct ucl_parser *)` | 1 | 6 | 6 |  |
| 35 | `ucl_parser_get_limits(struct ucl_parser *, struct ucl_parser_limits *)` | 2 | 6 | 6 |  |
| 36 | `ucl_parser_get_comments(struct ucl_parser *)` | 1 | 6 | 6 |  |
| 37 | `ucl_parser_get_column(struct ucl_parser *)` | 1 | 6 | 6 |  |
| 38 | `ucl_object_keyl(const ucl_object_t *, size_t *)` | 1 | 6 | 6 |  |
| 39 | `ucl_parser_set_default_priority(struct ucl_parser *, unsigned int)` | 1 | 4 | 4 |  |
| 40 | `ucl_parser_get_error_code(struct ucl_parser *)` | 1 | 4 | 4 |  |
| 41 | `ucl_parser_get_default_priority(struct ucl_parser *)` | 1 | 4 | 4 |  |
| 42 | `ucl_object_tostring_forced(const ucl_object_t *)` | 1 | 4 | 4 |  |
| 43 | `ucl_object_fromint(int64_t)` | 3 | 5 | 3 |  |
| 44 | `ucl_object_fromdouble(double)` | 3 | 5 | 3 |  |
| 45 | `ucl_object_frombool(bool)` | 3 | 5 | 3 |  |
| 46 | `ucl_object_validate(const ucl_object_t *, const ucl_object_t *, struct ucl_schema_error *)` | 73 | 1101 | 1 |  |
| 47 | `ucl_object_compare_qsort(const ucl_object_t **, const ucl_object_t **)` | 16 | 142 | 1 |  |
| 48 | `ucl_object_replace_key(ucl_object_t *, ucl_object_t *, const char *, size_t, bool)` | 5 | 129 | 1 |  |
| 49 | `ucl_object_insert_key_merged(ucl_object_t *, ucl_object_t *, const char *, size_t, bool)` | 5 | 129 | 1 |  |
| 50 | `ucl_object_fromlstring(const char *, size_t)` | 7 | 84 | 1 |  |
| 51 | `ucl_parser_set_variables_handler(struct ucl_parser *, ucl_variable_handler, void *)` | 1 | 1 | 1 |  |
| 52 | `ucl_parser_set_include_tracer(struct ucl_parser *, ucl_include_trace_func_t *, void *)` | 1 | 1 | 1 |  |
| 53 | `ucl_object_free(ucl_object_t *)` | 1 | 1 | 1 |  |
| 54 | `ucl_object_validate_root_ext(const ucl_object_t *, const ucl_object_t *, const ucl_object_t *, ucl_object_t *, struct ucl_schema_error *)` | 72 | 1100 | 0 |  |
| 55 | `ucl_array_merge(ucl_object_t *, ucl_object_t *, bool)` | 14 | 304 | 0 |  |
| 56 | `ucl_object_compare(const ucl_object_t *, const ucl_object_t *)` | 15 | 141 | 0 |  |
| 57 | `ucl_object_pop_keyl(ucl_object_t *, const char *, size_t)` | 7 | 91 | 0 |  |
| 58 | `ucl_object_fromstring(const char *)` | 7 | 84 | 0 |  |
| 59 | `ucl_object_lookup_path_char(const ucl_object_t *, const char *, char)` | 4 | 58 | 0 |  |
| 60 | `ucl_object_emit_len(const ucl_object_t *, enum ucl_emitter, size_t *)` | 10 | 48 | 0 |  |
| 61 | `ucl_object_string_to_type(const char *, ucl_type_t *)` | 2 | 26 | 0 |  |
| 62 | `ucl_object_emit_streamline_start_container(struct ucl_emitter_context *, const ucl_object_t *)` | 3 | 26 | 0 |  |
| 63 | `ucl_object_emit_memory_funcs(void **)` | 4 | 26 | 0 |  |
| 64 | `ucl_array_find_index(const ucl_object_t *, unsigned int)` | 1 | 15 | 0 |  |
| 65 | `ucl_object_todouble(const ucl_object_t *)` | 2 | 12 | 0 |  |
| 66 | `ucl_object_lookup(const ucl_object_t *, const char *)` | 3 | 12 | 0 |  |
| 67 | `ucl_object_tolstring_safe(const ucl_object_t *, const char **, size_t *)` | 1 | 11 | 0 |  |
| 68 | `ucl_object_todouble_safe(const ucl_object_t *, double *)` | 1 | 11 | 0 |  |
| 69 | `ucl_object_emit_full(const ucl_object_t *, enum ucl_emitter, struct ucl_emitter_functions *, const ucl_object_t *)` | 3 | 9 | 0 |  |
| 70 | `ucl_object_emit_streamline_end_container(struct ucl_emitter_context *)` | 2 | 7 | 0 |  |
| 71 | `ucl_object_emit_funcs_free(struct ucl_emitter_functions *)` | 2 | 5 | 0 |  |
| 72 | `ucl_object_key(const ucl_object_t *)` | 1 | 1 | 0 |  |
| 73 | `ucl_parser_add_fd(struct ucl_parser *, int)` | 10 | 33 | 0 | 파일 입출력 |
| 74 | `ucl_parser_add_fd_priority(struct ucl_parser *, int, unsigned int)` | 9 | 29 | 0 | 파일 입출력 |
| 75 | `ucl_parser_add_fd_full(struct ucl_parser *, int, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` | 8 | 25 | 0 | 파일 입출력 |
| 76 | `ucl_parser_add_file(struct ucl_parser *, const char *)` | 7 | 23 | 0 | 파일 입출력 |
| 77 | `ucl_parser_add_file_priority(struct ucl_parser *, const char *, unsigned int)` | 7 | 23 | 0 | 파일 입출력 |
| 78 | `ucl_parser_add_file_full(struct ucl_parser *, const char *, unsigned int, enum ucl_duplicate_strategy, enum ucl_parse_type)` | 6 | 19 | 0 | 파일 입출력 |
| 79 | `ucl_object_emit_fd_funcs(int)` | 5 | 7 | 0 | 파일 입출력 |
| 80 | `ucl_object_emit_file_funcs(FILE *)` | 2 | 3 | 0 | 파일 입출력 |
| 81 | `ucl_parser_get_cur_file(struct ucl_parser *)` | 1 | 1 | 0 | 파일 입출력 |
| 82 | `ucl_parser_pubkey_add(struct ucl_parser *, const unsigned char *, size_t)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
