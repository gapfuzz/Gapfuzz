# LLM 하네스 수정 — tinyxml2/official, 제안 1,2,4,5,6,7

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(13행에서 기본값) → 퍼저 입력으로 바꾸세요
- 제안: `XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 고정합니다(12행에서 기본값) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 제안: `XMLDocument::DeleteNode(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLDocument::Clear`, `XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `node`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 제안: `XMLElement::Attribute(const char *, const char *) const`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLElement::ParseAttributes`)에서만 불립니다. 내부 호출은 2번째 인자 `value`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 제안: `XMLNode::Value() const`를 `XMLDocument` 객체에서 부른 적이 없습니다(조건 `this->ToDocument()`가 한쪽으로만 감) → 하네스가 `XMLDocument` 객체에서 이 API를 불러 보세요
- 제안: `XMLNode::InsertEndChild(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `addThis`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 겨냥한 분기: 8개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 8/8 | 1: 2/2, 2: 1/1, 4: 2/2, 5: 1/1, 6: 1/1, 7: 1/1 | - | 7165/3282 |

**채택 후보: 시도 1** (`harnesses/tinyxml2/llm/official_combined/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -3,13 +3,66 @@
 #include "tinyxml2.h"
 #include <stddef.h>
 #include <stdint.h>
+#include <string.h>
 #include <string>
+#include <new>
 
 using namespace tinyxml2;
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
-    std::string data_string(reinterpret_cast<const char *>(data), size);
-    XMLDocument doc;
-    doc.Parse(data_string.c_str());
+    uint8_t h[6] = {0, 0, 0, 0, 0, 0};  // [gapfuzz-llm] 입력 앞 6바이트를 제안별로 겹치지 않게 배분(0:공백모드, 1~2:nBytes, 3:DeleteNode, 4:Attribute, 5:InsertEndChild)
+    size_t hdr = size < sizeof(h) ? size : sizeof(h);  // [gapfuzz-llm] 헤더로 쓸 바이트 수
+    if (hdr > 0) memcpy(h, data, hdr);  // [gapfuzz-llm] 짧은 입력은 나머지를 0(원래 동작)으로 둠
+    const uint8_t *payload = data + hdr;  // [gapfuzz-llm] 헤더 이후 바이트를 원래처럼 XML 본문으로 사용
+    size_t payload_size = size - hdr;  // [gapfuzz-llm] 본문 길이
+
+    std::string data_string(reinterpret_cast<const char *>(payload), payload_size);  // [gapfuzz-llm] 헤더를 뺀 본문으로 문자열 생성
+    XMLDocument doc(true, static_cast<Whitespace>(h[0] % 3));  // [gapfuzz-llm] whitespaceMode를 입력으로 선택(0=PRESERVE 기본값 유지, 2=PEDANTIC)
+
+    size_t nBytes = static_cast<size_t>(-1);  // [gapfuzz-llm] 기본값(-1, strlen 사용)이 계속 나오도록 유지
+    if ((h[1] & 3) != 0) {  // [gapfuzz-llm] 약 1/4은 원래 값 유지, 나머지는 입력으로 nBytes 선택
+        nBytes = ((static_cast<size_t>(h[1]) << 8) | h[2]) % (payload_size + 1);  // [gapfuzz-llm] 0~본문 길이로 제한해 nBytes==0 분기를 열고 버퍼 초과 읽기를 막음
+    }
+    doc.Parse(data_string.c_str(), nBytes);  // [gapfuzz-llm] 고정된 기본 nBytes 대신 퍼저가 고른 값 전달
+
+    const char *doc_value = doc.Value(); (void)doc_value;  // [gapfuzz-llm] XMLDocument에서 Value()를 호출해 ToDocument() 참 분기(null 반환) 실행, 역참조하지 않음
+
+    try {  // [gapfuzz-llm] 라이브러리/std 예외가 하네스 크래시가 되지 않도록 보호
+        int dmode = h[3] % 4;  // [gapfuzz-llm] DeleteNode에 넘길 노드 상태 선택(0이면 호출 안 함)
+        if (dmode == 1) {
+            doc.DeleteNode(nullptr);  // [gapfuzz-llm] node == 0 분기 (null 허용)
+        } else if (dmode == 2) {
+            doc.DeleteNode(doc.FirstChild());  // [gapfuzz-llm] 트리에 연결된 노드로 node->_parent 참 분기 (없으면 null)
+        } else if (dmode == 3) {
+            doc.DeleteNode(doc.NewElement("gapfuzz"));  // [gapfuzz-llm] 연결되지 않은 같은 문서 노드로 _parent 거짓 분기
+        }
+
+        const XMLElement *root = doc.RootElement();  // [gapfuzz-llm] DeleteNode 이후 새로 얻어 dangling 포인터 방지
+        const XMLAttribute *attr = root ? root->FirstAttribute() : 0;  // [gapfuzz-llm] 실제 존재하는 속성 이름을 쓰기 위해 첫 속성 획득
+        if (root && attr) {  // [gapfuzz-llm] name은 null 금지이므로 속성이 있을 때만 호출
+            unsigned amode = h[4] % 3;  // [gapfuzz-llm] value 전달 방식 선택
+            const char *value = 0;  // [gapfuzz-llm] 0: null(기존 경로)
+            if (amode == 1) {
+                value = attr->Value();  // [gapfuzz-llm] 속성값과 같은 값으로 StringEqual 참 경로
+            } else if (amode == 2) {
+                value = data_string.c_str();  // [gapfuzz-llm] 입력 문자열로 !value 거짓 및 불일치 경로
+            }
+            (void)root->Attribute(attr->Name(), value);  // [gapfuzz-llm] Attribute(name, value) 직접 호출
+        }
+
+        XMLDocument other;  // [gapfuzz-llm] 다른 문서의 노드를 만들기 위한 문서(스코프 종료 시 자동 해제)
+        int imode = h[5] % 4;  // [gapfuzz-llm] InsertEndChild 호출 방식 선택(0이면 호출 안 함)
+        if (imode == 1) {
+            doc.InsertEndChild(doc.NewElement("e"));  // [gapfuzz-llm] 같은 문서의 새 노드를 직접 삽입
+        } else if (imode == 2) {
+            doc.InsertEndChild(other.NewElement("f"));  // [gapfuzz-llm] 다른 문서 노드로 addThis->_document != _document 분기 (null 아님)
+        } else if (imode == 3) {
+            XMLNode *attached = doc.FirstChild();  // [gapfuzz-llm] 이미 연결된 노드를 다시 끝에 삽입
+            if (attached) {
+                doc.InsertEndChild(attached);  // [gapfuzz-llm] null이면 호출 생략
+            }
+        }
+    } catch (...) {  // [gapfuzz-llm] 예외는 무시하고 계속 진행
+    }
     return 0;
 }
```
