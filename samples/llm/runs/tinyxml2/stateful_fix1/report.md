# LLM 하네스 수정 — tinyxml2/stateful, 제안 1

- 모델: `claude-sonnet-5-5`
- 제안: `XMLComment::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요 (같은 호출이 5개 구현 클래스에 영향: `XMLComment::ShallowClone`, `XMLDeclaration::ShallowClone`, `XMLElement::ShallowClone`, `XMLText::ShallowClone`, `XMLUnknown::ShallowClone`)
- 겨냥한 분기: 5개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 5/5 | - | 7136/5695 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix1/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -158,10 +158,13 @@
                 XMLNode *clone = cur->DeepClone(&other);
                 if (clone) other.InsertEndChild(clone);
             } else if (cur != &doc) {
-                XMLNode *clone = cur->ShallowClone(&doc);
+                const int target = fdp.ConsumeIntegralInRange<int>(0, 2);  // [gapfuzz-llm] 복제 대상 문서를 입력으로 골라 doc/nullptr/other 모두 시도
+                XMLDocument *cloneDoc = (target == 0) ? &doc : (target == 1) ? nullptr : &other;  // [gapfuzz-llm] nullptr이면 !doc 분기(원본 문서로 대체)를 타고, 0이면 기존 &doc 동작 유지
+                XMLNode *clone = cur->ShallowClone(cloneDoc);  // [gapfuzz-llm] 고정된 &doc 대신 입력으로 고른 document 인자 전달
                 if (clone) {
                     clone->ShallowEqual(cur);
-                    if (XMLNode *p = cur->Parent()) p->InsertEndChild(clone);
+                    if (target == 2) other.InsertEndChild(clone);  // [gapfuzz-llm] 다른 문서 소속 노드를 doc 트리에 넣으면 라이브러리 assert가 나므로 소속 문서(other)에만 삽입
+                    else if (XMLNode *p = cur->Parent()) p->InsertEndChild(clone);
                 }
             }
             break;
```
