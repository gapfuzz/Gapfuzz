# LLM 하네스 수정 — tinyxml2/official, 제안 4

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::DeleteNode(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLDocument::Clear`, `XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `node`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 2/2 | - | 1493/1412 |

**채택 후보: 시도 1** (`harnesses/llm/official_fix4/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -11,5 +11,16 @@
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
     doc.Parse(data_string.c_str());
+    try {
+        int mode = size > 0 ? data[0] % 4 : 0; // [gapfuzz-llm] 입력 첫 바이트로 DeleteNode에 넘길 노드 상태를 고르고, 0이면 원래처럼 호출하지 않음
+        if (mode == 1) {
+            doc.DeleteNode(nullptr); // [gapfuzz-llm] node == 0 분기를 열기 위해 null 전달 (DeleteNode가 null을 허용함)
+        } else if (mode == 2) {
+            doc.DeleteNode(doc.FirstChild()); // [gapfuzz-llm] 트리에 연결된 같은 문서의 노드를 넘겨 node->_parent 참 분기를 열기 (파싱 결과가 없으면 null)
+        } else if (mode == 3) {
+            doc.DeleteNode(doc.NewElement("gapfuzz")); // [gapfuzz-llm] 트리에 연결되지 않은 같은 문서의 노드를 넘겨 _parent 거짓 분기도 확인
+        }
+    } catch (...) {
+    }
     return 0;
 }
```
