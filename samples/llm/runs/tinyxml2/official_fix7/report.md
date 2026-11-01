# LLM 하네스 수정 — tinyxml2/official, 제안 7

- 모델: `claude-sonnet-5-5`
- 제안: `XMLNode::InsertEndChild(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `addThis`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1306/2046 |

**채택 후보: 시도 1** (`harnesses/llm/official_fix7/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -4,6 +4,7 @@
 #include <stddef.h>
 #include <stdint.h>
 #include <string>
+#include <new>
 
 using namespace tinyxml2;
 
@@ -11,5 +12,22 @@
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
     doc.Parse(data_string.c_str());
+    uint8_t mode = size > 0 ? data[0] % 4 : 0; // [gapfuzz-llm] 입력 첫 바이트로 InsertEndChild 직접 호출 방식을 고름 (0이면 기존 동작)
+    try { // [gapfuzz-llm] 할당 실패 예외가 하네스 크래시가 되지 않도록 감쌈
+        XMLDocument other; // [gapfuzz-llm] 다른 문서의 노드를 만들기 위한 문서 (스코프 종료 시 노드까지 자동 해제)
+        if (mode == 1) {
+            XMLElement *e = doc.NewElement("e"); // [gapfuzz-llm] 같은 문서 소속의 새 노드를 직접 InsertEndChild에 전달
+            doc.InsertEndChild(e);
+        } else if (mode == 2) {
+            XMLElement *foreign = other.NewElement("f"); // [gapfuzz-llm] 다른 문서 소속 노드 → addThis->_document != _document 분기 도달 (문서상 0 반환, null은 넘기지 않음)
+            doc.InsertEndChild(foreign);
+        } else if (mode == 3) {
+            XMLNode *attached = doc.FirstChild(); // [gapfuzz-llm] 이미 트리에 연결된 노드를 다시 끝에 삽입 (null이면 호출 생략)
+            if (attached) {
+                doc.InsertEndChild(attached);
+            }
+        }
+    } catch (const std::bad_alloc &) {
+    }
     return 0;
 }
```
