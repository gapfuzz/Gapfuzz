# 호출 안 함 API 추가 — cjson/_union

- 모델: `claude-sonnet-5-5`
- 수정 전: 공개 API 78개 중 호출 안 함 71개, 라인 42.43% · 분기 45.07%
- 추가를 요청한 API 10개: `cJSON_Compare`, `cJSON_AddItemReferenceToObject`, `cJSON_ReplaceItemInObjectCaseSensitive`, `cJSON_Duplicate`, `cJSON_CreateIntArray`, `cJSON_DeleteItemFromArray`, `cJSON_CreateStringArray`, `cJSON_SetValuestring`, `cJSON_CreateFloatArray`, `cJSON_CreateDoubleArray`

| 시도 | 결과 | 실행된 API | 호출 안 함 | 라인 | 분기 | 사라진 API | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | 통과 | 10/10 | 53 | 45.57% | 47.3% | 0 | - | 3718/9360 |

수정 전 수치는 진단 때(기본 120초 × 1회), 시도별 수치는 검사 퍼징(짧음)의 중앙값이라 길이가 다릅니다. 정식 비교는 같은 조건의 긴 실험으로 하세요.

**채택: 시도 1** → `harnesses/cjson/gapfuzz_ops.c`. 사람이 읽고 쓰세요.

```diff
--- 수정 전
+++ 시도 1
@@ -0,0 +1,227 @@
+#include <stdlib.h>
+#include <stdint.h>
+#include <string.h>
+
+#ifdef __cplusplus
+extern "C" {
+#endif
+
+#include "cJSON.h"
+
+int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size); /* required by C89 */
+
+#define MAX_INPUT 65536
+#define MAX_OPS   64
+#define MAX_NUM   64
+#define MAX_STR   16
+#define STR_LEN   33
+
+/* 입력 바이트를 순환하며 읽는 커서 */
+typedef struct {
+    const uint8_t *p;
+    size_t len;
+    size_t pos;
+} cursor_t;
+
+static uint8_t next_byte(cursor_t *c)
+{
+    if (c->len == 0) return 0;
+    return c->p[c->pos++ % c->len];
+}
+
+/* 작업 슬롯 번호 */
+enum { S_DOC, S_SRC, S_WORK, S_ARR, S_REFS, S_STR, S_COUNT };
+
+/* 입력에서 NUL 로 끝나는 짧은 문자열을 만든다 */
+static void fill_string(cursor_t *c, char *out)
+{
+    size_t n = next_byte(c) % (STR_LEN - 1);
+    size_t i;
+    for (i = 0; i < n; i++) out[i] = (char)next_byte(c);
+    out[n] = '\0';
+}
+
+int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
+{
+    cJSON *s[S_COUNT] = {NULL};
+    cJSON *tmp;
+    cursor_t cur;
+    char *json_text;
+    size_t payload_len, json_len, rest_len, i;
+    int nops, op, ok = 1;
+
+    if (size < 4) return 0;
+    if (size > MAX_INPUT) size = MAX_INPUT;
+
+    nops = 1 + (data[0] % MAX_OPS);           /* 반복 횟수 (1..64) */
+    payload_len = size - 3;
+    json_len = (payload_len * (size_t)data[2]) / 255; /* JSON 텍스트와 나머지 데이터의 경계 */
+    if (json_len > payload_len) json_len = payload_len;
+    rest_len = payload_len - json_len;
+
+    json_text = (char*)malloc(json_len + 1);
+    if (json_text == NULL) return 0;
+    memcpy(json_text, data + 3, json_len);
+    json_text[json_len] = '\0';
+
+    cur.p = data + 3 + json_len;
+    cur.len = rest_len;
+    cur.pos = data[1];                        /* 시작 위치도 입력으로 변하게 한다 */
+
+    /* 준비: 문서 파싱, 실패하면 빈 객체 사용 */
+    s[S_DOC] = cJSON_ParseWithOpts(json_text, NULL, 0);
+    free(json_text);
+    if (s[S_DOC] == NULL) s[S_DOC] = cJSON_CreateObject();
+    if (s[S_DOC] != NULL) s[S_SRC] = cJSON_Duplicate(s[S_DOC], 1); /* 변경하지 않는 참조 대상 */
+    s[S_WORK] = cJSON_CreateObject();
+    s[S_ARR]  = cJSON_CreateArray();
+    s[S_REFS] = cJSON_CreateObject();
+    s[S_STR]  = cJSON_CreateString("init");
+    for (i = 0; i < S_COUNT; i++) if (s[i] == NULL) ok = 0;
+
+    for (op = 0; ok && op < nops; op++) {
+        switch (next_byte(&cur) % 10) {
+        case 0: {
+            /* [gapfuzz-ops] cJSON_Compare */
+            cJSON *a = s[next_byte(&cur) % S_COUNT];
+            cJSON *b = s[next_byte(&cur) % S_COUNT];
+            cJSON_bool cs = next_byte(&cur) & 1;
+            (void)cJSON_Compare(a, b, cs);
+            (void)cJSON_Compare(a, a, cs);
+            break;
+        }
+        case 1: {
+            /* [gapfuzz-ops] cJSON_AddItemReferenceToObject */
+            /* 참조 대상(src)은 변경하지 않고, 해제는 refs 를 먼저 한다 */
+            char key[STR_LEN];
+            fill_string(&cur, key);
+            (void)cJSON_AddItemReferenceToObject(s[S_REFS], key, s[S_SRC]);
+            break;
+        }
+        case 2: {
+            /* [gapfuzz-ops] cJSON_ReplaceItemInObjectCaseSensitive */
+            cJSON *target = (next_byte(&cur) & 1) ? s[S_WORK] : s[S_DOC];
+            cJSON *newitem = NULL;
+            char key[STR_LEN];
+            fill_string(&cur, key);
+            if ((next_byte(&cur) & 1) && target->child != NULL && target->child->string != NULL) {
+                /* 기존 키로 교체를 시도한다 */
+                strncpy(key, target->child->string, STR_LEN - 1);
+                key[STR_LEN - 1] = '\0';
+            }
+            switch (next_byte(&cur) % 4) {
+            case 0:  newitem = cJSON_CreateNumber((double)next_byte(&cur)); break;
+            case 1:  newitem = cJSON_Duplicate(s[S_SRC], 1); break;
+            case 2:  newitem = cJSON_CreateString(key); break;
+            default: newitem = cJSON_CreateNull(); break;
+            }
+            if (newitem == NULL) break;
+            if (!cJSON_IsObject(target) ||
+                !cJSON_ReplaceItemInObjectCaseSensitive(target, key, newitem)) {
+                cJSON_Delete(newitem); /* 실패하면 소유권이 넘어가지 않는다 */
+            }
+            break;
+        }
+        case 3: {
+            /* [gapfuzz-ops] cJSON_Duplicate */
+            cJSON *orig = s[next_byte(&cur) % S_COUNT];
+            cJSON_bool recurse = next_byte(&cur) & 1;
+            cJSON *dup = cJSON_Duplicate(orig, recurse);
+            if (dup != NULL) {
+                (void)cJSON_Compare(orig, dup, next_byte(&cur) & 1);
+                cJSON_Delete(dup);
+            }
+            break;
+        }
+        case 4: {
+            /* [gapfuzz-ops] cJSON_CreateIntArray */
+            int nums[MAX_NUM];
+            int n = next_byte(&cur) % (MAX_NUM + 1); /* 배열 크기 이하로 제한 */
+            int k;
+            for (k = 0; k < MAX_NUM; k++) {
+                nums[k] = (int)(((uint32_t)next_byte(&cur) << 24) | ((uint32_t)next_byte(&cur) << 16) |
+                                ((uint32_t)next_byte(&cur) << 8) | (uint32_t)next_byte(&cur));
+            }
+            tmp = cJSON_CreateIntArray(nums, n);
+            if (tmp != NULL) { cJSON_Delete(s[S_ARR]); s[S_ARR] = tmp; }
+            break;
+        }
+        case 5: {
+            /* [gapfuzz-ops] cJSON_DeleteItemFromArray */
+            cJSON *target = (next_byte(&cur) & 1) ? s[S_ARR] : s[S_DOC];
+            int which = (int)(signed char)next_byte(&cur); /* 음수 포함 */
+            if (cJSON_IsArray(target)) cJSON_DeleteItemFromArray(target, which);
+            break;
+        }
+        case 6: {
+            /* [gapfuzz-ops] cJSON_CreateStringArray */
+            char pool[MAX_STR][STR_LEN];
+            const char *ptrs[MAX_STR];
+            int n = next_byte(&cur) % (MAX_STR + 1);
+            int k;
+            for (k = 0; k < MAX_STR; k++) { fill_string(&cur, pool[k]); ptrs[k] = pool[k]; }
+            tmp = cJSON_CreateStringArray(ptrs, n);
+            if (tmp != NULL) { cJSON_Delete(s[S_ARR]); s[S_ARR] = tmp; }
+            break;
+        }
+        case 7: {
+            /* [gapfuzz-ops] cJSON_SetValuestring */
+            cJSON *target = s[S_STR];
+            cJSON *c;
+            char val[STR_LEN];
+            int k = next_byte(&cur) % 4;
+            fill_string(&cur, val);
+            if (k != 0) {
+                cJSON *parent = (k == 1) ? s[S_ARR] : (k == 2) ? s[S_DOC] : s[S_WORK];
+                for (c = parent->child; c != NULL; c = c->next) {
+                    if (cJSON_IsString(c)) { target = c; break; }
+                }
+            }
+            (void)cJSON_SetValuestring(target, val);
+            break;
+        }
+        case 8: {
+            /* [gapfuzz-ops] cJSON_CreateFloatArray */
+            float nums[MAX_NUM];
+            int n = next_byte(&cur) % (MAX_NUM + 1);
+            int k, b;
+            for (k = 0; k < MAX_NUM; k++) {
+                uint8_t raw[sizeof(float)];
+                for (b = 0; b < (int)sizeof(float); b++) raw[b] = next_byte(&cur);
+                memcpy(&nums[k], raw, sizeof(float));
+            }
+            tmp = cJSON_CreateFloatArray(nums, n);
+            if (tmp != NULL) { cJSON_Delete(s[S_ARR]); s[S_ARR] = tmp; }
+            break;
+        }
+        default: {
+            /* [gapfuzz-ops] cJSON_CreateDoubleArray */
+            double nums[MAX_NUM];
+            int n = next_byte(&cur) % (MAX_NUM + 1);
+            int k, b;
+            for (k = 0; k < MAX_NUM; k++) {
+                uint8_t raw[sizeof(double)];
+                for (b = 0; b < (int)sizeof(double); b++) raw[b] = next_byte(&cur);
+                memcpy(&nums[k], raw, sizeof(double));
+            }
+            tmp = cJSON_CreateDoubleArray(nums, n);
+            if (tmp != NULL) { cJSON_Delete(s[S_ARR]); s[S_ARR] = tmp; }
+            break;
+        }
+        }
+    }
+
+    /* 정리: 참조를 든 refs 를 src 보다 먼저 해제한다 */
+    cJSON_Delete(s[S_REFS]);
+    cJSON_Delete(s[S_SRC]);
+    cJSON_Delete(s[S_DOC]);
+    cJSON_Delete(s[S_WORK]);
+    cJSON_Delete(s[S_ARR]);
+    cJSON_Delete(s[S_STR]);
+
+    return 0;
+}
+
+#ifdef __cplusplus
+}
+#endif
```
