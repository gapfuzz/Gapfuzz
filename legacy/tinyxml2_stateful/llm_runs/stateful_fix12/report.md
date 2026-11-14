# LLM 하네스 수정 — tinyxml2/stateful, 제안 12

- 모델: `claude-sonnet-5-5`
- 제안: `XMLPrinter::VisitEnter(const XMLDocument &)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLDocument::Accept`)에서만 불립니다. 내부 호출은 1번째 인자 `doc`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6242/6019 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix12/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -177,6 +177,11 @@
         case 14: {  // XMLPrinter 직접 사용
             XMLPrinter printer(nullptr, fdp.ConsumeBool());
             printer.PushHeader(fdp.ConsumeBool(), fdp.ConsumeBool());
+            XMLDocument bomDoc;  // [gapfuzz-llm] VisitEnter에 넘길 BOM 상태를 바꿔 볼 별도 문서
+            bomDoc.SetBOM(fdp.ConsumeBool());  // [gapfuzz-llm] doc.HasBOM()이 참/거짓 모두 나오도록 입력에서 BOM 설정을 고름
+            const int visitSel = fdp.ConsumeIntegralInRange<int>(0, 2);  // [gapfuzz-llm] VisitEnter 인자로 쓸 문서를 입력에서 선택
+            const XMLDocument &visitDoc = visitSel == 0 ? doc : (visitSel == 1 ? other : bomDoc);  // [gapfuzz-llm] 원래 doc도 계속 나오게 하면서 다른 문서도 선택
+            printer.VisitEnter(visitDoc);  // [gapfuzz-llm] 내부 Accept 경로 대신 VisitEnter(const XMLDocument&)를 직접 호출해 BOM 분기 도달
             printer.OpenElement(str, fdp.ConsumeBool());
             printer.PushAttribute("a", fdp.ConsumeIntegral<int>());
             printer.PushText(fdp.ConsumeRandomLengthString(kMaxStr).c_str(), fdp.ConsumeBool());
```
