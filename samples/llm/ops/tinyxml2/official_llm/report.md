# 호출 안 함 API 추가 — tinyxml2/official_llm

- 모델: `claude-sonnet-5-5`
- 수정 전: 공개 API 303개 중 호출 안 함 251개, 라인 40.61% · 분기 45.58%
- 추가를 요청한 API 10개: `XMLPrinter::VisitEnter`, `XMLElement::BoolText`, `XMLDocument::Print`, `XMLElement::SetText`, `XMLElement::ShallowClone`, `XMLNode::InsertAfterChild`, `XMLElement::ShallowEqual`, `XMLElement::Int64Text`, `XMLDocument::DeepCopy`, `XMLPrinter::VisitExit`

| 시도 | 결과 | 실행된 API | 호출 안 함 | 라인 | 분기 | 사라진 API | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | 실패 | 10/10 | 189 | 45.72% | 43.02% | 6 | LIBRARY(약) | 4588/11886 |
| 2 | 실패 | 10/10 | 191 | 42.67% | 38.4% | 6 | LIBRARY(약) | 10141/4781 |
| 3 | 통과 | 10/10 | 191 | 45.7% | 43.44% | 3 | LIBRARY(약) | 14188/7031 |

수정 전 수치는 진단 때(기본 120초 × 1회), 시도별 수치는 검사 퍼징(짧음)의 중앙값이라 길이가 다릅니다. 정식 비교는 같은 조건의 긴 실험으로 하세요.

**채택: 시도 3** → `harnesses/tinyxml2/official_llm_ops.cpp`. 사람이 읽고 쓰세요.

```diff
--- 수정 전
+++ 시도 3
@@ -66,5 +66,92 @@
         }
     } catch (...) {  // [gapfuzz-llm] 예외는 무시하고 계속 진행
     }
+
+    // 아래부터 gapfuzz-ops 추가분. 위 원래 코드는 한 글자도 바꾸지 않았고, 추가분은 doc을 읽기/복사만 한다.
+    // 추가분이 실행 속도를 떨어뜨려 원래 경로 탐색을 방해하지 않도록, 입력이 작을 때만(4KB 이하)
+    // 그리고 끝 바이트 비트로 블록을 골라 일부 입력에서만 실행한다.
+    auto tail = [&](size_t i) -> uint8_t {  // 끝에서 i번째 바이트(입력이 짧으면 0)
+        return size > i ? data[size - 1 - i] : 0;
+    };
+
+    if (size <= 4096) {
+        try {  // 라이브러리/std 예외가 하네스 크래시가 되지 않도록 보호
+            XMLElement *root = doc.RootElement();  // 원래 코드의 변경이 끝난 뒤 새로 얻어 dangling 방지
+            if (root) {  // 루트가 없으면 추가 호출을 모두 건너뜀
+                const uint8_t sel = tail(5);  // 블록 선택 비트
+                uint64_t udef = 0;  // 기본값을 입력 끝 8바이트로 구성
+                for (size_t i = 0; i < 8; i++) udef = (udef << 8) | tail(6 + i);
+                const int64_t idef = static_cast<int64_t>(udef);
+                const bool bdef = (tail(0) & 1) != 0;
+                const XMLElement *child = root->FirstChildElement();  // 없으면 null
+
+                // [gapfuzz-ops] XMLElement::BoolText
+                // [gapfuzz-ops] XMLElement::Int64Text
+                if (sel & 1) {
+                    (void)root->BoolText(bdef);  // 텍스트가 없거나 불리언이 아니면 기본값 반환
+                    (void)root->Int64Text(idef);
+                    if (child) {
+                        (void)child->BoolText(!bdef);
+                        (void)child->Int64Text(-idef);
+                    }
+                }
+
+                const bool compact = ((tail(0) & 2) != 0) || size > 256;  // 들여쓰기 출력은 작은 입력에서만
+                const int depth = tail(1) % 4;  // 시작 들여쓰기 깊이(0~3)
+
+                // [gapfuzz-ops] XMLPrinter::VisitEnter
+                // [gapfuzz-ops] XMLPrinter::VisitExit
+                if (sel & 2) {
+                    XMLPrinter printer(0, compact, depth);  // FILE*가 null이면 메모리 버퍼에만 기록(파일·stdout 미사용)
+                    const XMLAttribute *firstAttr = (tail(1) & 4) ? 0 : root->FirstAttribute();  // 속성 null 허용
+                    printer.VisitEnter(*root, firstAttr);  // 열기와 닫기를 항상 짝지어 호출
+                    printer.VisitExit(*root);
+                    (void)printer.CStr();
+                }
+
+                // [gapfuzz-ops] XMLDocument::Print
+                if (sel & 4) {
+                    XMLPrinter printer2(0, compact, 0);
+                    doc.Print(&printer2);  // null이면 stdout으로 출력하므로 반드시 비null 프린터 전달
+                    (void)printer2.CStrSize();
+                }
+
+                // [gapfuzz-ops] XMLElement::ShallowClone
+                // [gapfuzz-ops] XMLElement::ShallowEqual
+                if (sel & 8) {
+                    XMLDocument scratch;  // 복제본을 소유할 별도 문서(스코프 종료 시 자동 해제)
+                    XMLNode *clone = root->ShallowClone(&scratch);  // document는 비null
+                    if (clone) {  // 실패하면 사용하지 않음
+                        (void)root->ShallowEqual(clone);  // 같은 요소라 참 경로
+                        if (child) (void)root->ShallowEqual(child);  // 이름이 다르면 거짓 경로
+                        (void)root->ShallowEqual(&doc);  // 요소가 아닌 노드 경로
+                        scratch.DeleteNode(clone);  // 연결되지 않은 노드는 소유 문서에서 삭제
+                    }
+                }
+
+                // [gapfuzz-ops] XMLDocument::DeepCopy
+                // [gapfuzz-ops] XMLNode::InsertAfterChild
+                // [gapfuzz-ops] XMLElement::SetText(bool)
+                if (sel & 16) {
+                    XMLDocument copy;  // doc과 다른 대상 문서(자기 자신을 대상으로 쓰지 않음)
+                    doc.DeepCopy(&copy);
+
+                    const int mode = tail(3) % 4;
+                    XMLNode *after = (mode == 1) ? copy.LastChild() : copy.FirstChild();  // copy의 자식만 afterThis로 사용
+                    XMLNode *add = (mode == 2) ? copy.LastChild() : copy.NewElement("g");  // 2: 기존 노드 이동, 그 외: 새 노드
+                    if (after && add) {  // afterThis는 null 금지
+                        (void)copy.InsertAfterChild(after, add);
+                    }
+
+                    XMLElement *croot = copy.RootElement();  // 삽입 후 새로 얻음
+                    if (croot) {
+                        croot->SetText((tail(4) & 1) != 0);  // 복사본에만 쓰기 (원본 doc은 유지)
+                        (void)croot->BoolText(false);
+                    }
+                }
+            }
+        } catch (...) {  // 예외는 무시하고 계속 진행
+        }
+    }
     return 0;
 }
```
