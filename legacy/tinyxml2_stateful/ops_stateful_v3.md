# 호출 안 함 API 우선순위와 연산 초안

하네스: `harnesses/stateful_v3.cpp`. 상위 15개를 `harnesses/stateful_auto.cpp`에 넣음.

| 순위 | API | 새로 실행될 수 있는 함수 | 코드 영역 | 생성 |
|---|---|---|---|---|
| 1 | `XMLDocument::LoadFile(const char *)` | 10 | 45 | 파일 입출력 |
| 2 | `XMLDocument::LoadFile(FILE *)` | 6 | 28 | 파일 입출력 |
| 3 | `XMLDocument::SaveFile(const char *, bool)` | 5 | 18 | 파일 입출력 |
| 4 | `XMLElement::Unsigned64Text(uint64_t) const` | 4 | 18 | ✓ |
| 5 | `XMLElement::QueryAttribute(const char *, uint64_t *) const` | 5 | 17 | ✓ |
| 6 | `XMLElement::QueryUnsigned64Text(uint64_t *) const` | 3 | 17 | ✓ |
| 7 | `XMLElement::Unsigned64Attribute(const char *, uint64_t) const` | 5 | 17 | ✓ |
| 8 | `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const` | 4 | 16 | ✓ |
| 9 | `XMLAttribute::Unsigned64Value() const` | 4 | 13 | ✓ |
| 10 | `XMLAttribute::QueryUnsigned64Value(uint64_t *) const` | 3 | 12 | ✓ |
| 11 | `XMLDocument::DeepCopy(XMLDocument *) const` | 1 | 10 | ✓ |
| 12 | `XMLElement::FloatText(float) const` | 2 | 10 | ✓ |
| 13 | `XMLElement::UnsignedText(unsigned int) const` | 2 | 10 | ✓ |
| 14 | `XMLElement::QueryFloatText(float *) const` | 1 | 9 | ✓ |
| 15 | `XMLElement::QueryUnsignedText(unsigned int *) const` | 1 | 9 | ✓ |
| 16 | `XMLUtil::ToUnsigned64(const char *, uint64_t *)` | 2 | 8 | ✓ |
| 17 | `XMLUtil::SetBoolSerialization(const char *, const char *)` | 1 | 7 | ✓ |
| 18 | `XMLElement::InsertNewDeclaration(const char *)` | 1 | 4 | ✓ |
| 19 | `XMLElement::SetAttribute(const char *, float)` | 4 | 4 | ✓ |
| 20 | `XMLAttribute::SetAttribute(float)` | 3 | 3 | ✓ |
| 21 | `XMLElement::SetText(float)` | 3 | 3 | ✓ |
| 22 | `XMLNode::ChildElementCount() const` | 1 | 3 | ✓ |
| 23 | `XMLNode::ChildElementCount(const char *) const` | 1 | 3 | ✓ |
| 24 | `XMLPrinter::PushText(float)` | 3 | 3 | ✓ |
| 25 | `XMLConstHandle::LastChild() const` | 2 | 2 | ✓ |
| 26 | `XMLConstHandle::ToDeclaration() const` | 2 | 2 | ✓ |
| 27 | `XMLConstHandle::ToUnknown() const` | 2 | 2 | ✓ |
| 28 | `XMLElement::QueryAttribute(const char *, const char **) const` | 2 | 2 | ✓ |
| 29 | `XMLElement::SetAttribute(const char *, uint64_t)` | 2 | 2 | ✓ |
| 30 | `XMLPrinter::ClearBuffer(bool)` | 2 | 2 | ✓ |
| 31 | `XMLUtil::ToStr(float, char *, int)` | 2 | 2 | ✓ |
| 32 | `XMLAttribute::FloatValue() const` | 1 | 1 | ✓ |
| 33 | `XMLAttribute::GetLineNum() const` | 1 | 1 | ✓ |
| 34 | `XMLAttribute::SetAttribute(uint64_t)` | 1 | 1 | ✓ |
| 35 | `XMLConstHandle::FirstChild() const` | 1 | 1 | ✓ |
| 36 | `XMLConstHandle::FirstChildElement(const char *) const` | 1 | 1 | ✓ |
| 37 | `XMLConstHandle::NextSibling() const` | 1 | 1 | ✓ |
| 38 | `XMLConstHandle::NextSiblingElement(const char *) const` | 1 | 1 | ✓ |
| 39 | `XMLConstHandle::PreviousSiblingElement(const char *) const` | 1 | 1 | ✓ |
| 40 | `XMLConstHandle::ToElement() const` | 1 | 1 | ✓ |
| 41 | `XMLConstHandle::ToText() const` | 1 | 1 | ✓ |
| 42 | `XMLConstHandle::XMLConstHandle(const XMLConstHandle &)` | 1 | 1 | 인자 타입 `const XMLConstHandle &`를 자동으로 채울 수 없음 |
| 43 | `XMLConstHandle::XMLConstHandle(const XMLNode &)` | 1 | 1 | 인자 타입 `const XMLNode &`를 자동으로 채울 수 없음 |
| 44 | `XMLConstHandle::operator=(const XMLConstHandle &)` | 1 | 1 | 연산자·템플릿 |
| 45 | `XMLDocument::PrintError() const` | 2 | 1 | ✓ |
| 46 | `XMLDocument::RootElement() const` | 1 | 1 | ✓ |
| 47 | `XMLDocument::SaveFile(FILE *, bool)` | 1 | 1 | 파일 입출력 |
| 48 | `XMLDocument::ShallowEqual(const XMLNode *) const` | 1 | 1 | ✓ |
| 49 | `XMLElement::BoolText(bool) const` | 1 | 1 | ✓ |
| 50 | `XMLElement::DoubleAttribute(const char *, double) const` | 1 | 1 | ✓ |
| 51 | `XMLElement::DoubleText(double) const` | 1 | 1 | ✓ |
| 52 | `XMLElement::FloatAttribute(const char *, float) const` | 1 | 1 | ✓ |
| 53 | `XMLElement::Int64Attribute(const char *, int64_t) const` | 1 | 1 | ✓ |
| 54 | `XMLElement::Int64Text(int64_t) const` | 1 | 1 | ✓ |
| 55 | `XMLElement::QueryAttribute(const char *, bool *) const` | 1 | 1 | ✓ |
| 56 | `XMLElement::QueryAttribute(const char *, double *) const` | 1 | 1 | ✓ |
| 57 | `XMLElement::QueryAttribute(const char *, float *) const` | 1 | 1 | ✓ |
| 58 | `XMLElement::QueryAttribute(const char *, int *) const` | 1 | 1 | ✓ |
| 59 | `XMLElement::QueryAttribute(const char *, int64_t *) const` | 1 | 1 | ✓ |
| 60 | `XMLElement::QueryAttribute(const char *, unsigned int *) const` | 1 | 1 | ✓ |
| 61 | `XMLElement::QueryStringAttribute(const char *, const char **) const` | 1 | 1 | ✓ |
| 62 | `XMLElement::SetText(int64_t)` | 1 | 1 | ✓ |
| 63 | `XMLElement::SetText(unsigned int)` | 1 | 1 | ✓ |
| 64 | `XMLElement::UnsignedAttribute(const char *, unsigned int) const` | 1 | 1 | ✓ |
| 65 | `XMLHandle::LastChild()` | 1 | 1 | ✓ |
| 66 | `XMLHandle::LastChildElement(const char *)` | 1 | 1 | ✓ |
| 67 | `XMLHandle::NextSibling()` | 1 | 1 | ✓ |
| 68 | `XMLHandle::PreviousSibling()` | 1 | 1 | ✓ |
| 69 | `XMLHandle::PreviousSiblingElement(const char *)` | 1 | 1 | ✓ |
| 70 | `XMLHandle::ToDeclaration()` | 1 | 1 | ✓ |
| 71 | `XMLHandle::ToNode()` | 1 | 1 | ✓ |
| 72 | `XMLHandle::ToText()` | 1 | 1 | ✓ |
| 73 | `XMLHandle::ToUnknown()` | 1 | 1 | ✓ |
| 74 | `XMLHandle::XMLHandle(XMLNode &)` | 1 | 1 | 인자 타입 `XMLNode &`를 자동으로 채울 수 없음 |
| 75 | `XMLHandle::XMLHandle(const XMLHandle &)` | 1 | 1 | 인자 타입 `const XMLHandle &`를 자동으로 채울 수 없음 |
| 76 | `XMLHandle::operator=(const XMLHandle &)` | 1 | 1 | 연산자·템플릿 |
| 77 | `XMLNode::GetDocument() const` | 1 | 1 | ✓ |
| 78 | `XMLNode::GetUserData() const` | 1 | 1 | ✓ |
| 79 | `XMLNode::LastChild() const` | 1 | 1 | ✓ |
| 80 | `XMLNode::LinkEndChild(XMLNode *)` | 1 | 1 | ✓ |
| 81 | `XMLNode::SetUserData(void *)` | 1 | 1 | 인자 타입 `void *`를 자동으로 채울 수 없음 |
| 82 | `XMLNode::ToDeclaration() const` | 1 | 1 | ✓ |
| 83 | `XMLNode::ToUnknown() const` | 1 | 1 | ✓ |
| 84 | `XMLPrinter::PushAttribute(const char *, bool)` | 1 | 1 | ✓ |
| 85 | `XMLPrinter::PushAttribute(const char *, double)` | 1 | 1 | ✓ |
| 86 | `XMLPrinter::PushAttribute(const char *, int64_t)` | 1 | 1 | ✓ |
| 87 | `XMLPrinter::PushAttribute(const char *, uint64_t)` | 1 | 1 | ✓ |
| 88 | `XMLPrinter::PushAttribute(const char *, unsigned int)` | 1 | 1 | ✓ |
| 89 | `XMLPrinter::PushText(bool)` | 1 | 1 | ✓ |
| 90 | `XMLPrinter::PushText(double)` | 1 | 1 | ✓ |
| 91 | `XMLPrinter::PushText(int)` | 1 | 1 | ✓ |
| 92 | `XMLPrinter::PushText(int64_t)` | 1 | 1 | ✓ |
| 93 | `XMLPrinter::PushText(uint64_t)` | 1 | 1 | ✓ |
| 94 | `XMLPrinter::PushText(unsigned int)` | 1 | 1 | ✓ |
| 95 | `XMLVisitor::Visit(const XMLComment &)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
| 96 | `XMLVisitor::Visit(const XMLDeclaration &)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
| 97 | `XMLVisitor::Visit(const XMLText &)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
| 98 | `XMLVisitor::Visit(const XMLUnknown &)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
| 99 | `XMLVisitor::VisitEnter(const XMLDocument &)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
| 100 | `XMLVisitor::VisitEnter(const XMLElement &, const XMLAttribute *)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
| 101 | `XMLVisitor::VisitExit(const XMLDocument &)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
| 102 | `XMLVisitor::VisitExit(const XMLElement &)` | 1 | 1 | 방문자 콜백 (방문자 클래스를 직접 만들어야 함) |
