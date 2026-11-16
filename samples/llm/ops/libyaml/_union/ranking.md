# 호출 안 함 API 우선순위 — libyaml/_union

'호출 안 함' API 13개. 추가 가능 11개, 제외 2개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `yaml_emitter_set_indent(yaml_emitter_t *, int)` | 2 | 7 | 7 | 이번에 추가 |
| 2 | `yaml_emitter_set_width(yaml_emitter_t *, int)` | 2 | 5 | 5 | 이번에 추가 |
| 3 | `yaml_parser_set_input(yaml_parser_t *, yaml_read_handler_t *, void *)` | 2 | 4 | 4 | 이번에 추가 |
| 4 | `yaml_emitter_set_output_string(yaml_emitter_t *, unsigned char *, size_t, size_t *)` | 2 | 4 | 4 | 이번에 추가 |
| 5 | `yaml_parser_set_encoding(yaml_parser_t *, yaml_encoding_t)` | 2 | 3 | 3 | 이번에 추가 |
| 6 | `yaml_emitter_set_encoding(yaml_emitter_t *, yaml_encoding_t)` | 2 | 3 | 3 | 이번에 추가 |
| 7 | `yaml_emitter_set_break(yaml_emitter_t *, yaml_break_t)` | 2 | 2 | 2 | 이번에 추가 |
| 8 | `yaml_set_max_nest_level(int)` | 1 | 1 | 1 | 이번에 추가 |
| 9 | `yaml_get_version_string(void)` | 1 | 1 | 1 | 이번에 추가 |
| 10 | `yaml_get_version(int *, int *, int *)` | 1 | 1 | 1 | 이번에 추가 |
| 11 | `yaml_get_max_nest_level()` | 1 | 1 | 1 |  |
| 12 | `yaml_emitter_set_output_file(yaml_emitter_t *, FILE *)` | 2 | 4 | 0 | 파일 입출력 |
| 13 | `yaml_parser_set_input_file(yaml_parser_t *, FILE *)` | 2 | 4 | 0 | 파일 입출력 |
