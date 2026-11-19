# LLM 하네스 수정 — zlib/official, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 1번째 인자 `dest`에 하네스가 null을 넘긴 적이 없습니다(17행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1359/1267 |

**채택 후보: 시도 1** (`harnesses/zlib/llm/official_fix3/try1.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -14,7 +14,8 @@
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
   uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
-  if (Z_OK != uncompress(buffer, &buffer_length, data,
+  Bytef* dest = (size > 0 && (data[0] & 0x07) == 0) ? nullptr : buffer;  // [gapfuzz-llm] 입력 첫 바이트로 dest에 nullptr도 가끔(약 1/8) 넘겨 dest == NULL 분기 도달
+  if (Z_OK != uncompress(dest, &buffer_length, data,  // [gapfuzz-llm] 고정 buffer 대신 입력으로 고른 dest 사용 (나머지 7/8은 원래 buffer)
                          static_cast<uLong>(size))) {
     return 0;
   }
```
