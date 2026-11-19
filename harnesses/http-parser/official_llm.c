// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2를 OSS-Fuzz 하네스 official에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/http-parser/official/).
// OSS-Fuzz 하네스: http-parser 저장소 fuzzers/fuzz_parser.c (보관된 저장소의 마지막 커밋, 커밋 ec8b5ee) 그대로.
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "http_parser.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
  static const http_parser_settings settings_null = {
    .on_message_begin = 0
    , .on_header_field = 0
    ,.on_header_value = 0
    ,.on_url = 0
    ,.on_status = 0
    ,.on_body = 0
    ,.on_headers_complete = 0
    ,.on_message_complete = 0
    ,.on_chunk_header = 0
    ,.on_chunk_complete = 0
  };

  // 앞 4바이트를 하네스 설정용으로 소비(서로 겹치지 않게 순서대로 배분)하고 나머지를 파서 입력으로 사용
  uint8_t type_sel = 0, split_a = 0, split_b = 0, opt_sel = 0;
  if (size >= 4) {
    type_sel = data[0];
    split_a = data[1];
    split_b = data[2];
    opt_sel = data[3];
    data += 4;
    size -= 4;
  }

  http_parser parser;
  enum http_parser_type type = (enum http_parser_type)(type_sel % 3); // HTTP_REQUEST/RESPONSE/HTTP_BOTH 모두 나오도록 입력에서 선택
  http_parser_init(&parser, type);
  parser.lenient_http_headers = (opt_sel >> 1) & 1; // init이 0으로 초기화하므로 이후 입력으로 lenient 모드 선택(!lenient 분기 도달)

  if ((opt_sel & 1) == 0 && split_a % 4 == 0) { // 일부 입력은 원래처럼 한 번에 실행
    http_parser_execute(&parser, &settings_null, (char*)data, size);
  } else {
    // 입력을 세 조각으로 나눠 이어서 실행: 헤더/청크/본문 중간 상태에서 다음 호출이 시작되게 함
    size_t p1 = ((size_t)split_a * size) / 256;
    size_t p2 = p1 + ((size_t)split_b * (size - p1)) / 256;
    http_parser_execute(&parser, &settings_null, (char*)data, p1); // 파서 상태를 다양하게 만들기 위해 앞부분만 먼저 실행
    http_parser_execute(&parser, &settings_null, (char*)data + p1, p2 - p1); // 중간 조각을 이어서 실행
    http_parser_execute(&parser, &settings_null, (char*)data + p2, size - p2); // 나머지 조각 실행
    if (opt_sel & 4) {
      http_parser_execute(&parser, &settings_null, (char*)data + size, 0); // 길이 0 호출로 EOF 상태 분기(body_identity_eof, dead 등) 도달
    }
  }

  return 0;
}
