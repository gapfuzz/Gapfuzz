# LLM 하네스 수정 — zlib/official, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: `uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 3번째 인자 `source`에 하네스가 null을 넘긴 적이 없습니다(17행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1353/1142 |

**채택 후보: 시도 1** (`harnesses/zlib/llm/official_fix2/try1.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -14,7 +14,8 @@
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
   uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
-  if (Z_OK != uncompress(buffer, &buffer_length, data,
+  const Bytef* source = (size > 0 && (data[0] & 3) == 0) ? nullptr : data;  // [gapfuzz-llm] 입력 첫 바이트로 약 1/4 확률로 source에 nullptr을 넘겨 source == NULL 분기(Z_STREAM_ERROR 반환)를 도달시킴
+  if (Z_OK != uncompress(buffer, &buffer_length, source,  // [gapfuzz-llm] data 대신 입력에서 고른 source 사용(원래 data도 계속 전달됨)
                          static_cast<uLong>(size))) {
     return 0;
   }
```
