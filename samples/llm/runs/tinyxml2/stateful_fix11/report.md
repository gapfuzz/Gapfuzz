# LLM 하네스 수정 — tinyxml2/stateful, 제안 11

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 `COLLAPSE_WHITESPACE`, `PRESERVE_WHITESPACE`, `기본값` 중에서만 고릅니다(42행, 46행) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6346/5474 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix11/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -39,7 +39,7 @@
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
     FuzzedDataProvider fdp(data, size);
 
-    XMLDocument doc(fdp.ConsumeBool(), fdp.ConsumeBool() ? COLLAPSE_WHITESPACE : PRESERVE_WHITESPACE);
+    XMLDocument doc(fdp.ConsumeBool(), fdp.PickValueInArray<Whitespace>({PRESERVE_WHITESPACE, COLLAPSE_WHITESPACE, PEDANTIC_WHITESPACE}));  // [gapfuzz-llm] PEDANTIC_WHITESPACE도 입력에서 고르게 해 752행 분기를 열고, 기존 두 모드도 계속 나오게 함
     std::string xml = fdp.ConsumeRandomLengthString(4096);
     doc.Parse(xml.c_str());
```
