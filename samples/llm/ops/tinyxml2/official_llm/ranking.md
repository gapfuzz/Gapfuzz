# 호출 안 함 API 우선순위 — tinyxml2/official_llm

'호출 안 함' API 251개. 추가 가능 246개, 제외 5개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)` | 21 | 117 | 117 | 이번에 추가 |
| 2 | `XMLElement::BoolText(bool) const` | 8 | 49 | 49 | 이번에 추가 |
| 3 | `XMLDocument::Print(XMLPrinter *) const` | 12 | 60 | 45 | 이번에 추가 |
| 4 | `XMLElement::SetText(bool)` | 8 | 40 | 40 | 이번에 추가 |
| 5 | `XMLElement::ShallowClone(XMLDocument *) const` | 6 | 30 | 29 | 이번에 추가 |
| 6 | `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)` | 1 | 25 | 25 | 이번에 추가 |
| 7 | `XMLElement::ShallowEqual(const XMLNode *) const` | 2 | 23 | 22 | 이번에 추가 |
| 8 | `XMLElement::Int64Text(int64_t) const` | 7 | 30 | 21 | 이번에 추가 |
| 9 | `XMLDocument::DeepCopy(XMLDocument *) const` | 5 | 22 | 20 | 이번에 추가 |
| 10 | `XMLPrinter::VisitExit(const XMLElement &)` | 14 | 51 | 19 | 이번에 추가 |
| 11 | `XMLElement::UnsignedText(unsigned int) const` | 7 | 27 | 18 |  |
| 12 | `XMLElement::Unsigned64Text(uint64_t) const` | 7 | 27 | 18 |  |
| 13 | `XMLElement::FloatText(float) const` | 6 | 17 | 15 |  |
| 14 | `XMLElement::DoubleText(double) const` | 6 | 17 | 15 |  |
| 15 | `XMLElement::Accept(XMLVisitor *) const` | 6 | 15 | 13 |  |
| 16 | `XMLElement::GetText() const` | 5 | 15 | 12 |  |
| 17 | `XMLPrinter::VisitEnter(const XMLDocument &)` | 16 | 54 | 10 |  |
| 18 | `XMLElement::IntText(int) const` | 7 | 30 | 10 |  |
| 19 | `XMLNode::ChildElementCount(const char *) const` | 2 | 10 | 10 |  |
| 20 | `XMLHandle::PreviousSiblingElement(const char *)` | 4 | 10 | 10 |  |
| 21 | `XMLElement::DeleteAttribute(const char *)` | 1 | 10 | 10 |  |
| 22 | `XMLElement::QueryAttribute(const char *, bool *) const` | 7 | 46 | 9 |  |
| 23 | `XMLElement::QueryAttribute(const char *, int64_t *) const` | 6 | 27 | 9 |  |
| 24 | `XMLElement::QueryAttribute(const char *, int *) const` | 6 | 27 | 9 |  |
| 25 | `XMLElement::UnsignedAttribute(const char *, unsigned int) const` | 6 | 24 | 9 |  |
| 26 | `XMLElement::Unsigned64Attribute(const char *, uint64_t) const` | 6 | 24 | 9 |  |
| 27 | `XMLElement::QueryAttribute(const char *, float *) const` | 5 | 14 | 9 |  |
| 28 | `XMLElement::QueryAttribute(const char *, double *) const` | 5 | 14 | 9 |  |
| 29 | `XMLHandle::LastChildElement(const char *)` | 4 | 10 | 9 |  |
| 30 | `XMLElement::InsertNewDeclaration(const char *)` | 2 | 8 | 8 |  |
| 31 | `XMLPrinter::PushText(unsigned int)` | 15 | 77 | 7 |  |
| 32 | `XMLUtil::SetBoolSerialization(const char *, const char *)` | 1 | 7 | 7 |  |
| 33 | `XMLUnknown::ShallowEqual(const XMLNode *) const` | 2 | 7 | 7 |  |
| 34 | `XMLDeclaration::ShallowEqual(const XMLNode *) const` | 2 | 7 | 7 |  |
| 35 | `XMLText::ShallowEqual(const XMLNode *) const` | 2 | 7 | 6 |  |
| 36 | `XMLComment::ShallowEqual(const XMLNode *) const` | 2 | 7 | 6 |  |
| 37 | `XMLUnknown::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 38 | `XMLText::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 39 | `XMLElement::InsertNewUnknown(const char *)` | 2 | 5 | 5 |  |
| 40 | `XMLElement::InsertNewComment(const char *)` | 2 | 5 | 5 |  |
| 41 | `XMLDocument::PrintError() const` | 3 | 5 | 5 |  |
| 42 | `XMLDeclaration::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 43 | `XMLComment::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 44 | `XMLElement::SetAttribute(const char *, uint64_t)` | 6 | 25 | 4 |  |
| 45 | `XMLElement::SetAttribute(const char *, int64_t)` | 6 | 25 | 4 |  |
| 46 | `XMLElement::SetAttribute(const char *, int)` | 6 | 25 | 4 |  |
| 47 | `XMLElement::SetAttribute(const char *, float)` | 6 | 25 | 4 |  |
| 48 | `XMLElement::SetAttribute(const char *, double)` | 6 | 25 | 4 |  |
| 49 | `XMLElement::InsertNewText(const char *)` | 2 | 5 | 4 |  |
| 50 | `XMLElement::InsertNewChildElement(const char *)` | 1 | 4 | 4 |  |
| 51 | `XMLNode::ChildElementCount() const` | 2 | 10 | 3 |  |
| 52 | `XMLDeclaration::ShallowClone(XMLDocument *) const` | 2 | 7 | 3 |  |
| 53 | `XMLUnknown::ShallowClone(XMLDocument *) const` | 2 | 4 | 3 |  |
| 54 | `XMLText::ShallowClone(XMLDocument *) const` | 2 | 4 | 3 |  |
| 55 | `XMLComment::ShallowClone(XMLDocument *) const` | 2 | 4 | 3 |  |
| 56 | `XMLConstHandle::PreviousSibling() const` | 3 | 3 | 3 |  |
| 57 | `XMLPrinter::Visit(const XMLUnknown &)` | 14 | 46 | 2 |  |
| 58 | `XMLPrinter::Visit(const XMLComment &)` | 14 | 46 | 2 |  |
| 59 | `XMLElement::SetAttribute(const char *, bool)` | 6 | 28 | 2 |  |
| 60 | `XMLElement::SetAttribute(const char *, unsigned int)` | 6 | 25 | 2 |  |
| 61 | `XMLPrinter::ClearBuffer(bool)` | 5 | 20 | 2 |  |
| 62 | `XMLHandle::NextSiblingElement(const char *)` | 4 | 10 | 2 |  |
| 63 | `XMLHandle::PreviousSibling()` | 3 | 3 | 2 |  |
| 64 | `XMLHandle::NextSibling()` | 3 | 3 | 2 |  |
| 65 | `XMLConstHandle::LastChild() const` | 3 | 3 | 2 |  |
| 66 | `XMLPrinter::CStrSize() const` | 2 | 2 | 2 |  |
| 67 | `XMLPrinter::CStr() const` | 2 | 2 | 2 |  |
| 68 | `XMLHandle::ToUnknown()` | 2 | 2 | 2 |  |
| 69 | `XMLElement::QueryAttribute(const char *, const char **) const` | 2 | 2 | 2 |  |
| 70 | `XMLPrinter::PushText(bool)` | 15 | 80 | 1 |  |
| 71 | `XMLPrinter::PushText(uint64_t)` | 15 | 77 | 1 |  |
| 72 | `XMLPrinter::PushText(int64_t)` | 15 | 77 | 1 |  |
| 73 | `XMLPrinter::PushText(int)` | 15 | 77 | 1 |  |
| 74 | `XMLPrinter::PushText(float)` | 15 | 77 | 1 |  |
| 75 | `XMLPrinter::PushText(double)` | 15 | 77 | 1 |  |
| 76 | `XMLPrinter::PushAttribute(const char *, bool)` | 14 | 76 | 1 |  |
| 77 | `XMLPrinter::Visit(const XMLText &)` | 13 | 75 | 1 |  |
| 78 | `XMLPrinter::PushAttribute(const char *, unsigned int)` | 14 | 73 | 1 |  |
| 79 | `XMLPrinter::PushAttribute(const char *, uint64_t)` | 14 | 73 | 1 |  |
| 80 | `XMLPrinter::PushAttribute(const char *, int64_t)` | 14 | 73 | 1 |  |
| 81 | `XMLPrinter::PushAttribute(const char *, int)` | 14 | 73 | 1 |  |
| 82 | `XMLPrinter::PushAttribute(const char *, double)` | 14 | 73 | 1 |  |
| 83 | `XMLPrinter::Visit(const XMLDeclaration &)` | 14 | 46 | 1 |  |
| 84 | `XMLElement::BoolAttribute(const char *, bool) const` | 7 | 46 | 1 |  |
| 85 | `XMLAttribute::BoolValue() const` | 6 | 42 | 1 |  |
| 86 | `XMLElement::SetText(unsigned int)` | 8 | 37 | 1 |  |
| 87 | `XMLElement::SetText(uint64_t)` | 8 | 37 | 1 |  |
| 88 | `XMLElement::SetText(int64_t)` | 8 | 37 | 1 |  |
| 89 | `XMLElement::SetText(int)` | 8 | 37 | 1 |  |
| 90 | `XMLElement::SetText(float)` | 8 | 37 | 1 |  |
| 91 | `XMLElement::SetText(double)` | 8 | 37 | 1 |  |
| 92 | `XMLElement::IntAttribute(const char *, int) const` | 6 | 27 | 1 |  |
| 93 | `XMLElement::Int64Attribute(const char *, int64_t) const` | 6 | 27 | 1 |  |
| 94 | `XMLElement::QueryAttribute(const char *, unsigned int *) const` | 6 | 24 | 1 |  |
| 95 | `XMLElement::QueryAttribute(const char *, uint64_t *) const` | 6 | 24 | 1 |  |
| 96 | `XMLAttribute::IntValue() const` | 5 | 23 | 1 |  |
| 97 | `XMLAttribute::Int64Value() const` | 5 | 23 | 1 |  |
| 98 | `XMLAttribute::UnsignedValue() const` | 5 | 20 | 1 |  |
| 99 | `XMLAttribute::Unsigned64Value() const` | 5 | 20 | 1 |  |
| 100 | `XMLElement::FloatAttribute(const char *, float) const` | 5 | 14 | 1 |  |
| 101 | `XMLElement::DoubleAttribute(const char *, double) const` | 5 | 14 | 1 |  |
| 102 | `XMLAttribute::FloatValue() const` | 4 | 10 | 1 |  |
| 103 | `XMLAttribute::DoubleValue() const` | 4 | 10 | 1 |  |
| 104 | `XMLConstHandle::PreviousSiblingElement(const char *) const` | 3 | 9 | 1 |  |
| 105 | `XMLConstHandle::NextSiblingElement(const char *) const` | 3 | 9 | 1 |  |
| 106 | `XMLConstHandle::LastChildElement(const char *) const` | 3 | 9 | 1 |  |
| 107 | `XMLConstHandle::NextSibling() const` | 3 | 3 | 1 |  |
| 108 | `XMLConstHandle::FirstChild() const` | 3 | 3 | 1 |  |
| 109 | `XMLHandle::ToText()` | 2 | 2 | 1 |  |
| 110 | `XMLHandle::LastChild()` | 2 | 2 | 1 |  |
| 111 | `XMLHandle::FirstChildElement(const char *)` | 2 | 2 | 1 |  |
| 112 | `XMLHandle::FirstChild()` | 2 | 2 | 1 |  |
| 113 | `XMLConstHandle::ToUnknown() const` | 2 | 2 | 1 |  |
| 114 | `XMLConstHandle::ToText() const` | 2 | 2 | 1 |  |
| 115 | `XMLConstHandle::ToDeclaration() const` | 2 | 2 | 1 |  |
| 116 | `XMLConstHandle::FirstChildElement(const char *) const` | 2 | 2 | 1 |  |
| 117 | `XMLUnknown::ToUnknown() const` | 1 | 1 | 1 |  |
| 118 | `XMLUnknown::ToUnknown()` | 1 | 1 | 1 |  |
| 119 | `XMLText::ToText() const` | 1 | 1 | 1 |  |
| 120 | `XMLText::ToText()` | 1 | 1 | 1 |  |
| 121 | `XMLPrinter::VisitExit(const XMLDocument &)` | 1 | 1 | 1 |  |
| 122 | `XMLNode::ToComment()` | 1 | 1 | 1 |  |
| 123 | `XMLNode::SetUserData(void *)` | 1 | 1 | 1 |  |
| 124 | `XMLNode::Parent()` | 1 | 1 | 1 |  |
| 125 | `XMLNode::NoChildren() const` | 1 | 1 | 1 |  |
| 126 | `XMLNode::LinkEndChild(XMLNode *)` | 1 | 1 | 1 |  |
| 127 | `XMLNode::GetUserData() const` | 1 | 1 | 1 |  |
| 128 | `XMLNode::GetLineNum() const` | 1 | 1 | 1 |  |
| 129 | `XMLNode::GetDocument() const` | 1 | 1 | 1 |  |
| 130 | `XMLHandle::operator=(const XMLHandle &)` | 1 | 1 | 1 |  |
| 131 | `XMLHandle::XMLHandle(const XMLHandle &)` | 1 | 1 | 1 |  |
| 132 | `XMLHandle::XMLHandle(XMLNode &)` | 1 | 1 | 1 |  |
| 133 | `XMLHandle::ToNode()` | 1 | 1 | 1 |  |
| 134 | `XMLHandle::ToElement()` | 1 | 1 | 1 |  |
| 135 | `XMLHandle::ToDeclaration()` | 1 | 1 | 1 |  |
| 136 | `XMLDocument::ShallowEqual(const XMLNode *) const` | 1 | 1 | 1 |  |
| 137 | `XMLDocument::ShallowClone(XMLDocument *) const` | 1 | 1 | 1 |  |
| 138 | `XMLDocument::SetBOM(bool)` | 1 | 1 | 1 |  |
| 139 | `XMLDocument::RootElement() const` | 1 | 1 | 1 |  |
| 140 | `XMLDocument::ErrorName() const` | 1 | 1 | 1 |  |
| 141 | `XMLDocument::ErrorLineNum() const` | 1 | 1 | 1 |  |
| 142 | `XMLDocument::ErrorID() const` | 1 | 1 | 1 |  |
| 143 | `XMLDeclaration::ToDeclaration() const` | 1 | 1 | 1 |  |
| 144 | `XMLConstHandle::operator=(const XMLConstHandle &)` | 1 | 1 | 1 |  |
| 145 | `XMLConstHandle::XMLConstHandle(const XMLNode &)` | 1 | 1 | 1 |  |
| 146 | `XMLConstHandle::XMLConstHandle(const XMLConstHandle &)` | 1 | 1 | 1 |  |
| 147 | `XMLConstHandle::ToNode() const` | 1 | 1 | 1 |  |
| 148 | `XMLConstHandle::ToElement() const` | 1 | 1 | 1 |  |
| 149 | `XMLComment::ToComment() const` | 1 | 1 | 1 |  |
| 150 | `XMLComment::ToComment()` | 1 | 1 | 1 |  |
| 151 | `XMLAttribute::GetLineNum() const` | 1 | 1 | 1 |  |
| 152 | `XMLPrinter::PushText(const char *, bool)` | 12 | 74 | 0 |  |
| 153 | `XMLPrinter::PushAttribute(const char *, const char *)` | 11 | 70 | 0 |  |
| 154 | `XMLPrinter::OpenElement(const char *, bool)` | 15 | 63 | 0 |  |
| 155 | `XMLPrinter::PushHeader(bool, bool)` | 14 | 50 | 0 |  |
| 156 | `XMLPrinter::CloseElement(bool)` | 12 | 49 | 0 |  |
| 157 | `XMLElement::QueryBoolText(bool *) const` | 7 | 48 | 0 |  |
| 158 | `XMLPrinter::PushUnknown(const char *)` | 13 | 45 | 0 |  |
| 159 | `XMLPrinter::PushDeclaration(const char *)` | 13 | 45 | 0 |  |
| 160 | `XMLPrinter::PushComment(const char *)` | 13 | 45 | 0 |  |
| 161 | `XMLElement::QueryBoolAttribute(const char *, bool *) const` | 6 | 45 | 0 |  |
| 162 | `XMLAttribute::QueryBoolValue(bool *) const` | 5 | 41 | 0 |  |
| 163 | `XMLUtil::ToBool(const char *, bool *)` | 4 | 37 | 0 |  |
| 164 | `XMLElement::SetText(const char *)` | 5 | 34 | 0 |  |
| 165 | `XMLElement::QueryIntText(int *) const` | 6 | 29 | 0 |  |
| 166 | `XMLElement::QueryInt64Text(int64_t *) const` | 6 | 29 | 0 |  |
| 167 | `XMLElement::QueryUnsignedText(unsigned int *) const` | 6 | 26 | 0 |  |
| 168 | `XMLElement::QueryUnsigned64Text(uint64_t *) const` | 6 | 26 | 0 |  |
| 169 | `XMLElement::QueryIntAttribute(const char *, int *) const` | 5 | 26 | 0 |  |
| 170 | `XMLElement::QueryInt64Attribute(const char *, int64_t *) const` | 5 | 26 | 0 |  |
| 171 | `XMLElement::SetAttribute(const char *, const char *)` | 4 | 23 | 0 |  |
| 172 | `XMLElement::QueryUnsignedAttribute(const char *, unsigned int *) const` | 5 | 23 | 0 |  |
| 173 | `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const` | 5 | 23 | 0 |  |
| 174 | `XMLNode::InsertFirstChild(XMLNode *)` | 1 | 22 | 0 |  |
| 175 | `XMLAttribute::QueryIntValue(int *) const` | 4 | 22 | 0 |  |
| 176 | `XMLAttribute::QueryInt64Value(int64_t *) const` | 4 | 22 | 0 |  |
| 177 | `XMLAttribute::QueryUnsignedValue(unsigned int *) const` | 4 | 19 | 0 |  |
| 178 | `XMLAttribute::QueryUnsigned64Value(uint64_t *) const` | 4 | 19 | 0 |  |
| 179 | `XMLUtil::ToInt64(const char *, int64_t *)` | 3 | 18 | 0 |  |
| 180 | `XMLUtil::ToInt(const char *, int *)` | 3 | 18 | 0 |  |
| 181 | `XMLElement::QueryFloatText(float *) const` | 5 | 16 | 0 |  |
| 182 | `XMLElement::QueryDoubleText(double *) const` | 5 | 16 | 0 |  |
| 183 | `XMLUtil::ToUnsigned64(const char *, uint64_t *)` | 3 | 15 | 0 |  |
| 184 | `XMLUtil::ToUnsigned(const char *, unsigned int *)` | 3 | 15 | 0 |  |
| 185 | `XMLDocument::Accept(XMLVisitor *) const` | 6 | 15 | 0 |  |
| 186 | `XMLElement::QueryFloatAttribute(const char *, float *) const` | 4 | 13 | 0 |  |
| 187 | `XMLElement::QueryDoubleAttribute(const char *, double *) const` | 4 | 13 | 0 |  |
| 188 | `XMLNode::DeepClone(XMLDocument *) const` | 4 | 12 | 0 |  |
| 189 | `XMLAttribute::QueryFloatValue(float *) const` | 3 | 9 | 0 |  |
| 190 | `XMLAttribute::QueryDoubleValue(double *) const` | 3 | 9 | 0 |  |
| 191 | `XMLNode::PreviousSiblingElement(const char *)` | 2 | 8 | 0 |  |
| 192 | `XMLNode::NextSiblingElement(const char *)` | 2 | 8 | 0 |  |
| 193 | `XMLNode::LastChildElement(const char *)` | 2 | 8 | 0 |  |
| 194 | `XMLUtil::IsPrefixHex(const char *)` | 1 | 7 | 0 |  |
| 195 | `XMLNode::PreviousSiblingElement(const char *) const` | 1 | 7 | 0 |  |
| 196 | `XMLNode::NextSiblingElement(const char *) const` | 1 | 7 | 0 |  |
| 197 | `XMLNode::LastChildElement(const char *) const` | 1 | 7 | 0 |  |
| 198 | `XMLAttribute::SetAttribute(bool)` | 3 | 6 | 0 |  |
| 199 | `XMLUtil::ToStr(bool, char *, int)` | 2 | 5 | 0 |  |
| 200 | `XMLUtil::ToFloat(const char *, float *)` | 2 | 5 | 0 |  |
| 201 | `XMLUtil::ToDouble(const char *, double *)` | 2 | 5 | 0 |  |
| 202 | `XMLNode::GetDocument()` | 1 | 4 | 0 |  |
| 203 | `XMLDocument::NewDeclaration(const char *)` | 1 | 4 | 0 |  |
| 204 | `XMLDocument::ErrorStr() const` | 1 | 4 | 0 |  |
| 205 | `XMLAttribute::SetAttribute(unsigned int)` | 3 | 3 | 0 |  |
| 206 | `XMLAttribute::SetAttribute(uint64_t)` | 3 | 3 | 0 |  |
| 207 | `XMLAttribute::SetAttribute(int64_t)` | 3 | 3 | 0 |  |
| 208 | `XMLAttribute::SetAttribute(int)` | 3 | 3 | 0 |  |
| 209 | `XMLAttribute::SetAttribute(float)` | 3 | 3 | 0 |  |
| 210 | `XMLAttribute::SetAttribute(double)` | 3 | 3 | 0 |  |
| 211 | `XMLUtil::ToStr(unsigned int, char *, int)` | 2 | 2 | 0 |  |
| 212 | `XMLUtil::ToStr(uint64_t, char *, int)` | 2 | 2 | 0 |  |
| 213 | `XMLUtil::ToStr(int64_t, char *, int)` | 2 | 2 | 0 |  |
| 214 | `XMLUtil::ToStr(int, char *, int)` | 2 | 2 | 0 |  |
| 215 | `XMLUtil::ToStr(float, char *, int)` | 2 | 2 | 0 |  |
| 216 | `XMLUtil::ToStr(double, char *, int)` | 2 | 2 | 0 |  |
| 217 | `XMLVisitor::VisitExit(const XMLElement &)` | 1 | 1 | 0 |  |
| 218 | `XMLVisitor::VisitExit(const XMLDocument &)` | 1 | 1 | 0 |  |
| 219 | `XMLVisitor::VisitEnter(const XMLElement &, const XMLAttribute *)` | 1 | 1 | 0 |  |
| 220 | `XMLVisitor::VisitEnter(const XMLDocument &)` | 1 | 1 | 0 |  |
| 221 | `XMLVisitor::Visit(const XMLUnknown &)` | 1 | 1 | 0 |  |
| 222 | `XMLVisitor::Visit(const XMLText &)` | 1 | 1 | 0 |  |
| 223 | `XMLVisitor::Visit(const XMLDeclaration &)` | 1 | 1 | 0 |  |
| 224 | `XMLVisitor::Visit(const XMLComment &)` | 1 | 1 | 0 |  |
| 225 | `XMLNode::ToUnknown() const` | 1 | 1 | 0 |  |
| 226 | `XMLNode::ToUnknown()` | 1 | 1 | 0 |  |
| 227 | `XMLNode::ToText() const` | 1 | 1 | 0 |  |
| 228 | `XMLNode::ToText()` | 1 | 1 | 0 |  |
| 229 | `XMLNode::ToDeclaration() const` | 1 | 1 | 0 |  |
| 230 | `XMLNode::ToComment() const` | 1 | 1 | 0 |  |
| 231 | `XMLNode::PreviousSibling() const` | 1 | 1 | 0 |  |
| 232 | `XMLNode::PreviousSibling()` | 1 | 1 | 0 |  |
| 233 | `XMLNode::Parent() const` | 1 | 1 | 0 |  |
| 234 | `XMLNode::NextSibling() const` | 1 | 1 | 0 |  |
| 235 | `XMLNode::NextSibling()` | 1 | 1 | 0 |  |
| 236 | `XMLNode::LastChild() const` | 1 | 1 | 0 |  |
| 237 | `XMLNode::FirstChild() const` | 1 | 1 | 0 |  |
| 238 | `XMLHandle::XMLHandle(XMLNode *)` | 1 | 1 | 0 |  |
| 239 | `XMLElement::QueryStringAttribute(const char *, const char **) const` | 1 | 1 | 0 |  |
| 240 | `XMLDocument::NewUnknown(const char *)` | 1 | 1 | 0 |  |
| 241 | `XMLDocument::NewText(const char *)` | 1 | 1 | 0 |  |
| 242 | `XMLDocument::NewComment(const char *)` | 1 | 1 | 0 |  |
| 243 | `XMLDocument::HasBOM() const` | 1 | 1 | 0 |  |
| 244 | `XMLConstHandle::XMLConstHandle(const XMLNode *)` | 1 | 1 | 0 |  |
| 245 | `XMLAttribute::SetAttribute(const char *)` | 1 | 1 | 0 |  |
| 246 | `XMLAttribute::Next() const` | 1 | 1 | 0 |  |
| 247 | `XMLDocument::SaveFile(const char *, bool)` | 17 | 78 | 0 | 파일 입출력 |
| 248 | `XMLDocument::SaveFile(FILE *, bool)` | 13 | 61 | 0 | 파일 입출력 |
| 249 | `XMLDocument::LoadFile(const char *)` | 10 | 45 | 0 | 파일 입출력 |
| 250 | `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)` | 5 | 41 | 0 | 파일 입출력 |
| 251 | `XMLDocument::LoadFile(FILE *)` | 6 | 28 | 0 | 파일 입출력 |
