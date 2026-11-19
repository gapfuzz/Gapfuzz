라이브러리: http-parser
OSS-Fuzz 하네스 2개(official, official_url)의 커버리지를 모두 합쳐도, 공개 API 14개 중 10개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `http_status_str(enum http_status)` — 새로 실행될 수 있는 코드 영역 297개
```
/* Returns a string version of the HTTP status code. */
const char *http_status_str(enum http_status s);
/* Return a string name of the given error */
```

### 2. `http_parser_pause(http_parser *, int)` — 새로 실행될 수 있는 코드 영역 14개
```
/* Pause or un-pause the parser; a nonzero value pauses */
void http_parser_pause(http_parser *parser, int paused);
/* Checks if this is the final chunk of the body. */
```

### 3. `http_should_keep_alive(const http_parser *)` — 새로 실행될 수 있는 코드 영역 11개
```
/* If http_should_keep_alive() in the on_headers_complete or
 * on_message_complete callback returns 0, then this should be
 * the last message on the connection.
 * If you are the server, respond with the "Connection: close" header.
 * If you are the client, close the connection.
 */
int http_should_keep_alive(const http_parser *parser);
/* Returns a string version of the HTTP method. */
```

### 4. `http_method_str(enum http_method)` — 새로 실행될 수 있는 코드 영역 6개
```
/* Returns a string version of the HTTP method. */
const char *http_method_str(enum http_method m);
/* Returns a string version of the HTTP status code. */
```

### 5. `http_parser_version(void)` — 새로 실행될 수 있는 코드 영역 4개
```
/* Returns the library version. Bits 16-23 contain the major version number,
 * bits 8-15 the minor version number and bits 0-7 the patch level.
 * Usage example:
 *
 *   unsigned long version = http_parser_version();
 *   unsigned major = (version >> 16) & 255;
 *   unsigned minor = (version >> 8) & 255;
 *   unsigned patch = version & 255;
 *   printf("http_parser v%u.%u.%u\n", major, minor, patch);
 */
unsigned long http_parser_version(void);
```

### 6. `http_errno_name(enum http_errno)` — 새로 실행될 수 있는 코드 영역 2개
```
/* Return a string name of the given error */
const char *http_errno_name(enum http_errno err);
/* Return a string description of the given error */
```

### 7. `http_errno_description(enum http_errno)` — 새로 실행될 수 있는 코드 영역 2개
```
/* Return a string description of the given error */
const char *http_errno_description(enum http_errno err);
/* Initialize all http_parser_url members to 0 */
```

### 8. `http_parser_settings_init(http_parser_settings *)` — 새로 실행될 수 있는 코드 영역 1개
```
/* Initialize http_parser_settings members to 0
 */
void http_parser_settings_init(http_parser_settings *settings);
/* Executes the parser. Returns number of parsed bytes. Sets
 * `parser->http_errno` on error. */
```

### 9. `http_parser_set_max_header_size(uint32_t)` — 새로 실행될 수 있는 코드 영역 1개
```
/* Change the maximum header size provided at compile time. */
void http_parser_set_max_header_size(uint32_t size);
```

### 10. `http_body_is_final(const http_parser *)` — 새로 실행될 수 있는 코드 영역 1개
```
/* Checks if this is the final chunk of the body. */
int http_body_is_final(const http_parser *parser);
/* Change the maximum header size provided at compile time. */
```

## 참고: 기존 하네스 official.c (고치지 마세요. include와 작성 방식만 참고)
```
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

  http_parser parser;
  http_parser_init(&parser, HTTP_BOTH);
  http_parser_execute(&parser, &settings_null, (char*)data, size);

  return 0;
}

```