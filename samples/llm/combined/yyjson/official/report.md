# LLM 하네스 수정 — yyjson/official, 제안 1,2,3,4,5,9

- 모델: `claude-sonnet-5-5`
- 제안: `yyjson_read_opts(char *, size_t, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)`의 5번째 인자 `err`를 하네스가 고정합니다(39행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 제안: `yyjson_read_opts(char *, size_t, yyjson_read_flag, const yyjson_alc *, yyjson_read_err *)`의 4번째 인자 `alc`를 하네스가 고정합니다(39행에서 항상 같은 객체 `&FUZZ_ALC`) → 퍼저 입력으로 바꾸세요
- 제안: `yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 3번째 인자 `alc`를 하네스가 고정합니다(41행에서 항상 같은 객체 `&FUZZ_ALC`) (라이브러리 내부 `write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 5번째 인자 `err`를 하네스가 고정합니다(41행에서 항상 `0`) (라이브러리 내부 `write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `yyjson_write_opts(const yyjson_doc *, yyjson_write_flag, const yyjson_alc *, size_t *, yyjson_write_err *)`의 4번째 인자 `len`를 하네스가 고정합니다(41행에서 항상 `0`) (라이브러리 내부 `write_root`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `yyjson_doc_mut_copy(const yyjson_doc *, const yyjson_alc *)`의 2번째 인자 `alc`를 하네스가 고정합니다(40행에서 항상 같은 객체 `&FUZZ_ALC`) (라이브러리 내부 `yyjson_mut_doc_new`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 7개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 6/7 | 1: 1/2, 2: 1/1, 3: 1/1, 4: 1/1, 5: 1/1, 9: 1/1 | - | 5225/3056 |
| 2 | 통과 | 7/7 | 1: 2/2, 2: 1/1, 3: 1/1, 4: 1/1, 5: 1/1, 9: 1/1 | - | 7742/4283 |

**채택 후보: 시도 2** (`harnesses/yyjson/llm/official_combined/try2.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -32,13 +32,49 @@
     fuzz_malloc, fuzz_realloc, fuzz_free, NULL
 };
 
+/* [gapfuzz-llm] n번째 malloc만 실패시키는 할당자: 읽기 중 메모리 할당 실패 경로(MEMORY_ALLOCATION)를 만들기 위함 */
+typedef struct {
+    unsigned count;
+    unsigned fail_at;
+} fail_ctx;
+
+static void *failing_malloc(void *ctx, size_t size) { // [gapfuzz-llm] 지정한 순번의 malloc에서 NULL 반환
+    fail_ctx *fc = (fail_ctx *)ctx;
+    fc->count++;
+    if (fc->fail_at != 0 && fc->count == fc->fail_at) return NULL;
+    return fuzz_malloc(NULL, size);
+}
+
+static void *failing_realloc(void *ctx, void *ptr, size_t old_size, size_t size) { // [gapfuzz-llm] realloc은 기존 동작 그대로 전달
+    (void)ctx;
+    return fuzz_realloc(NULL, ptr, old_size, size);
+}
+
+static void failing_free(void *ctx, void *ptr) { // [gapfuzz-llm] free는 기존 동작 그대로 전달
+    (void)ctx;
+    fuzz_free(NULL, ptr);
+}
+
 /*----------------------------------------------------------------------------*/
 
 static void test_with_flags(const uint8_t *data, size_t size,
-                            yyjson_read_flag rflg, yyjson_write_flag wflg) {
-    yyjson_doc *idoc = yyjson_read_opts((char *)data, size, rflg, &FUZZ_ALC, NULL);
-    yyjson_mut_doc *mdoc = yyjson_doc_mut_copy(idoc, &FUZZ_ALC);
-    char *ijson = yyjson_write_opts(idoc, wflg, &FUZZ_ALC, NULL, NULL);
+                            yyjson_read_flag rflg, yyjson_write_flag wflg,
+                            uint8_t sel, uint8_t fail_at) { // [gapfuzz-llm] 실패 순번 인자 추가
+    yyjson_read_err rerr; // [gapfuzz-llm] err 인자를 NULL/비NULL로 번갈아 넘기기 위한 버퍼
+    yyjson_write_err werr; // [gapfuzz-llm] 쓰기 err 인자용 버퍼
+    size_t wlen = 0; // [gapfuzz-llm] 쓰기 길이 인자용 버퍼
+    fail_ctx fctx = { 0, fail_at }; // [gapfuzz-llm] 할당 실패 시점 제어용 컨텍스트
+    yyjson_alc fail_alc = { failing_malloc, failing_realloc, failing_free, &fctx }; // [gapfuzz-llm] 일부 malloc을 실패시키는 할당자
+    const yyjson_alc *read_alc = (sel & 0x01) ? &FUZZ_ALC : NULL; // [gapfuzz-llm] 읽기 alc를 입력 비트로 NULL/FUZZ_ALC 선택
+    if ((sel & 0x01) && fail_at != 0) read_alc = &fail_alc; // [gapfuzz-llm] 실패 순번이 있으면 실패 할당자로 읽어 MEMORY_ALLOCATION 에러 유도
+    yyjson_read_err *read_err = (sel & 0x02) ? &rerr : NULL; // [gapfuzz-llm] 읽기 err를 입력 비트로 NULL/비NULL 선택
+    const yyjson_alc *write_alc = (sel & 0x04) ? &FUZZ_ALC : NULL; // [gapfuzz-llm] 쓰기 alc를 입력 비트로 NULL/FUZZ_ALC 선택
+    yyjson_write_err *write_err = (sel & 0x08) ? &werr : NULL; // [gapfuzz-llm] 쓰기 err를 입력 비트로 NULL/비NULL 선택
+    size_t *write_len = (sel & 0x10) ? &wlen : NULL; // [gapfuzz-llm] 쓰기 len을 입력 비트로 NULL/비NULL 선택
+    const yyjson_alc *copy_alc = (sel & 0x20) ? &FUZZ_ALC : NULL; // [gapfuzz-llm] 복사 alc를 입력 비트로 NULL/FUZZ_ALC 선택
+    yyjson_doc *idoc = yyjson_read_opts((char *)data, size, rflg, read_alc, read_err); // [gapfuzz-llm] alc, err 인자를 퍼저 입력 기반으로 변경
+    yyjson_mut_doc *mdoc = yyjson_doc_mut_copy(idoc, copy_alc); // [gapfuzz-llm] alc 인자를 퍼저 입력 기반으로 변경
+    char *ijson = yyjson_write_opts(idoc, wflg, write_alc, write_len, write_err); // [gapfuzz-llm] alc, len, err 인자를 퍼저 입력 기반으로 변경
     if (ijson) FUZZ_ALC.free(FUZZ_ALC.ctx, ijson);
     char *mjson = yyjson_mut_write_opts(mdoc, wflg, &FUZZ_ALC, NULL, NULL);
     if (mjson) FUZZ_ALC.free(FUZZ_ALC.ctx, mjson);
@@ -47,14 +83,24 @@
 }
 
 int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
+    uint8_t sel = 0x3F; // [gapfuzz-llm] 입력이 비었을 땐 원래 동작(모든 인자 고정값)을 유지
+    uint8_t fail_at = 0; // [gapfuzz-llm] 0이면 할당 실패 없음(원래 동작)
+    if (size >= 2) { // [gapfuzz-llm] 앞쪽 2바이트를 인자 선택/실패 순번용으로 사용
+        sel = data[0]; // [gapfuzz-llm] 선택 비트를 첫 바이트에서 얻음
+        fail_at = data[1] & 0x07; // [gapfuzz-llm] 둘째 바이트로 몇 번째 malloc을 실패시킬지 선택(0~7)
+        data += 2; // [gapfuzz-llm] 나머지 바이트는 기존대로 JSON 입력으로 사용
+        size -= 2; // [gapfuzz-llm] 소비한 바이트만큼 길이 보정
+    }
     test_with_flags(data, size,
                     YYJSON_READ_NOFLAG,
-                    YYJSON_WRITE_NOFLAG);
+                    YYJSON_WRITE_NOFLAG,
+                    sel, fail_at); // [gapfuzz-llm] 선택 비트와 실패 순번 전달
     test_with_flags(data, size,
                     YYJSON_READ_JSON5,
                     YYJSON_WRITE_PRETTY |
                     YYJSON_WRITE_ESCAPE_UNICODE |
                     YYJSON_WRITE_ESCAPE_SLASHES |
-                    YYJSON_WRITE_ALLOW_INF_AND_NAN);
+                    YYJSON_WRITE_ALLOW_INF_AND_NAN,
+                    sel, fail_at); // [gapfuzz-llm] 선택 비트와 실패 순번 전달
     return 0;
 }
```
