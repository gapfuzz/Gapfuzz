// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,4,5,6,8,9,10,12,13,14를 OSS-Fuzz 하네스 official_patch에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: samples/llm/combined/yyjson/official_patch/).
// OSS-Fuzz 하네스: yyjson 저장소 fuzz/patch_fuzzer.c (0.13.0, 커밋 6447536) 기반.
#include <stdlib.h>
#include <string.h>
#include <yyjson.h>

#define YYJSON_PATCH_MAX_INPUT_SIZE 8192
#define FUZZ_CTRL_BYTES 3 // [gapfuzz-llm] 입력 앞쪽 제어 바이트 3개를 겹치지 않게 나눠 씀

/* Fuzzer-only allocator cap (not a library limit).
   OSS-Fuzz kills processes above ~2560MB RSS. Valid JSON Patch "copy" from
   the root can grow exponentially; return NULL before the process is killed. */
#ifndef YYJSON_PATCH_FUZZ_ALLOC_LIMIT
#   define YYJSON_PATCH_FUZZ_ALLOC_LIMIT (128u * 1024u * 1024u)
#endif

static void *fuzz_malloc(void *ctx, size_t size) {
    (void)ctx;
    if (size > YYJSON_PATCH_FUZZ_ALLOC_LIMIT) return NULL;
    return malloc(size);
}

static void *fuzz_realloc(void *ctx, void *ptr, size_t old_size, size_t size) {
    (void)ctx;
    (void)old_size;
    if (size > YYJSON_PATCH_FUZZ_ALLOC_LIMIT) return NULL;
    return realloc(ptr, size);
}

static void fuzz_free(void *ctx, void *ptr) {
    (void)ctx;
    free(ptr);
}

static const yyjson_alc FUZZ_ALC = {
    fuzz_malloc, fuzz_realloc, fuzz_free, NULL
};

/* 퍼저 입력에서 고른 설정 (LLVMFuzzerTestOneInput에서 매 입력마다 설정) */
static yyjson_write_flag g_write_flags = YYJSON_WRITE_NOFLAG;
static int g_write_null_alc = 0;
static int g_write_pass_err = 0;
static int g_write_pass_len = 0;
static int g_patch_err_null = 0;
static int g_mut_patch_err_null = 0;
static int g_null_doc_root = 0;
static int g_null_patch_doc = 0;
static int g_copy_mode = 0; // [gapfuzz-llm] yyjson_mut_val_mut_copy 직접 호출 방식 (0: 안 함, 1: doc NULL, 2~3: 정상 doc)
static int g_key_mode = 0;
static char g_key_buf[9];

/*----------------------------------------------------------------------------*/

static void write_and_free_mut_val(yyjson_mut_val *val) {
    char *json;
    size_t wlen = 0;
    yyjson_write_err werr;
    memset(&werr, 0, sizeof(werr));
    if (!val) return;
    json = yyjson_mut_val_write_opts(
        val,
        g_write_flags, // [gapfuzz-llm] 쓰기 플래그(PRETTY, NEWLINE_AT_END 등)를 입력에서 선택
        g_write_null_alc ? NULL : &FUZZ_ALC, // [gapfuzz-llm] alc에 NULL도 전달
        g_write_pass_len ? &wlen : NULL, // [gapfuzz-llm] len 포인터도 전달
        g_write_pass_err ? &werr : NULL); // [gapfuzz-llm] err 포인터도 전달
    if (json) FUZZ_ALC.free(FUZZ_ALC.ctx, json);
}

static const char *pick_key(void) {
    switch (g_key_mode) { // [gapfuzz-llm] key로 NULL, 빈 문자열, 고정 문자열, 입력 유래 문자열 사용
        case 0: return NULL;
        case 1: return "";
        case 2: return "a";
        default: return g_key_buf;
    }
}

static void run_json_patch(yyjson_doc *base_doc, yyjson_doc *patch_doc) {
    yyjson_val *base_root = yyjson_doc_get_root(base_doc);
    yyjson_val *patch_root = yyjson_doc_get_root(patch_doc);

    if (g_null_doc_root) {
        (void)yyjson_doc_get_root(NULL); // [gapfuzz-llm] doc에 NULL을 넘기는 경로 추가
    }

    if (base_root == NULL || patch_root == NULL) {
        return;
    }

    (void)yyjson_obj_get(base_root, pick_key()); // [gapfuzz-llm] yyjson_obj_get을 직접 호출, key에 NULL 포함

    yyjson_mut_doc *result_doc = yyjson_mut_doc_new(&FUZZ_ALC);
    if (result_doc != NULL) {
        yyjson_patch_err err;
        memset(&err, 0, sizeof(err));

        yyjson_mut_val *result =
            yyjson_patch(g_null_patch_doc ? NULL : result_doc, base_root, patch_root, // [gapfuzz-llm] doc에 NULL도 전달
                         g_patch_err_null ? NULL : &err); // [gapfuzz-llm] err에 NULL도 전달
        write_and_free_mut_val(result);

        yyjson_mut_doc_free(result_doc);
    }

    yyjson_mut_doc *mut_doc = yyjson_mut_doc_new(&FUZZ_ALC);
    if (mut_doc != NULL) {
        yyjson_mut_val *base_mut = yyjson_val_mut_copy(mut_doc, base_root);
        yyjson_mut_val *patch_mut = yyjson_val_mut_copy(mut_doc, patch_root);

        if (g_copy_mode != 0) {
            // [gapfuzz-llm] yyjson_mut_val_mut_copy를 직접 호출해 doc==NULL 분기 도달 (yyjson_patch는 NULL doc을 먼저 걸러내 내부 호출이 안 됨)
            (void)yyjson_mut_val_mut_copy(g_copy_mode == 1 ? NULL : mut_doc, base_mut);
        }

        if (base_mut != NULL && patch_mut != NULL) {
            yyjson_patch_err err;
            memset(&err, 0, sizeof(err));

            (void)yyjson_mut_obj_get(base_mut, pick_key()); // [gapfuzz-llm] yyjson_mut_obj_get을 직접 호출, key에 NULL 포함

            yyjson_mut_val *result =
                yyjson_mut_patch(mut_doc, base_mut, patch_mut,
                                 g_mut_patch_err_null ? NULL : &err); // [gapfuzz-llm] err에 NULL도 전달
            write_and_free_mut_val(result);
        }

        yyjson_mut_doc_free(mut_doc);
    }
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (data == NULL ||
        size < sizeof(uint16_t) + 1 ||
        size > YYJSON_PATCH_MAX_INPUT_SIZE) {
        return 0;
    }

    /* [gapfuzz-llm] 입력이 충분히 길면 앞 3바이트를 제어용으로 쓰고, 아니면 원래 동작(0)으로 둠 */
    uint8_t ctrl[FUZZ_CTRL_BYTES] = {0, 0, 0};
    if (size >= FUZZ_CTRL_BYTES + sizeof(uint16_t) + 1) {
        memcpy(ctrl, data, FUZZ_CTRL_BYTES);
        data += FUZZ_CTRL_BYTES;
        size -= FUZZ_CTRL_BYTES;
    }

    g_write_flags = YYJSON_WRITE_NOFLAG; // [gapfuzz-llm] ctrl[0] 비트로 쓰기 플래그 구성
    if (ctrl[0] & 0x01) g_write_flags |= YYJSON_WRITE_PRETTY;
    if (ctrl[0] & 0x02) g_write_flags |= YYJSON_WRITE_ESCAPE_UNICODE;
    if (ctrl[0] & 0x04) g_write_flags |= YYJSON_WRITE_ESCAPE_SLASHES;
    if (ctrl[0] & 0x08) g_write_flags |= YYJSON_WRITE_ALLOW_INF_AND_NAN;
    if (ctrl[0] & 0x10) g_write_flags |= YYJSON_WRITE_ALLOW_INVALID_UNICODE;
    if (ctrl[0] & 0x20) g_write_flags |= YYJSON_WRITE_PRETTY_TWO_SPACES;
    if (ctrl[0] & 0x40) g_write_flags |= YYJSON_WRITE_NEWLINE_AT_END;

    g_write_null_alc = (ctrl[1] & 0x01) != 0; // [gapfuzz-llm] ctrl[1]로 write 인자 선택
    g_write_pass_err = (ctrl[1] & 0x02) != 0;
    g_write_pass_len = (ctrl[1] & 0x04) != 0;
    g_patch_err_null = (ctrl[1] & 0x08) != 0;
    g_mut_patch_err_null = (ctrl[1] & 0x10) != 0;

    g_key_mode = ctrl[2] & 0x03; // [gapfuzz-llm] ctrl[2]로 key/NULL doc 선택
    g_null_doc_root = (ctrl[2] & 0x04) != 0;
    g_null_patch_doc = (ctrl[2] & 0x08) != 0;
    g_copy_mode = (ctrl[2] >> 4) & 0x03; // [gapfuzz-llm] ctrl[2] 상위 비트로 mut_val_mut_copy 호출 방식 선택 (0이면 원래 동작)

    uint16_t split_len_raw;
    memcpy(&split_len_raw, data, sizeof(split_len_raw));

    data += sizeof(split_len_raw);
    size -= sizeof(split_len_raw);

    size_t base_size = split_len_raw % (size + 1);
    size_t patch_size = size - base_size;

    const uint8_t *base_data = data;
    const uint8_t *patch_data = data + base_size;

    /* [gapfuzz-llm] 입력 데이터 앞부분에서 NUL 종료된 key 문자열 생성 */
    {
        size_t n = size < 8 ? size : 8;
        memcpy(g_key_buf, data, n);
        g_key_buf[n] = '\0';
    }

    yyjson_read_flag flags =
        YYJSON_READ_ALLOW_INVALID_UNICODE |
        YYJSON_READ_ALLOW_COMMENTS;

    yyjson_doc *base_doc =
        yyjson_read_opts((char *)(void *)base_data, base_size, flags,
                         &FUZZ_ALC, NULL);
    yyjson_doc *patch_doc =
        yyjson_read_opts((char *)(void *)patch_data, patch_size, flags,
                         &FUZZ_ALC, NULL);

    if (base_doc != NULL && patch_doc != NULL) {
        run_json_patch(base_doc, patch_doc);
    }

    yyjson_doc_free(base_doc);
    yyjson_doc_free(patch_doc);

    return 0;
}
