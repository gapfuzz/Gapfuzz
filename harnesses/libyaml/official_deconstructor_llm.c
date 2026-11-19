// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 2,3,4,5,6,10를 OSS-Fuzz 하네스 official_deconstructor에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/libyaml/official_deconstructor/).
// OSS-Fuzz 하네스: oss-fuzz/projects/libyaml/libyaml_deconstructor_fuzzer.c 그대로.
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
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef NDEBUG
#undef NDEBUG
#endif

/* [gapfuzz-llm] 빌드 환경에 yaml_write_handler.h가 없어 같은 역할의 버퍼 타입과 쓰기 핸들러를 하네스에 직접 정의 */
typedef struct yaml_output_buffer {
  unsigned char *buf;
  size_t size;
  size_t capacity;
} yaml_output_buffer_t;

static int yaml_write_handler(void *data, unsigned char *buffer, size_t size) {
  yaml_output_buffer_t *out = (yaml_output_buffer_t *)data;
  if (out->capacity == 0)
    out->capacity = 1000;
  if (out->buf == NULL) {
    out->buf = (unsigned char *)malloc(out->capacity);
    if (out->buf == NULL)
      return 0;
  }
  if (size > out->capacity - out->size) {
    size_t new_capacity = out->capacity;
    while (size > new_capacity - out->size)
      new_capacity *= 2;
    unsigned char *new_buf = (unsigned char *)realloc(out->buf, new_capacity);
    if (new_buf == NULL)
      return 0;
    out->buf = new_buf;
    out->capacity = new_capacity;
  }
  memcpy(out->buf + out->size, buffer, size);
  out->size += size;
  return 1;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  if (size < 2)
    return 0;

  bool done = false;
  bool is_canonical = data[0] & 1;
  bool is_unicode = data[1] & 1;
  data += 2;
  size -= 2;

  /* [gapfuzz-llm] 입력 앞쪽 바이트를 순서대로 배분해 서로 겹치지 않게 선택값으로 사용 */
  uint8_t sel[6] = {0, 0, 0, 0, 0, 0};
  size_t nsel = size < 6 ? size : 6;
  memcpy(sel, data, nsel);
  data += nsel;
  size -= nsel;

  /* 스칼라 anchor 후보: NULL이 자주 나오도록 하고, 유효/잘린 UTF-8도 포함 */
  const yaml_char_t *scalar_anchor = NULL;
  switch (sel[0] % 6) {
  case 1: scalar_anchor = (const yaml_char_t *)"a"; break;
  case 2: scalar_anchor = (const yaml_char_t *)"anchor1"; break;
  case 3: scalar_anchor = (const yaml_char_t *)"\xc3\xa9"; break;
  case 4: scalar_anchor = (const yaml_char_t *)"\xe3\x81"; break; /* 잘린 UTF-8 */
  default: scalar_anchor = NULL; break;
  }

  /* 스칼라 tag 후보: 원래 값 3개 + NULL + 사용자 정의 + 잘린 UTF-8 */
  const yaml_char_t *scalar_tag = NULL;
  switch (sel[1] % 7) {
  case 0: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:str"; break;
  case 1: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:int"; break;
  case 2: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:bool"; break;
  case 3: scalar_tag = NULL; break;
  case 4: scalar_tag = (const yaml_char_t *)"!custom"; break;
  case 5: scalar_tag = (const yaml_char_t *)"\xe3\x81"; break;
  default: scalar_tag = (const yaml_char_t *)"tag:yaml.org,2002:str"; break;
  }

  /* 시퀀스 tag 후보 */
  const yaml_char_t *seq_tag = NULL;
  switch (sel[2] % 5) {
  case 0: seq_tag = (const yaml_char_t *)"tag:yaml.org,2002:seq"; break;
  case 1: seq_tag = NULL; break;
  case 2: seq_tag = (const yaml_char_t *)"!myseq"; break;
  case 3: seq_tag = (const yaml_char_t *)"\xc3\xa9"; break;
  default: seq_tag = (const yaml_char_t *)"\xe3\x81"; break;
  }

  /* 매핑 tag 후보 */
  const yaml_char_t *map_tag = NULL;
  switch (sel[3] % 5) {
  case 0: map_tag = (const yaml_char_t *)"tag:yaml.org,2002:map"; break;
  case 1: map_tag = NULL; break;
  case 2: map_tag = (const yaml_char_t *)"!mymap"; break;
  case 3: map_tag = (const yaml_char_t *)"\xc3\xa9"; break;
  default: map_tag = (const yaml_char_t *)"\xe3\x81"; break;
  }

  /* 문서 시작의 version_directive 후보 */
  yaml_version_directive_t doc_version = {1, (sel[4] >> 4) & 1 ? 2 : 1};
  yaml_version_directive_t *doc_version_ptr = (sel[4] & 1) ? &doc_version : NULL;

  /* 문서 시작의 tag_directives 후보 */
  yaml_tag_directive_t doc_tag_directive = {
      (yaml_char_t *)"!e!", (yaml_char_t *)"tag:example.com,2000:"};
  yaml_tag_directive_t *doc_tags_start = (sel[5] & 1) ? &doc_tag_directive : NULL;
  yaml_tag_directive_t *doc_tags_end = (sel[5] & 1) ? &doc_tag_directive + 1 : NULL;

  yaml_parser_t parser;
  yaml_emitter_t emitter;
  yaml_event_t input_event;
  yaml_event_t output_event;

  /* Initialize the parser and emitter objects. */

  if (!yaml_parser_initialize(&parser)) {
    return 1;
  }

  if (!yaml_emitter_initialize(&emitter)) {
    yaml_parser_delete(&parser);
    return 1;
  }

  /* Set the parser parameters. */

  yaml_parser_set_input_string(&parser, data, size);

  /* Set the emitter parameters. */
  yaml_output_buffer_t out = {/*buf=*/NULL, /*size=*/0, /*capacity=*/1000};
  yaml_emitter_set_output(&emitter, yaml_write_handler, &out);

  yaml_emitter_set_canonical(&emitter, is_canonical);
  yaml_emitter_set_unicode(&emitter, is_unicode);

  /* Create and emit the STREAM-START event. */

  if (!yaml_stream_start_event_initialize(&output_event, YAML_UTF8_ENCODING))
    goto error;
  if (!yaml_emitter_emit(&emitter, &output_event))
    goto error;

  /* Create and emit the DOCUMENT-START event. */

  if (!yaml_document_start_event_initialize(&output_event, doc_version_ptr, doc_tags_start, doc_tags_end, 0)) // [gapfuzz-llm] version_directive와 tag_directives를 퍼저 입력으로 선택
    goto error;
  if (!yaml_emitter_emit(&emitter, &output_event))
    goto error;

  /* Create and emit the SEQUENCE-START event. */

  if (!yaml_sequence_start_event_initialize(
          &output_event, NULL, seq_tag, 1, // [gapfuzz-llm] 시퀀스 tag를 퍼저 입력으로 선택
          YAML_BLOCK_SEQUENCE_STYLE))
    goto error;
  if (!yaml_emitter_emit(&emitter, &output_event))
    goto error;

  /* Loop through the input events. */

  while (!done) {
    /* Get the next event. */

    if (!yaml_parser_parse(&parser, &input_event))
      goto error;

    /* Check if this is the stream end. */

    done = (input_event.type == YAML_STREAM_END_EVENT);

    /* Create and emit a MAPPING-START event. */

    if (!yaml_mapping_start_event_initialize(
            &output_event, NULL, map_tag, 1, // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
            YAML_BLOCK_MAPPING_STYLE))
      goto error;
    if (!yaml_emitter_emit(&emitter, &output_event))
      goto error;

    /* Analyze the event. */

    switch (input_event.type) {
    case YAML_STREAM_START_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'STREAM-START'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"STREAM-START", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display encoding information. */

      if (input_event.data.stream_start.encoding) {
        yaml_encoding_t encoding = input_event.data.stream_start.encoding;

        /* Write 'encoding'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"encoding", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the stream encoding. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)(encoding == YAML_UTF8_ENCODING
                                    ? "utf-8"
                                    : encoding == YAML_UTF16LE_ENCODING
                                          ? "utf-16-le"
                                          : encoding == YAML_UTF16BE_ENCODING
                                                ? "utf-16-be"
                                                : "unknown"),
                -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      break;

    case YAML_STREAM_END_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'STREAM-END'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"STREAM-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      break;

    case YAML_DOCUMENT_START_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'DOCUMENT-START'. */

      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                        (yaml_char_t *)"DOCUMENT-START", -1, 1,
                                        1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display the document version numbers. */

      if (input_event.data.document_start.version_directive) {
        yaml_version_directive_t *version =
            input_event.data.document_start.version_directive;
        char number[64];

        /* Write 'version'. */
        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"version", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write '{'. */

        if (!yaml_mapping_start_event_initialize(
                &output_event, NULL, map_tag, 1, // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
                YAML_FLOW_MAPPING_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write 'major'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"major", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write a number. */

        sprintf(number, "%d", version->major);
        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)number, -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write 'minor'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"minor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write a number. */

        sprintf(number, "%d", version->minor);
        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)number, -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write '}'. */

        if (!yaml_mapping_end_event_initialize(&output_event))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Display the document tag directives. */

      if (input_event.data.document_start.tag_directives.start !=
          input_event.data.document_start.tag_directives.end) {
        yaml_tag_directive_t *tag;

        /* Write 'tags'. */
        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"tags", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Start a block sequence. */

        if (!yaml_sequence_start_event_initialize(
                &output_event, NULL, seq_tag, 1, // [gapfuzz-llm] 시퀀스 tag를 퍼저 입력으로 선택
                YAML_BLOCK_SEQUENCE_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        for (tag = input_event.data.document_start.tag_directives.start;
             tag != input_event.data.document_start.tag_directives.end; tag++) {
          /* Write '{'. */

          if (!yaml_mapping_start_event_initialize(
                  &output_event, NULL, map_tag,
                  1, YAML_FLOW_MAPPING_STYLE)) // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
            goto error;
          if (!yaml_emitter_emit(&emitter, &output_event))
            goto error;

          /* Write 'handle'. */

          if (!yaml_scalar_event_initialize(
                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                  (yaml_char_t *)"handle", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
            goto error;
          if (!yaml_emitter_emit(&emitter, &output_event))
            goto error;

          /* Write the tag directive handle. */

          if (!yaml_scalar_event_initialize(
                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                  (yaml_char_t *)tag->handle, -1, 0, 1,
                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
            goto error;
          if (!yaml_emitter_emit(&emitter, &output_event))
            goto error;

          /* Write 'prefix'. */

          if (!yaml_scalar_event_initialize(
                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                  (yaml_char_t *)"prefix", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
            goto error;
          if (!yaml_emitter_emit(&emitter, &output_event))
            goto error;

          /* Write the tag directive prefix. */

          if (!yaml_scalar_event_initialize(
                  &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                  (yaml_char_t *)tag->prefix, -1, 0, 1,
                  YAML_DOUBLE_QUOTED_SCALAR_STYLE))
            goto error;
          if (!yaml_emitter_emit(&emitter, &output_event))
            goto error;

          /* Write '}'. */

          if (!yaml_mapping_end_event_initialize(&output_event))
            goto error;
          if (!yaml_emitter_emit(&emitter, &output_event))
            goto error;
        }

        /* End a block sequence. */

        if (!yaml_sequence_end_event_initialize(&output_event))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Write 'implicit'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write if the document is implicit. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)(input_event.data.document_start.implicit
                                  ? "true"
                                  : "false"),
              -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      break;

    case YAML_DOCUMENT_END_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'DOCUMENT-END'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"DOCUMENT-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'implicit'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write if the document is implicit. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)(input_event.data.document_end.implicit ? "true"
                                                                     : "false"),
              -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      break;

    case YAML_ALIAS_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'ALIAS'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"ALIAS", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'anchor'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write the alias anchor. */

      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                        input_event.data.alias.anchor, -1, 0, 1,
                                        YAML_DOUBLE_QUOTED_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      break;

    case YAML_SCALAR_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'SCALAR'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"SCALAR", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display the scalar anchor. */

      if (input_event.data.scalar.anchor) {
        /* Write 'anchor'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the scalar anchor. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                input_event.data.scalar.anchor, -1, 0, 1,
                YAML_DOUBLE_QUOTED_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Display the scalar tag. */

      if (input_event.data.scalar.tag) {
        /* Write 'tag'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the scalar tag. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                input_event.data.scalar.tag, -1, 0, 1,
                YAML_DOUBLE_QUOTED_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Display the scalar value. */

      /* Write 'value'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"value", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write the scalar value. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              input_event.data.scalar.value, input_event.data.scalar.length, 0,
              1, YAML_DOUBLE_QUOTED_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display if the scalar tag is implicit. */

      /* Write 'implicit'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write '{'. */

      if (!yaml_mapping_start_event_initialize(
              &output_event, NULL, map_tag, 1, // [gapfuzz-llm] 매핑 tag를 퍼저 입력으로 선택
              YAML_FLOW_MAPPING_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'plain'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"plain", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write if the scalar is implicit in the plain style. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)(input_event.data.scalar.plain_implicit ? "true"
                                                                     : "false"),
              -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'quoted'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"non-plain", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write if the scalar is implicit in a non-plain style. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)(input_event.data.scalar.quoted_implicit
                                  ? "true"
                                  : "false"),
              -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write '}'. */

      if (!yaml_mapping_end_event_initialize(&output_event))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display the style information. */

      if (input_event.data.scalar.style) {
        yaml_scalar_style_t style = input_event.data.scalar.style;

        /* Write 'style'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the scalar style. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t
                     *)(style == YAML_PLAIN_SCALAR_STYLE
                            ? "plain"
                            : style == YAML_SINGLE_QUOTED_SCALAR_STYLE
                                  ? "single-quoted"
                                  : style == YAML_DOUBLE_QUOTED_SCALAR_STYLE
                                        ? "double-quoted"
                                        : style == YAML_LITERAL_SCALAR_STYLE
                                              ? "literal"
                                              : style ==
                                                        YAML_FOLDED_SCALAR_STYLE
                                                    ? "folded"
                                                    : "unknown"),
                -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      break;

    case YAML_SEQUENCE_START_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'SEQUENCE-START'. */

      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                        (yaml_char_t *)"SEQUENCE-START", -1, 1,
                                        1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display the sequence anchor. */

      if (input_event.data.sequence_start.anchor) {
        /* Write 'anchor'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the sequence anchor. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                input_event.data.sequence_start.anchor, -1, 0, 1,
                YAML_DOUBLE_QUOTED_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Display the sequence tag. */

      if (input_event.data.sequence_start.tag) {
        /* Write 'tag'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the sequence tag. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                input_event.data.sequence_start.tag, -1, 0, 1,
                YAML_DOUBLE_QUOTED_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Write 'implicit'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write if the sequence tag is implicit. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)(input_event.data.sequence_start.implicit
                                  ? "true"
                                  : "false"),
              -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display the style information. */

      if (input_event.data.sequence_start.style) {
        yaml_sequence_style_t style = input_event.data.sequence_start.style;

        /* Write 'style'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the scalar style. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)(style == YAML_BLOCK_SEQUENCE_STYLE
                                    ? "block"
                                    : style == YAML_FLOW_SEQUENCE_STYLE
                                          ? "flow"
                                          : "unknown"),
                -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      break;

    case YAML_SEQUENCE_END_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'SEQUENCE-END'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"SEQUENCE-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      break;

    case YAML_MAPPING_START_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'MAPPING-START'. */

      if (!yaml_scalar_event_initialize(&output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                                        (yaml_char_t *)"MAPPING-START", -1, 1,
                                        1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display the mapping anchor. */

      if (input_event.data.mapping_start.anchor) {
        /* Write 'anchor'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"anchor", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the mapping anchor. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                input_event.data.mapping_start.anchor, -1, 0, 1,
                YAML_DOUBLE_QUOTED_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Display the mapping tag. */

      if (input_event.data.mapping_start.tag) {
        /* Write 'tag'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"tag", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the mapping tag. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                input_event.data.mapping_start.tag, -1, 0, 1,
                YAML_DOUBLE_QUOTED_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      /* Write 'implicit'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"implicit", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write if the mapping tag is implicit. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)(input_event.data.mapping_start.implicit
                                  ? "true"
                                  : "false"),
              -1, 1, 0, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Display the style information. */

      if (input_event.data.mapping_start.style) {
        yaml_mapping_style_t style = input_event.data.mapping_start.style;

        /* Write 'style'. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)"style", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;

        /* Write the scalar style. */

        if (!yaml_scalar_event_initialize(
                &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
                (yaml_char_t *)(style == YAML_BLOCK_MAPPING_STYLE
                                    ? "block"
                                    : style == YAML_FLOW_MAPPING_STYLE
                                          ? "flow"
                                          : "unknown"),
                -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
          goto error;
        if (!yaml_emitter_emit(&emitter, &output_event))
          goto error;
      }

      break;

    case YAML_MAPPING_END_EVENT:

      /* Write 'type'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"type", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      /* Write 'MAPPING-END'. */

      if (!yaml_scalar_event_initialize(
              &output_event, scalar_anchor, scalar_tag, // [gapfuzz-llm] anchor와 tag를 퍼저 입력으로 선택
              (yaml_char_t *)"MAPPING-END", -1, 1, 1, YAML_PLAIN_SCALAR_STYLE))
        goto error;
      if (!yaml_emitter_emit(&emitter, &output_event))
        goto error;

      break;

    default:
      /* It couldn't really happen. */
      break;
    }

    /* Delete the event object. */

    yaml_event_delete(&input_event);

    /* Create and emit a MAPPING-END event. */

    if (!yaml_mapping_end_event_initialize(&output_event))
      goto error;
    if (!yaml_emitter_emit(&emitter, &output_event))
      goto error;
  }

  /* Create and emit the SEQUENCE-END event. */

  if (!yaml_sequence_end_event_initialize(&output_event))
    goto error;
  if (!yaml_emitter_emit(&emitter, &output_event))
    goto error;

  /* Create and emit the DOCUMENT-END event. */

  if (!yaml_document_end_event_initialize(&output_event, 0))
    goto error;
  if (!yaml_emitter_emit(&emitter, &output_event))
    goto error;

  /* Create and emit the STREAM-END event. */

  if (!yaml_stream_end_event_initialize(&output_event))
    goto error;
  yaml_emitter_emit(&emitter, &output_event);

error:

  free(out.buf);

  yaml_event_delete(&input_event);
  yaml_parser_delete(&parser);
  yaml_emitter_delete(&emitter);

  return 0;
}
