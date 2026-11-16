# 호출 안 함 API 우선순위 — yyjson/_union

'호출 안 함' API 327개. 추가 가능 317개, 제외 10개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `yyjson_incr_read(yyjson_incr_state *, size_t, yyjson_read_err *)` | 4 | 670 | 670 | 이번에 추가 |
| 2 | `yyjson_mut_ptr_set(yyjson_mut_val *, const char *, yyjson_mut_val *, yyjson_mut_doc *)` | 26 | 481 | 481 | 이번에 추가 |
| 3 | `yyjson_mut_write_number(const yyjson_mut_val *, char *)` | 16 | 222 | 222 | 이번에 추가 |
| 4 | `yyjson_equals(const yyjson_val *, const yyjson_val *)` | 9 | 99 | 99 | 이번에 추가 |
| 5 | `yyjson_mut_doc_imut_copy(const yyjson_mut_doc *, const yyjson_alc *)` | 6 | 81 | 81 | 이번에 추가 |
| 6 | `yyjson_ptr_get_str(const yyjson_val *, const char *, const char **)` | 15 | 151 | 66 | 이번에 추가 |
| 7 | `yyjson_mut_ptr_replace(yyjson_mut_val *, const char *, yyjson_mut_val *)` | 19 | 287 | 61 | 이번에 추가 |
| 8 | `yyjson_locate_pos(const char *, size_t, size_t, size_t *, size_t *, size_t *)` | 2 | 42 | 42 | 이번에 추가 |
| 9 | `yyjson_mut_ptr_add(yyjson_mut_val *, const char *, yyjson_mut_val *, yyjson_mut_doc *)` | 23 | 444 | 36 | 이번에 추가 |
| 10 | `yyjson_mut_ptr_remove(yyjson_mut_val *, const char *)` | 19 | 283 | 32 | 이번에 추가 |
| 11 | `yyjson_mut_read_number(const char *, yyjson_mut_val *, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)` | 3 | 31 | 31 |  |
| 12 | `yyjson_mut_get_pointer(yyjson_mut_val *, const char *)` | 14 | 209 | 30 |  |
| 13 | `yyjson_incr_new(char *, size_t, yyjson_read_flag, const yyjson_alc *)` | 4 | 28 | 28 |  |
| 14 | `yyjson_alc_pool_init(yyjson_alc *, void *, size_t)` | 5 | 17 | 17 |  |
| 15 | `yyjson_write_buf(char *, size_t, const yyjson_doc *, yyjson_write_flag, yyjson_write_err *)` | 3 | 14 | 14 |  |
| 16 | `yyjson_mut_write_buf(char *, size_t, const yyjson_mut_doc *, yyjson_write_flag, yyjson_write_err *)` | 3 | 14 | 14 |  |
| 17 | `yyjson_mut_obj_iter_get(yyjson_mut_obj_iter *, const char *)` | 3 | 13 | 13 |  |
| 18 | `yyjson_mut_doc_mut_copy(const yyjson_mut_doc *, const yyjson_alc *)` | 1 | 13 | 13 |  |
| 19 | `yyjson_alc_dyn_free(yyjson_alc *)` | 2 | 11 | 11 |  |
| 20 | `yyjson_mut_doc_set_val_pool_size(yyjson_mut_doc *, size_t)` | 1 | 9 | 9 |  |
| 21 | `yyjson_mut_doc_set_str_pool_size(yyjson_mut_doc *, size_t)` | 1 | 9 | 9 |  |
| 22 | `yyjson_incr_free(yyjson_incr_state *)` | 2 | 9 | 9 |  |
| 23 | `yyjson_mut_obj_add_arr(yyjson_mut_doc *, yyjson_mut_val *, const char *)` | 9 | 7 | 5 |  |
| 24 | `yyjson_mut_get_uint(const yyjson_mut_val *)` | 5 | 5 | 5 |  |
| 25 | `yyjson_mut_get_real(const yyjson_mut_val *)` | 5 | 5 | 5 |  |
| 26 | `yyjson_mut_get_raw(const yyjson_mut_val *)` | 5 | 5 | 5 |  |
| 27 | `yyjson_alc_dyn_new(void)` | 3 | 5 | 5 |  |
| 28 | `yyjson_mut_doc_get_pointer(yyjson_mut_doc *, const char *)` | 14 | 183 | 4 |  |
| 29 | `yyjson_ptr_get_num(const yyjson_val *, const char *, double *)` | 17 | 151 | 4 |  |
| 30 | `yyjson_doc_get_pointer(yyjson_doc *, const char *)` | 14 | 148 | 4 |  |
| 31 | `yyjson_mut_get_bool(const yyjson_mut_val *)` | 4 | 4 | 4 |  |
| 32 | `yyjson_mut_doc_ptr_set(yyjson_mut_doc *, const char *, yyjson_mut_val *)` | 26 | 481 | 3 |  |
| 33 | `yyjson_mut_doc_ptr_add(yyjson_mut_doc *, const char *, yyjson_mut_val *)` | 23 | 411 | 3 |  |
| 34 | `yyjson_mut_doc_ptr_replace(yyjson_mut_doc *, const char *, yyjson_mut_val *)` | 19 | 256 | 3 |  |
| 35 | `yyjson_mut_doc_ptr_remove(yyjson_mut_doc *, const char *)` | 19 | 254 | 3 |  |
| 36 | `yyjson_ptr_get_uint(const yyjson_val *, const char *, uint64_t *)` | 16 | 150 | 3 |  |
| 37 | `yyjson_mut_obj_rename_key(yyjson_mut_doc *, yyjson_mut_val *, const char *, const char *)` | 10 | 24 | 3 |  |
| 38 | `yyjson_mut_arr_add_uint(yyjson_mut_doc *, yyjson_mut_val *, uint64_t)` | 6 | 14 | 3 |  |
| 39 | `yyjson_mut_arr_add_true(yyjson_mut_doc *, yyjson_mut_val *)` | 6 | 14 | 3 |  |
| 40 | `yyjson_mut_arr_add_sint(yyjson_mut_doc *, yyjson_mut_val *, int64_t)` | 6 | 14 | 3 |  |
| 41 | `yyjson_mut_arr_add_real(yyjson_mut_doc *, yyjson_mut_val *, double)` | 6 | 14 | 3 |  |
| 42 | `yyjson_mut_arr_add_null(yyjson_mut_doc *, yyjson_mut_val *)` | 6 | 14 | 3 |  |
| 43 | `yyjson_mut_arr_add_float(yyjson_mut_doc *, yyjson_mut_val *, float)` | 6 | 14 | 3 |  |
| 44 | `yyjson_mut_arr_add_double(yyjson_mut_doc *, yyjson_mut_val *, double)` | 6 | 14 | 3 |  |
| 45 | `yyjson_mut_get_sint(const yyjson_mut_val *)` | 5 | 5 | 3 |  |
| 46 | `yyjson_mut_get_int(const yyjson_mut_val *)` | 5 | 5 | 3 |  |
| 47 | `yyjson_mut_set_fp_to_float(yyjson_mut_val *, bool)` | 5 | 4 | 3 |  |
| 48 | `yyjson_mut_get_type_desc(const yyjson_mut_val *)` | 3 | 3 | 3 |  |
| 49 | `yyjson_mut_equals_str(const yyjson_mut_val *, const char *)` | 5 | 3 | 3 |  |
| 50 | `yyjson_mut_obj_remove_str(yyjson_mut_val *, const char *)` | 8 | 30 | 2 |  |
| 51 | `yyjson_mut_arr_add_strcpy(yyjson_mut_doc *, yyjson_mut_val *, const char *)` | 8 | 14 | 2 |  |
| 52 | `yyjson_mut_arr_add_false(yyjson_mut_doc *, yyjson_mut_val *)` | 6 | 14 | 2 |  |
| 53 | `yyjson_mut_arr_add_bool(yyjson_mut_doc *, yyjson_mut_val *, bool)` | 6 | 14 | 2 |  |
| 54 | `yyjson_set_str_noesc(yyjson_val *, bool)` | 4 | 5 | 2 |  |
| 55 | `yyjson_mut_get_str(const yyjson_mut_val *)` | 3 | 5 | 2 |  |
| 56 | `yyjson_mut_arr_with_uint(yyjson_mut_doc *, const uint64_t *, size_t)` | 5 | 5 | 2 |  |
| 57 | `yyjson_mut_arr_with_sint(yyjson_mut_doc *, const int64_t *, size_t)` | 5 | 5 | 2 |  |
| 58 | `yyjson_set_raw(yyjson_val *, const char *, size_t)` | 4 | 4 | 2 |  |
| 59 | `yyjson_set_fp_to_fixed(yyjson_val *, int)` | 5 | 4 | 2 |  |
| 60 | `yyjson_mut_set_obj(yyjson_mut_val *)` | 4 | 4 | 2 |  |
| 61 | `yyjson_mut_set_arr(yyjson_mut_val *)` | 4 | 4 | 2 |  |
| 62 | `yyjson_mut_get_num(const yyjson_mut_val *)` | 3 | 3 | 2 |  |
| 63 | `yyjson_version(void)` | 1 | 2 | 2 |  |
| 64 | `yyjson_val_write(const yyjson_val *, yyjson_write_flag, size_t *)` | 2 | 2 | 2 |  |
| 65 | `yyjson_ptr_ctx_append(yyjson_ptr_ctx *, yyjson_mut_val *, yyjson_mut_val *)` | 2 | 2 | 2 |  |
| 66 | `yyjson_mut_obj_rotate(yyjson_mut_val *, size_t)` | 3 | 2 | 2 |  |
| 67 | `yyjson_mut_obj_replace(yyjson_mut_val *, yyjson_mut_val *, yyjson_mut_val *)` | 3 | 2 | 2 |  |
| 68 | `yyjson_mut_obj_remove_keyn(yyjson_mut_val *, const char *, size_t)` | 3 | 2 | 2 |  |
| 69 | `yyjson_mut_is_true(const yyjson_mut_val *)` | 2 | 2 | 2 |  |
| 70 | `yyjson_mut_is_false(const yyjson_mut_val *)` | 2 | 2 | 2 |  |
| 71 | `yyjson_mut_get_type(const yyjson_mut_val *)` | 2 | 2 | 2 |  |
| 72 | `yyjson_mut_get_subtype(const yyjson_mut_val *)` | 2 | 2 | 2 |  |
| 73 | `yyjson_mut_get_len(const yyjson_mut_val *)` | 2 | 2 | 2 |  |
| 74 | `yyjson_mut_equals_strn(const yyjson_mut_val *, const char *, size_t)` | 3 | 2 | 2 |  |
| 75 | `yyjson_mut_arr_get_last(const yyjson_mut_val *)` | 3 | 2 | 2 |  |
| 76 | `yyjson_mut_get_pointern(yyjson_mut_val *, const char *, size_t)` | 12 | 208 | 1 |  |
| 77 | `yyjson_mut_doc_get_pointern(yyjson_mut_doc *, const char *, size_t)` | 12 | 182 | 1 |  |
| 78 | `unsafe_yyjson_mut_get_pointer(yyjson_mut_val *, const char *, size_t)` | 9 | 180 | 1 |  |
| 79 | `yyjson_ptr_get_real(const yyjson_val *, const char *, double *)` | 17 | 151 | 1 |  |
| 80 | `yyjson_ptr_get_sint(const yyjson_val *, const char *, int64_t *)` | 16 | 150 | 1 |  |
| 81 | `yyjson_ptr_get_bool(const yyjson_val *, const char *, bool *)` | 16 | 150 | 1 |  |
| 82 | `yyjson_get_pointer(yyjson_val *, const char *)` | 14 | 148 | 1 |  |
| 83 | `yyjson_get_pointern(yyjson_val *, const char *, size_t)` | 12 | 147 | 1 |  |
| 84 | `yyjson_doc_get_pointern(yyjson_doc *, const char *, size_t)` | 12 | 147 | 1 |  |
| 85 | `unsafe_yyjson_get_pointer(yyjson_val *, const char *, size_t)` | 10 | 145 | 1 |  |
| 86 | `yyjson_mut_arr_add_strncpy(yyjson_mut_doc *, yyjson_mut_val *, const char *, size_t)` | 6 | 28 | 1 |  |
| 87 | `yyjson_mut_arr_add_strn(yyjson_mut_doc *, yyjson_mut_val *, const char *, size_t)` | 6 | 25 | 1 |  |
| 88 | `yyjson_obj_iter_get(yyjson_obj_iter *, const char *)` | 4 | 18 | 1 |  |
| 89 | `yyjson_mut_arr_add_str(yyjson_mut_doc *, yyjson_mut_val *, const char *)` | 9 | 15 | 1 |  |
| 90 | `yyjson_mut_arr_add_int(yyjson_mut_doc *, yyjson_mut_val *, int64_t)` | 6 | 14 | 1 |  |
| 91 | `yyjson_mut_obj_iter_with(yyjson_mut_val *)` | 4 | 11 | 1 |  |
| 92 | `yyjson_mut_arr_add_arr(yyjson_mut_doc *, yyjson_mut_val *)` | 4 | 11 | 1 |  |
| 93 | `yyjson_obj_iter_with(const yyjson_val *)` | 4 | 10 | 1 |  |
| 94 | `yyjson_mut_arr_add_val(yyjson_mut_val *, yyjson_mut_val *)` | 3 | 10 | 1 |  |
| 95 | `yyjson_mut_arr_add_obj(yyjson_mut_doc *, yyjson_mut_val *)` | 3 | 10 | 1 |  |
| 96 | `yyjson_set_strn(yyjson_val *, const char *, size_t)` | 4 | 6 | 1 |  |
| 97 | `yyjson_mut_obj_add_obj(yyjson_mut_doc *, yyjson_mut_val *, const char *)` | 8 | 6 | 1 |  |
| 98 | `yyjson_mut_arr_with_strncpy(yyjson_mut_doc *, const char **, const size_t *, size_t)` | 4 | 6 | 1 |  |
| 99 | `yyjson_mut_arr_with_strn(yyjson_mut_doc *, const char **, const size_t *, size_t)` | 4 | 6 | 1 |  |
| 100 | `yyjson_mut_arr_with_strcpy(yyjson_mut_doc *, const char **, size_t)` | 5 | 6 | 1 |  |
| 101 | `yyjson_set_str(yyjson_val *, const char *)` | 7 | 5 | 1 |  |
| 102 | `yyjson_mut_set_str(yyjson_mut_val *, const char *)` | 7 | 5 | 1 |  |
| 103 | `yyjson_mut_obj_add_uint(yyjson_mut_doc *, yyjson_mut_val *, const char *, uint64_t)` | 7 | 5 | 1 |  |
| 104 | `yyjson_mut_obj_add_true(yyjson_mut_doc *, yyjson_mut_val *, const char *)` | 7 | 5 | 1 |  |
| 105 | `yyjson_mut_obj_add_sint(yyjson_mut_doc *, yyjson_mut_val *, const char *, int64_t)` | 7 | 5 | 1 |  |
| 106 | `yyjson_mut_obj_add_real(yyjson_mut_doc *, yyjson_mut_val *, const char *, double)` | 7 | 5 | 1 |  |
| 107 | `yyjson_mut_obj_add_null(yyjson_mut_doc *, yyjson_mut_val *, const char *)` | 7 | 5 | 1 |  |
| 108 | `yyjson_mut_obj_add_int(yyjson_mut_doc *, yyjson_mut_val *, const char *, int64_t)` | 7 | 5 | 1 |  |
| 109 | `yyjson_mut_obj_add_float(yyjson_mut_doc *, yyjson_mut_val *, const char *, float)` | 7 | 5 | 1 |  |
| 110 | `yyjson_mut_obj_add_false(yyjson_mut_doc *, yyjson_mut_val *, const char *)` | 7 | 5 | 1 |  |
| 111 | `yyjson_mut_obj_add_double(yyjson_mut_doc *, yyjson_mut_val *, const char *, double)` | 7 | 5 | 1 |  |
| 112 | `yyjson_mut_obj_add_bool(yyjson_mut_doc *, yyjson_mut_val *, const char *, bool)` | 7 | 5 | 1 |  |
| 113 | `yyjson_mut_arr_with_str(yyjson_mut_doc *, const char **, size_t)` | 7 | 5 | 1 |  |
| 114 | `yyjson_set_uint(yyjson_val *, uint64_t)` | 4 | 4 | 1 |  |
| 115 | `yyjson_set_sint(yyjson_val *, int64_t)` | 4 | 4 | 1 |  |
| 116 | `yyjson_set_real(yyjson_val *, double)` | 4 | 4 | 1 |  |
| 117 | `yyjson_set_null(yyjson_val *)` | 4 | 4 | 1 |  |
| 118 | `yyjson_set_int(yyjson_val *, int64_t)` | 4 | 4 | 1 |  |
| 119 | `yyjson_set_fp_to_float(yyjson_val *, bool)` | 5 | 4 | 1 |  |
| 120 | `yyjson_set_float(yyjson_val *, float)` | 4 | 4 | 1 |  |
| 121 | `yyjson_set_double(yyjson_val *, double)` | 4 | 4 | 1 |  |
| 122 | `yyjson_set_bool(yyjson_val *, bool)` | 4 | 4 | 1 |  |
| 123 | `yyjson_mut_set_uint(yyjson_mut_val *, uint64_t)` | 4 | 4 | 1 |  |
| 124 | `yyjson_mut_set_sint(yyjson_mut_val *, int64_t)` | 4 | 4 | 1 |  |
| 125 | `yyjson_mut_set_real(yyjson_mut_val *, double)` | 4 | 4 | 1 |  |
| 126 | `yyjson_mut_set_raw(yyjson_mut_val *, const char *, size_t)` | 4 | 4 | 1 |  |
| 127 | `yyjson_mut_set_null(yyjson_mut_val *)` | 4 | 4 | 1 |  |
| 128 | `yyjson_mut_set_int(yyjson_mut_val *, int64_t)` | 4 | 4 | 1 |  |
| 129 | `yyjson_mut_set_fp_to_fixed(yyjson_mut_val *, int)` | 5 | 4 | 1 |  |
| 130 | `yyjson_mut_set_float(yyjson_mut_val *, float)` | 4 | 4 | 1 |  |
| 131 | `yyjson_mut_set_double(yyjson_mut_val *, double)` | 4 | 4 | 1 |  |
| 132 | `yyjson_mut_set_bool(yyjson_mut_val *, bool)` | 4 | 4 | 1 |  |
| 133 | `yyjson_mut_rawncpy(yyjson_mut_doc *, const char *, size_t)` | 4 | 4 | 1 |  |
| 134 | `yyjson_mut_rawn(yyjson_mut_doc *, const char *, size_t)` | 4 | 4 | 1 |  |
| 135 | `yyjson_mut_rawcpy(yyjson_mut_doc *, const char *)` | 5 | 4 | 1 |  |
| 136 | `yyjson_mut_raw(yyjson_mut_doc *, const char *)` | 5 | 4 | 1 |  |
| 137 | `yyjson_mut_int(yyjson_mut_doc *, int64_t)` | 4 | 4 | 1 |  |
| 138 | `yyjson_mut_arr_with_uint8(yyjson_mut_doc *, const uint8_t *, size_t)` | 4 | 4 | 1 |  |
| 139 | `yyjson_mut_arr_with_uint32(yyjson_mut_doc *, const uint32_t *, size_t)` | 4 | 4 | 1 |  |
| 140 | `yyjson_mut_arr_with_uint16(yyjson_mut_doc *, const uint16_t *, size_t)` | 4 | 4 | 1 |  |
| 141 | `yyjson_mut_arr_with_sint8(yyjson_mut_doc *, const int8_t *, size_t)` | 4 | 4 | 1 |  |
| 142 | `yyjson_mut_arr_with_sint32(yyjson_mut_doc *, const int32_t *, size_t)` | 4 | 4 | 1 |  |
| 143 | `yyjson_mut_arr_with_sint16(yyjson_mut_doc *, const int16_t *, size_t)` | 4 | 4 | 1 |  |
| 144 | `yyjson_mut_arr_with_real(yyjson_mut_doc *, const double *, size_t)` | 4 | 4 | 1 |  |
| 145 | `yyjson_mut_arr_with_float(yyjson_mut_doc *, const float *, size_t)` | 4 | 4 | 1 |  |
| 146 | `yyjson_mut_arr_with_double(yyjson_mut_doc *, const double *, size_t)` | 4 | 4 | 1 |  |
| 147 | `yyjson_mut_arr_with_bool(yyjson_mut_doc *, const bool *, size_t)` | 4 | 4 | 1 |  |
| 148 | `yyjson_arr_get_last(const yyjson_val *)` | 3 | 3 | 1 |  |
| 149 | `yyjson_arr_get(const yyjson_val *, size_t)` | 3 | 3 | 1 |  |
| 150 | `yyjson_mut_set_str_noesc(yyjson_mut_val *, bool)` | 3 | 2 | 1 |  |
| 151 | `yyjson_mut_obj_remove_key(yyjson_mut_val *, const char *)` | 4 | 2 | 1 |  |
| 152 | `yyjson_mut_obj_remove(yyjson_mut_val *, yyjson_mut_val *)` | 3 | 2 | 1 |  |
| 153 | `yyjson_mut_obj_insert(yyjson_mut_val *, yyjson_mut_val *, yyjson_mut_val *, size_t)` | 3 | 2 | 1 |  |
| 154 | `yyjson_mut_obj_add_val(yyjson_mut_doc *, yyjson_mut_val *, const char *, yyjson_mut_val *)` | 5 | 2 | 1 |  |
| 155 | `yyjson_mut_obj_add_strncpy(yyjson_mut_doc *, yyjson_mut_val *, const char *, const char *, size_t)` | 5 | 2 | 1 |  |
| 156 | `yyjson_mut_obj_add_strn(yyjson_mut_doc *, yyjson_mut_val *, const char *, const char *, size_t)` | 5 | 2 | 1 |  |
| 157 | `yyjson_mut_obj_add_strcpy(yyjson_mut_doc *, yyjson_mut_val *, const char *, const char *)` | 5 | 2 | 1 |  |
| 158 | `yyjson_mut_obj_add_str(yyjson_mut_doc *, yyjson_mut_val *, const char *, const char *)` | 5 | 2 | 1 |  |
| 159 | `yyjson_mut_is_uint(const yyjson_mut_val *)` | 2 | 2 | 1 |  |
| 160 | `yyjson_mut_is_sint(const yyjson_mut_val *)` | 2 | 2 | 1 |  |
| 161 | `yyjson_mut_is_raw(const yyjson_mut_val *)` | 2 | 2 | 1 |  |
| 162 | `yyjson_mut_is_num(const yyjson_mut_val *)` | 2 | 2 | 1 |  |
| 163 | `yyjson_mut_is_int(const yyjson_mut_val *)` | 2 | 2 | 1 |  |
| 164 | `yyjson_mut_is_bool(const yyjson_mut_val *)` | 2 | 2 | 1 |  |
| 165 | `yyjson_mut_get_tag(const yyjson_mut_val *)` | 2 | 2 | 1 |  |
| 166 | `yyjson_mut_arr_get_first(const yyjson_mut_val *)` | 3 | 2 | 1 |  |
| 167 | `yyjson_mut_arr_get(const yyjson_mut_val *, size_t)` | 3 | 2 | 1 |  |
| 168 | `yyjson_is_uint(const yyjson_val *)` | 2 | 2 | 1 |  |
| 169 | `yyjson_is_true(const yyjson_val *)` | 2 | 2 | 1 |  |
| 170 | `yyjson_is_sint(const yyjson_val *)` | 2 | 2 | 1 |  |
| 171 | `yyjson_is_false(const yyjson_val *)` | 2 | 2 | 1 |  |
| 172 | `yyjson_write(const yyjson_doc *, yyjson_write_flag, size_t *)` | 1 | 1 | 1 |  |
| 173 | `yyjson_read_max_memory_usage(size_t, yyjson_read_flag)` | 1 | 1 | 1 |  |
| 174 | `yyjson_read(const char *, size_t, yyjson_read_flag)` | 1 | 1 | 1 |  |
| 175 | `yyjson_obj_iter_next(yyjson_obj_iter *)` | 1 | 1 | 1 |  |
| 176 | `yyjson_obj_iter_has_next(yyjson_obj_iter *)` | 1 | 1 | 1 |  |
| 177 | `yyjson_obj_iter_get_val(yyjson_val *)` | 1 | 1 | 1 |  |
| 178 | `yyjson_mut_write(const yyjson_mut_doc *, yyjson_write_flag, size_t *)` | 1 | 1 | 1 |  |
| 179 | `yyjson_mut_val_write(const yyjson_mut_val *, yyjson_write_flag, size_t *)` | 1 | 1 | 1 |  |
| 180 | `yyjson_mut_obj_with_str(yyjson_mut_doc *, const char **, const char **, size_t)` | 3 | 1 | 1 |  |
| 181 | `yyjson_mut_obj_with_kv(yyjson_mut_doc *, const char **, size_t)` | 3 | 1 | 1 |  |
| 182 | `yyjson_mut_obj_iter_has_next(yyjson_mut_obj_iter *)` | 1 | 1 | 1 |  |
| 183 | `yyjson_mut_obj_iter_get_val(yyjson_mut_val *)` | 1 | 1 | 1 |  |
| 184 | `yyjson_mut_obj_clear(yyjson_mut_val *)` | 2 | 1 | 1 |  |
| 185 | `yyjson_mut_is_null(const yyjson_mut_val *)` | 1 | 1 | 1 |  |
| 186 | `yyjson_mut_is_ctn(const yyjson_mut_val *)` | 1 | 1 | 1 |  |
| 187 | `yyjson_mut_doc_get_root(yyjson_mut_doc *)` | 1 | 1 | 1 |  |
| 188 | `yyjson_mut_arr_rotate(yyjson_mut_val *, size_t)` | 2 | 1 | 1 |  |
| 189 | `yyjson_mut_arr_replace(yyjson_mut_val *, size_t, yyjson_mut_val *)` | 2 | 1 | 1 |  |
| 190 | `yyjson_mut_arr_remove_range(yyjson_mut_val *, size_t, size_t)` | 2 | 1 | 1 |  |
| 191 | `yyjson_mut_arr_remove_last(yyjson_mut_val *)` | 2 | 1 | 1 |  |
| 192 | `yyjson_mut_arr_remove_first(yyjson_mut_val *)` | 2 | 1 | 1 |  |
| 193 | `yyjson_mut_arr_remove(yyjson_mut_val *, size_t)` | 2 | 1 | 1 |  |
| 194 | `yyjson_mut_arr_prepend(yyjson_mut_val *, yyjson_mut_val *)` | 2 | 1 | 1 |  |
| 195 | `yyjson_mut_arr_iter_with(yyjson_mut_val *)` | 1 | 1 | 1 |  |
| 196 | `yyjson_mut_arr_iter_remove(yyjson_mut_arr_iter *)` | 2 | 1 | 1 |  |
| 197 | `yyjson_mut_arr_iter_has_next(yyjson_mut_arr_iter *)` | 1 | 1 | 1 |  |
| 198 | `yyjson_mut_arr_insert(yyjson_mut_val *, yyjson_mut_val *, size_t)` | 2 | 1 | 1 |  |
| 199 | `yyjson_mut_arr_clear(yyjson_mut_val *)` | 2 | 1 | 1 |  |
| 200 | `yyjson_is_null(const yyjson_val *)` | 1 | 1 | 1 |  |
| 201 | `yyjson_is_ctn(const yyjson_val *)` | 1 | 1 | 1 |  |
| 202 | `yyjson_doc_get_val_count(const yyjson_doc *)` | 1 | 1 | 1 |  |
| 203 | `yyjson_doc_get_read_size(const yyjson_doc *)` | 1 | 1 | 1 |  |
| 204 | `yyjson_arr_size(const yyjson_val *)` | 1 | 1 | 1 |  |
| 205 | `yyjson_arr_iter_with(const yyjson_val *)` | 1 | 1 | 1 |  |
| 206 | `yyjson_arr_iter_has_next(yyjson_arr_iter *)` | 1 | 1 | 1 |  |
| 207 | `yyjson_arr_get_first(const yyjson_val *)` | 2 | 1 | 1 |  |
| 208 | `unsafe_yyjson_set_type(void *, yyjson_type, yyjson_subtype)` | 1 | 1 | 1 |  |
| 209 | `yyjson_mut_ptr_setn(yyjson_mut_val *, const char *, size_t, yyjson_mut_val *, yyjson_mut_doc *)` | 24 | 480 | 0 |  |
| 210 | `yyjson_mut_doc_ptr_setn(yyjson_mut_doc *, const char *, size_t, yyjson_mut_val *)` | 24 | 480 | 0 |  |
| 211 | `yyjson_mut_ptr_setx(yyjson_mut_val *, const char *, size_t, yyjson_mut_val *, yyjson_mut_doc *, bool, yyjson_ptr_ctx *, yyjson_ptr_err *)` | 23 | 479 | 0 |  |
| 212 | `yyjson_mut_doc_ptr_setx(yyjson_mut_doc *, const char *, size_t, yyjson_mut_val *, bool, yyjson_ptr_ctx *, yyjson_ptr_err *)` | 23 | 479 | 0 |  |
| 213 | `yyjson_mut_ptr_addn(yyjson_mut_val *, const char *, size_t, yyjson_mut_val *, yyjson_mut_doc *)` | 21 | 443 | 0 |  |
| 214 | `yyjson_mut_doc_ptr_addn(yyjson_mut_doc *, const char *, size_t, yyjson_mut_val *)` | 21 | 410 | 0 |  |
| 215 | `yyjson_mut_doc_ptr_addx(yyjson_mut_doc *, const char *, size_t, yyjson_mut_val *, bool, yyjson_ptr_ctx *, yyjson_ptr_err *)` | 20 | 409 | 0 |  |
| 216 | `yyjson_mut_ptr_replacen(yyjson_mut_val *, const char *, size_t, yyjson_mut_val *)` | 17 | 286 | 0 |  |
| 217 | `yyjson_mut_ptr_removen(yyjson_mut_val *, const char *, size_t)` | 17 | 282 | 0 |  |
| 218 | `yyjson_mut_doc_ptr_replacen(yyjson_mut_doc *, const char *, size_t, yyjson_mut_val *)` | 17 | 255 | 0 |  |
| 219 | `yyjson_mut_doc_ptr_replacex(yyjson_mut_doc *, const char *, size_t, yyjson_mut_val *, yyjson_ptr_ctx *, yyjson_ptr_err *)` | 16 | 254 | 0 |  |
| 220 | `yyjson_mut_doc_ptr_removen(yyjson_mut_doc *, const char *, size_t)` | 17 | 253 | 0 |  |
| 221 | `yyjson_mut_doc_ptr_removex(yyjson_mut_doc *, const char *, size_t, yyjson_ptr_ctx *, yyjson_ptr_err *)` | 16 | 252 | 0 |  |
| 222 | `yyjson_write_number(const yyjson_val *, char *)` | 15 | 221 | 0 |  |
| 223 | `yyjson_mut_ptr_get(const yyjson_mut_val *, const char *)` | 13 | 208 | 0 |  |
| 224 | `yyjson_mut_ptr_getn(const yyjson_mut_val *, const char *, size_t)` | 11 | 207 | 0 |  |
| 225 | `yyjson_mut_doc_ptr_get(const yyjson_mut_doc *, const char *)` | 13 | 182 | 0 |  |
| 226 | `yyjson_mut_doc_ptr_getn(const yyjson_mut_doc *, const char *, size_t)` | 11 | 181 | 0 |  |
| 227 | `yyjson_mut_doc_ptr_getx(const yyjson_mut_doc *, const char *, size_t, yyjson_ptr_ctx *, yyjson_ptr_err *)` | 10 | 180 | 0 |  |
| 228 | `yyjson_ptr_get(const yyjson_val *, const char *)` | 13 | 147 | 0 |  |
| 229 | `yyjson_doc_ptr_get(const yyjson_doc *, const char *)` | 13 | 147 | 0 |  |
| 230 | `yyjson_ptr_getn(const yyjson_val *, const char *, size_t)` | 11 | 146 | 0 |  |
| 231 | `yyjson_doc_ptr_getn(const yyjson_doc *, const char *, size_t)` | 11 | 146 | 0 |  |
| 232 | `yyjson_ptr_getx(const yyjson_val *, const char *, size_t, yyjson_ptr_err *)` | 10 | 145 | 0 |  |
| 233 | `yyjson_doc_ptr_getx(const yyjson_doc *, const char *, size_t, yyjson_ptr_err *)` | 10 | 145 | 0 |  |
| 234 | `unsafe_yyjson_ptr_getx(const yyjson_val *, const char *, size_t, yyjson_ptr_err *)` | 9 | 144 | 0 |  |
| 235 | `unsafe_yyjson_equals(const yyjson_val *, const yyjson_val *)` | 8 | 98 | 0 |  |
| 236 | `yyjson_mut_val_imut_copy(const yyjson_mut_val *, const yyjson_alc *)` | 5 | 77 | 0 |  |
| 237 | `yyjson_read_number(const char *, yyjson_val *, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)` | 2 | 30 | 0 |  |
| 238 | `yyjson_mut_obj_remove_strn(yyjson_mut_val *, const char *, size_t)` | 6 | 29 | 0 |  |
| 239 | `yyjson_mut_obj_rename_keyn(yyjson_mut_doc *, yyjson_mut_val *, const char *, size_t, const char *, size_t)` | 8 | 23 | 0 |  |
| 240 | `yyjson_obj_iter_getn(yyjson_obj_iter *, const char *, size_t)` | 2 | 17 | 0 |  |
| 241 | `yyjson_val_write_buf(char *, size_t, const yyjson_val *, yyjson_write_flag, yyjson_write_err *)` | 2 | 11 | 0 |  |
| 242 | `yyjson_mut_val_write_buf(char *, size_t, const yyjson_mut_val *, yyjson_write_flag, yyjson_write_err *)` | 2 | 11 | 0 |  |
| 243 | `yyjson_obj_iter_init(const yyjson_val *, yyjson_obj_iter *)` | 3 | 9 | 0 |  |
| 244 | `yyjson_mut_set_strn(yyjson_mut_val *, const char *, size_t)` | 4 | 6 | 0 |  |
| 245 | `yyjson_mut_str(yyjson_mut_doc *, const char *)` | 7 | 5 | 0 |  |
| 246 | `yyjson_mut_uint(yyjson_mut_doc *, uint64_t)` | 4 | 4 | 0 |  |
| 247 | `yyjson_mut_true(yyjson_mut_doc *)` | 4 | 4 | 0 |  |
| 248 | `yyjson_mut_strcpy(yyjson_mut_doc *, const char *)` | 6 | 4 | 0 |  |
| 249 | `yyjson_mut_sint(yyjson_mut_doc *, int64_t)` | 4 | 4 | 0 |  |
| 250 | `yyjson_mut_real(yyjson_mut_doc *, double)` | 4 | 4 | 0 |  |
| 251 | `yyjson_mut_null(yyjson_mut_doc *)` | 4 | 4 | 0 |  |
| 252 | `yyjson_mut_float(yyjson_mut_doc *, float)` | 4 | 4 | 0 |  |
| 253 | `yyjson_mut_false(yyjson_mut_doc *)` | 4 | 4 | 0 |  |
| 254 | `yyjson_mut_double(yyjson_mut_doc *, double)` | 4 | 4 | 0 |  |
| 255 | `yyjson_mut_bool(yyjson_mut_doc *, bool)` | 4 | 4 | 0 |  |
| 256 | `yyjson_mut_arr_with_uint64(yyjson_mut_doc *, const uint64_t *, size_t)` | 4 | 4 | 0 |  |
| 257 | `yyjson_mut_arr_with_sint64(yyjson_mut_doc *, const int64_t *, size_t)` | 4 | 4 | 0 |  |
| 258 | `yyjson_get_uint(const yyjson_val *)` | 4 | 4 | 0 |  |
| 259 | `yyjson_get_str(const yyjson_val *)` | 2 | 4 | 0 |  |
| 260 | `yyjson_get_sint(const yyjson_val *)` | 4 | 4 | 0 |  |
| 261 | `yyjson_get_real(const yyjson_val *)` | 4 | 4 | 0 |  |
| 262 | `yyjson_get_raw(const yyjson_val *)` | 4 | 4 | 0 |  |
| 263 | `yyjson_get_int(const yyjson_val *)` | 4 | 4 | 0 |  |
| 264 | `unsafe_yyjson_set_str(void *, const char *)` | 5 | 4 | 0 |  |
| 265 | `yyjson_get_bool(const yyjson_val *)` | 3 | 3 | 0 |  |
| 266 | `unsafe_yyjson_set_uint(void *, uint64_t)` | 2 | 3 | 0 |  |
| 267 | `unsafe_yyjson_set_sint(void *, int64_t)` | 2 | 3 | 0 |  |
| 268 | `unsafe_yyjson_set_real(void *, double)` | 2 | 3 | 0 |  |
| 269 | `unsafe_yyjson_set_raw(void *, const char *, size_t)` | 2 | 3 | 0 |  |
| 270 | `unsafe_yyjson_set_obj(void *, size_t)` | 2 | 3 | 0 |  |
| 271 | `unsafe_yyjson_set_null(void *)` | 2 | 3 | 0 |  |
| 272 | `unsafe_yyjson_set_float(void *, float)` | 2 | 3 | 0 |  |
| 273 | `unsafe_yyjson_set_double(void *, double)` | 2 | 3 | 0 |  |
| 274 | `unsafe_yyjson_set_bool(void *, bool)` | 2 | 3 | 0 |  |
| 275 | `unsafe_yyjson_set_arr(void *, size_t)` | 2 | 3 | 0 |  |
| 276 | `yyjson_mut_is_real(const yyjson_mut_val *)` | 2 | 2 | 0 |  |
| 277 | `yyjson_is_real(const yyjson_val *)` | 2 | 2 | 0 |  |
| 278 | `yyjson_is_raw(const yyjson_val *)` | 2 | 2 | 0 |  |
| 279 | `yyjson_is_num(const yyjson_val *)` | 2 | 2 | 0 |  |
| 280 | `yyjson_is_int(const yyjson_val *)` | 2 | 2 | 0 |  |
| 281 | `yyjson_is_bool(const yyjson_val *)` | 2 | 2 | 0 |  |
| 282 | `yyjson_get_type_desc(const yyjson_val *)` | 2 | 2 | 0 |  |
| 283 | `yyjson_get_num(const yyjson_val *)` | 2 | 2 | 0 |  |
| 284 | `yyjson_equals_str(const yyjson_val *, const char *)` | 4 | 2 | 0 |  |
| 285 | `unsafe_yyjson_arr_is_flat(const yyjson_val *)` | 1 | 2 | 0 |  |
| 286 | `yyjson_val_write_opts(const yyjson_val *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)` | 1 | 1 | 0 |  |
| 287 | `yyjson_mut_arr_size(const yyjson_mut_val *)` | 1 | 1 | 0 |  |
| 288 | `yyjson_mut_arr(yyjson_mut_doc *)` | 2 | 1 | 0 |  |
| 289 | `yyjson_get_type(const yyjson_val *)` | 1 | 1 | 0 |  |
| 290 | `yyjson_get_tag(const yyjson_val *)` | 1 | 1 | 0 |  |
| 291 | `yyjson_get_subtype(const yyjson_val *)` | 1 | 1 | 0 |  |
| 292 | `yyjson_get_len(const yyjson_val *)` | 1 | 1 | 0 |  |
| 293 | `yyjson_equals_strn(const yyjson_val *, const char *, size_t)` | 2 | 1 | 0 |  |
| 294 | `unsafe_yyjson_set_str_noesc(void *, bool)` | 1 | 1 | 0 |  |
| 295 | `unsafe_yyjson_set_fp_to_float(void *, bool)` | 1 | 1 | 0 |  |
| 296 | `unsafe_yyjson_set_fp_to_fixed(void *, int)` | 1 | 1 | 0 |  |
| 297 | `unsafe_yyjson_mut_obj_rotate(yyjson_mut_val *, size_t)` | 1 | 1 | 0 |  |
| 298 | `unsafe_yyjson_mut_obj_replace(yyjson_mut_val *, yyjson_mut_val *, yyjson_mut_val *)` | 1 | 1 | 0 |  |
| 299 | `unsafe_yyjson_mut_obj_remove(yyjson_mut_val *, const char *, size_t)` | 1 | 1 | 0 |  |
| 300 | `unsafe_yyjson_is_uint(const void *)` | 1 | 1 | 0 |  |
| 301 | `unsafe_yyjson_is_true(const void *)` | 1 | 1 | 0 |  |
| 302 | `unsafe_yyjson_is_str_noesc(const char *, size_t)` | 2 | 1 | 0 |  |
| 303 | `unsafe_yyjson_is_sint(const void *)` | 1 | 1 | 0 |  |
| 304 | `unsafe_yyjson_is_real(const void *)` | 1 | 1 | 0 |  |
| 305 | `unsafe_yyjson_is_raw(const void *)` | 1 | 1 | 0 |  |
| 306 | `unsafe_yyjson_is_num(const void *)` | 1 | 1 | 0 |  |
| 307 | `unsafe_yyjson_is_int(const void *)` | 1 | 1 | 0 |  |
| 308 | `unsafe_yyjson_is_false(const void *)` | 1 | 1 | 0 |  |
| 309 | `unsafe_yyjson_is_bool(const void *)` | 1 | 1 | 0 |  |
| 310 | `unsafe_yyjson_inc_len(void *)` | 1 | 1 | 0 |  |
| 311 | `unsafe_yyjson_get_uint(const void *)` | 1 | 1 | 0 |  |
| 312 | `unsafe_yyjson_get_sint(const void *)` | 1 | 1 | 0 |  |
| 313 | `unsafe_yyjson_get_real(const void *)` | 1 | 1 | 0 |  |
| 314 | `unsafe_yyjson_get_raw(const void *)` | 1 | 1 | 0 |  |
| 315 | `unsafe_yyjson_get_num(const void *)` | 1 | 1 | 0 |  |
| 316 | `unsafe_yyjson_get_int(const void *)` | 1 | 1 | 0 |  |
| 317 | `unsafe_yyjson_equals_str(const void *, const char *)` | 2 | 1 | 0 |  |
| 318 | `yyjson_read_file(const char *, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)` | 13 | 98 | 0 | 파일 입출력 |
| 319 | `yyjson_read_fp(FILE *, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)` | 8 | 82 | 0 | 파일 입출력 |
| 320 | `yyjson_mut_write_file(const char *, const yyjson_mut_doc *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 9 | 45 | 0 | 파일 입출력 |
| 321 | `yyjson_write_file(const char *, const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 9 | 45 | 0 | 파일 입출력 |
| 322 | `yyjson_mut_val_write_file(const char *, const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 8 | 42 | 0 | 파일 입출력 |
| 323 | `yyjson_val_write_file(const char *, const yyjson_val *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 8 | 42 | 0 | 파일 입출력 |
| 324 | `yyjson_mut_write_fp(FILE *, const yyjson_mut_doc *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 5 | 22 | 0 | 파일 입출력 |
| 325 | `yyjson_write_fp(FILE *, const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 5 | 22 | 0 | 파일 입출력 |
| 326 | `yyjson_mut_val_write_fp(FILE *, const yyjson_mut_val *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 4 | 19 | 0 | 파일 입출력 |
| 327 | `yyjson_val_write_fp(FILE *, const yyjson_val *, yyjson_write_flag, const yyjson_alc *, yyjson_write_err *)` | 4 | 19 | 0 | 파일 입출력 |
