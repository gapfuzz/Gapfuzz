# 커버리지 갭 리포트 — stateful-r1

- 하네스: `harnesses/stateful.cpp`
- 대상 헤더: `third_party/tinyxml2/tinyxml2.h`
- 공개 API 수: **303**

## 요약

| 분류 | 개수 | 비율 | 조치 |
|---|---:|---:|---|
| 호출 안 함 | 103 | 34% | 하네스에 이 API(또는 상위 API) 호출을 추가 |
| 호출 경로 있음 · 조건에 막힘 | 0 | 0% | 막힌 조건을 만족시키는 입력·상태를 만들어 줌 |
| 도달 · 일부 분기 미실행 | 37 | 12% | 입력·옵션 다양화(분기 조건 확인) |
| 완전 도달 | 163 | 54% | 조치 불필요 |

## 클래스별

| 클래스 | 호출 안 함 | 호출 경로 있음 · 조건에 막힘 | 도달 · 일부 분기 미실행 | 완전 도달 |
|---|---:|---:|---:|---:|
| XMLAttribute | 6 | 0 | 0 | 20 |
| XMLComment | 0 | 0 | 2 | 3 |
| XMLConstHandle | 13 | 0 | 1 | 3 |
| XMLDeclaration | 0 | 0 | 2 | 3 |
| XMLDocument | 9 | 0 | 6 | 21 |
| XMLElement | 30 | 0 | 7 | 34 |
| XMLHandle | 12 | 0 | 1 | 4 |
| XMLNode | 9 | 0 | 4 | 34 |
| XMLPrinter | 13 | 0 | 3 | 17 |
| XMLText | 0 | 0 | 2 | 5 |
| XMLUnknown | 0 | 0 | 2 | 3 |
| XMLUtil | 3 | 0 | 7 | 16 |
| XMLVisitor | 8 | 0 | 0 | 0 |

## 하네스에서 고칠 곳

도달한 API 안에서 한쪽으로만 간 조건을 거슬러 올라가, 그 값이 **하네스의 어떤 호출·인자에서 정해지는지** 찾은 결과입니다.

| 막힌 분기의 원인 | 개수 |
|---|---:|
| 하네스가 인자를 고정 | 14 |
| 값을 정하는 API를 하네스가 안 부름 | 1 |
| 하네스가 값의 범위를 좁힘 | 4 |
| 인자는 바뀌지만 맞는 값이 안 나옴 | 20 |
| 라이브러리 내부에서 정해짐 | 22 |
| 합계 | 61 |

### 1. [하네스가 인자를 고정] 161행
- `XMLComment::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요 (같은 호출이 5개 구현 클래스에 영향: `XMLComment::ShallowClone`, `XMLDeclaration::ShallowClone`, `XMLElement::ShallowClone`, `XMLText::ShallowClone`, `XMLUnknown::ShallowClone`)
- 하네스 코드: `XMLNode *clone = cur->ShallowClone(&doc);`
- 이 때문에 막힌 분기 5개:
  - `XMLText::ShallowClone(XMLDocument *) const` 1268행 조건 `!doc` 한 번도 참 아님
  - `XMLComment::ShallowClone(XMLDocument *) const` 1317행 조건 `!doc` 한 번도 참 아님
  - `XMLDeclaration::ShallowClone(XMLDocument *) const` 1366행 조건 `!doc` 한 번도 참 아님
  - `XMLUnknown::ShallowClone(XMLDocument *) const` 1414행 조건 `!doc` 한 번도 참 아님
  - `XMLElement::ShallowClone(XMLDocument *) const` 2112행 조건 `!doc` 한 번도 참 아님

### 2. [하네스가 인자를 고정] 172행
- `XMLDocument::Accept(XMLVisitor *) const`의 1번째 인자 `visitor`를 하네스가 고정합니다(172행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요 (같은 호출이 2개 구현 클래스에 영향: `XMLDocument::Accept`, `XMLElement::Accept`)
- 하네스 코드: `else cur->Accept(&printer);`
- 이 때문에 막힌 분기 4개:
  - `XMLDocument::Accept(XMLVisitor *) const` 781행 조건 `visitor->VisitEnter( *this )` 한 번도 거짓 아님
  - `XMLDocument::Accept(XMLVisitor *) const` 783행 조건 `!node->Accept( visitor )` 한 번도 참 아님
  - `XMLElement::Accept(XMLVisitor *) const` 2152행 조건 `visitor->VisitEnter( *this, _rootAttribute )` 한 번도 거짓 아님
  - `XMLElement::Accept(XMLVisitor *) const` 2154행 조건 `!node->Accept( visitor )` 한 번도 참 아님

### 3. [하네스가 인자를 고정] 44행, 233행
- `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(44행에서 기본값, 233행에서 기본값) → 퍼저 입력으로 바꾸세요
- 하네스 코드: `doc.Parse(xml.c_str());`
- 하네스 코드: `if (fdp.ConsumeBool()) doc.Parse(str);`
- 이 때문에 막힌 분기 2개:
  - `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `nBytes == 0` 한 번도 참 아님
  - `XMLDocument::Parse(const char *, size_t)` 2463행 조건 `nBytes == static_cast<size_t>(-1)` 한 번도 거짓 아님

### 4. [하네스가 인자를 고정] 171행
- `XMLDocument::Print(XMLPrinter *) const`의 1번째 인자 `streamer`를 하네스가 고정합니다(171행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요
- 하네스 코드: `if (fdp.ConsumeBool()) doc.Print(&printer);`
- 이 때문에 막힌 분기 1개:
  - `XMLDocument::Print(XMLPrinter *) const` 2488행 조건 `streamer` 한 번도 거짓 아님

### 5. [하네스가 인자를 고정] 188행
- `XMLHandle::XMLHandle(XMLNode *)`의 1번째 인자 `node`를 하네스가 고정합니다(188행에서 항상 같은 객체 `&doc`) (필드 `_node`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요 (또는 `XMLHandle::XMLHandle(XMLNode &)`로도 이 값을 바꿀 수 있음)
- 하네스 코드: `XMLHandle h(&doc);`
- 이 때문에 막힌 분기 1개:
  - `XMLHandle::FirstChildElement(const char *)` 2075행 조건 `_node` 한 번도 거짓 아님

### 6. [하네스가 인자를 고정] 170행, 178행
- `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)`의 4번째 인자 `aposInAttributes`를 하네스가 고정합니다(170행에서 기본값, 178행에서 기본값) → 퍼저 입력으로 바꾸세요
- 하네스 코드: `XMLPrinter printer(nullptr, fdp.ConsumeBool(), fdp.ConsumeIntegralInRange<int>(0, 4));`
- 하네스 코드: `XMLPrinter printer(nullptr, fdp.ConsumeBool());`
- 이 때문에 막힌 분기 1개:
  - `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)` 2605행 조건 `(aposInAttributes == ESCAPE_APOS_CHARS_IN_ATTRIBUTES)` 한 번도 거짓 아님

### 7. [값을 정하는 API를 하네스가 안 부름] 하네스에 호출 없음
- 하네스가 `XMLDocument::SetBOM(bool)`를 부르지 않아 1번째 인자 `useBOM` 값이 들어가지 않습니다 (필드 `_writeBOM`를 거쳐 조건에 쓰임) → 호출을 추가하세요
- 이 때문에 막힌 분기 1개:
  - `XMLPrinter::VisitEnter(const XMLDocument &)` 2973행 조건 `doc.HasBOM()` 한 번도 참 아님

### 8. [하네스가 값의 범위를 좁힘] 190행
- `XMLConstHandle::XMLConstHandle(const XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(190행) (필드 `_node`를 거쳐 조건에 쓰임) → nullptr도 넘겨 보세요
- 하네스 코드: `XMLConstHandle ch(cur);`
- 이 때문에 막힌 분기 1개:
  - `XMLConstHandle::LastChildElement(const char *) const` 2157행 조건 `_node` 한 번도 거짓 아님

### 9. [하네스가 값의 범위를 좁힘] 44행, 233행
- `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(44행, 233행) → nullptr도 넘겨 보세요
- 하네스 코드: `doc.Parse(xml.c_str());`
- 하네스 코드: `if (fdp.ConsumeBool()) doc.Parse(str);`
- 이 때문에 막힌 분기 1개:
  - `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `!xml` 한 번도 참 아님

### 10. [하네스가 값의 범위를 좁힘] 150행
- `XMLDocument::DeleteNode(XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(150행) → nullptr도 넘겨 보세요
- 하네스 코드: `else doc.DeleteNode(c);`
- 이 때문에 막힌 분기 1개:
  - `XMLDocument::DeleteNode(XMLNode *)` 2333행 조건 `node == 0` 한 번도 참 아님

### 11. [하네스가 값의 범위를 좁힘] 42행, 46행
- `XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 `COLLAPSE_WHITESPACE`, `PRESERVE_WHITESPACE`, `기본값` 중에서만 고릅니다(42행, 46행) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 하네스 코드: `XMLDocument doc(fdp.ConsumeBool(), fdp.ConsumeBool() ? COLLAPSE_WHITESPACE : PRESERVE_WHITESPACE);`
- 하네스 코드: `XMLDocument other;          // DeepClone / 다른 문서 간 동작 확인용`
- 이 때문에 막힌 분기 1개:
  - `XMLDocument::Identify(char *, XMLNode **, bool)` 752행 조건 `WhitespaceMode() == PEDANTIC_WHITESPACE` 한 번도 참 아님

## 호출 안 함

하네스의 실행 경로에서 이 함수로 가는 호출 자체가 없습니다. 퍼징을 오래 돌려도 열리지 않으므로 하네스를 바꿔야 합니다.

- `XMLAttribute::GetLineNum() const` (헤더 1149행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::Unsigned64Value() const` (헤더 1172행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::FloatValue() const` (헤더 1197행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::QueryUnsigned64Value(uint64_t *) const` (헤더 1213행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::Unsigned64Value() const`, `XMLElement::QueryAttribute(const char *, uint64_t *) const`, `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const`, `XMLElement::Unsigned64Attribute(const char *, uint64_t) const`
- `XMLAttribute::SetAttribute(uint64_t)` (헤더 1230행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, uint64_t)`
- `XMLAttribute::SetAttribute(float)` (헤더 1236행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, float)`
- `XMLConstHandle::XMLConstHandle(const XMLNode &)` (헤더 2137행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::XMLConstHandle(const XMLConstHandle &)` (헤더 2139행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::operator=(const XMLConstHandle &)` (헤더 2142행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::FirstChild() const` (헤더 2147행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::FirstChildElement(const char *) const` (헤더 2150행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::LastChild() const` (헤더 2153행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::PreviousSiblingElement(const char *) const` (헤더 2162행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::NextSibling() const` (헤더 2165행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::NextSiblingElement(const char *) const` (헤더 2168행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToElement() const` (헤더 2176행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToText() const` (헤더 2179행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToUnknown() const` (헤더 2182행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToDeclaration() const` (헤더 2185행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::LoadFile(const char *)` (헤더 1756행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::LoadFile(FILE *)` (헤더 1769행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::LoadFile(const char *)`
- `XMLDocument::SaveFile(const char *, bool)` (헤더 1776행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::SaveFile(FILE *, bool)` (헤더 1785행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::SaveFile(const char *, bool)`
- `XMLDocument::SetBOM(bool)` (헤더 1802행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::RootElement() const` (헤더 1812행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::PrintError() const` (헤더 1896행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::DeepCopy(XMLDocument *) const` (헤더 1914행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::ShallowEqual(const XMLNode *) const` (헤더 1925행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLElement::UnsignedAttribute(const char *, unsigned int) const` (헤더 1316행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Int64Attribute(const char *, int64_t) const` (헤더 1318행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Unsigned64Attribute(const char *, uint64_t) const` (헤더 1320행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::DoubleAttribute(const char *, double) const` (헤더 1324행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::FloatAttribute(const char *, float) const` (헤더 1326행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const` (헤더 1368행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::QueryAttribute(const char *, uint64_t *) const`, `XMLElement::Unsigned64Attribute(const char *, uint64_t) const`
- `XMLElement::QueryStringAttribute(const char *, const char **) const` (헤더 1402행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::QueryAttribute(const char *, const char **) const`
- `XMLElement::QueryAttribute(const char *, int *) const` (헤더 1430행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryAttribute(const char *, unsigned int *) const` (헤더 1434행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryAttribute(const char *, int64_t *) const` (헤더 1438행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryAttribute(const char *, uint64_t *) const` (헤더 1442행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryAttribute(const char *, bool *) const` (헤더 1446행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryAttribute(const char *, double *) const` (헤더 1450행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryAttribute(const char *, float *) const` (헤더 1454행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryAttribute(const char *, const char **) const` (헤더 1458행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, uint64_t)` (헤더 1485행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, float)` (헤더 1501행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(unsigned int)` (헤더 1586행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(int64_t)` (헤더 1588행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(float)` (헤더 1596행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryUnsignedText(unsigned int *) const` (헤더 1626행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::UnsignedText(unsigned int) const`
- `XMLElement::QueryUnsigned64Text(uint64_t *) const` (헤더 1630행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::Unsigned64Text(uint64_t) const`
- `XMLElement::QueryFloatText(float *) const` (헤더 1636행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::FloatText(float) const`
- `XMLElement::UnsignedText(unsigned int) const` (헤더 1641행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Int64Text(int64_t) const` (헤더 1643행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Unsigned64Text(uint64_t) const` (헤더 1645행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::BoolText(bool) const` (헤더 1647행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::DoubleText(double) const` (헤더 1649행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::FloatText(float) const` (헤더 1651행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::InsertNewDeclaration(const char *)` (헤더 1663행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::XMLHandle(XMLNode &)` (헤더 2058행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::XMLHandle(const XMLHandle &)` (헤더 2061행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::operator=(const XMLHandle &)` (헤더 2064행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::LastChild()` (헤더 2078행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::LastChildElement(const char *)` (헤더 2082행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::PreviousSibling()` (헤더 2086행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::PreviousSiblingElement(const char *)` (헤더 2090행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::NextSibling()` (헤더 2094행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToNode()` (헤더 2103행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToText()` (헤더 2111행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToUnknown()` (헤더 2115행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToDeclaration()` (헤더 2119행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::GetDocument() const` (헤더 673행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::ToDeclaration() const` (헤더 720행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)  
  경로를 여는 상위 API: `XMLConstHandle::ToDeclaration() const`
- `XMLNode::ToUnknown() const` (헤더 723행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)  
  경로를 여는 상위 API: `XMLConstHandle::ToUnknown() const`
- `XMLNode::ChildElementCount(const char *) const` (헤더 729행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::ChildElementCount() const` (헤더 731행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::LastChild() const` (헤더 785행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::LastChild() const`
- `XMLNode::LinkEndChild(XMLNode *)` (헤더 843행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::SetUserData(void *)` (헤더 937행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::GetUserData() const` (헤더 944행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, unsigned int)` (헤더 2262행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, int64_t)` (헤더 2263행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, uint64_t)` (헤더 2264행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, bool)` (헤더 2265행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, double)` (헤더 2266행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(int)` (헤더 2273행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(unsigned int)` (헤더 2275행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(int64_t)` (헤더 2277행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(uint64_t)` (헤더 2279행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(bool)` (헤더 2281행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(float)` (헤더 2283행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(double)` (헤더 2285행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::ClearBuffer(bool)` (헤더 2325행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLUtil::ToStr(float, char *, int)` (헤더 615행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(float)`, `XMLElement::SetAttribute(const char *, float)`, `XMLElement::SetText(float)`, `XMLPrinter::PushText(float)`
- `XMLUtil::ToUnsigned64(const char *, uint64_t *)` (헤더 627행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::QueryUnsigned64Value(uint64_t *) const`, `XMLAttribute::Unsigned64Value() const`, `XMLElement::QueryAttribute(const char *, uint64_t *) const`, `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const`, `XMLElement::QueryUnsigned64Text(uint64_t *) const`, `XMLElement::Unsigned64Attribute(const char *, uint64_t) const`
- `XMLUtil::SetBoolSerialization(const char *, const char *)` (헤더 633행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLVisitor::VisitEnter(const XMLDocument &)` (헤더 479행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLVisitor::VisitExit(const XMLDocument &)` (헤더 483행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLVisitor::VisitEnter(const XMLElement &, const XMLAttribute *)` (헤더 488행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLVisitor::VisitExit(const XMLElement &)` (헤더 492행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLVisitor::Visit(const XMLDeclaration &)` (헤더 497행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLVisitor::Visit(const XMLText &)` (헤더 501행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLVisitor::Visit(const XMLComment &)` (헤더 505행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLVisitor::Visit(const XMLUnknown &)` (헤더 509행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)

## 호출 경로 있음 · 조건에 막힘

이미 실행된 함수 안에 이 API로 가는 호출이 있지만, 그 줄까지 실행이 도달하지 못했습니다. 아래 조건을 만족시키는 입력·상태가 필요합니다.

## 도달 · 일부 분기 미실행

API는 실행됐지만 안쪽 조건문 일부가 한 방향으로만 갔습니다. '한 번도 참/거짓 아님'인 조건을 만족시키는 입력·상태·옵션을 만들면 열립니다.

### `XMLUtil::ToInt(const char *, int *)` — 영역 7/11 실행
- third_party/tinyxml2/tinyxml2.cpp:601 조건 `IsPrefixHex(str)` 한 번도 **참** 아님 — `if (IsPrefixHex(str)) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ToInt(const char *, int *)`의 1번째 인자 `str`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLAttribute::QueryIntValue(int *) const`, `XMLElement::QueryIntText(int *) const`, `XMLUtil::ToBool(const char *, bool *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ToInt`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLUtil::ToInt64(const char *, int64_t *)` — 영역 7/11 실행
- third_party/tinyxml2/tinyxml2.cpp:670 조건 `IsPrefixHex(str)` 한 번도 **참** 아님 — `if (IsPrefixHex(str)) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ToInt64(const char *, int64_t *)`의 1번째 인자 `str`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLAttribute::QueryInt64Value(int64_t *) const`, `XMLElement::QueryInt64Text(int64_t *) const`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ToInt64`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)` — 영역 16/25 실행
- third_party/tinyxml2/tinyxml2.cpp:995 조건 `addThis->_document != _document` 한 번도 **참** 아님 — `if ( addThis->_document != _document ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`의 2번째 인자 `addThis`는 하네스에서 바뀌지만(69행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다
- third_party/tinyxml2/tinyxml2.cpp:1002 조건 `afterThis->_parent != this` 한 번도 **참** 아님 — `if ( afterThis->_parent != this ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`의 1번째 인자 `afterThis`는 하네스에서 바뀌지만(69행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `_parent`는 `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`, `XMLNode::InsertEndChild(XMLNode *)`, `XMLNode::InsertFirstChild(XMLNode *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)
- third_party/tinyxml2/tinyxml2.cpp:1006 조건 `afterThis == addThis` 한 번도 **참** 아님 — `if ( afterThis == addThis ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`의 1번째 인자 `afterThis`는 하네스에서 바뀌지만(69행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`의 2번째 인자 `addThis`는 하네스에서 바뀌지만(69행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLComment::ShallowClone(XMLDocument *) const` — 영역 2/3 실행
- third_party/tinyxml2/tinyxml2.cpp:1317 조건 `!doc` 한 번도 **참** 아님 — `if ( !doc ) {`
  - 원인(하네스가 인자를 고정): `XMLComment::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요

### `XMLDeclaration::ShallowClone(XMLDocument *) const` — 영역 2/3 실행
- third_party/tinyxml2/tinyxml2.cpp:1366 조건 `!doc` 한 번도 **참** 아님 — `if ( !doc ) {`
  - 원인(하네스가 인자를 고정): `XMLDeclaration::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요

### `XMLDocument::Clear()` — 영역 2/3 실행
- third_party/tinyxml2/tinyxml2.cpp:2233 조건 `_unlinked.Size()` 한 번도 **참** 아님 — `while( _unlinked.Size()) {`
  - 원인(라이브러리 내부에서 정해짐): `DynArray::PushArr(size_t)`의 1번째 인자 `count`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLPrinter::Putc(char)`, `XMLPrinter::Write(const char *, size_t)`에서 호출) (필드 `_size`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다
  - 원인(라이브러리 내부에서 정해짐): `_size`는 `DynArray::Clear()`, `DynArray::DynArray()`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLPrinter::VisitEnter(const XMLDocument &)` — 영역 2/3 실행
- third_party/tinyxml2/tinyxml2.cpp:2973 조건 `doc.HasBOM()` 한 번도 **참** 아님 — `if ( doc.HasBOM() ) {`
  - 원인(값을 정하는 API를 하네스가 안 부름): 하네스가 `XMLDocument::SetBOM(bool)`를 부르지 않아 1번째 인자 `useBOM` 값이 들어가지 않습니다 (필드 `_writeBOM`를 거쳐 조건에 쓰임) → 호출을 추가하세요
  - 원인(라이브러리 내부에서 정해짐): `XMLPrinter::VisitEnter(const XMLDocument &)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLDocument::Accept(XMLVisitor *) const`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLPrinter::VisitEnter`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLText::ShallowClone(XMLDocument *) const` — 영역 2/3 실행
- third_party/tinyxml2/tinyxml2.cpp:1268 조건 `!doc` 한 번도 **참** 아님 — `if ( !doc ) {`
  - 원인(하네스가 인자를 고정): `XMLText::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요

### `XMLUnknown::ShallowClone(XMLDocument *) const` — 영역 2/3 실행
- third_party/tinyxml2/tinyxml2.cpp:1414 조건 `!doc` 한 번도 **참** 아님 — `if ( !doc ) {`
  - 원인(하네스가 인자를 고정): `XMLUnknown::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요

### `XMLConstHandle::LastChildElement(const char *) const` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.h:2157 조건 `_node` 한 번도 **거짓** 아님 — `return XMLConstHandle( _node ? _node->LastChildElement( name ) : 0 );`
  - 원인(하네스가 값의 범위를 좁힘): `XMLConstHandle::XMLConstHandle(const XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(190행) (필드 `_node`를 거쳐 조건에 쓰임) → nullptr도 넘겨 보세요

### `XMLDocument::Print(XMLPrinter *) const` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.cpp:2488 조건 `streamer` 한 번도 **거짓** 아님 — `if ( streamer ) {`
  - 원인(하네스가 인자를 고정): `XMLDocument::Print(XMLPrinter *) const`의 1번째 인자 `streamer`를 하네스가 고정합니다(171행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요

### `XMLElement::InsertNewChildElement(const char *)` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.cpp:2048 조건 `InsertEndChild(node)` 한 번도 **거짓** 아님 — `return InsertEndChild(node) ? node : 0;`
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다
  - 원인(라이브러리 내부에서 정해짐): `_document`는 `XMLDocument::XMLDocument(bool, Whitespace)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLElement::InsertNewComment(const char *)` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.cpp:2054 조건 `InsertEndChild(node)` 한 번도 **거짓** 아님 — `return InsertEndChild(node) ? node : 0;`
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다
  - 원인(라이브러리 내부에서 정해짐): `_document`는 `XMLDocument::XMLDocument(bool, Whitespace)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLElement::InsertNewText(const char *)` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.cpp:2060 조건 `InsertEndChild(node)` 한 번도 **거짓** 아님 — `return InsertEndChild(node) ? node : 0;`
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다
  - 원인(라이브러리 내부에서 정해짐): `_document`는 `XMLDocument::XMLDocument(bool, Whitespace)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLElement::InsertNewUnknown(const char *)` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.cpp:2072 조건 `InsertEndChild(node)` 한 번도 **거짓** 아님 — `return InsertEndChild(node) ? node : 0;`
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다
  - 원인(라이브러리 내부에서 정해짐): `_document`는 `XMLDocument::XMLDocument(bool, Whitespace)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLHandle::FirstChildElement(const char *)` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.h:2075 조건 `_node` 한 번도 **거짓** 아님 — `return XMLHandle( _node ? _node->FirstChildElement( name ) : 0 );`
  - 원인(하네스가 인자를 고정): `XMLHandle::XMLHandle(XMLNode *)`의 1번째 인자 `node`를 하네스가 고정합니다(188행에서 항상 같은 객체 `&doc`) (필드 `_node`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요 (또는 `XMLHandle::XMLHandle(XMLNode &)`로도 이 값을 바꿀 수 있음)

### `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)` — 영역 19/25 실행
- third_party/tinyxml2/tinyxml2.cpp:422 조건 `input < 0x10000` 한 번도 **참** 아님 — `else if ( input < 0x10000 ) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`의 1번째 인자 `input`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::GetCharacterRef(const char *, char *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ConvertUTF32ToUTF8`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.cpp:425 조건 `input < 0x200000` 한 번도 **거짓** 아님 — `else if ( input < 0x200000 ) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`의 1번째 인자 `input`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::GetCharacterRef(const char *, char *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ConvertUTF32ToUTF8`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.cpp:443 조건 `case 3` 한 번도 **참** 아님 — `case 3:`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`의 3번째 인자 `length`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::GetCharacterRef(const char *, char *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ConvertUTF32ToUTF8`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.cpp:457 조건 `default` 한 번도 **참** 아님 — `default:`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`의 3번째 인자 `length`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::GetCharacterRef(const char *, char *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ConvertUTF32ToUTF8`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLNode::InsertEndChild(XMLNode *)` — 영역 18/22 실행
- third_party/tinyxml2/tinyxml2.cpp:934 조건 `addThis->_document != _document` 한 번도 **참** 아님 — `if ( addThis->_document != _document ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertEndChild(XMLNode *)`의 1번째 인자 `addThis`는 하네스에서 바뀌지만(57행(변수), 73행(변수), 159행(변수), 164행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다

### `XMLNode::InsertFirstChild(XMLNode *)` — 영역 18/22 실행
- third_party/tinyxml2/tinyxml2.cpp:964 조건 `addThis->_document != _document` 한 번도 **참** 아님 — `if ( addThis->_document != _document ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertFirstChild(XMLNode *)`의 1번째 인자 `addThis`는 하네스에서 바뀌지만(61행(변수), 62행(변수), 63행(변수), 64행(변수), 74행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다

### `XMLElement::ShallowClone(XMLDocument *) const` — 영역 5/6 실행
- third_party/tinyxml2/tinyxml2.cpp:2112 조건 `!doc` 한 번도 **참** 아님 — `if ( !doc ) {`
  - 원인(하네스가 인자를 고정): `XMLElement::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요

### `XMLNode::PreviousSiblingElement(const char *) const` — 영역 6/7 실행
- third_party/tinyxml2/tinyxml2.cpp:1070 조건 `element` 한 번도 **참** 아님 — `if ( element ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertFirstChild(XMLNode *)`의 1번째 인자 `addThis`는 하네스에서 바뀌지만(61행(변수), 62행(변수), 63행(변수), 64행(변수), 74행(변수)) 조건을 만족하는 값이 나오지 않았습니다 (필드 `_prev`를 거쳐 조건에 쓰임). 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`의 1번째 인자 `afterThis`는 하네스에서 바뀌지만(69행(변수)) 조건을 만족하는 값이 나오지 않았습니다 (필드 `_prev`를 거쳐 조건에 쓰임). 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLElement::ShallowEqual(const XMLNode *) const` — 영역 19/22 실행
- third_party/tinyxml2/tinyxml2.cpp:2127 조건 `other` 한 번도 **거짓** 아님 — `if ( other && XMLUtil::StringEqual( other->Name(), Name() )) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLElement::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:2127 조건 `XMLUtil::StringEqual( other->Name(), Name() )` 한 번도 **거짓** 아님 — `if ( other && XMLUtil::StringEqual( other->Name(), Name() )) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLElement::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:2132 조건 `b` 한 번도 **거짓** 아님 — `while ( a && b ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLElement::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `_rootAttribute`는 `XMLElement::DeleteAttribute(const char *)`, `XMLElement::FindOrCreateAttribute(const char *)`, `XMLElement::ParseAttributes(char *, int *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)
- third_party/tinyxml2/tinyxml2.cpp:2133 조건 `!XMLUtil::StringEqual( a->Value(), b->Value() )` 한 번도 **참** 아님 — `if ( !XMLUtil::StringEqual( a->Value(), b->Value() ) ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLElement::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `_rootAttribute`는 `XMLElement::DeleteAttribute(const char *)`, `XMLElement::FindOrCreateAttribute(const char *)`, `XMLElement::ParseAttributes(char *, int *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)
- third_party/tinyxml2/tinyxml2.cpp:2139 조건 `a` 한 번도 **참** 아님 — `if ( a || b ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLElement::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `_rootAttribute`는 `XMLElement::DeleteAttribute(const char *)`, `XMLElement::FindOrCreateAttribute(const char *)`, `XMLElement::ParseAttributes(char *, int *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)
- third_party/tinyxml2/tinyxml2.cpp:2139 조건 `b` 한 번도 **참** 아님 — `if ( a || b ) {`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLElement::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
  - 원인(라이브러리 내부에서 정해짐): `_rootAttribute`는 `XMLElement::DeleteAttribute(const char *)`, `XMLElement::FindOrCreateAttribute(const char *)`, `XMLElement::ParseAttributes(char *, int *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLUtil::ToUnsigned(const char *, unsigned int *)` — 영역 7/8 실행
- third_party/tinyxml2/tinyxml2.cpp:618 조건 `IsPrefixHex(str)` 한 번도 **참** 아님 — `if (TIXML_SSCANF(str, IsPrefixHex(str) ? "%x" : "%u", value) == 1) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ToUnsigned(const char *, unsigned int *)`의 1번째 인자 `str`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLAttribute::QueryUnsignedValue(unsigned int *) const`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ToUnsigned`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLDocument::DeleteNode(XMLNode *)` — 영역 9/10 실행
- third_party/tinyxml2/tinyxml2.cpp:2333 조건 `node == 0` 한 번도 **참** 아님 — `if(node == 0) {`
  - 원인(하네스가 값의 범위를 좁힘): `XMLDocument::DeleteNode(XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(150행) → nullptr도 넘겨 보세요

### `XMLDocument::Accept(XMLVisitor *) const` — 영역 10/11 실행
- third_party/tinyxml2/tinyxml2.cpp:781 조건 `visitor->VisitEnter( *this )` 한 번도 **거짓** 아님 — `if ( visitor->VisitEnter( *this ) ) {`
  - 원인(하네스가 인자를 고정): `XMLDocument::Accept(XMLVisitor *) const`의 1번째 인자 `visitor`를 하네스가 고정합니다(172행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요
- third_party/tinyxml2/tinyxml2.cpp:783 조건 `!node->Accept( visitor )` 한 번도 **참** 아님 — `if ( !node->Accept( visitor ) ) {`
  - 원인(하네스가 인자를 고정): `XMLDocument::Accept(XMLVisitor *) const`의 1번째 인자 `visitor`를 하네스가 고정합니다(172행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertEndChild(XMLNode *)`의 1번째 인자 `addThis`는 하네스에서 바뀌지만(57행(변수), 73행(변수), 159행(변수), 164행(변수)) 조건을 만족하는 값이 나오지 않았습니다 (필드 `_firstChild`를 거쳐 조건에 쓰임). 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLElement::Accept(XMLVisitor *) const` — 영역 10/11 실행
- third_party/tinyxml2/tinyxml2.cpp:2152 조건 `visitor->VisitEnter( *this, _rootAttribute )` 한 번도 **거짓** 아님 — `if ( visitor->VisitEnter( *this, _rootAttribute ) ) {`
  - 원인(하네스가 인자를 고정): `XMLElement::Accept(XMLVisitor *) const`의 1번째 인자 `visitor`를 하네스가 고정합니다(172행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요
  - 원인(라이브러리 내부에서 정해짐): `_rootAttribute`는 `XMLElement::DeleteAttribute(const char *)`, `XMLElement::FindOrCreateAttribute(const char *)`, `XMLElement::ParseAttributes(char *, int *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)
- third_party/tinyxml2/tinyxml2.cpp:2154 조건 `!node->Accept( visitor )` 한 번도 **참** 아님 — `if ( !node->Accept( visitor ) ) {`
  - 원인(하네스가 인자를 고정): `XMLElement::Accept(XMLVisitor *) const`의 1번째 인자 `visitor`를 하네스가 고정합니다(172행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLNode::InsertEndChild(XMLNode *)`의 1번째 인자 `addThis`는 하네스에서 바뀌지만(57행(변수), 73행(변수), 159행(변수), 164행(변수)) 조건을 만족하는 값이 나오지 않았습니다 (필드 `_firstChild`를 거쳐 조건에 쓰임). 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLDocument::Identify(char *, XMLNode **, bool)` — 영역 45/49 실행
- third_party/tinyxml2/tinyxml2.cpp:752 조건 `WhitespaceMode() == PEDANTIC_WHITESPACE` 한 번도 **참** 아님 — `if (WhitespaceMode() == PEDANTIC_WHITESPACE && first && p != start && *(p + elementHeaderLen) == '/') {`
  - 원인(하네스가 값의 범위를 좁힘): `XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 `COLLAPSE_WHITESPACE`, `PRESERVE_WHITESPACE`, `기본값` 중에서만 고릅니다(42행, 46행) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
  - 원인(라이브러리 내부에서 정해짐): `XMLDocument::Identify(char *, XMLNode **, bool)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLNode::ParseDeep(char *, StrPair *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLDocument::Identify`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLUtil::ReadBOM(const char *, bool *)` — 영역 15/16 실행
- third_party/tinyxml2/tinyxml2.cpp:401 조건 `*(pu+2) == TIXML_UTF_LEAD_2` 한 번도 **참** 아님 — `&& *(pu+2) == TIXML_UTF_LEAD_2 ) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ReadBOM(const char *, bool *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLDocument::Parse()`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ReadBOM`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLUtil::GetCharacterRef(const char *, char *, int *)` — 영역 54/57 실행
- third_party/tinyxml2/tinyxml2.cpp:470 조건 `*(p + 1) == '#'` 한 번도 **거짓** 아님 — `if (*(p + 1) == '#' && *(p + 2)) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::GetCharacterRef(const char *, char *, int *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`StrPair::GetStr()`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::GetCharacterRef`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.cpp:528 조건 `ucs > MAX_CODE_POINT - digitScaled` 한 번도 **참** 아님 — `if (digitScaled > MAX_CODE_POINT || ucs > MAX_CODE_POINT - digitScaled) {`
  - 원인(라이브러리 내부에서 정해짐): 조건이 매개변수·필드가 아니라 지역 변수나 입력 데이터에 달려 있습니다 (입력 내용·딕셔너리로 열어야 함)
- third_party/tinyxml2/tinyxml2.cpp:533 조건 `mult > MAX_CODE_POINT` 한 번도 **참** 아님 — `if (mult > MAX_CODE_POINT) {`
  - 원인(라이브러리 내부에서 정해짐): 조건이 매개변수·필드가 아니라 지역 변수나 입력 데이터에 달려 있습니다 (입력 내용·딕셔너리로 열어야 함)
- third_party/tinyxml2/tinyxml2.cpp:539 조건 `ucs > MAX_CODE_POINT` 한 번도 **참** 아님 — `if (ucs > MAX_CODE_POINT) {`
  - 원인(라이브러리 내부에서 정해짐): 조건이 매개변수·필드가 아니라 지역 변수나 입력 데이터에 달려 있습니다 (입력 내용·딕셔너리로 열어야 함)
- third_party/tinyxml2/tinyxml2.cpp:544 조건 `*length == 0` 한 번도 **참** 아님 — `if (*length == 0) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::GetCharacterRef(const char *, char *, int *)`의 3번째 인자 `length`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`StrPair::GetStr()`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::GetCharacterRef`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)` — 영역 22/23 실행
- third_party/tinyxml2/tinyxml2.cpp:2605 조건 `(aposInAttributes == ESCAPE_APOS_CHARS_IN_ATTRIBUTES)` 한 번도 **거짓** 아님 — `if ((aposInAttributes == ESCAPE_APOS_CHARS_IN_ATTRIBUTES) || (entityValue != SINGLE_QUOTE)) {`
  - 원인(하네스가 인자를 고정): `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)`의 4번째 인자 `aposInAttributes`를 하네스가 고정합니다(170행에서 기본값, 178행에서 기본값) → 퍼저 입력으로 바꾸세요

### `XMLComment::ShallowEqual(const XMLNode *) const` — 영역 6/6 실행
- third_party/tinyxml2/tinyxml2.cpp:1329 조건 `comment` 한 번도 **거짓** 아님 — `return ( comment && XMLUtil::StringEqual( comment->Value(), Value() ));`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLComment::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:1329 조건 `XMLUtil::StringEqual( comment->Value(), Value() )` 한 번도 **거짓** 아님 — `return ( comment && XMLUtil::StringEqual( comment->Value(), Value() ));`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLComment::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLDeclaration::ShallowEqual(const XMLNode *) const` — 영역 6/6 실행
- third_party/tinyxml2/tinyxml2.cpp:1378 조건 `declaration` 한 번도 **거짓** 아님 — `return ( declaration && XMLUtil::StringEqual( declaration->Value(), Value() ));`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLDeclaration::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:1378 조건 `XMLUtil::StringEqual( declaration->Value(), Value() )` 한 번도 **거짓** 아님 — `return ( declaration && XMLUtil::StringEqual( declaration->Value(), Value() ));`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLDeclaration::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLDocument::Parse(const char *, size_t)` — 영역 15/15 실행
- third_party/tinyxml2/tinyxml2.cpp:2459 조건 `nBytes == 0` 한 번도 **참** 아님 — `if ( nBytes == 0 || !xml || !*xml ) {`
  - 원인(하네스가 인자를 고정): `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(44행에서 기본값, 233행에서 기본값) → 퍼저 입력으로 바꾸세요
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`는 하네스에서 바뀌지만(44행(변수), 233행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:2459 조건 `!xml` 한 번도 **참** 아님 — `if ( nBytes == 0 || !xml || !*xml ) {`
  - 원인(하네스가 값의 범위를 좁힘): `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(44행, 233행) → nullptr도 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:2463 조건 `nBytes == static_cast<size_t>(-1)` 한 번도 **거짓** 아님 — `if ( nBytes == static_cast<size_t>(-1) ) {`
  - 원인(하네스가 인자를 고정): `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(44행에서 기본값, 233행에서 기본값) → 퍼저 입력으로 바꾸세요

### `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)` — 영역 8/8 실행
- third_party/tinyxml2/tinyxml2.cpp:2983 조건 `element.Parent()` 한 번도 **거짓** 아님 — `if ( element.Parent() ) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)`의 1번째 인자 `element`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLElement::Accept(XMLVisitor *) const`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLPrinter::VisitEnter`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
  - 원인(라이브러리 내부에서 정해짐): `_parent`는 `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`, `XMLNode::InsertEndChild(XMLNode *)`, `XMLNode::InsertFirstChild(XMLNode *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLText::ShallowEqual(const XMLNode *) const` — 영역 6/6 실행
- third_party/tinyxml2/tinyxml2.cpp:1281 조건 `text` 한 번도 **거짓** 아님 — `return ( text && XMLUtil::StringEqual( text->Value(), Value() ) );`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLText::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:1281 조건 `XMLUtil::StringEqual( text->Value(), Value() )` 한 번도 **거짓** 아님 — `return ( text && XMLUtil::StringEqual( text->Value(), Value() ) );`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLText::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLUnknown::ShallowEqual(const XMLNode *) const` — 영역 6/6 실행
- third_party/tinyxml2/tinyxml2.cpp:1426 조건 `unknown` 한 번도 **거짓** 아님 — `return ( unknown && XMLUtil::StringEqual( unknown->Value(), Value() ));`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLUnknown::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요
- third_party/tinyxml2/tinyxml2.cpp:1426 조건 `XMLUtil::StringEqual( unknown->Value(), Value() )` 한 번도 **거짓** 아님 — `return ( unknown && XMLUtil::StringEqual( unknown->Value(), Value() ));`
  - 원인(인자는 바뀌지만 맞는 값이 안 나옴): `XMLUnknown::ShallowEqual(const XMLNode *) const`의 1번째 인자 `compare`는 하네스에서 바뀌지만(163행(변수)) 조건을 만족하는 값이 나오지 않았습니다. 포인터·참조로 넘기는 객체의 상태가 조건과 맞지 않습니다 → null, 다른 문서·다른 부모 소속 객체 등 다른 종류의 객체를 넘겨 보세요

### `XMLUtil::IsPrefixHex(const char *)` — 영역 7/7 실행
- third_party/tinyxml2/tinyxml2.h:588 조건 `p` 한 번도 **거짓** 아님 — `return p && *p == '0' && ( *(p + 1) == 'x' || *(p + 1) == 'X');`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::IsPrefixHex(const char *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::ToInt(const char *, int *)`, `XMLUtil::ToInt64(const char *, int64_t *)`, `XMLUtil::ToUnsigned(const char *, unsigned int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::IsPrefixHex`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.h:588 조건 `*(p + 1) == 'x'` 한 번도 **참** 아님 — `return p && *p == '0' && ( *(p + 1) == 'x' || *(p + 1) == 'X');`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::IsPrefixHex(const char *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::ToInt(const char *, int *)`, `XMLUtil::ToInt64(const char *, int64_t *)`, `XMLUtil::ToUnsigned(const char *, unsigned int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::IsPrefixHex`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.h:588 조건 `*(p + 1) == 'X'` 한 번도 **참** 아님 — `return p && *p == '0' && ( *(p + 1) == 'x' || *(p + 1) == 'X');`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::IsPrefixHex(const char *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::ToInt(const char *, int *)`, `XMLUtil::ToInt64(const char *, int64_t *)`, `XMLUtil::ToUnsigned(const char *, unsigned int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::IsPrefixHex`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

## 완전 도달

`XMLAttribute::Name() const`, `XMLAttribute::Value() const`, `XMLAttribute::Next() const`, `XMLAttribute::IntValue() const`, `XMLAttribute::Int64Value() const`, `XMLAttribute::UnsignedValue() const`, `XMLAttribute::BoolValue() const`, `XMLAttribute::DoubleValue() const`, `XMLAttribute::QueryIntValue(int *) const`, `XMLAttribute::QueryUnsignedValue(unsigned int *) const`, `XMLAttribute::QueryInt64Value(int64_t *) const`, `XMLAttribute::QueryBoolValue(bool *) const`, `XMLAttribute::QueryDoubleValue(double *) const`, `XMLAttribute::QueryFloatValue(float *) const`, `XMLAttribute::SetAttribute(const char *)`, `XMLAttribute::SetAttribute(int)`, `XMLAttribute::SetAttribute(unsigned int)`, `XMLAttribute::SetAttribute(int64_t)`, `XMLAttribute::SetAttribute(bool)`, `XMLAttribute::SetAttribute(double)`, `XMLComment::ToComment()`, `XMLComment::ToComment() const`, `XMLComment::Accept(XMLVisitor *) const`, `XMLConstHandle::XMLConstHandle(const XMLNode *)`, `XMLConstHandle::PreviousSibling() const`, `XMLConstHandle::ToNode() const`, `XMLDeclaration::ToDeclaration()`, `XMLDeclaration::ToDeclaration() const`, `XMLDeclaration::Accept(XMLVisitor *) const`, `XMLDocument::XMLDocument(bool, Whitespace)`, `XMLDocument::ToDocument()`, `XMLDocument::ToDocument() const`, `XMLDocument::ProcessEntities() const`, `XMLDocument::WhitespaceMode() const`, `XMLDocument::HasBOM() const`, `XMLDocument::RootElement()`, `XMLDocument::NewElement(const char *)`, `XMLDocument::NewComment(const char *)`, `XMLDocument::NewText(const char *)`, `XMLDocument::NewDeclaration(const char *)`, `XMLDocument::NewUnknown(const char *)`, `XMLDocument::ClearError()`, `XMLDocument::Error() const`, `XMLDocument::ErrorID() const`, `XMLDocument::ErrorName() const`, `XMLDocument::ErrorIDToName(XMLError)`, `XMLDocument::ErrorStr() const`, `XMLDocument::ErrorLineNum() const`, `XMLDocument::MarkInUse(const XMLNode *const)`, `XMLDocument::ShallowClone(XMLDocument *) const`, `XMLElement::Name() const`, `XMLElement::SetName(const char *, bool)`, `XMLElement::ToElement()`, `XMLElement::ToElement() const`, `XMLElement::Attribute(const char *, const char *) const`, `XMLElement::IntAttribute(const char *, int) const`, `XMLElement::BoolAttribute(const char *, bool) const`, `XMLElement::QueryIntAttribute(const char *, int *) const`, `XMLElement::QueryUnsignedAttribute(const char *, unsigned int *) const`, `XMLElement::QueryInt64Attribute(const char *, int64_t *) const`, `XMLElement::QueryBoolAttribute(const char *, bool *) const`, `XMLElement::QueryDoubleAttribute(const char *, double *) const`, `XMLElement::QueryFloatAttribute(const char *, float *) const`, `XMLElement::SetAttribute(const char *, const char *)`, `XMLElement::SetAttribute(const char *, int)`, `XMLElement::SetAttribute(const char *, unsigned int)`, `XMLElement::SetAttribute(const char *, int64_t)`, `XMLElement::SetAttribute(const char *, bool)`, `XMLElement::SetAttribute(const char *, double)`, `XMLElement::DeleteAttribute(const char *)`, `XMLElement::FirstAttribute() const`, `XMLElement::FindAttribute(const char *) const`, `XMLElement::GetText() const`, `XMLElement::SetText(const char *)`, `XMLElement::SetText(int)`, `XMLElement::SetText(uint64_t)`, `XMLElement::SetText(bool)`, `XMLElement::SetText(double)`, `XMLElement::QueryIntText(int *) const`, `XMLElement::QueryInt64Text(int64_t *) const`, `XMLElement::QueryBoolText(bool *) const`, `XMLElement::QueryDoubleText(double *) const`, `XMLElement::IntText(int) const`, `XMLElement::ClosingType() const`, `XMLHandle::XMLHandle(XMLNode *)`, `XMLHandle::FirstChild()`, `XMLHandle::NextSiblingElement(const char *)`, `XMLHandle::ToElement()`, `XMLNode::GetDocument()`, `XMLNode::ToElement()`, `XMLNode::ToText()`, `XMLNode::ToComment()`, `XMLNode::ToDocument()`, `XMLNode::ToDeclaration()`, `XMLNode::ToUnknown()`, `XMLNode::ToElement() const`, `XMLNode::ToText() const`, `XMLNode::ToComment() const`, `XMLNode::ToDocument() const`, `XMLNode::Value() const`, `XMLNode::SetValue(const char *, bool)`, `XMLNode::GetLineNum() const`, `XMLNode::Parent() const`, `XMLNode::Parent()`, `XMLNode::NoChildren() const`, `XMLNode::FirstChild() const`, `XMLNode::FirstChild()`, `XMLNode::FirstChildElement(const char *) const`, `XMLNode::FirstChildElement(const char *)`, `XMLNode::LastChild()`, `XMLNode::LastChildElement(const char *) const`, `XMLNode::LastChildElement(const char *)`, `XMLNode::PreviousSibling() const`, `XMLNode::PreviousSibling()`, `XMLNode::PreviousSiblingElement(const char *)`, `XMLNode::NextSibling() const`, `XMLNode::NextSibling()`, `XMLNode::NextSiblingElement(const char *) const`, `XMLNode::NextSiblingElement(const char *)`, `XMLNode::DeleteChildren()`, `XMLNode::DeleteChild(XMLNode *)`, `XMLNode::DeepClone(XMLDocument *) const`, `XMLPrinter::PushHeader(bool, bool)`, `XMLPrinter::OpenElement(const char *, bool)`, `XMLPrinter::PushAttribute(const char *, const char *)`, `XMLPrinter::PushAttribute(const char *, int)`, `XMLPrinter::CloseElement(bool)`, `XMLPrinter::PushText(const char *, bool)`, `XMLPrinter::PushComment(const char *)`, `XMLPrinter::PushDeclaration(const char *)`, `XMLPrinter::PushUnknown(const char *)`, `XMLPrinter::VisitExit(const XMLDocument &)`, `XMLPrinter::VisitExit(const XMLElement &)`, `XMLPrinter::Visit(const XMLText &)`, `XMLPrinter::Visit(const XMLComment &)`, `XMLPrinter::Visit(const XMLDeclaration &)`, `XMLPrinter::Visit(const XMLUnknown &)`, `XMLPrinter::CStr() const`, `XMLPrinter::CStrSize() const`, `XMLText::Accept(XMLVisitor *) const`, `XMLText::ToText()`, `XMLText::ToText() const`, `XMLText::SetCData(bool)`, `XMLText::CData() const`, `XMLUnknown::ToUnknown()`, `XMLUnknown::ToUnknown() const`, `XMLUnknown::Accept(XMLVisitor *) const`, `XMLUtil::SkipWhiteSpace(const char *, int *)`, `XMLUtil::SkipWhiteSpace(char *const, int *)`, `XMLUtil::IsWhiteSpace(char)`, `XMLUtil::IsNameStartChar(unsigned char)`, `XMLUtil::IsNameChar(unsigned char)`, `XMLUtil::StringEqual(const char *, const char *, int)`, `XMLUtil::IsUTF8Continuation(const char)`, `XMLUtil::ToStr(int, char *, int)`, `XMLUtil::ToStr(unsigned int, char *, int)`, `XMLUtil::ToStr(bool, char *, int)`, `XMLUtil::ToStr(double, char *, int)`, `XMLUtil::ToStr(int64_t, char *, int)`, `XMLUtil::ToStr(uint64_t, char *, int)`, `XMLUtil::ToBool(const char *, bool *)`, `XMLUtil::ToFloat(const char *, float *)`, `XMLUtil::ToDouble(const char *, double *)`
