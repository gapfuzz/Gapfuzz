라이브러리: tinyxml2
하네스 파일: official_llm.cpp
지금 하네스는 공개 API 303개 중 251개를 한 번도 부르지 않습니다.

## 하네스에 추가할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)` — 새로 실행될 수 있는 코드 영역 117개
```
    virtual bool VisitEnter( const XMLElement& element, const XMLAttribute* attribute ) override;
```

### 2. `XMLElement::BoolText(bool) const` — 새로 실행될 수 있는 코드 영역 49개
```
	/// See QueryIntText()
	bool BoolText(bool defaultValue = false) const;
```

### 3. `XMLDocument::Print(XMLPrinter *) const` — 새로 실행될 수 있는 코드 영역 45개
```
    */
    void Print( XMLPrinter* streamer=0 ) const;
```

### 4. `XMLElement::SetText(bool)` — 새로 실행될 수 있는 코드 영역 40개
```
	/// Convenience method for setting text inside an element. See SetText() for important limitations.
    void SetText( bool value );
```

### 5. `XMLElement::ShallowClone(XMLDocument *) const` — 새로 실행될 수 있는 코드 영역 29개
```
    virtual XMLNode* ShallowClone( XMLDocument* document ) const override;
```

### 6. `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)` — 새로 실행될 수 있는 코드 영역 25개
```
    */
    XMLNode* InsertAfterChild( XMLNode* afterThis, XMLNode* addThis );
    /**
    	Delete all the children of this node.
    */
```

### 7. `XMLElement::ShallowEqual(const XMLNode *) const` — 새로 실행될 수 있는 코드 영역 22개
```
    virtual bool ShallowEqual( const XMLNode* compare ) const override;
```

### 8. `XMLElement::Int64Text(int64_t) const` — 새로 실행될 수 있는 코드 영역 21개
```
	/// See QueryIntText()
	int64_t Int64Text(int64_t defaultValue = 0) const;
```

### 9. `XMLDocument::DeepCopy(XMLDocument *) const` — 새로 실행될 수 있는 코드 영역 20개
```
	*/
	void DeepCopy(XMLDocument* target) const;
```

### 10. `XMLPrinter::VisitExit(const XMLElement &)` — 새로 실행될 수 있는 코드 영역 19개
```
    virtual bool VisitExit( const XMLElement& element ) override;
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,4,5,6,7를 OSS-Fuzz 하네스에 적용하고
   2  // [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness.py, 기록: samples/llm/combined/tinyxml2/).
   3  // TinyXML2 공식 OSS-Fuzz 하네스 (projects/tinyxml2/xmltest.cpp)와 동일한 동작.
   4  // 입력을 문자열로 바꿔 Parse 한 번만 호출한다.
   5  #include "tinyxml2.h"
   6  #include <stddef.h>
   7  #include <stdint.h>
   8  #include <string.h>
   9  #include <string>
  10  #include <new>
  11  
  12  using namespace tinyxml2;
  13  
  14  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  15      uint8_t h[6] = {0, 0, 0, 0, 0, 0};  // [gapfuzz-llm] 입력 앞 6바이트를 제안별로 겹치지 않게 배분(0:공백모드, 1~2:nBytes, 3:DeleteNode, 4:Attribute, 5:InsertEndChild)
  16      size_t hdr = size < sizeof(h) ? size : sizeof(h);  // [gapfuzz-llm] 헤더로 쓸 바이트 수
  17      if (hdr > 0) memcpy(h, data, hdr);  // [gapfuzz-llm] 짧은 입력은 나머지를 0(원래 동작)으로 둠
  18      const uint8_t *payload = data + hdr;  // [gapfuzz-llm] 헤더 이후 바이트를 원래처럼 XML 본문으로 사용
  19      size_t payload_size = size - hdr;  // [gapfuzz-llm] 본문 길이
  20  
  21      std::string data_string(reinterpret_cast<const char *>(payload), payload_size);  // [gapfuzz-llm] 헤더를 뺀 본문으로 문자열 생성
  22      XMLDocument doc(true, static_cast<Whitespace>(h[0] % 3));  // [gapfuzz-llm] whitespaceMode를 입력으로 선택(0=PRESERVE 기본값 유지, 2=PEDANTIC)
  23  
  24      size_t nBytes = static_cast<size_t>(-1);  // [gapfuzz-llm] 기본값(-1, strlen 사용)이 계속 나오도록 유지
  25      if ((h[1] & 3) != 0) {  // [gapfuzz-llm] 약 1/4은 원래 값 유지, 나머지는 입력으로 nBytes 선택
  26          nBytes = ((static_cast<size_t>(h[1]) << 8) | h[2]) % (payload_size + 1);  // [gapfuzz-llm] 0~본문 길이로 제한해 nBytes==0 분기를 열고 버퍼 초과 읽기를 막음
  27      }
  28      doc.Parse(data_string.c_str(), nBytes);  // [gapfuzz-llm] 고정된 기본 nBytes 대신 퍼저가 고른 값 전달
  29  
  30      const char *doc_value = doc.Value(); (void)doc_value;  // [gapfuzz-llm] XMLDocument에서 Value()를 호출해 ToDocument() 참 분기(null 반환) 실행, 역참조하지 않음
  31  
  32      try {  // [gapfuzz-llm] 라이브러리/std 예외가 하네스 크래시가 되지 않도록 보호
  33          int dmode = h[3] % 4;  // [gapfuzz-llm] DeleteNode에 넘길 노드 상태 선택(0이면 호출 안 함)
  34          if (dmode == 1) {
  35              doc.DeleteNode(nullptr);  // [gapfuzz-llm] node == 0 분기 (null 허용)
  36          } else if (dmode == 2) {
  37              doc.DeleteNode(doc.FirstChild());  // [gapfuzz-llm] 트리에 연결된 노드로 node->_parent 참 분기 (없으면 null)
  38          } else if (dmode == 3) {
  39              doc.DeleteNode(doc.NewElement("gapfuzz"));  // [gapfuzz-llm] 연결되지 않은 같은 문서 노드로 _parent 거짓 분기
  40          }
  41  
  42          const XMLElement *root = doc.RootElement();  // [gapfuzz-llm] DeleteNode 이후 새로 얻어 dangling 포인터 방지
  43          const XMLAttribute *attr = root ? root->FirstAttribute() : 0;  // [gapfuzz-llm] 실제 존재하는 속성 이름을 쓰기 위해 첫 속성 획득
  44          if (root && attr) {  // [gapfuzz-llm] name은 null 금지이므로 속성이 있을 때만 호출
  45              unsigned amode = h[4] % 3;  // [gapfuzz-llm] value 전달 방식 선택
  46              const char *value = 0;  // [gapfuzz-llm] 0: null(기존 경로)
  47              if (amode == 1) {
  48                  value = attr->Value();  // [gapfuzz-llm] 속성값과 같은 값으로 StringEqual 참 경로
  49              } else if (amode == 2) {
  50                  value = data_string.c_str();  // [gapfuzz-llm] 입력 문자열로 !value 거짓 및 불일치 경로
  51              }
  52              (void)root->Attribute(attr->Name(), value);  // [gapfuzz-llm] Attribute(name, value) 직접 호출
  53          }
  54  
  55          XMLDocument other;  // [gapfuzz-llm] 다른 문서의 노드를 만들기 위한 문서(스코프 종료 시 자동 해제)
  56          int imode = h[5] % 4;  // [gapfuzz-llm] InsertEndChild 호출 방식 선택(0이면 호출 안 함)
  57          if (imode == 1) {
  58              doc.InsertEndChild(doc.NewElement("e"));  // [gapfuzz-llm] 같은 문서의 새 노드를 직접 삽입
  59          } else if (imode == 2) {
  60              doc.InsertEndChild(other.NewElement("f"));  // [gapfuzz-llm] 다른 문서 노드로 addThis->_document != _document 분기 (null 아님)
  61          } else if (imode == 3) {
  62              XMLNode *attached = doc.FirstChild();  // [gapfuzz-llm] 이미 연결된 노드를 다시 끝에 삽입
  63              if (attached) {
  64                  doc.InsertEndChild(attached);  // [gapfuzz-llm] null이면 호출 생략
  65              }
  66          }
  67      } catch (...) {  // [gapfuzz-llm] 예외는 무시하고 계속 진행
  68      }
  69      return 0;
  70  }
```