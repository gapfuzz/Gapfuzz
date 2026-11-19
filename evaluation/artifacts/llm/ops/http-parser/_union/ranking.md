# 호출 안 함 API 우선순위 — http-parser/_union

'호출 안 함' API 10개. 추가 가능 10개, 제외 0개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `http_status_str(enum http_status)` | 1 | 297 | 297 | 이번에 추가 |
| 2 | `http_parser_pause(http_parser *, int)` | 2 | 14 | 14 | 이번에 추가 |
| 3 | `http_should_keep_alive(const http_parser *)` | 1 | 11 | 11 | 이번에 추가 |
| 4 | `http_method_str(enum http_method)` | 1 | 6 | 6 | 이번에 추가 |
| 5 | `http_parser_version(void)` | 1 | 4 | 4 | 이번에 추가 |
| 6 | `http_errno_name(enum http_errno)` | 2 | 2 | 2 | 이번에 추가 |
| 7 | `http_errno_description(enum http_errno)` | 2 | 2 | 2 | 이번에 추가 |
| 8 | `http_parser_settings_init(http_parser_settings *)` | 2 | 1 | 1 | 이번에 추가 |
| 9 | `http_parser_set_max_header_size(uint32_t)` | 1 | 1 | 1 | 이번에 추가 |
| 10 | `http_body_is_final(const http_parser *)` | 1 | 1 | 1 | 이번에 추가 |
