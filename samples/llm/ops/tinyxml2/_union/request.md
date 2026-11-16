라이브러리: tinyxml2
OSS-Fuzz 하네스 2개(official, official_xmltest2)의 커버리지를 모두 합쳐도, 공개 API 303개 중 259개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)` — 새로 실행될 수 있는 코드 영역 118개
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

### 4. `XMLElement::SetText(bool)` — 새로 실행될 수 있는 코드 영역 45개
```
	/// Convenience method for setting text inside an element. See SetText() for important limitations.
    void SetText( bool value );
```

### 5. `XMLElement::ShallowClone(XMLDocument *) const` — 새로 실행될 수 있는 코드 영역 32개
```
    virtual XMLNode* ShallowClone( XMLDocument* document ) const override;
```

### 6. `XMLNode::ChildElementCount(const char *) const` — 새로 실행될 수 있는 코드 영역 27개
```
    int ChildElementCount(const char *value) const;
```

### 7. `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)` — 새로 실행될 수 있는 코드 영역 25개
```
    */
    XMLNode* InsertAfterChild( XMLNode* afterThis, XMLNode* addThis );
    /**
    	Delete all the children of this node.
    */
```

### 8. `XMLElement::ShallowEqual(const XMLNode *) const` — 새로 실행될 수 있는 코드 영역 22개
```
    virtual bool ShallowEqual( const XMLNode* compare ) const override;
```

### 9. `XMLElement::Int64Text(int64_t) const` — 새로 실행될 수 있는 코드 영역 21개
```
	/// See QueryIntText()
	int64_t Int64Text(int64_t defaultValue = 0) const;
```

### 10. `XMLDocument::DeepCopy(XMLDocument *) const` — 새로 실행될 수 있는 코드 영역 20개
```
	*/
	void DeepCopy(XMLDocument* target) const;
```

## 참고: 기존 하네스 official.cpp (고치지 마세요. include와 작성 방식만 참고)
```
// TinyXML2 공식 OSS-Fuzz 하네스 (projects/tinyxml2/xmltest.cpp)와 동일한 동작.
// 입력을 문자열로 바꿔 Parse 한 번만 호출한다.
#include "tinyxml2.h"
#include <stddef.h>
#include <stdint.h>
#include <string>

using namespace tinyxml2;

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string data_string(reinterpret_cast<const char *>(data), size);
    XMLDocument doc;
    doc.Parse(data_string.c_str());
    return 0;
}

```