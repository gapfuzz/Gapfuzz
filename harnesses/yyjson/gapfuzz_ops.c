// [gapfuzz-ops] 이 파일은 Claude(claude-sonnet-5-5)가 새로 쓴 하네스입니다. OSS-Fuzz 하네스 전체를 합쳐도 불리지 않던 API 10개를 부릅니다.
// [gapfuzz-ops] gapfuzz가 검사해 통과했습니다 (python3 -m gapfuzz llmops yyjson --union, 기록: samples/llm/ops/yyjson/_union/).
// gapfuzz 새 하네스: yyjson 미커버 API (incr_read, JSON pointer 변경 계열,
// write_number, equals, imut_copy, ptr_get_str, locate_pos)
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <yyjson.h>

#define MAX_INPUT   (64u * 1024u)
#define MAX_OPS     16
#define MAX_ITER    64
#define ALLOC_LIMIT (64u * 1024u * 1024u)

/* 퍼저 전용 할당자: 과도한 할당은 NULL 반환 */
static void *fz_malloc(void *ctx, size_t size) {
    (void)ctx;
    if (size > ALLOC_LIMIT) return NULL;
    return malloc(size);
}
static void *fz_realloc(void *ctx, void *ptr, size_t old_size, size_t size) {
    (void)ctx; (void)old_size;
    if (size > ALLOC_LIMIT) return NULL;
    return realloc(ptr, size);
}
static void fz_free(void *ctx, void *ptr) { (void)ctx; free(ptr); }
static const yyjson_alc ALC = { fz_malloc, fz_realloc, fz_free, NULL };

static yyjson_read_flag pick_read_flag(uint8_t b) {
    yyjson_read_flag f = YYJSON_READ_NOFLAG;
    if (b & 1)  f |= YYJSON_READ_ALLOW_TRAILING_COMMAS;
    if (b & 2)  f |= YYJSON_READ_ALLOW_COMMENTS;
    if (b & 4)  f |= YYJSON_READ_ALLOW_INF_AND_NAN;
    if (b & 8)  f |= YYJSON_READ_NUMBER_AS_RAW;
    if (b & 16) f |= YYJSON_READ_ALLOW_INVALID_UNICODE;
    if (b & 32) f |= YYJSON_READ_ALLOW_BOM;
    if (b & 64) f |= YYJSON_READ_BIGNUM_AS_RAW;
    return f;
}

/* 입력 바이트로 새 mutable 값을 만든다 (실패 시 NULL) */
static yyjson_mut_val *make_val(yyjson_mut_doc *doc, uint8_t kind,
                                const uint8_t *p, size_t n) {
    uint64_t u = 0;
    size_t i;
    for (i = 0; i < n && i < 8; i++) u |= ((uint64_t)p[i]) << (8 * i);
    switch (kind % 8) {
    case 0: return yyjson_mut_null(doc);
    case 1: return yyjson_mut_bool(doc, (u & 1) != 0);
    case 2: return yyjson_mut_sint(doc, (int64_t)u);
    case 3: return yyjson_mut_uint(doc, u);
    case 4: { double d; memcpy(&d, &u, sizeof(d)); return yyjson_mut_real(doc, d); }
    case 5: {
        char tmp[33];
        size_t l = n > 32 ? 32 : n;
        memcpy(tmp, p, l); tmp[l] = 0;
        return yyjson_mut_strcpy(doc, tmp);
    }
    case 6: return yyjson_mut_arr(doc);
    default: return yyjson_mut_obj(doc);
    }
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 8) return 0;
    if (size > MAX_INPUT) size = MAX_INPUT;

    /* 헤더: 읽기옵션, 값종류, JSON 길이(2), 포인터 길이, 연산 수 */
    yyjson_read_flag rflg = pick_read_flag(data[0]);
    uint8_t vkind = data[1];
    size_t body_total = size - 6;
    size_t jlen = (((size_t)data[2]) | ((size_t)data[3] << 8)) % (body_total + 1);
    size_t plen_req = data[4];
    size_t nops = data[5] % (MAX_OPS + 1);
    const uint8_t *ops = data + 6;
    size_t avail = size - 6;
    if (nops > avail) nops = avail;
    const uint8_t *body = ops + nops;
    size_t blen = avail - nops;
    if (jlen > blen) jlen = blen;
    const uint8_t *jsrc = body;
    size_t plen = plen_req > blen - jlen ? blen - jlen : plen_req;
    const uint8_t *pool = body + jlen;
    const uint8_t *extra = pool + plen;
    size_t elen = blen - jlen - plen;

    /* JSON 텍스트 복사본 (정확한 크기 + NUL) */
    char *jbuf = (char *)malloc(jlen + 1);
    if (!jbuf) return 0;
    memcpy(jbuf, jsrc, jlen);
    jbuf[jlen] = 0;

    /* 포인터 문자열 풀 (NUL 종료) */
    char *pbuf = (char *)malloc(plen + 1);
    if (!pbuf) { free(jbuf); return 0; }
    memcpy(pbuf, pool, plen);
    pbuf[plen] = 0;

    yyjson_doc *idoc = yyjson_read_opts(jbuf, jlen, rflg, &ALC, NULL);
    yyjson_mut_doc *mdoc = NULL;
    if (idoc) mdoc = yyjson_doc_mut_copy(idoc, &ALC);
    if (!mdoc) {
        mdoc = yyjson_mut_doc_new(&ALC);
        if (!mdoc) goto done;
        yyjson_mut_val *r = yyjson_mut_obj(mdoc);
        if (!r) goto done;
        yyjson_mut_doc_set_root(mdoc, r);
    }

    size_t i;
    for (i = 0; i < nops; i++) {
        uint8_t op = ops[i];
        yyjson_mut_val *root = yyjson_mut_doc_get_root(mdoc);
        if (!root) break;

        /* 이 연산에서 쓸 포인터 문자열 */
        size_t start = (size_t)(op >> 4) * (plen + 1) / 16;
        if (start > plen) start = plen;
        const char *ptr = pbuf + start;

        /* 새 값 재료 */
        size_t eoff = (size_t)(op >> 4) % (elen + 1);
        const uint8_t *vp = extra + eoff;
        size_t vn = elen - eoff;

        switch (op % 9) {
        case 0: { // [gapfuzz-ops] yyjson_mut_ptr_set
            yyjson_mut_val *nv = make_val(mdoc, vkind + (uint8_t)i, vp, vn);
            if (!nv) break;
            (void)yyjson_mut_ptr_set(root, ptr, nv, mdoc);
            break;
        }
        case 1: { // [gapfuzz-ops] yyjson_mut_ptr_replace
            yyjson_mut_val *nv = make_val(mdoc, vkind + (uint8_t)i, vp, vn);
            if (!nv) break;
            (void)yyjson_mut_ptr_replace(root, ptr, nv);
            break;
        }
        case 2: { // [gapfuzz-ops] yyjson_mut_ptr_add
            yyjson_mut_val *nv = make_val(mdoc, vkind + (uint8_t)i, vp, vn);
            if (!nv) break;
            (void)yyjson_mut_ptr_add(root, ptr, nv, mdoc);
            break;
        }
        case 3: { // [gapfuzz-ops] yyjson_mut_ptr_remove
            (void)yyjson_mut_ptr_remove(root, ptr);
            break;
        }
        case 4: { // [gapfuzz-ops] yyjson_mut_doc_imut_copy
            // [gapfuzz-ops] yyjson_ptr_get_str
            yyjson_doc *cp = yyjson_mut_doc_imut_copy(mdoc, &ALC);
            if (!cp) break;
            yyjson_val *ir = yyjson_doc_get_root(cp);
            if (ir) {
                const char *s = NULL;
                if (yyjson_ptr_get_str(ir, ptr, &s) && s) {
                    volatile char c = s[0]; (void)c;
                }
            }
            yyjson_doc_free(cp);
            break;
        }
        case 5: { // [gapfuzz-ops] yyjson_mut_write_number
            yyjson_mut_val *nv = make_val(mdoc, (uint8_t)(2 + (op >> 4) % 3), vp, vn);
            if (!nv || !yyjson_mut_is_num(nv)) break;
            char nb[64]; // 헤더 규정: 최소 40바이트
            char *end = yyjson_mut_write_number(nv, nb);
            if (end && end >= nb && end <= nb + sizeof(nb)) {
                volatile size_t l = (size_t)(end - nb); (void)l;
            }
            break;
        }
        case 6: { // [gapfuzz-ops] yyjson_equals
            // 원본 문서, mutable 복사본, extra로 읽은 다른 문서끼리 비교
            yyjson_doc *cp = yyjson_mut_doc_imut_copy(mdoc, &ALC);
            if (!cp) break;
            yyjson_val *a = yyjson_doc_get_root(cp);
            yyjson_val *b = idoc ? yyjson_doc_get_root(idoc) : NULL;
            if (a) (void)yyjson_equals(a, a);
            if (a && b) {
                (void)yyjson_equals(a, b);
                (void)yyjson_equals(b, a);
            }
            char *ebuf = (char *)malloc(elen + 1);
            if (ebuf) {
                memcpy(ebuf, extra, elen);
                ebuf[elen] = 0;
                yyjson_doc *d2 = yyjson_read_opts(ebuf, elen, rflg, &ALC, NULL);
                if (d2) {
                    yyjson_val *c = yyjson_doc_get_root(d2);
                    if (a && c) (void)yyjson_equals(a, c);
                    yyjson_doc_free(d2);
                }
                free(ebuf);
            }
            yyjson_doc_free(cp);
            break;
        }
        case 7: { // [gapfuzz-ops] yyjson_locate_pos
            size_t line = 0, col = 0, chr = 0;
            size_t pos = vn ? ((size_t)vp[0] | ((vn > 1 ? (size_t)vp[1] : 0) << 8))
                            : 0;
            pos %= (jlen + 2); // 범위 안팎 모두 시도
            if (yyjson_locate_pos(jbuf, jlen, pos, &line, &col, &chr)) {
                volatile size_t s = line + col + chr; (void)s;
            }
            break;
        }
        default: { // [gapfuzz-ops] yyjson_incr_read
            if (jlen == 0) break;
            // 인크리멘털 읽기: 버퍼를 조금씩 늘려가며 호출 (비 INSITU)
            yyjson_incr_state *st = yyjson_incr_new(jbuf, jlen, rflg, &ALC);
            if (!st) break;
            size_t iters = 1 + (size_t)(op >> 4) * 4; // 최대 61
            if (iters > MAX_ITER) iters = MAX_ITER;
            size_t step = (jlen + iters - 1) / iters;
            if (step == 0) step = 1;
            size_t len = 0, k;
            for (k = 0; k < MAX_ITER; k++) {
                len += step;
                if (len > jlen) len = jlen;
                yyjson_read_err err;
                memset(&err, 0, sizeof(err));
                yyjson_doc *d = yyjson_incr_read(st, len, &err);
                if (d) {
                    yyjson_doc_free(d);
                    break;
                }
                if (err.code != YYJSON_READ_ERROR_MORE) break; // 실패면 더 쓰지 않음
                if (len >= jlen) break;
            }
            yyjson_incr_free(st);
            break;
        }
        }
    }

done:
    yyjson_doc_free(idoc);
    yyjson_mut_doc_free(mdoc);
    free(pbuf);
    free(jbuf);
    return 0;
}
