// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,3,4,5,9를 OSS-Fuzz 하네스 official에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: samples/llm/combined/yyjson/official/).
// OSS-Fuzz 하네스: yyjson 저장소 fuzz/fuzzer.c (0.13.0, 커밋 6447536) 그대로.
#include <stdlib.h>
#include <string.h>
#include <yyjson.h>

/* Fuzzer-only allocator cap (not a library limit).
   OSS-Fuzz kills processes above ~2560MB RSS. Valid deep nesting with
   pretty-print can expand hugely; return NULL before the process is killed. */
#ifndef YYJSON_FUZZ_ALLOC_LIMIT
#   define YYJSON_FUZZ_ALLOC_LIMIT (512u * 1024u * 1024u)
#endif

static void *fuzz_malloc(void *ctx, size_t size) {
    (void)ctx;
    if (size > YYJSON_FUZZ_ALLOC_LIMIT) return NULL;
    return malloc(size);
}

static void *fuzz_realloc(void *ctx, void *ptr, size_t old_size, size_t size) {
    (void)ctx;
    (void)old_size;
    if (size > YYJSON_FUZZ_ALLOC_LIMIT) return NULL;
    return realloc(ptr, size);
}

static void fuzz_free(void *ctx, void *ptr) {
    (void)ctx;
    free(ptr);
}

static const yyjson_alc FUZZ_ALC = {
    fuzz_malloc, fuzz_realloc, fuzz_free, NULL
};

/* [gapfuzz-llm] n번째 malloc만 실패시키는 할당자: 읽기 중 메모리 할당 실패 경로(MEMORY_ALLOCATION)를 만들기 위함 */
typedef struct {
    unsigned count;
    unsigned fail_at;
} fail_ctx;

static void *failing_malloc(void *ctx, size_t size) { // [gapfuzz-llm] 지정한 순번의 malloc에서 NULL 반환
    fail_ctx *fc = (fail_ctx *)ctx;
    fc->count++;
    if (fc->fail_at != 0 && fc->count == fc->fail_at) return NULL;
    return fuzz_malloc(NULL, size);
}

static void *failing_realloc(void *ctx, void *ptr, size_t old_size, size_t size) { // [gapfuzz-llm] realloc은 기존 동작 그대로 전달
    (void)ctx;
    return fuzz_realloc(NULL, ptr, old_size, size);
}

static void failing_free(void *ctx, void *ptr) { // [gapfuzz-llm] free는 기존 동작 그대로 전달
    (void)ctx;
    fuzz_free(NULL, ptr);
}

/*----------------------------------------------------------------------------*/

static void test_with_flags(const uint8_t *data, size_t size,
                            yyjson_read_flag rflg, yyjson_write_flag wflg,
                            uint8_t sel, uint8_t fail_at) { // [gapfuzz-llm] 실패 순번 인자 추가
    yyjson_read_err rerr; // [gapfuzz-llm] err 인자를 NULL/비NULL로 번갈아 넘기기 위한 버퍼
    yyjson_write_err werr; // [gapfuzz-llm] 쓰기 err 인자용 버퍼
    size_t wlen = 0; // [gapfuzz-llm] 쓰기 길이 인자용 버퍼
    fail_ctx fctx = { 0, fail_at }; // [gapfuzz-llm] 할당 실패 시점 제어용 컨텍스트
    yyjson_alc fail_alc = { failing_malloc, failing_realloc, failing_free, &fctx }; // [gapfuzz-llm] 일부 malloc을 실패시키는 할당자
    const yyjson_alc *read_alc = (sel & 0x01) ? &FUZZ_ALC : NULL; // [gapfuzz-llm] 읽기 alc를 입력 비트로 NULL/FUZZ_ALC 선택
    if ((sel & 0x01) && fail_at != 0) read_alc = &fail_alc; // [gapfuzz-llm] 실패 순번이 있으면 실패 할당자로 읽어 MEMORY_ALLOCATION 에러 유도
    yyjson_read_err *read_err = (sel & 0x02) ? &rerr : NULL; // [gapfuzz-llm] 읽기 err를 입력 비트로 NULL/비NULL 선택
    const yyjson_alc *write_alc = (sel & 0x04) ? &FUZZ_ALC : NULL; // [gapfuzz-llm] 쓰기 alc를 입력 비트로 NULL/FUZZ_ALC 선택
    yyjson_write_err *write_err = (sel & 0x08) ? &werr : NULL; // [gapfuzz-llm] 쓰기 err를 입력 비트로 NULL/비NULL 선택
    size_t *write_len = (sel & 0x10) ? &wlen : NULL; // [gapfuzz-llm] 쓰기 len을 입력 비트로 NULL/비NULL 선택
    const yyjson_alc *copy_alc = (sel & 0x20) ? &FUZZ_ALC : NULL; // [gapfuzz-llm] 복사 alc를 입력 비트로 NULL/FUZZ_ALC 선택
    yyjson_doc *idoc = yyjson_read_opts((char *)data, size, rflg, read_alc, read_err); // [gapfuzz-llm] alc, err 인자를 퍼저 입력 기반으로 변경
    yyjson_mut_doc *mdoc = yyjson_doc_mut_copy(idoc, copy_alc); // [gapfuzz-llm] alc 인자를 퍼저 입력 기반으로 변경
    char *ijson = yyjson_write_opts(idoc, wflg, write_alc, write_len, write_err); // [gapfuzz-llm] alc, len, err 인자를 퍼저 입력 기반으로 변경
    if (ijson) FUZZ_ALC.free(FUZZ_ALC.ctx, ijson);
    char *mjson = yyjson_mut_write_opts(mdoc, wflg, &FUZZ_ALC, NULL, NULL);
    if (mjson) FUZZ_ALC.free(FUZZ_ALC.ctx, mjson);
    yyjson_doc_free(idoc);
    yyjson_mut_doc_free(mdoc);
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    uint8_t sel = 0x3F; // [gapfuzz-llm] 입력이 비었을 땐 원래 동작(모든 인자 고정값)을 유지
    uint8_t fail_at = 0; // [gapfuzz-llm] 0이면 할당 실패 없음(원래 동작)
    if (size >= 2) { // [gapfuzz-llm] 앞쪽 2바이트를 인자 선택/실패 순번용으로 사용
        sel = data[0]; // [gapfuzz-llm] 선택 비트를 첫 바이트에서 얻음
        fail_at = data[1] & 0x07; // [gapfuzz-llm] 둘째 바이트로 몇 번째 malloc을 실패시킬지 선택(0~7)
        data += 2; // [gapfuzz-llm] 나머지 바이트는 기존대로 JSON 입력으로 사용
        size -= 2; // [gapfuzz-llm] 소비한 바이트만큼 길이 보정
    }
    test_with_flags(data, size,
                    YYJSON_READ_NOFLAG,
                    YYJSON_WRITE_NOFLAG,
                    sel, fail_at); // [gapfuzz-llm] 선택 비트와 실패 순번 전달
    test_with_flags(data, size,
                    YYJSON_READ_JSON5,
                    YYJSON_WRITE_PRETTY |
                    YYJSON_WRITE_ESCAPE_UNICODE |
                    YYJSON_WRITE_ESCAPE_SLASHES |
                    YYJSON_WRITE_ALLOW_INF_AND_NAN,
                    sel, fail_at); // [gapfuzz-llm] 선택 비트와 실패 순번 전달
    return 0;
}
