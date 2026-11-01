# LLM 하네스 수정 — zlib/official, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `uncompress(Bytef *, uLongf *, const Bytef *, uLong)`의 2번째 인자 `destLen`를 하네스가 고정합니다(17행에서 항상 같은 객체 `&buffer_length`) (라이브러리 내부 `uncompress2` → `uncompress2_z`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 3개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/3 | - | 1879/2318 |
| 2 | 통과 | 1/3 | - | 3216/2719 |

**채택 후보: 시도 1** (`harnesses/zlib/llm/official_fix1/try1.cc`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -14,6 +14,19 @@
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
   uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
+  if (size >= 1) {  // [gapfuzz-llm] 입력 첫 바이트를 destLen 선택용으로 사용하기 위해 확인
+    uint8_t selector = data[0];  // [gapfuzz-llm] 첫 바이트로 destLen을 원래 값으로 둘지 바꿀지 결정
+    data++;  // [gapfuzz-llm] 선택용 바이트를 소비하고 나머지를 압축 데이터로 사용
+    size--;  // [gapfuzz-llm] 소비한 만큼 입력 크기 감소
+    if ((selector & 1) && size >= 3) {  // [gapfuzz-llm] 홀수일 때만 destLen을 입력에서 가져와 원래 값(전체 버퍼)도 계속 나오게 함
+      uint32_t v = (static_cast<uint32_t>(data[0]) << 16) |
+                   (static_cast<uint32_t>(data[1]) << 8) |
+                   static_cast<uint32_t>(data[2]);  // [gapfuzz-llm] 입력 3바이트로 destLen 후보 값 생성
+      buffer_length = static_cast<uLongf>(v % (sizeof(buffer) + 1));  // [gapfuzz-llm] 0부터 버퍼 크기까지(0 포함)로 제한해 버퍼 오버플로 방지
+      data += 3;  // [gapfuzz-llm] destLen용으로 쓴 바이트 소비
+      size -= 3;  // [gapfuzz-llm] 소비한 만큼 입력 크기 감소
+    }
+  }
   if (Z_OK != uncompress(buffer, &buffer_length, data,
                          static_cast<uLong>(size))) {
     return 0;
```
