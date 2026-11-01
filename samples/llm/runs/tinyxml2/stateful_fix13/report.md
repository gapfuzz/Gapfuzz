# LLM 하네스 수정 — tinyxml2/stateful, 제안 13

- 모델: `claude-sonnet-5-5`
- 제안: `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLElement::Accept`)에서만 불립니다. 내부 호출은 1번째 인자 `element`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6317/6308 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix13/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -182,6 +182,16 @@
             printer.PushText(fdp.ConsumeRandomLengthString(kMaxStr).c_str(), fdp.ConsumeBool());
             printer.PushComment(str);
             printer.CloseElement(fdp.ConsumeBool());
+            {
+                XMLPrinter visitPrinter(nullptr, fdp.ConsumeBool());  // [gapfuzz-llm] VisitEnter를 직접 호출하기 위한 별도 프린터
+                XMLElement *target = nullptr;  // [gapfuzz-llm] VisitEnter에 넘길 요소(트리 연결/미연결/다른 문서)를 입력으로 고름
+                switch (fdp.ConsumeIntegralInRange<int>(0, 2)) {  // [gapfuzz-llm] 입력 바이트로 요소 상태 선택
+                case 0: target = ele ? ele : doc.RootElement(); break;  // [gapfuzz-llm] 기존처럼 트리에 연결된 요소(부모 있음)도 계속 나오게 함
+                case 1: target = doc.NewElement(str); break;  // [gapfuzz-llm] 트리에 연결 안 된 요소로 element.Parent()가 null인 경로 도달
+                default: target = other.NewElement(str); break;  // [gapfuzz-llm] 다른 문서의 부모 없는 요소 사용
+                }
+                if (target) visitPrinter.VisitEnter(*target, target->FirstAttribute());  // [gapfuzz-llm] null 참조를 넘기지 않도록 검사 후 직접 호출
+            }
             break;
         }
         case 15: {  // 핸들 탐색
```
