# LLM 하네스 수정 — tinyxml2/official, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(13행에서 기본값) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 2/2 | - | 1509/1624 |

**채택 후보: 시도 1** (`harnesses/llm/official_fix1/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -10,6 +10,10 @@
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
-    doc.Parse(data_string.c_str());
+    size_t nBytes = static_cast<size_t>(-1);  // [gapfuzz-llm] 기본값(-1, strlen 사용)이 계속 나오도록 유지
+    if (size >= 2 && (data[0] & 3) != 0) {  // [gapfuzz-llm] 입력 앞쪽 바이트로 nBytes를 쓸지 고름(약 1/4은 원래 값 유지)
+        nBytes = ((static_cast<size_t>(data[0]) << 8) | data[1]) % (size + 1);  // [gapfuzz-llm] 0~size 범위로 제한해 nBytes==0 분기를 열고 버퍼 초과 읽기를 막음
+    }  // [gapfuzz-llm] nBytes를 퍼저 입력에서 선택
+    doc.Parse(data_string.c_str(), nBytes);  // [gapfuzz-llm] 고정된 기본 nBytes 대신 퍼저가 고른 값 전달
     return 0;
 }
```
