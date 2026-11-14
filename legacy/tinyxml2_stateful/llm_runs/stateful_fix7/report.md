# LLM 하네스 수정 — tinyxml2/stateful, 제안 7

- 모델: `claude-sonnet-5-5`
- 제안: 하네스가 `XMLDocument::SetBOM(bool)`를 부르지 않아 1번째 인자 `useBOM` 값이 들어가지 않습니다 (필드 `_writeBOM`를 거쳐 조건에 쓰임) → 호출을 추가하세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6162/5630 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix7/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -42,6 +42,7 @@
     XMLDocument doc(fdp.ConsumeBool(), fdp.ConsumeBool() ? COLLAPSE_WHITESPACE : PRESERVE_WHITESPACE);
     std::string xml = fdp.ConsumeRandomLengthString(4096);
     doc.Parse(xml.c_str());
+    switch (fdp.ConsumeIntegralInRange<int>(0, 2)) { case 1: doc.SetBOM(true); break; case 2: doc.SetBOM(false); break; default: break; }  // [gapfuzz-llm] SetBOM을 호출하지 않아 HasBOM()이 참이 되지 않았음; 0이면 파싱 결과 그대로 두고 1·2에서 BOM 값을 퍼저 입력으로 선택
 
     XMLDocument other;          // DeepClone / 다른 문서 간 동작 확인용
     XMLNode *cur = &doc;
```
