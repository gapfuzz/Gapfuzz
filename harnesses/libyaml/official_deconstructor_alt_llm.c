// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,3,4,5,6,8,9를 OSS-Fuzz 하네스 official_deconstructor_alt에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: evaluation/artifacts/llm/combined/libyaml/official_deconstructor_alt/).
// OSS-Fuzz 하네스: oss-fuzz/projects/libyaml/libyaml_deconstructor_alt_fuzzer.c 그대로.
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

typedef struct yaml_output_buffer { // [gapfuzz-llm] yaml_write_handler.h가 빌드 환경에 없어 같은 역할의 타입을 하네스에 직접 정의
  unsigned char *buf;
  size_t size;
  size_t capacity;
} yaml_output_buffer_t;

static int yaml_write_handler(void *data, unsigned char *buffer, size_t size) { // [gapfuzz-llm] 헤더 대신 쓰기 핸들러를 하네스에 직접 구현 (용량 초과 시 실패 반환)
  yaml_output_buffer_t *out = (yaml_output_buffer_t *)data;
  if (size > out->capacity || out->size > out->capacity - size)
    return 0;
  if (size == 0)
    return 1;
  unsigned char *nb = (unsigned char *)realloc(out->buf, out->size + size);
  if (!nb)
    return 0;
  out->buf = nb;
  memcpy(out->buf + out->size, buffer, size);
  out->size += size;
  return 1;
}

/* 태그 선택용 상태: 입력 바이트로 시드되고 호출마다 갱신된다. */
static uint8_t g_tag_state; // [gapfuzz-llm] 태그를 퍼저 입력에서 고르기 위한 상태 변수 추가
static bool g_pick_enabled; // [gapfuzz-llm] 대체 문서를 만들 때는 태그 변경을 끄기 위한 플래그
static unsigned g_calls; // [gapfuzz-llm] 태그 선택 호출 횟수
static int g_bad_at; // [gapfuzz-llm] 잘못된 UTF-8 태그를 낼 호출 번호 (-1이면 사용 안 함)

static const yaml_char_t *pick_tag(const yaml_char_t *orig) { // [gapfuzz-llm] 원래 태그(NULL/INT/BOOL)와 다른 태그 값을 입력에서 고름
  static const yaml_char_t *const alt_tags[] = {
      (const yaml_char_t *)"tag:yaml.org,2002:int",
      (const yaml_char_t *)"tag:yaml.org,2002:bool",
      (const yaml_char_t *)"!custom",
  };
  static const yaml_char_t *const bad_tags[] = {
      (const yaml_char_t *)"\xff\xfe", /* 잘못된 UTF-8 */
      (const yaml_char_t *)"\xE3\x81", /* 잘린 UTF-8 */
  };
  if (!g_pick_enabled)
    return orig;
  unsigned n = g_calls++;
  if (g_bad_at >= 0 && n == (unsigned)g_bad_at) // [gapfuzz-llm] 잘못된 태그는 실행당 최대 1번만 내서 이후 흐름(dump)이 막히지 않게 함
    return bad_tags[g_tag_state & 1];
  g_tag_state = (uint8_t)(g_tag_state * 167u + 13u);
  unsigned idx = (g_tag_state >> 5) % 6u;
  if (idx < 3)
    return orig; /* 원래 값도 계속 나오게 함 */
  return alt_tags[idx - 3];
}

static int harness_add_scalar(yaml_document_t *d, const yaml_char_t *tag,
                              const yaml_char_t *value, int length,
                              yaml_scalar_style_t style) {
  return yaml_document_add_scalar(d, pick_tag(tag), value, length, style);
}

static int harness_add_sequence(yaml_document_t *d, const yaml_char_t *tag,
                                yaml_sequence_style_t style) {
  return yaml_document_add_sequence(d, pick_tag(tag), style);
}

static int harness_add_mapping(yaml_document_t *d, const yaml_char_t *tag,
                               yaml_mapping_style_t style) {
  return yaml_document_add_mapping(d, pick_tag(tag), style);
}

#define yaml_document_add_scalar(d, t, v, l, s) harness_add_scalar(d, t, v, l, s) // [gapfuzz-llm] scalar tag를 입력으로 선택하는 래퍼로 교체
#define yaml_document_add_sequence(d, t, s) harness_add_sequence(d, t, s) // [gapfuzz-llm] sequence tag를 입력으로 선택하는 래퍼로 교체
#define yaml_document_add_mapping(d, t, s) harness_add_mapping(d, t, s) // [gapfuzz-llm] mapping tag를 입력으로 선택하는 래퍼로 교체

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  if (size < 2)
    return 0;

  bool done = false;
  uint8_t hb[8] = {0}; // [gapfuzz-llm] 앞쪽 헤더 바이트를 순서대로 배분해 겹치지 않게 사용
  size_t hn = size < 8 ? size : 8; // [gapfuzz-llm] 헤더 길이 (최대 8바이트)
  memcpy(hb, data, hn); // [gapfuzz-llm] 헤더 바이트 복사
  bool is_canonical = hb[0] & 1;
  bool is_unicode = hb[1] & 1;
  data += hn; // [gapfuzz-llm] 사용한 헤더 바이트만큼 건너뜀
  size -= hn; // [gapfuzz-llm] 나머지는 원래대로 파서 입력으로 사용

  g_tag_state = hb[5]; // [gapfuzz-llm] 태그 선택 상태를 입력으로 시드
  g_calls = 0; // [gapfuzz-llm] 호출 카운터 초기화
  g_bad_at = (hb[5] & 0x80) ? (int)((hb[5] >> 1) & 0x3F) : -1; // [gapfuzz-llm] 잘못된 태그를 낼 호출 번호를 입력으로 결정
  g_pick_enabled = true; // [gapfuzz-llm] 태그 변경 켬

  yaml_parser_t parser;
  yaml_emitter_t emitter;
  yaml_event_t input_event;
  yaml_document_t output_document;
  yaml_document_t alt_document; // [gapfuzz-llm] 앵커/별칭이 생기는 대체 문서
  yaml_document_t *dump_doc = &output_document; // [gapfuzz-llm] dump 대상 문서를 입력으로 선택
  yaml_document_t *other_doc = &alt_document; // [gapfuzz-llm] 선택되지 않은 문서
  bool dumped = false; // [gapfuzz-llm] yaml_emitter_dump가 문서 소유권을 가져갔는지 표시 (이중 해제 방지)
  yaml_version_directive_t ver = {1, 1 + ((hb[6] >> 3) & 1)}; // [gapfuzz-llm] 입력으로 정하는 버전 지시자
  yaml_tag_directive_t tds[2] = {
      {(yaml_char_t *)"!e!", (yaml_char_t *)"tag:example.com,2000:app/"},
      {(yaml_char_t *)"!f!", (yaml_char_t *)"tag:example.org,2001:"}}; // [gapfuzz-llm] 유효한 태그 지시자 후보
  int td_n = (hb[6] >> 1) & 3; // [gapfuzz-llm] 태그 지시자 개수를 입력으로 선택
  if (td_n > 2)
    td_n = 2;

  int root;
  int a_root, a_item, a_map, a_val; // [gapfuzz-llm] 대체 문서 노드 ID

  memset(&input_event, 0, sizeof(input_event)); // [gapfuzz-llm] 조기 error 경로에서 안전한 해제를 위해 0 초기화
  memset(&output_document, 0, sizeof(output_document)); // [gapfuzz-llm] 조기 error 경로에서 안전한 해제를 위해 0 초기화
  memset(&alt_document, 0, sizeof(alt_document)); // [gapfuzz-llm] 조기 error 경로에서 안전한 해제를 위해 0 초기화

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
  if (hb[2] % 4 != 0) // [gapfuzz-llm] emitter 폭 설정을 입력으로 변경 (0이면 기본값 유지)
    yaml_emitter_set_width(&emitter, (int)(hb[2] % 100) - 1);
  if (hb[3] & 0x80) // [gapfuzz-llm] emitter 들여쓰기를 입력으로 변경
    yaml_emitter_set_indent(&emitter, hb[3] & 0x0F);
  yaml_emitter_set_break(&emitter, (yaml_break_t)(hb[4] % 4)); // [gapfuzz-llm] emitter 줄바꿈 종류를 입력으로 변경

  /* Create and emit the STREAM-START event. */

  if (!yaml_emitter_open(&emitter))
    goto error;

  /* Create a output_document object. */

  if (!yaml_document_initialize(&output_document,
                                (hb[6] & 1) ? &ver : NULL,
                                td_n ? tds : NULL, td_n ? tds + td_n : NULL, 0,
                                0)) // [gapfuzz-llm] 버전/태그 지시자를 입력에 따라 전달
    goto error;

  /* Build the alternative document (shared nodes -> anchors/aliases). */

  if (hb[7] & 1) { // [gapfuzz-llm] 대체 문서 사용 여부를 입력으로 선택
    g_pick_enabled = false; // [gapfuzz-llm] 대체 문서는 항상 유효한 기본 태그로 만들어 anchor/alias 경로가 막히지 않게 함
    if (!yaml_document_initialize(&alt_document, NULL, NULL, NULL, 1, 1))
      goto error;
    a_root = yaml_document_add_sequence(
        &alt_document, NULL,
        (hb[7] & 2) ? YAML_FLOW_SEQUENCE_STYLE : YAML_BLOCK_SEQUENCE_STYLE);
    if (!a_root)
      goto error;
    a_item = yaml_document_add_scalar(&alt_document, NULL, (yaml_char_t *)"a",
                                      -1, YAML_PLAIN_SCALAR_STYLE);
    if (!a_item)
      goto error;
    if (!yaml_document_append_sequence_item(&alt_document, a_root, a_item))
      goto error;
    if (!yaml_document_append_sequence_item(&alt_document, a_root, a_item))
      goto error;
    a_map = yaml_document_add_mapping(&alt_document, NULL,
                                      YAML_FLOW_MAPPING_STYLE);
    if (!a_map)
      goto error;
    a_val = yaml_document_add_scalar(&alt_document, NULL, (yaml_char_t *)"b",
                                     -1, YAML_PLAIN_SCALAR_STYLE);
    if (!a_val)
      goto error;
    if (!yaml_document_append_mapping_pair(&alt_document, a_map, a_item, a_val))
      goto error;
    if (!yaml_document_append_sequence_item(&alt_document, a_root, a_map))
      goto error;
    g_pick_enabled = true; // [gapfuzz-llm] 이후 output_document 구성에서는 태그 변경 다시 켬
    dump_doc = &alt_document; // [gapfuzz-llm] 대체 문서를 dump 대상으로 선택
    other_doc = &output_document; // [gapfuzz-llm] 나머지 문서도 마지막에 해제
  }

  /* Create the root sequence. */

  root = yaml_document_add_sequence(&output_document, NULL,
                                    YAML_BLOCK_SEQUENCE_STYLE);
  if (!root)
    goto error;

  /* Loop through the input events. */

  while (!done) {
    int properties, key, value, map, seq;

    /* Get the next event. */

    if (!yaml_parser_parse(&parser, &input_event))
      goto error;

    /* Check if this is the stream end. */

    done = (input_event.type == YAML_STREAM_END_EVENT);

    /* Create a mapping node and attach it to the root sequence. */

    properties = yaml_document_add_mapping(&output_document, NULL,
                                           YAML_BLOCK_MAPPING_STYLE);
    if (!properties)
      goto error;
    if (!yaml_document_append_sequence_item(&output_document, root, properties))
      goto error;

    /* Analyze the event. */

    switch (input_event.type) {
    case YAML_STREAM_START_EVENT:

      /* Add 'type': 'STREAM-START'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"STREAM-START", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Add 'encoding': <encoding>. */

      if (input_event.data.stream_start.encoding) {
        yaml_encoding_t encoding = input_event.data.stream_start.encoding;

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"encoding", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(
            &output_document, NULL,
            (encoding == YAML_UTF8_ENCODING
                 ? (yaml_char_t *)"utf-8"
                 : encoding == YAML_UTF16LE_ENCODING
                       ? (yaml_char_t *)"utf-16-le"
                       : encoding == YAML_UTF16BE_ENCODING
                             ? (yaml_char_t *)"utf-16-be"
                             : (yaml_char_t *)"unknown"),
            -1, YAML_PLAIN_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      break;

    case YAML_STREAM_END_EVENT:

      /* Add 'type': 'STREAM-END'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"STREAM-END", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      break;

    case YAML_DOCUMENT_START_EVENT:

      /* Add 'type': 'DOCUMENT-START'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"DOCUMENT-START", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Display the output_document version numbers. */

      if (input_event.data.document_start.version_directive) {
        yaml_version_directive_t *version =
            input_event.data.document_start.version_directive;
        char number[64];

        /* Add 'version': {}. */

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"version", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        map = yaml_document_add_mapping(&output_document, NULL,
                                        YAML_FLOW_MAPPING_STYLE);
        if (!map)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, map))
          goto error;

        /* Add 'major': <number>. */

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"major", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        sprintf(number, "%d", version->major);
        value = yaml_document_add_scalar(
            &output_document, (yaml_char_t *)YAML_INT_TAG,
            (yaml_char_t *)number, -1, YAML_PLAIN_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, map, key,
                                               value))
          goto error;

        /* Add 'minor': <number>. */

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"minor", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        sprintf(number, "%d", version->minor);
        value = yaml_document_add_scalar(
            &output_document, (yaml_char_t *)YAML_INT_TAG,
            (yaml_char_t *)number, -1, YAML_PLAIN_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, map, key,
                                               value))
          goto error;
      }

      /* Display the output_document tag directives. */

      if (input_event.data.document_start.tag_directives.start !=
          input_event.data.document_start.tag_directives.end) {
        yaml_tag_directive_t *tag;

        /* Add 'tags': []. */

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"tags", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        seq = yaml_document_add_sequence(&output_document, NULL,
                                         YAML_BLOCK_SEQUENCE_STYLE);
        if (!seq)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, seq))
          goto error;

        for (tag = input_event.data.document_start.tag_directives.start;
             tag != input_event.data.document_start.tag_directives.end; tag++) {
          /* Add {}. */

          map = yaml_document_add_mapping(&output_document, NULL,
                                          YAML_FLOW_MAPPING_STYLE);
          if (!map)
            goto error;
          if (!yaml_document_append_sequence_item(&output_document, seq, map))
            goto error;

          /* Add 'handle': <handle>. */

          key = yaml_document_add_scalar(&output_document, NULL,
                                         (yaml_char_t *)"handle", -1,
                                         YAML_PLAIN_SCALAR_STYLE);
          if (!key)
            goto error;
          value = yaml_document_add_scalar(&output_document, NULL, tag->handle,
                                           -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
          if (!value)
            goto error;
          if (!yaml_document_append_mapping_pair(&output_document, map, key,
                                                 value))
            goto error;

          /* Add 'prefix': <prefix>. */

          key = yaml_document_add_scalar(&output_document, NULL,
                                         (yaml_char_t *)"prefix", -1,
                                         YAML_PLAIN_SCALAR_STYLE);
          if (!key)
            goto error;
          value = yaml_document_add_scalar(&output_document, NULL, tag->prefix,
                                           -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
          if (!value)
            goto error;
          if (!yaml_document_append_mapping_pair(&output_document, map, key,
                                                 value))
            goto error;
        }
      }

      /* Add 'implicit': <flag>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"implicit", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(
          &output_document, (yaml_char_t *)YAML_BOOL_TAG,
          (input_event.data.document_start.implicit ? (yaml_char_t *)"true"
                                                    : (yaml_char_t *)"false"),
          -1, YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      break;

    case YAML_DOCUMENT_END_EVENT:

      /* Add 'type': 'DOCUMENT-END'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"DOCUMENT-END", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Add 'implicit': <flag>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"implicit", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(
          &output_document, (yaml_char_t *)YAML_BOOL_TAG,
          (input_event.data.document_end.implicit ? (yaml_char_t *)"true"
                                                  : (yaml_char_t *)"false"),
          -1, YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      break;

    case YAML_ALIAS_EVENT:

      /* Add 'type': 'ALIAS'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"ALIAS", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Add 'anchor': <anchor>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"anchor", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       input_event.data.alias.anchor, -1,
                                       YAML_DOUBLE_QUOTED_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      break;

    case YAML_SCALAR_EVENT:

      /* Add 'type': 'SCALAR'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"SCALAR", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Add 'anchor': <anchor>. */

      if (input_event.data.scalar.anchor) {
        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"anchor", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(&output_document, NULL,
                                         input_event.data.scalar.anchor, -1,
                                         YAML_DOUBLE_QUOTED_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      /* Add 'tag': <tag>. */

      if (input_event.data.scalar.tag) {
        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"tag", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(&output_document, NULL,
                                         input_event.data.scalar.tag, -1,
                                         YAML_DOUBLE_QUOTED_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      /* Add 'value': <value>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"value", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(
          &output_document, NULL, input_event.data.scalar.value,
          input_event.data.scalar.length, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Display if the scalar tag is implicit. */

      /* Add 'implicit': {} */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"version", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      map = yaml_document_add_mapping(&output_document, NULL,
                                      YAML_FLOW_MAPPING_STYLE);
      if (!map)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             map))
        goto error;

      /* Add 'plain': <flag>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"plain", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(
          &output_document, (yaml_char_t *)YAML_BOOL_TAG,
          (input_event.data.scalar.plain_implicit ? (yaml_char_t *)"true"
                                                  : (yaml_char_t *)"false"),
          -1, YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, map, key, value))
        goto error;

      /* Add 'quoted': <flag>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"quoted", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(
          &output_document, (yaml_char_t *)YAML_BOOL_TAG,
          (input_event.data.scalar.quoted_implicit ? (yaml_char_t *)"true"
                                                   : (yaml_char_t *)"false"),
          -1, YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, map, key, value))
        goto error;

      /* Display the style information. */

      if (input_event.data.scalar.style) {
        yaml_scalar_style_t style = input_event.data.scalar.style;

        /* Add 'style': <style>. */

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"style", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(
            &output_document, NULL,
            (yaml_char_t
                 *)(style == YAML_PLAIN_SCALAR_STYLE
                        ? "plain"
                        : style == YAML_SINGLE_QUOTED_SCALAR_STYLE
                              ? "single-quoted"
                              : style == YAML_DOUBLE_QUOTED_SCALAR_STYLE
                                    ? "double-quoted"
                                    : style == YAML_LITERAL_SCALAR_STYLE
                                          ? "literal"
                                          : style == YAML_FOLDED_SCALAR_STYLE
                                                ? "folded"
                                                : "unknown"),
            -1, YAML_PLAIN_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      break;

    case YAML_SEQUENCE_START_EVENT:

      /* Add 'type': 'SEQUENCE-START'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"SEQUENCE-START", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Add 'anchor': <anchor>. */

      if (input_event.data.sequence_start.anchor) {
        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"anchor", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(&output_document, NULL,
                                         input_event.data.sequence_start.anchor,
                                         -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      /* Add 'tag': <tag>. */

      if (input_event.data.sequence_start.tag) {
        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"tag", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(&output_document, NULL,
                                         input_event.data.sequence_start.tag,
                                         -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      /* Add 'implicit': <flag>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"implicit", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(
          &output_document, (yaml_char_t *)YAML_BOOL_TAG,
          (input_event.data.sequence_start.implicit ? (yaml_char_t *)"true"
                                                    : (yaml_char_t *)"false"),
          -1, YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Display the style information. */

      if (input_event.data.sequence_start.style) {
        yaml_sequence_style_t style = input_event.data.sequence_start.style;

        /* Add 'style': <style>. */

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"style", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(
            &output_document, NULL,
            (yaml_char_t *)(style == YAML_BLOCK_SEQUENCE_STYLE
                                ? "block"
                                : style == YAML_FLOW_SEQUENCE_STYLE
                                      ? "flow"
                                      : "unknown"),
            -1, YAML_PLAIN_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      break;

    case YAML_SEQUENCE_END_EVENT:

      /* Add 'type': 'SEQUENCE-END'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"SEQUENCE-END", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      break;

    case YAML_MAPPING_START_EVENT:

      /* Add 'type': 'MAPPING-START'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"MAPPING-START", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Add 'anchor': <anchor>. */

      if (input_event.data.mapping_start.anchor) {
        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"anchor", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(&output_document, NULL,
                                         input_event.data.mapping_start.anchor,
                                         -1, YAML_DOUBLE_QUOTED_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      /* Add 'tag': <tag>. */

      if (input_event.data.mapping_start.tag) {
        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"tag", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(&output_document, NULL,
                                         input_event.data.mapping_start.tag, -1,
                                         YAML_DOUBLE_QUOTED_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      /* Add 'implicit': <flag>. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"implicit", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(
          &output_document, (yaml_char_t *)YAML_BOOL_TAG,
          (yaml_char_t *)(input_event.data.mapping_start.implicit ? "true"
                                                                  : "false"),
          -1, YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      /* Display the style information. */

      if (input_event.data.sequence_start.style) {
        yaml_sequence_style_t style = input_event.data.sequence_start.style;

        /* Add 'style': <style>. */

        key = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"style", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
        if (!key)
          goto error;
        value = yaml_document_add_scalar(
            &output_document, NULL,
            (yaml_char_t *)(style == YAML_BLOCK_MAPPING_STYLE
                                ? "block"
                                : style == YAML_FLOW_MAPPING_STYLE ? "flow"
                                                                   : "unknown"),
            -1, YAML_PLAIN_SCALAR_STYLE);
        if (!value)
          goto error;
        if (!yaml_document_append_mapping_pair(&output_document, properties,
                                               key, value))
          goto error;
      }

      break;

    case YAML_MAPPING_END_EVENT:

      /* Add 'type': 'MAPPING-END'. */

      key = yaml_document_add_scalar(&output_document, NULL,
                                     (yaml_char_t *)"type", -1,
                                     YAML_PLAIN_SCALAR_STYLE);
      if (!key)
        goto error;
      value = yaml_document_add_scalar(&output_document, NULL,
                                       (yaml_char_t *)"MAPPING-END", -1,
                                       YAML_PLAIN_SCALAR_STYLE);
      if (!value)
        goto error;
      if (!yaml_document_append_mapping_pair(&output_document, properties, key,
                                             value))
        goto error;

      break;

    default:
      /* It couldn't really happen. */
      break;
    }

    /* Delete the event object. */

    yaml_event_delete(&input_event);
  }

  dumped = true; // [gapfuzz-llm] yaml_emitter_dump는 성공/실패와 무관하게 문서를 해제하므로 이후 직접 해제하지 않음
  if (!yaml_emitter_dump(&emitter, dump_doc)) // [gapfuzz-llm] 입력으로 고른 문서를 dump
    goto error;

  yaml_emitter_close(&emitter);

error:

  free(out.buf);

  yaml_event_delete(&input_event);
  if (!dumped) // [gapfuzz-llm] dump가 소유권을 가져간 문서는 이중 해제(double free)를 피하려고 직접 해제하지 않음
    yaml_document_delete(dump_doc);
  yaml_document_delete(other_doc); // [gapfuzz-llm] dump 대상이 아닌 문서는 직접 해제 (0 초기화되어 안전)
  yaml_parser_delete(&parser);
  yaml_emitter_delete(&emitter);

  return 0;
}
