라이브러리: libyaml
OSS-Fuzz 하네스 9개(official, official_deconstructor_alt, official_deconstructor, official_dumper, official_emitter, official_loader, official_reformatter_alt, official_reformatter, official_scanner)의 커버리지를 모두 합쳐도, 공개 API 50개 중 13개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `yaml_emitter_set_indent(yaml_emitter_t *, int)` — 새로 실행될 수 있는 코드 영역 7개
```
yaml_emitter_set_indent(yaml_emitter_t *emitter, int indent);
/**
 * Set the preferred line width. @c -1 means unlimited.
 *
 * @param[in,out]   emitter     An emitter object.
 * @param[in]       width       The preferred line width.
 */
```

### 2. `yaml_emitter_set_width(yaml_emitter_t *, int)` — 새로 실행될 수 있는 코드 영역 5개
```
yaml_emitter_set_width(yaml_emitter_t *emitter, int width);
/**
 * Set if unescaped non-ASCII characters are allowed.
 *
 * @param[in,out]   emitter     An emitter object.
 * @param[in]       unicode     If unescaped Unicode characters are allowed.
 */
```

### 3. `yaml_parser_set_input(yaml_parser_t *, yaml_read_handler_t *, void *)` — 새로 실행될 수 있는 코드 영역 4개
```
yaml_parser_set_input(yaml_parser_t *parser,
        yaml_read_handler_t *handler, void *data);
/**
 * Set the source encoding.
 *
 * @param[in,out]   parser      A parser object.
 * @param[in]       encoding    The source encoding.
 */
```

### 4. `yaml_emitter_set_output_string(yaml_emitter_t *, unsigned char *, size_t, size_t *)` — 새로 실행될 수 있는 코드 영역 4개
```
yaml_emitter_set_output_string(yaml_emitter_t *emitter,
        unsigned char *output, size_t size, size_t *size_written);
/**
 * Set a file output.
 *
 * @a file should be a file object open for writing.  The application is
 * responsible for closing the @a file.
 *
 * @param[in,out]   emitter     An emitter object.
 * @param[in]       file        An open file.
 */
```

### 5. `yaml_parser_set_encoding(yaml_parser_t *, yaml_encoding_t)` — 새로 실행될 수 있는 코드 영역 3개
```
yaml_parser_set_encoding(yaml_parser_t *parser, yaml_encoding_t encoding);
/**
 * Scan the input stream and produce the next token.
 *
 * Call the function subsequently to produce a sequence of tokens corresponding
 * to the input stream.  The initial token has the type
 * @c YAML_STREAM_START_TOKEN while the ending token has the type
 * @c YAML_STREAM_END_TOKEN.
 *
 * An application is responsible for freeing any buffers associated with the
 * produced token object using the @c yaml_token_delete function.
 *
 * An application must not alternate the calls of yaml_parser_scan() with the
 * calls of yaml_parser_parse() or yaml_parser_load(). Doing this will break
 * the parser.
 *
 * @param[in,out]   parser      A parser object.
 * @param[out]      token       An empty token object.
 *
 * @returns @c 1 if the function succeeded, @c 0 on error.
 */
```

### 6. `yaml_emitter_set_encoding(yaml_emitter_t *, yaml_encoding_t)` — 새로 실행될 수 있는 코드 영역 3개
```
yaml_emitter_set_encoding(yaml_emitter_t *emitter, yaml_encoding_t encoding);
/**
 * Set if the output should be in the "canonical" format as in the YAML
 * specification.
 *
 * @param[in,out]   emitter     An emitter object.
 * @param[in]       canonical   If the output is canonical.
 */
```

### 7. `yaml_emitter_set_break(yaml_emitter_t *, yaml_break_t)` — 새로 실행될 수 있는 코드 영역 2개
```
yaml_emitter_set_break(yaml_emitter_t *emitter, yaml_break_t line_break);
/**
 * Emit an event.
 *
 * The event object may be generated using the yaml_parser_parse() function.
 * The emitter takes the responsibility for the event object and destroys its
 * content after it is emitted. The event object is destroyed even if the
 * function fails.
 *
 * @param[in,out]   emitter     An emitter object.
 * @param[in,out]   event       An event object.
 *
 * @returns @c 1 if the function succeeded, @c 0 on error.
 */
```

### 8. `yaml_set_max_nest_level(int)` — 새로 실행될 수 있는 코드 영역 1개
```
yaml_set_max_nest_level(int max);
/** @} */
```

### 9. `yaml_get_version_string(void)` — 새로 실행될 수 있는 코드 영역 1개
```
yaml_get_version_string(void);
/**
 * Get the library version numbers.
 *
 * @param[out]      major   Major version number.
 * @param[out]      minor   Minor version number.
 * @param[out]      patch   Patch version number.
 */
```

### 10. `yaml_get_version(int *, int *, int *)` — 새로 실행될 수 있는 코드 영역 1개
```
yaml_get_version(int *major, int *minor, int *patch);
/** @} */
```

## 참고: 기존 하네스 official.c (고치지 마세요. include와 작성 방식만 참고)
```
// Copyright 2020 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "yaml.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef NDEBUG
#undef NDEBUG
#endif

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  yaml_parser_t parser;
  yaml_event_t event;
  bool done = false;

  if(!yaml_parser_initialize(&parser))
    return 0;

  yaml_parser_set_input_string(&parser, data, size);

  while (!done)
  {
      if (!yaml_parser_parse(&parser, &event)) break;

      done = (event.type == YAML_STREAM_END_EVENT);

      yaml_event_delete(&event);
  }

  yaml_parser_delete(&parser);

  return 0;
}

```