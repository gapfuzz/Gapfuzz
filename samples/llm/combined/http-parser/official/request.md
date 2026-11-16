라이브러리: http-parser
하네스 파일: official.c

아래 제안 2개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)`의 1번째 인자 `parser`를 하네스가 고정합니다(24행에서 항상 같은 객체 `&parser`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (57개)
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 633행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
  629        }
  630  
  631        break;
  632  
  633>     default:
  634        break;
  635    }
  636  
  637    /* We should never fall out of the switch above unless there's an error */
```
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 667행, 조건 `case s_body_identity_eof`가 퍼징 중 한 번도 '참'이 되지 않음
```
  663    }
  664  
  665    if (len == 0) {
  666      switch (CURRENT_STATE()) {
  667>       case s_body_identity_eof:
  668          /* Use of CALLBACK_NOTIFY() here would erroneously return 1 byte read if
  669           * we got paused.
  670           */
  671          CALLBACK_NOTIFY_NOADVANCE(message_complete);
```
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 674행, 조건 `case s_dead`가 퍼징 중 한 번도 '참'이 되지 않음
```
  670           */
  671          CALLBACK_NOTIFY_NOADVANCE(message_complete);
  672          return 0;
  673  
  674>       case s_dead:
  675        case s_start_req_or_res:
  676        case s_start_res:
  677        case s_start_req:
  678          return 0;
```
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 675행, 조건 `case s_start_req_or_res`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
  671          CALLBACK_NOTIFY_NOADVANCE(message_complete);
  672          return 0;
  673  
  674        case s_dead:
  675>       case s_start_req_or_res:
  676        case s_start_res:
  677        case s_start_req:
  678          return 0;
  679  
```
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 676행, 조건 `case s_start_res`가 퍼징 중 한 번도 '참'이 되지 않음
```
  672          return 0;
  673  
  674        case s_dead:
  675        case s_start_req_or_res:
  676>       case s_start_res:
  677        case s_start_req:
  678          return 0;
  679  
  680        default:
```
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 677행, 조건 `case s_start_req`가 퍼징 중 한 번도 '참'이 되지 않음
```
  673  
  674        case s_dead:
  675        case s_start_req_or_res:
  676        case s_start_res:
  677>       case s_start_req:
  678          return 0;
  679  
  680        default:
  681          SET_ERRNO(HPE_INVALID_EOF_STATE);
```
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 680행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
  676        case s_start_res:
  677        case s_start_req:
  678          return 0;
  679  
  680>       default:
  681          SET_ERRNO(HPE_INVALID_EOF_STATE);
  682          return 1;
  683      }
  684    }
```
- `http_parser_execute(http_parser *, const http_parser_settings *, const char *, size_t)` 687행, 조건 `CURRENT_STATE() == s_header_field`가 퍼징 중 한 번도 '참'이 되지 않음
```
  683      }
  684    }
  685  
  686  
  687>   if (CURRENT_STATE() == s_header_field)
  688      header_field_mark = data;
  689    if (CURRENT_STATE() == s_header_value)
  690      header_value_mark = data;
  691    switch (CURRENT_STATE()) {
```

## 제안 2
`http_parser_init(http_parser *, enum http_parser_type)`의 2번째 인자 `type`를 하네스가 고정합니다(23행에서 항상 `HTTP_BOTH`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `http_parser_init(http_parser *, enum http_parser_type)` 2231행, 조건 `t == HTTP_REQUEST`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2227    void *data = parser->data; /* preserve application data */
 2228    memset(parser, 0, sizeof(*parser));
 2229    parser->data = data;
 2230    parser->type = t;
 2231>   parser->state = (t == HTTP_REQUEST ? s_start_req : (t == HTTP_RESPONSE ? s_start_res : s_start_req_or_res));
 2232    parser->http_errno = HPE_OK;
 2233  }
 2234  
 2235  void
```
- `http_parser_init(http_parser *, enum http_parser_type)` 2231행, 조건 `t == HTTP_RESPONSE`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2227    void *data = parser->data; /* preserve application data */
 2228    memset(parser, 0, sizeof(*parser));
 2229    parser->data = data;
 2230    parser->type = t;
 2231>   parser->state = (t == HTTP_REQUEST ? s_start_req : (t == HTTP_RESPONSE ? s_start_res : s_start_req_or_res));
 2232    parser->http_errno = HPE_OK;
 2233  }
 2234  
 2235  void
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: http-parser 저장소 fuzzers/fuzz_parser.c (보관된 저장소의 마지막 커밋, 커밋 ec8b5ee) 그대로.
   2  #include <stdint.h>
   3  #include <stdlib.h>
   4  #include <string.h>
   5  #include "http_parser.h"
   6  
   7  int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
   8  {
   9    static const http_parser_settings settings_null = {
  10      .on_message_begin = 0
  11      , .on_header_field = 0
  12      ,.on_header_value = 0
  13      ,.on_url = 0
  14      ,.on_status = 0
  15      ,.on_body = 0
  16      ,.on_headers_complete = 0
  17      ,.on_message_complete = 0
  18      ,.on_chunk_header = 0
  19      ,.on_chunk_complete = 0
  20    };
  21  
  22    http_parser parser;
  23    http_parser_init(&parser, HTTP_BOTH);
  24    http_parser_execute(&parser, &settings_null, (char*)data, size);
  25  
  26    return 0;
  27  }
```