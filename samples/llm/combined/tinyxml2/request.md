라이브러리: tinyxml2
하네스 파일: official.cpp

아래 제안 6개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(13행에서 기본값) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `XMLDocument::Parse(const char *, size_t)` 2459행, 조건 `nBytes == 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2455  XMLError XMLDocument::Parse( const char* xml, size_t nBytes )
 2456  {
 2457      Clear();
 2458  
 2459>     if ( nBytes == 0 || !xml || !*xml ) {
 2460          SetError( XML_ERROR_EMPTY_DOCUMENT, 0, 0 );
 2461          return _errorID;
 2462      }
 2463      if ( nBytes == static_cast<size_t>(-1) ) {
```
- `XMLDocument::Parse(const char *, size_t)` 2463행, 조건 `nBytes == static_cast<size_t>(-1)`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 2459      if ( nBytes == 0 || !xml || !*xml ) {
 2460          SetError( XML_ERROR_EMPTY_DOCUMENT, 0, 0 );
 2461          return _errorID;
 2462      }
 2463>     if ( nBytes == static_cast<size_t>(-1) ) {
 2464          nBytes = strlen( xml );
 2465      }
 2466      TIXMLASSERT( _charBuffer == 0 );
 2467      _charBuffer = new char[ nBytes+1 ];
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 제안 2
`XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 고정합니다(12행에서 기본값) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XMLDocument::Identify(char *, XMLNode **, bool)` 752행, 조건 `WhitespaceMode() == PEDANTIC_WHITESPACE`가 퍼징 중 한 번도 '참'이 되지 않음
```
  748      }
  749      else if ( XMLUtil::StringEqual( p, elementHeader, elementHeaderLen ) ) {
  750  
  751          // Preserve whitespace pedantically before closing tag, when it's immediately after opening tag
  752>         if (WhitespaceMode() == PEDANTIC_WHITESPACE && first && p != start && *(p + elementHeaderLen) == '/') {
  753              returnNode = CreateUnlinkedNode<XMLText>(_textPool);
  754              returnNode->_parseLineNum = startLine;
  755              p = start;	// Back it up, all the text counts.
  756              _parseCurLineNum = startLine;
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -9,7 +9,7 @@
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
     std::string data_string(reinterpret_cast<const char *>(data), size);
-    XMLDocument doc;
+    XMLDocument doc(true, static_cast<Whitespace>(size > 0 ? data[0] % 3 : 0)); // [gapfuzz-llm] whitespaceMode가 기본값(PRESERVE)으로 고정되어 PEDANTIC 분기에 못 가므로 입력 첫 바이트로 세 모드(0=PRESERVE, 1=COLLAPSE, 2=PEDANTIC)를 고름
     doc.Parse(data_string.c_str());
     return 0;
 }
```

## 제안 4
`XMLDocument::DeleteNode(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLDocument::Clear`, `XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `node`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `XMLDocument::DeleteNode(XMLNode *)` 2333행, 조건 `node == 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2329      return fp;
 2330  }
 2331  
 2332  void XMLDocument::DeleteNode( XMLNode* node )	{   
 2333>     if(node == 0) {
 2334          return; // check for null pointer
 2335      }
 2336      TIXMLASSERT(node->_document == this);
 2337      if (node->_parent) {
```
- `XMLDocument::DeleteNode(XMLNode *)` 2337행, 조건 `node->_parent`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2333      if(node == 0) {
 2334          return; // check for null pointer
 2335      }
 2336      TIXMLASSERT(node->_document == this);
 2337>     if (node->_parent) {
 2338          node->_parent->DeleteChild( node );
 2339      }
 2340      else {
 2341          // Isn't in the tree.
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 제안 5
`XMLElement::Attribute(const char *, const char *) const`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLElement::ParseAttributes`)에서만 불립니다. 내부 호출은 2번째 인자 `value`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XMLElement::Attribute(const char *, const char *) const` 1639행, 조건 `!value`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1635      const XMLAttribute* a = FindAttribute( name );
 1636      if ( !a ) {
 1637          return 0;
 1638      }
 1639>     if ( !value || XMLUtil::StringEqual( a->Value(), value )) {
 1640          return a->Value();
 1641      }
 1642      return 0;
 1643  }
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -11,5 +11,20 @@
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
     doc.Parse(data_string.c_str());
+    try { // [gapfuzz-llm] 라이브러리/std 예외가 하네스 크래시로 이어지지 않도록 보호
+        const XMLElement *root = doc.RootElement(); // [gapfuzz-llm] Attribute를 직접 부를 대상 요소를 얻음
+        const XMLAttribute *attr = root ? root->FirstAttribute() : 0; // [gapfuzz-llm] 실제 존재하는 속성 이름을 쓰기 위해 첫 속성을 얻음
+        if (root && attr) { // [gapfuzz-llm] name은 null이면 안 되므로 속성이 있을 때만 호출
+            unsigned mode = size > 0 ? (data[0] % 3) : 0; // [gapfuzz-llm] 입력 앞 바이트로 value 전달 방식을 고름
+            const char *value = 0; // [gapfuzz-llm] mode 0: value가 null인 기존 경로
+            if (mode == 1) {
+                value = attr->Value(); // [gapfuzz-llm] mode 1: 속성값과 같은 값을 넘겨 StringEqual 참 경로 도달
+            } else if (mode == 2) {
+                value = data_string.c_str(); // [gapfuzz-llm] mode 2: 입력 문자열(대개 다른 값)을 넘겨 !value 거짓 및 불일치 경로 도달
+            }
+            (void)root->Attribute(attr->Name(), value); // [gapfuzz-llm] Attribute(name, value)를 직접 호출해 1639행 분기를 퍼징
+        }
+    } catch (...) { // [gapfuzz-llm] 예외는 무시하고 계속 진행
+    }
     return 0;
 }
```

## 제안 6
`XMLNode::Value() const`를 `XMLDocument` 객체에서 부른 적이 없습니다(조건 `this->ToDocument()`가 한쪽으로만 감) → 하네스가 `XMLDocument` 객체에서 이 API를 불러 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XMLNode::Value() const` 856행, 조건 `this->ToDocument()`가 퍼징 중 한 번도 '참'이 되지 않음
```
  852  
  853  const char* XMLNode::Value() const
  854  {
  855      // Edge case: XMLDocuments don't have a Value. Return null.
  856>     if ( this->ToDocument() )
  857          return 0;
  858      return _value.GetStr();
  859  }
  860  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -11,5 +11,6 @@
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
     doc.Parse(data_string.c_str());
+    const char *doc_value = doc.Value(); (void)doc_value; // [gapfuzz-llm] XMLDocument 객체에서 Value()를 호출해 ToDocument()가 참이 되는 분기(null 반환)를 실행. 반환값은 역참조하지 않음
     return 0;
 }
```

## 제안 7
`XMLNode::InsertEndChild(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `addThis`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XMLNode::InsertEndChild(XMLNode *)` 934행, 조건 `addThis->_document != _document`가 퍼징 중 한 번도 '참'이 되지 않음
```
  930  
  931  XMLNode* XMLNode::InsertEndChild( XMLNode* addThis )
  932  {
  933      TIXMLASSERT( addThis );
  934>     if ( addThis->_document != _document ) {
  935          TIXMLASSERT( false );
  936          return 0;
  937      }
  938      InsertChildPreamble( addThis );
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
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

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // TinyXML2 공식 OSS-Fuzz 하네스 (projects/tinyxml2/xmltest.cpp)와 동일한 동작.
   2  // 입력을 문자열로 바꿔 Parse 한 번만 호출한다.
   3  #include "tinyxml2.h"
   4  #include <stddef.h>
   5  #include <stdint.h>
   6  #include <string>
   7  
   8  using namespace tinyxml2;
   9  
  10  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  11      std::string data_string(reinterpret_cast<const char *>(data), size);
  12      XMLDocument doc;
  13      doc.Parse(data_string.c_str());
  14      return 0;
  15  }
```