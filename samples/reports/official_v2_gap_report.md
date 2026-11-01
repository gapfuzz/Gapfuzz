# 커버리지 갭 리포트 — official_v2-r1

- 하네스: `harnesses/official_v2.cpp`
- 대상 헤더: `third_party/tinyxml2/tinyxml2.h`
- 공개 API 수: **303**

## 요약

| 분류 | 개수 | 비율 | 조치 |
|---|---:|---:|---|
| 호출 안 함 | 261 | 86% | 하네스에 이 API(또는 상위 API) 호출을 추가 |
| 호출 경로 있음 · 조건에 막힘 | 0 | 0% | 막힌 조건을 만족시키는 입력·상태를 만들어 줌 |
| 도달 · 일부 분기 미실행 | 11 | 4% | 입력·옵션 다양화(분기 조건 확인) |
| 완전 도달 | 31 | 10% | 조치 불필요 |

## 클래스별

| 클래스 | 호출 안 함 | 호출 경로 있음 · 조건에 막힘 | 도달 · 일부 분기 미실행 | 완전 도달 |
|---|---:|---:|---:|---:|
| XMLAttribute | 24 | 0 | 0 | 2 |
| XMLComment | 5 | 0 | 0 | 0 |
| XMLConstHandle | 17 | 0 | 0 | 0 |
| XMLDeclaration | 4 | 0 | 0 | 1 |
| XMLDocument | 24 | 0 | 3 | 9 |
| XMLElement | 66 | 0 | 1 | 4 |
| XMLHandle | 17 | 0 | 0 | 0 |
| XMLNode | 37 | 0 | 2 | 8 |
| XMLPrinter | 33 | 0 | 0 | 0 |
| XMLText | 5 | 0 | 0 | 2 |
| XMLUnknown | 5 | 0 | 0 | 0 |
| XMLUtil | 16 | 0 | 5 | 5 |
| XMLVisitor | 8 | 0 | 0 | 0 |

## 하네스에서 고칠 곳

도달한 API 안에서 한쪽으로만 간 조건을 거슬러 올라가, 그 값이 **하네스의 어떤 호출·인자에서 정해지는지** 찾은 결과입니다.

| 막힌 분기의 원인 | 개수 |
|---|---:|
| 하네스가 값의 범위를 좁힘 | 1 |
| 라이브러리 내부에서 정해짐 | 14 |
| 합계 | 15 |

### 1. [하네스가 값의 범위를 좁힘] 27행, 29행
- `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(27행, 29행) → nullptr도 넘겨 보세요
- 하네스 코드: `doc.Parse(data_string.c_str(), n);`
- 하네스 코드: `doc.Parse(data_string.c_str());`
- 이 때문에 막힌 분기 1개:
  - `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `!xml` 한 번도 참 아님

## 호출 안 함

하네스의 실행 경로에서 이 함수로 가는 호출 자체가 없습니다. 퍼징을 오래 돌려도 열리지 않으므로 하네스를 바꿔야 합니다.

- `XMLAttribute::GetLineNum() const` (헤더 1149행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::Next() const` (헤더 1152행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLAttribute::IntValue() const` (헤더 1160행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::Int64Value() const` (헤더 1166행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::Unsigned64Value() const` (헤더 1172행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::UnsignedValue() const` (헤더 1179행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::BoolValue() const` (헤더 1185행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::DoubleValue() const` (헤더 1191행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::FloatValue() const` (헤더 1197행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLAttribute::QueryIntValue(int *) const` (헤더 1207행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::IntValue() const`, `XMLElement::IntAttribute(const char *, int) const`, `XMLElement::QueryAttribute(const char *, int *) const`, `XMLElement::QueryIntAttribute(const char *, int *) const`
- `XMLAttribute::QueryUnsignedValue(unsigned int *) const` (헤더 1209행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::UnsignedValue() const`, `XMLElement::QueryAttribute(const char *, unsigned int *) const`, `XMLElement::QueryUnsignedAttribute(const char *, unsigned int *) const`, `XMLElement::UnsignedAttribute(const char *, unsigned int) const`
- `XMLAttribute::QueryInt64Value(int64_t *) const` (헤더 1211행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::Int64Value() const`, `XMLElement::Int64Attribute(const char *, int64_t) const`, `XMLElement::QueryAttribute(const char *, int64_t *) const`, `XMLElement::QueryInt64Attribute(const char *, int64_t *) const`
- `XMLAttribute::QueryUnsigned64Value(uint64_t *) const` (헤더 1213행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::Unsigned64Value() const`, `XMLElement::QueryAttribute(const char *, uint64_t *) const`, `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const`, `XMLElement::Unsigned64Attribute(const char *, uint64_t) const`
- `XMLAttribute::QueryBoolValue(bool *) const` (헤더 1215행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::BoolValue() const`, `XMLElement::BoolAttribute(const char *, bool) const`, `XMLElement::QueryAttribute(const char *, bool *) const`, `XMLElement::QueryBoolAttribute(const char *, bool *) const`
- `XMLAttribute::QueryDoubleValue(double *) const` (헤더 1217행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::DoubleValue() const`, `XMLElement::DoubleAttribute(const char *, double) const`, `XMLElement::QueryAttribute(const char *, double *) const`, `XMLElement::QueryDoubleAttribute(const char *, double *) const`
- `XMLAttribute::QueryFloatValue(float *) const` (헤더 1219행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::FloatValue() const`, `XMLElement::FloatAttribute(const char *, float) const`, `XMLElement::QueryAttribute(const char *, float *) const`, `XMLElement::QueryFloatAttribute(const char *, float *) const`
- `XMLAttribute::SetAttribute(const char *)` (헤더 1222행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::SetAttribute(const char *, const char *)`, `XMLElement::ShallowClone(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLAttribute::SetAttribute(int)` (헤더 1224행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, int)`
- `XMLAttribute::SetAttribute(unsigned int)` (헤더 1226행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, unsigned int)`
- `XMLAttribute::SetAttribute(int64_t)` (헤더 1228행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, int64_t)`
- `XMLAttribute::SetAttribute(uint64_t)` (헤더 1230행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, uint64_t)`
- `XMLAttribute::SetAttribute(bool)` (헤더 1232행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, bool)`
- `XMLAttribute::SetAttribute(double)` (헤더 1234행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, double)`
- `XMLAttribute::SetAttribute(float)` (헤더 1236행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetAttribute(const char *, float)`
- `XMLComment::ToComment()` (헤더 1033행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLComment::ToComment() const` (헤더 1036행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLComment::ShallowEqual(const XMLNode *) const`, `XMLElement::GetText() const`
- `XMLComment::Accept(XMLVisitor *) const` (헤더 1040행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLComment::ShallowClone(XMLDocument *) const` (헤더 1042행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLComment::ShallowEqual(const XMLNode *) const` (헤더 1043행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::XMLConstHandle(const XMLNode *)` (헤더 2135행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::FirstChild() const`, `XMLConstHandle::FirstChildElement(const char *) const`, `XMLConstHandle::LastChild() const`, `XMLConstHandle::LastChildElement(const char *) const`, `XMLConstHandle::NextSibling() const`, `XMLConstHandle::NextSiblingElement(const char *) const`
- `XMLConstHandle::XMLConstHandle(const XMLNode &)` (헤더 2137행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::XMLConstHandle(const XMLConstHandle &)` (헤더 2139행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::operator=(const XMLConstHandle &)` (헤더 2142행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::FirstChild() const` (헤더 2147행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::FirstChildElement(const char *) const` (헤더 2150행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::LastChild() const` (헤더 2153행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::LastChildElement(const char *) const` (헤더 2156행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::PreviousSibling() const` (헤더 2159행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::PreviousSiblingElement(const char *) const` (헤더 2162행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::NextSibling() const` (헤더 2165행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::NextSiblingElement(const char *) const` (헤더 2168행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToNode() const` (헤더 2173행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToElement() const` (헤더 2176행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToText() const` (헤더 2179행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToUnknown() const` (헤더 2182행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLConstHandle::ToDeclaration() const` (헤더 2185행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDeclaration::ToDeclaration() const` (헤더 1075행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::ToDeclaration() const`, `XMLDeclaration::ShallowEqual(const XMLNode *) const`
- `XMLDeclaration::Accept(XMLVisitor *) const` (헤더 1079행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLDeclaration::ShallowClone(XMLDocument *) const` (헤더 1081행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLDeclaration::ShallowEqual(const XMLNode *) const` (헤더 1082행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::ToDocument() const` (헤더 1734행) — 호출 지점은 실행됐지만 다른 클래스의 구현으로 분기됨(가상 함수/생성자)
- `XMLDocument::LoadFile(const char *)` (헤더 1756행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::LoadFile(FILE *)` (헤더 1769행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::LoadFile(const char *)`
- `XMLDocument::SaveFile(const char *, bool)` (헤더 1776행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::SaveFile(FILE *, bool)` (헤더 1785행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::SaveFile(const char *, bool)`
- `XMLDocument::HasBOM() const` (헤더 1797행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::VisitEnter(const XMLDocument &)`
- `XMLDocument::SetBOM(bool)` (헤더 1802행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::RootElement()` (헤더 1809행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::RootElement() const` (헤더 1812행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::Print(XMLPrinter *) const` (헤더 1830행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`
- `XMLDocument::Accept(XMLVisitor *) const` (헤더 1831행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLDocument::NewElement(const char *)` (헤더 1838행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::InsertNewChildElement(const char *)`, `XMLElement::ShallowClone(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLDocument::NewComment(const char *)` (헤더 1844행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLComment::ShallowClone(XMLDocument *) const`, `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::InsertNewComment(const char *)`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLDocument::NewText(const char *)` (헤더 1850행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::InsertNewText(const char *)`, `XMLElement::SetText(bool)`, `XMLElement::SetText(const char *)`, `XMLElement::SetText(double)`, `XMLElement::SetText(float)`
- `XMLDocument::NewDeclaration(const char *)` (헤더 1862행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDeclaration::ShallowClone(XMLDocument *) const`, `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::InsertNewDeclaration(const char *)`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLDocument::NewUnknown(const char *)` (헤더 1868행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::InsertNewUnknown(const char *)`, `XMLNode::DeepClone(XMLDocument *) const`, `XMLUnknown::ShallowClone(XMLDocument *) const`
- `XMLDocument::ErrorID() const` (헤더 1884행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::ErrorName() const` (헤더 1887행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::ErrorStr() const` (헤더 1893행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::PrintError() const`
- `XMLDocument::PrintError() const` (헤더 1896행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::ErrorLineNum() const` (헤더 1899행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::DeepCopy(XMLDocument *) const` (헤더 1914행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLDocument::ShallowClone(XMLDocument *) const` (헤더 1922행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLDocument::ShallowEqual(const XMLNode *) const` (헤더 1925행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetName(const char *, bool)` (헤더 1271행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLDocument::NewElement(const char *)`, `XMLElement::InsertNewChildElement(const char *)`, `XMLElement::ShallowClone(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLElement::ToElement() const` (헤더 1278행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::FirstChildElement(const char *) const`, `XMLConstHandle::LastChildElement(const char *) const`, `XMLConstHandle::NextSiblingElement(const char *) const`, `XMLConstHandle::PreviousSiblingElement(const char *) const`, `XMLConstHandle::ToElement() const`, `XMLDocument::Accept(XMLVisitor *) const`
- `XMLElement::Accept(XMLVisitor *) const` (헤더 1281행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`
- `XMLElement::IntAttribute(const char *, int) const` (헤더 1314행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::UnsignedAttribute(const char *, unsigned int) const` (헤더 1316행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Int64Attribute(const char *, int64_t) const` (헤더 1318행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Unsigned64Attribute(const char *, uint64_t) const` (헤더 1320행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::BoolAttribute(const char *, bool) const` (헤더 1322행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::DoubleAttribute(const char *, double) const` (헤더 1324행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::FloatAttribute(const char *, float) const` (헤더 1326행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryIntAttribute(const char *, int *) const` (헤더 1341행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::IntAttribute(const char *, int) const`, `XMLElement::QueryAttribute(const char *, int *) const`
- `XMLElement::QueryUnsignedAttribute(const char *, unsigned int *) const` (헤더 1350행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::QueryAttribute(const char *, unsigned int *) const`, `XMLElement::UnsignedAttribute(const char *, unsigned int) const`
- `XMLElement::QueryInt64Attribute(const char *, int64_t *) const` (헤더 1359행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::Int64Attribute(const char *, int64_t) const`, `XMLElement::QueryAttribute(const char *, int64_t *) const`
- `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const` (헤더 1368행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::QueryAttribute(const char *, uint64_t *) const`, `XMLElement::Unsigned64Attribute(const char *, uint64_t) const`
- `XMLElement::QueryBoolAttribute(const char *, bool *) const` (헤더 1377행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::BoolAttribute(const char *, bool) const`, `XMLElement::QueryAttribute(const char *, bool *) const`
- `XMLElement::QueryDoubleAttribute(const char *, double *) const` (헤더 1385행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::DoubleAttribute(const char *, double) const`, `XMLElement::QueryAttribute(const char *, double *) const`
- `XMLElement::QueryFloatAttribute(const char *, float *) const` (헤더 1393행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::FloatAttribute(const char *, float) const`, `XMLElement::QueryAttribute(const char *, float *) const`
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
- `XMLElement::SetAttribute(const char *, const char *)` (헤더 1463행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::ShallowClone(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLElement::SetAttribute(const char *, int)` (헤더 1468행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, unsigned int)` (헤더 1473행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, int64_t)` (헤더 1479행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, uint64_t)` (헤더 1485행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, bool)` (헤더 1491행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, double)` (헤더 1496행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetAttribute(const char *, float)` (헤더 1501행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::DeleteAttribute(const char *)` (헤더 1509행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::FirstAttribute() const` (헤더 1512행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLElement::ShallowClone(XMLDocument *) const`, `XMLElement::ShallowEqual(const XMLNode *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLElement::GetText() const` (헤더 1546행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(const char *)` (헤더 1582행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetText(bool)`, `XMLElement::SetText(double)`, `XMLElement::SetText(float)`, `XMLElement::SetText(int)`, `XMLElement::SetText(int64_t)`, `XMLElement::SetText(uint64_t)`
- `XMLElement::SetText(int)` (헤더 1584행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(unsigned int)` (헤더 1586행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(int64_t)` (헤더 1588행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(uint64_t)` (헤더 1590행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(bool)` (헤더 1592행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(double)` (헤더 1594행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::SetText(float)` (헤더 1596행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::QueryIntText(int *) const` (헤더 1624행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::IntText(int) const`
- `XMLElement::QueryUnsignedText(unsigned int *) const` (헤더 1626행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::UnsignedText(unsigned int) const`
- `XMLElement::QueryInt64Text(int64_t *) const` (헤더 1628행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::Int64Text(int64_t) const`
- `XMLElement::QueryUnsigned64Text(uint64_t *) const` (헤더 1630행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::Unsigned64Text(uint64_t) const`
- `XMLElement::QueryBoolText(bool *) const` (헤더 1632행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::BoolText(bool) const`
- `XMLElement::QueryDoubleText(double *) const` (헤더 1634행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::DoubleText(double) const`
- `XMLElement::QueryFloatText(float *) const` (헤더 1636행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::FloatText(float) const`
- `XMLElement::IntText(int) const` (헤더 1638행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::UnsignedText(unsigned int) const` (헤더 1641행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Int64Text(int64_t) const` (헤더 1643행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::Unsigned64Text(uint64_t) const` (헤더 1645행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::BoolText(bool) const` (헤더 1647행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::DoubleText(double) const` (헤더 1649행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::FloatText(float) const` (헤더 1651행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::InsertNewChildElement(const char *)` (헤더 1657행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::InsertNewComment(const char *)` (헤더 1659행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::InsertNewText(const char *)` (헤더 1661행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::InsertNewDeclaration(const char *)` (헤더 1663행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::InsertNewUnknown(const char *)` (헤더 1665행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLElement::ShallowClone(XMLDocument *) const` (헤더 1677행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLElement::ShallowEqual(const XMLNode *) const` (헤더 1678행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::XMLHandle(XMLNode *)` (헤더 2055행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::FirstChild()`, `XMLHandle::FirstChildElement(const char *)`, `XMLHandle::LastChild()`, `XMLHandle::LastChildElement(const char *)`, `XMLHandle::NextSibling()`, `XMLHandle::NextSiblingElement(const char *)`
- `XMLHandle::XMLHandle(XMLNode &)` (헤더 2058행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::XMLHandle(const XMLHandle &)` (헤더 2061행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::operator=(const XMLHandle &)` (헤더 2064행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::FirstChild()` (헤더 2070행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::FirstChildElement(const char *)` (헤더 2074행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::LastChild()` (헤더 2078행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::LastChildElement(const char *)` (헤더 2082행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::PreviousSibling()` (헤더 2086행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::PreviousSiblingElement(const char *)` (헤더 2090행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::NextSibling()` (헤더 2094행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::NextSiblingElement(const char *)` (헤더 2098행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToNode()` (헤더 2103행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToElement()` (헤더 2107행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToText()` (헤더 2111행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToUnknown()` (헤더 2115행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLHandle::ToDeclaration()` (헤더 2119행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::GetDocument() const` (헤더 673행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::GetDocument()` (헤더 678행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetText(bool)`, `XMLElement::SetText(const char *)`, `XMLElement::SetText(double)`, `XMLElement::SetText(float)`, `XMLElement::SetText(int)`, `XMLElement::SetText(int64_t)`
- `XMLNode::ToText()` (헤더 688행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetText(bool)`, `XMLElement::SetText(const char *)`, `XMLElement::SetText(double)`, `XMLElement::SetText(float)`, `XMLElement::SetText(int)`, `XMLElement::SetText(int64_t)`
- `XMLNode::ToComment()` (헤더 692행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::ToUnknown()` (헤더 704행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::ToUnknown()`
- `XMLNode::ToElement() const` (헤더 708행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::FirstChildElement(const char *) const`, `XMLConstHandle::LastChildElement(const char *) const`, `XMLConstHandle::NextSiblingElement(const char *) const`, `XMLConstHandle::PreviousSiblingElement(const char *) const`, `XMLConstHandle::ToElement() const`, `XMLDocument::Accept(XMLVisitor *) const`
- `XMLNode::ToText() const` (헤더 711행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::ToText() const`, `XMLElement::BoolText(bool) const`, `XMLElement::DoubleText(double) const`, `XMLElement::FloatText(float) const`, `XMLElement::GetText() const`, `XMLElement::Int64Text(int64_t) const`
- `XMLNode::ToComment() const` (헤더 714행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLComment::ShallowEqual(const XMLNode *) const`, `XMLElement::GetText() const`
- `XMLNode::ToDeclaration() const` (헤더 720행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::ToDeclaration() const`, `XMLDeclaration::ShallowEqual(const XMLNode *) const`
- `XMLNode::ToUnknown() const` (헤더 723행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::ToUnknown() const`, `XMLUnknown::ShallowEqual(const XMLNode *) const`
- `XMLNode::ChildElementCount(const char *) const` (헤더 729행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::ChildElementCount() const` (헤더 731행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::SetValue(const char *, bool)` (헤더 747행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLComment::ShallowClone(XMLDocument *) const`, `XMLDeclaration::ShallowClone(XMLDocument *) const`, `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLDocument::NewComment(const char *)`, `XMLDocument::NewDeclaration(const char *)`, `XMLDocument::NewElement(const char *)`
- `XMLNode::GetLineNum() const` (헤더 750행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::Parent() const` (헤더 753행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)`
- `XMLNode::Parent()` (헤더 757행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::NoChildren() const` (헤더 762행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::FirstChild() const` (헤더 767행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::FirstChild() const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`
- `XMLNode::FirstChildElement(const char *) const` (헤더 778행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::FirstChildElement(const char *) const`, `XMLDocument::RootElement()`, `XMLDocument::RootElement() const`, `XMLHandle::FirstChildElement(const char *)`, `XMLNode::ChildElementCount() const`, `XMLNode::ChildElementCount(const char *) const`
- `XMLNode::FirstChildElement(const char *)` (헤더 780행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::RootElement()`, `XMLHandle::FirstChildElement(const char *)`
- `XMLNode::LastChild() const` (헤더 785행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::LastChild() const`
- `XMLNode::LastChildElement(const char *) const` (헤더 796행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::LastChildElement(const char *) const`, `XMLHandle::LastChildElement(const char *)`, `XMLNode::LastChildElement(const char *)`
- `XMLNode::LastChildElement(const char *)` (헤더 798행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::LastChildElement(const char *)`
- `XMLNode::PreviousSibling() const` (헤더 803행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::PreviousSibling() const`
- `XMLNode::PreviousSibling()` (헤더 807행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::PreviousSibling()`
- `XMLNode::PreviousSiblingElement(const char *) const` (헤더 812행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::PreviousSiblingElement(const char *) const`, `XMLHandle::PreviousSiblingElement(const char *)`, `XMLNode::PreviousSiblingElement(const char *)`
- `XMLNode::PreviousSiblingElement(const char *)` (헤더 814행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::PreviousSiblingElement(const char *)`
- `XMLNode::NextSibling() const` (헤더 819행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::NextSibling() const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`
- `XMLNode::NextSibling()` (헤더 823행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::NextSibling()`
- `XMLNode::NextSiblingElement(const char *) const` (헤더 828행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::NextSiblingElement(const char *) const`, `XMLHandle::NextSiblingElement(const char *)`, `XMLNode::ChildElementCount() const`, `XMLNode::ChildElementCount(const char *) const`, `XMLNode::NextSiblingElement(const char *)`
- `XMLNode::NextSiblingElement(const char *)` (헤더 830행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::NextSiblingElement(const char *)`
- `XMLNode::LinkEndChild(XMLNode *)` (헤더 843행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::InsertFirstChild(XMLNode *)` (헤더 853행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetText(bool)`, `XMLElement::SetText(const char *)`, `XMLElement::SetText(double)`, `XMLElement::SetText(float)`, `XMLElement::SetText(int)`, `XMLElement::SetText(int64_t)`
- `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)` (헤더 862행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::DeepClone(XMLDocument *) const` (헤더 898행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`
- `XMLNode::SetUserData(void *)` (헤더 937행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLNode::GetUserData() const` (헤더 944행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)` (헤더 2250행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`
- `XMLPrinter::PushHeader(bool, bool)` (헤더 2254행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::VisitEnter(const XMLDocument &)`
- `XMLPrinter::OpenElement(const char *, bool)` (헤더 2258행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)`
- `XMLPrinter::PushAttribute(const char *, const char *)` (헤더 2260행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::PushAttribute(const char *, bool)`
- `XMLPrinter::PushAttribute(const char *, int)` (헤더 2261행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, unsigned int)` (헤더 2262행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, int64_t)` (헤더 2263행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, uint64_t)` (헤더 2264행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, bool)` (헤더 2265행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushAttribute(const char *, double)` (헤더 2266행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::CloseElement(bool)` (헤더 2268행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::VisitExit(const XMLElement &)`
- `XMLPrinter::PushText(const char *, bool)` (헤더 2271행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::PushText(bool)`
- `XMLPrinter::PushText(int)` (헤더 2273행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(unsigned int)` (헤더 2275행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(int64_t)` (헤더 2277행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(uint64_t)` (헤더 2279행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(bool)` (헤더 2281행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(float)` (헤더 2283행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushText(double)` (헤더 2285행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::PushComment(const char *)` (헤더 2288행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLComment::Accept(XMLVisitor *) const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::PushDeclaration(const char *)` (헤더 2290행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDeclaration::Accept(XMLVisitor *) const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::PushUnknown(const char *)` (헤더 2291행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLPrinter::Visit(const XMLUnknown &)`
- `XMLPrinter::VisitEnter(const XMLDocument &)` (헤더 2293행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::VisitExit(const XMLDocument &)` (헤더 2294행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)` (헤더 2298행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::VisitExit(const XMLElement &)` (헤더 2299행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::Visit(const XMLText &)` (헤더 2301행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLText::Accept(XMLVisitor *) const`
- `XMLPrinter::Visit(const XMLComment &)` (헤더 2302행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLComment::Accept(XMLVisitor *) const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::Visit(const XMLDeclaration &)` (헤더 2303행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDeclaration::Accept(XMLVisitor *) const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLPrinter::Visit(const XMLUnknown &)` (헤더 2304행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLUnknown::Accept(XMLVisitor *) const`
- `XMLPrinter::CStr() const` (헤더 2310행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::CStrSize() const` (헤더 2318행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLPrinter::ClearBuffer(bool)` (헤더 2325행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLText::Accept(XMLVisitor *) const` (헤더 993행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLText::ToText()` (헤더 995행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLElement::SetText(bool)`, `XMLElement::SetText(const char *)`, `XMLElement::SetText(double)`, `XMLElement::SetText(float)`, `XMLElement::SetText(int)`, `XMLElement::SetText(int64_t)`
- `XMLText::ToText() const` (헤더 998행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::ToText() const`, `XMLElement::BoolText(bool) const`, `XMLElement::DoubleText(double) const`, `XMLElement::FloatText(float) const`, `XMLElement::GetText() const`, `XMLElement::Int64Text(int64_t) const`
- `XMLText::ShallowClone(XMLDocument *) const` (헤더 1011행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLText::ShallowEqual(const XMLNode *) const` (헤더 1012행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLUnknown::ToUnknown()` (헤더 1107행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLHandle::ToUnknown()`
- `XMLUnknown::ToUnknown() const` (헤더 1110행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLConstHandle::ToUnknown() const`, `XMLUnknown::ShallowEqual(const XMLNode *) const`
- `XMLUnknown::Accept(XMLVisitor *) const` (헤더 1114행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLUnknown::ShallowClone(XMLDocument *) const` (헤더 1116행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::DeepCopy(XMLDocument *) const`, `XMLNode::DeepClone(XMLDocument *) const`
- `XMLUnknown::ShallowEqual(const XMLNode *) const` (헤더 1117행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLUtil::IsPrefixHex(const char *)` (헤더 586행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::BoolValue() const`, `XMLAttribute::Int64Value() const`, `XMLAttribute::IntValue() const`, `XMLAttribute::QueryBoolValue(bool *) const`, `XMLAttribute::QueryInt64Value(int64_t *) const`, `XMLAttribute::QueryIntValue(int *) const`
- `XMLUtil::ToStr(int, char *, int)` (헤더 612행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(int)`, `XMLElement::SetAttribute(const char *, int)`, `XMLElement::SetText(int)`, `XMLPrinter::PushAttribute(const char *, int)`, `XMLPrinter::PushText(int)`
- `XMLUtil::ToStr(unsigned int, char *, int)` (헤더 613행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(unsigned int)`, `XMLElement::SetAttribute(const char *, unsigned int)`, `XMLElement::SetText(unsigned int)`, `XMLPrinter::PushAttribute(const char *, unsigned int)`, `XMLPrinter::PushText(unsigned int)`
- `XMLUtil::ToStr(bool, char *, int)` (헤더 614행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(bool)`, `XMLElement::SetAttribute(const char *, bool)`, `XMLElement::SetText(bool)`, `XMLPrinter::PushAttribute(const char *, bool)`, `XMLPrinter::PushText(bool)`
- `XMLUtil::ToStr(float, char *, int)` (헤더 615행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(float)`, `XMLElement::SetAttribute(const char *, float)`, `XMLElement::SetText(float)`, `XMLPrinter::PushText(float)`
- `XMLUtil::ToStr(double, char *, int)` (헤더 616행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(double)`, `XMLElement::SetAttribute(const char *, double)`, `XMLElement::SetText(double)`, `XMLPrinter::PushAttribute(const char *, double)`, `XMLPrinter::PushText(double)`
- `XMLUtil::ToStr(int64_t, char *, int)` (헤더 617행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(int64_t)`, `XMLElement::SetAttribute(const char *, int64_t)`, `XMLElement::SetText(int64_t)`, `XMLPrinter::PushAttribute(const char *, int64_t)`, `XMLPrinter::PushText(int64_t)`
- `XMLUtil::ToStr(uint64_t, char *, int)` (헤더 618행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::SetAttribute(uint64_t)`, `XMLElement::SetAttribute(const char *, uint64_t)`, `XMLElement::SetText(uint64_t)`, `XMLPrinter::PushAttribute(const char *, uint64_t)`, `XMLPrinter::PushText(uint64_t)`
- `XMLUtil::ToInt(const char *, int *)` (헤더 621행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::BoolValue() const`, `XMLAttribute::IntValue() const`, `XMLAttribute::QueryBoolValue(bool *) const`, `XMLAttribute::QueryIntValue(int *) const`, `XMLElement::BoolAttribute(const char *, bool) const`, `XMLElement::BoolText(bool) const`
- `XMLUtil::ToUnsigned(const char *, unsigned int *)` (헤더 622행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::QueryUnsignedValue(unsigned int *) const`, `XMLAttribute::UnsignedValue() const`, `XMLElement::QueryAttribute(const char *, unsigned int *) const`, `XMLElement::QueryUnsignedAttribute(const char *, unsigned int *) const`, `XMLElement::QueryUnsignedText(unsigned int *) const`, `XMLElement::UnsignedAttribute(const char *, unsigned int) const`
- `XMLUtil::ToBool(const char *, bool *)` (헤더 623행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::BoolValue() const`, `XMLAttribute::QueryBoolValue(bool *) const`, `XMLElement::BoolAttribute(const char *, bool) const`, `XMLElement::BoolText(bool) const`, `XMLElement::QueryAttribute(const char *, bool *) const`, `XMLElement::QueryBoolAttribute(const char *, bool *) const`
- `XMLUtil::ToFloat(const char *, float *)` (헤더 624행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::FloatValue() const`, `XMLAttribute::QueryFloatValue(float *) const`, `XMLElement::FloatAttribute(const char *, float) const`, `XMLElement::FloatText(float) const`, `XMLElement::QueryAttribute(const char *, float *) const`, `XMLElement::QueryFloatAttribute(const char *, float *) const`
- `XMLUtil::ToDouble(const char *, double *)` (헤더 625행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::DoubleValue() const`, `XMLAttribute::QueryDoubleValue(double *) const`, `XMLElement::DoubleAttribute(const char *, double) const`, `XMLElement::DoubleText(double) const`, `XMLElement::QueryAttribute(const char *, double *) const`, `XMLElement::QueryDoubleAttribute(const char *, double *) const`
- `XMLUtil::ToInt64(const char *, int64_t *)` (헤더 626행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::Int64Value() const`, `XMLAttribute::QueryInt64Value(int64_t *) const`, `XMLElement::Int64Attribute(const char *, int64_t) const`, `XMLElement::Int64Text(int64_t) const`, `XMLElement::QueryAttribute(const char *, int64_t *) const`, `XMLElement::QueryInt64Attribute(const char *, int64_t *) const`
- `XMLUtil::ToUnsigned64(const char *, uint64_t *)` (헤더 627행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLAttribute::QueryUnsigned64Value(uint64_t *) const`, `XMLAttribute::Unsigned64Value() const`, `XMLElement::QueryAttribute(const char *, uint64_t *) const`, `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const`, `XMLElement::QueryUnsigned64Text(uint64_t *) const`, `XMLElement::Unsigned64Attribute(const char *, uint64_t) const`
- `XMLUtil::SetBoolSerialization(const char *, const char *)` (헤더 633행) — 라이브러리 안에서 이 함수를 부르는 곳이 없음 → 하네스가 직접 호출해야 함
- `XMLVisitor::VisitEnter(const XMLDocument &)` (헤더 479행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLVisitor::VisitExit(const XMLDocument &)` (헤더 483행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLVisitor::VisitEnter(const XMLElement &, const XMLAttribute *)` (헤더 488행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLVisitor::VisitExit(const XMLElement &)` (헤더 492행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLVisitor::Visit(const XMLDeclaration &)` (헤더 497행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDeclaration::Accept(XMLVisitor *) const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLVisitor::Visit(const XMLText &)` (헤더 501행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLText::Accept(XMLVisitor *) const`
- `XMLVisitor::Visit(const XMLComment &)` (헤더 505행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLComment::Accept(XMLVisitor *) const`, `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`
- `XMLVisitor::Visit(const XMLUnknown &)` (헤더 509행) — 이 함수를 부르는 상위 함수들도 모두 미실행 → 상위 API를 하네스에 추가해야 함  
  경로를 여는 상위 API: `XMLDocument::Accept(XMLVisitor *) const`, `XMLDocument::Print(XMLPrinter *) const`, `XMLDocument::SaveFile(FILE *, bool)`, `XMLDocument::SaveFile(const char *, bool)`, `XMLElement::Accept(XMLVisitor *) const`, `XMLUnknown::Accept(XMLVisitor *) const`

## 호출 경로 있음 · 조건에 막힘

이미 실행된 함수 안에 이 API로 가는 호출이 있지만, 그 줄까지 실행이 도달하지 못했습니다. 아래 조건을 만족시키는 입력·상태가 필요합니다.

## 도달 · 일부 분기 미실행

API는 실행됐지만 안쪽 조건문 일부가 한 방향으로만 갔습니다. '한 번도 참/거짓 아님'인 조건을 만족시키는 입력·상태·옵션을 만들면 열립니다.

### `XMLDocument::Clear()` — 영역 2/3 실행
- third_party/tinyxml2/tinyxml2.cpp:2233 조건 `_unlinked.Size()` 한 번도 **참** 아님 — `while( _unlinked.Size()) {`
  - 원인(라이브러리 내부에서 정해짐): `DynArray::PushArr(size_t)`의 1번째 인자 `count`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (필드 `_size`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다
  - 원인(라이브러리 내부에서 정해짐): `_size`는 `DynArray::Clear()`, `DynArray::DynArray()`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLNode::Value() const` — 영역 3/4 실행
- third_party/tinyxml2/tinyxml2.cpp:856 조건 `this->ToDocument()` 한 번도 **참** 아님 — `if ( this->ToDocument() )`
  - 원인(라이브러리 내부에서 정해짐): 조건이 매개변수·필드가 아니라 지역 변수나 입력 데이터에 달려 있습니다 (입력 내용·딕셔너리로 열어야 함)

### `XMLElement::Attribute(const char *, const char *) const` — 영역 7/9 실행
- third_party/tinyxml2/tinyxml2.cpp:1639 조건 `!value` 한 번도 **거짓** 아님 — `if ( !value || XMLUtil::StringEqual( a->Value(), value )) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLElement::Attribute(const char *, const char *) const`의 2번째 인자 `value`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLElement::ParseAttributes(char *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLElement::Attribute`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLDocument::DeleteNode(XMLNode *)` — 영역 8/10 실행
- third_party/tinyxml2/tinyxml2.cpp:2333 조건 `node == 0` 한 번도 **참** 아님 — `if(node == 0) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLDocument::DeleteNode(XMLNode *)`의 1번째 인자 `node`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLDocument::Clear()`, `XMLNode::ParseDeep(char *, StrPair *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLDocument::DeleteNode`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.cpp:2337 조건 `node->_parent` 한 번도 **참** 아님 — `if (node->_parent) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLDocument::DeleteNode(XMLNode *)`의 1번째 인자 `node`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLDocument::Clear()`, `XMLNode::ParseDeep(char *, StrPair *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLDocument::DeleteNode`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
  - 원인(라이브러리 내부에서 정해짐): `_parent`는 `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`, `XMLNode::InsertEndChild(XMLNode *)`, `XMLNode::InsertFirstChild(XMLNode *)`에서 내부적으로 정해집니다 (입력 내용이나 이전 상태에 따라 달라짐)

### `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)` — 영역 20/25 실행
- third_party/tinyxml2/tinyxml2.cpp:425 조건 `input < 0x200000` 한 번도 **거짓** 아님 — `else if ( input < 0x200000 ) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`의 1번째 인자 `input`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::GetCharacterRef(const char *, char *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ConvertUTF32ToUTF8`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.cpp:457 조건 `default` 한 번도 **참** 아님 — `default:`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`의 3번째 인자 `length`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::GetCharacterRef(const char *, char *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ConvertUTF32ToUTF8`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLNode::InsertEndChild(XMLNode *)` — 영역 18/22 실행
- third_party/tinyxml2/tinyxml2.cpp:934 조건 `addThis->_document != _document` 한 번도 **참** 아님 — `if ( addThis->_document != _document ) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::InsertEndChild(XMLNode *)`의 1번째 인자 `addThis`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLNode::ParseDeep(char *, StrPair *, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLNode::InsertEndChild`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
  - 원인(라이브러리 내부에서 정해짐): `XMLNode::XMLNode(XMLDocument *)`의 1번째 인자 `doc`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLComment::XMLComment(XMLDocument *)`, `XMLDeclaration::XMLDeclaration(XMLDocument *)`, `XMLDocument::XMLDocument(bool, Whitespace)`에서 호출) (필드 `_document`를 거쳐 조건에 쓰임) → 그 상위 API의 입력·상태를 바꿔야 합니다

### `XMLUtil::ReadBOM(const char *, bool *)` — 영역 14/16 실행
- third_party/tinyxml2/tinyxml2.cpp:400 조건 `*(pu+1) == TIXML_UTF_LEAD_1` 한 번도 **참** 아님 — `&& *(pu+1) == TIXML_UTF_LEAD_1`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::ReadBOM(const char *, bool *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLDocument::Parse()`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::ReadBOM`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLUtil::StringEqual(const char *, const char *, int)` — 영역 12/13 실행
- third_party/tinyxml2/tinyxml2.h:592 조건 `p == q` 한 번도 **참** 아님 — `if ( p == q ) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::StringEqual(const char *, const char *, int)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLDocument::Identify(char *, XMLNode **, bool)`, `XMLElement::Attribute(const char *, const char *) const`, `XMLElement::FindAttribute(const char *) const`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::StringEqual`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::StringEqual(const char *, const char *, int)`의 2번째 인자 `q`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLDocument::Identify(char *, XMLNode **, bool)`, `XMLElement::Attribute(const char *, const char *) const`, `XMLElement::FindAttribute(const char *) const`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::StringEqual`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLUtil::GetCharacterRef(const char *, char *, int *)` — 영역 55/57 실행
- third_party/tinyxml2/tinyxml2.cpp:470 조건 `*(p + 1) == '#'` 한 번도 **거짓** 아님 — `if (*(p + 1) == '#' && *(p + 2)) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::GetCharacterRef(const char *, char *, int *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`StrPair::GetStr()`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::GetCharacterRef`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
- third_party/tinyxml2/tinyxml2.cpp:539 조건 `ucs > MAX_CODE_POINT` 한 번도 **참** 아님 — `if (ucs > MAX_CODE_POINT) {`
  - 원인(라이브러리 내부에서 정해짐): 조건이 매개변수·필드가 아니라 지역 변수나 입력 데이터에 달려 있습니다 (입력 내용·딕셔너리로 열어야 함)
- third_party/tinyxml2/tinyxml2.cpp:544 조건 `*length == 0` 한 번도 **참** 아님 — `if (*length == 0) {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::GetCharacterRef(const char *, char *, int *)`의 3번째 인자 `length`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`StrPair::GetStr()`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::GetCharacterRef`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

### `XMLDocument::Parse(const char *, size_t)` — 영역 15/15 실행
- third_party/tinyxml2/tinyxml2.cpp:2459 조건 `!xml` 한 번도 **참** 아님 — `if ( nBytes == 0 || !xml || !*xml ) {`
  - 원인(하네스가 값의 범위를 좁힘): `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(27행, 29행) → nullptr도 넘겨 보세요

### `XMLUtil::SkipWhiteSpace(const char *, int *)` — 영역 13/13 실행
- third_party/tinyxml2/tinyxml2.h:550 조건 `curLineNumPtr` 한 번도 **거짓** 아님 — `if (curLineNumPtr && *p == '\n') {`
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::SkipWhiteSpace(const char *, int *)`의 1번째 인자 `p`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::SkipWhiteSpace(char *const, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::SkipWhiteSpace`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다
  - 원인(라이브러리 내부에서 정해짐): `XMLUtil::SkipWhiteSpace(const char *, int *)`의 2번째 인자 `curLineNumPtr`는 하네스가 아니라 라이브러리 내부 호출로 정해집니다 (`XMLUtil::SkipWhiteSpace(char *const, int *)`에서 호출) → 그 상위 API의 입력·상태를 바꿔야 합니다. `XMLUtil::SkipWhiteSpace`는 공개 API이므로 하네스가 직접 불러 이 인자를 정해 볼 수도 있습니다

## 완전 도달

`XMLAttribute::Name() const`, `XMLAttribute::Value() const`, `XMLDeclaration::ToDeclaration()`, `XMLDocument::XMLDocument(bool, Whitespace)`, `XMLDocument::ToDocument()`, `XMLDocument::ProcessEntities() const`, `XMLDocument::WhitespaceMode() const`, `XMLDocument::ClearError()`, `XMLDocument::Error() const`, `XMLDocument::ErrorIDToName(XMLError)`, `XMLDocument::Identify(char *, XMLNode **, bool)`, `XMLDocument::MarkInUse(const XMLNode *const)`, `XMLElement::Name() const`, `XMLElement::ToElement()`, `XMLElement::FindAttribute(const char *) const`, `XMLElement::ClosingType() const`, `XMLNode::ToElement()`, `XMLNode::ToDocument()`, `XMLNode::ToDeclaration()`, `XMLNode::ToDocument() const`, `XMLNode::FirstChild()`, `XMLNode::LastChild()`, `XMLNode::DeleteChildren()`, `XMLNode::DeleteChild(XMLNode *)`, `XMLText::SetCData(bool)`, `XMLText::CData() const`, `XMLUtil::SkipWhiteSpace(char *const, int *)`, `XMLUtil::IsWhiteSpace(char)`, `XMLUtil::IsNameStartChar(unsigned char)`, `XMLUtil::IsNameChar(unsigned char)`, `XMLUtil::IsUTF8Continuation(const char)`
