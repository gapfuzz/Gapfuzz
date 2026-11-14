// OSS-Fuzz 하네스: http-parser 저장소 fuzzers/fuzz_url.c (보관된 저장소의 마지막 커밋, 커밋 ec8b5ee) 그대로.
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "http_parser.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
  struct http_parser_url u;
  http_parser_url_init(&u);
  http_parser_parse_url((char*)data, size, 0, &u);
  http_parser_parse_url((char*)data, size, 1, &u);

  return 0;
}
