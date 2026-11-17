# 호출 안 함 API 우선순위 — tinyxml2/_union

'호출 안 함' API 259개. 추가 가능 256개, 제외 3개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)` | 22 | 118 | 118 | 이번에 추가 |
| 2 | `XMLElement::BoolText(bool) const` | 8 | 49 | 49 | 이번에 추가 |
| 3 | `XMLDocument::Print(XMLPrinter *) const` | 12 | 60 | 45 | 이번에 추가 |
| 4 | `XMLElement::SetText(bool)` | 10 | 45 | 45 | 이번에 추가 |
| 5 | `XMLElement::ShallowClone(XMLDocument *) const` | 11 | 38 | 32 | 이번에 추가 |
| 6 | `XMLNode::ChildElementCount(const char *) const` | 5 | 28 | 27 | 이번에 추가 |
| 7 | `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)` | 1 | 25 | 25 | 이번에 추가 |
| 8 | `XMLElement::ShallowEqual(const XMLNode *) const` | 4 | 25 | 22 | 이번에 추가 |
| 9 | `XMLElement::Int64Text(int64_t) const` | 7 | 30 | 21 | 이번에 추가 |
| 10 | `XMLDocument::DeepCopy(XMLDocument *) const` | 5 | 22 | 20 | 이번에 추가 |
| 11 | `XMLPrinter::VisitExit(const XMLElement &)` | 14 | 51 | 19 |  |
| 12 | `XMLElement::UnsignedText(unsigned int) const` | 7 | 27 | 18 |  |
| 13 | `XMLElement::Unsigned64Text(uint64_t) const` | 7 | 27 | 18 |  |
| 14 | `XMLElement::FloatText(float) const` | 6 | 17 | 15 |  |
| 15 | `XMLElement::DoubleText(double) const` | 6 | 17 | 15 |  |
| 16 | `XMLElement::Accept(XMLVisitor *) const` | 6 | 15 | 13 |  |
| 17 | `XMLElement::GetText() const` | 5 | 15 | 12 |  |
| 18 | `XMLPrinter::VisitEnter(const XMLDocument &)` | 16 | 54 | 10 |  |
| 19 | `XMLElement::IntText(int) const` | 7 | 30 | 10 |  |
| 20 | `XMLHandle::PreviousSiblingElement(const char *)` | 6 | 21 | 10 |  |
| 21 | `XMLElement::DeleteAttribute(const char *)` | 1 | 10 | 10 |  |
| 22 | `XMLElement::QueryAttribute(const char *, bool *) const` | 7 | 46 | 9 |  |
| 23 | `XMLElement::QueryAttribute(const char *, int64_t *) const` | 6 | 27 | 9 |  |
| 24 | `XMLElement::QueryAttribute(const char *, int *) const` | 6 | 27 | 9 |  |
| 25 | `XMLElement::UnsignedAttribute(const char *, unsigned int) const` | 6 | 24 | 9 |  |
| 26 | `XMLElement::Unsigned64Attribute(const char *, uint64_t) const` | 6 | 24 | 9 |  |
| 27 | `XMLHandle::LastChildElement(const char *)` | 6 | 21 | 9 |  |
| 28 | `XMLElement::QueryAttribute(const char *, float *) const` | 5 | 14 | 9 |  |
| 29 | `XMLElement::QueryAttribute(const char *, double *) const` | 5 | 14 | 9 |  |
| 30 | `XMLElement::InsertNewDeclaration(const char *)` | 4 | 13 | 8 |  |
| 31 | `XMLPrinter::PushText(unsigned int)` | 15 | 77 | 7 |  |
| 32 | `XMLUtil::SetBoolSerialization(const char *, const char *)` | 1 | 7 | 7 |  |
| 33 | `XMLUnknown::ShallowEqual(const XMLNode *) const` | 2 | 7 | 7 |  |
| 34 | `XMLDeclaration::ShallowEqual(const XMLNode *) const` | 2 | 7 | 7 |  |
| 35 | `XMLText::ShallowEqual(const XMLNode *) const` | 2 | 7 | 6 |  |
| 36 | `XMLComment::ShallowEqual(const XMLNode *) const` | 2 | 7 | 6 |  |
| 37 | `XMLElement::InsertNewUnknown(const char *)` | 4 | 10 | 5 |  |
| 38 | `XMLElement::InsertNewComment(const char *)` | 4 | 10 | 5 |  |
| 39 | `XMLUnknown::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 40 | `XMLText::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 41 | `XMLDocument::PrintError() const` | 3 | 5 | 5 |  |
| 42 | `XMLDeclaration::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 43 | `XMLComment::Accept(XMLVisitor *) const` | 2 | 5 | 5 |  |
| 44 | `XMLElement::SetAttribute(const char *, uint64_t)` | 6 | 25 | 4 |  |
| 45 | `XMLElement::SetAttribute(const char *, int64_t)` | 6 | 25 | 4 |  |
| 46 | `XMLElement::SetAttribute(const char *, int)` | 6 | 25 | 4 |  |
| 47 | `XMLElement::SetAttribute(const char *, float)` | 6 | 25 | 4 |  |
| 48 | `XMLElement::SetAttribute(const char *, double)` | 6 | 25 | 4 |  |
| 49 | `XMLElement::InsertNewChildElement(const char *)` | 5 | 11 | 4 |  |
| 50 | `XMLElement::InsertNewText(const char *)` | 4 | 10 | 4 |  |
| 51 | `XMLDocument::ToDocument() const` | 1 | 4 | 4 |  |
| 52 | `XMLNode::ChildElementCount() const` | 5 | 28 | 3 |  |
| 53 | `XMLDeclaration::ShallowClone(XMLDocument *) const` | 4 | 12 | 3 |  |
| 54 | `XMLUnknown::ShallowClone(XMLDocument *) const` | 4 | 9 | 3 |  |
| 55 | `XMLText::ShallowClone(XMLDocument *) const` | 4 | 9 | 3 |  |
| 56 | `XMLComment::ShallowClone(XMLDocument *) const` | 4 | 9 | 3 |  |
| 57 | `XMLConstHandle::PreviousSibling() const` | 3 | 3 | 3 |  |
| 58 | `XMLPrinter::Visit(const XMLUnknown &)` | 14 | 46 | 2 |  |
| 59 | `XMLPrinter::Visit(const XMLComment &)` | 14 | 46 | 2 |  |
| 60 | `XMLElement::SetAttribute(const char *, bool)` | 6 | 28 | 2 |  |
| 61 | `XMLElement::SetAttribute(const char *, unsigned int)` | 6 | 25 | 2 |  |
| 62 | `XMLHandle::NextSiblingElement(const char *)` | 6 | 21 | 2 |  |
| 63 | `XMLHandle::FirstChildElement(const char *)` | 6 | 21 | 2 |  |
| 64 | `XMLPrinter::ClearBuffer(bool)` | 5 | 20 | 2 |  |
| 65 | `XMLHandle::PreviousSibling()` | 3 | 3 | 2 |  |
| 66 | `XMLHandle::NextSibling()` | 3 | 3 | 2 |  |
| 67 | `XMLConstHandle::LastChild() const` | 3 | 3 | 2 |  |
| 68 | `XMLPrinter::CStrSize() const` | 2 | 2 | 2 |  |
| 69 | `XMLPrinter::CStr() const` | 2 | 2 | 2 |  |
| 70 | `XMLHandle::ToUnknown()` | 2 | 2 | 2 |  |
| 71 | `XMLElement::QueryAttribute(const char *, const char **) const` | 2 | 2 | 2 |  |
| 72 | `XMLPrinter::PushText(bool)` | 15 | 80 | 1 |  |
| 73 | `XMLPrinter::PushText(uint64_t)` | 15 | 77 | 1 |  |
| 74 | `XMLPrinter::PushText(int64_t)` | 15 | 77 | 1 |  |
| 75 | `XMLPrinter::PushText(int)` | 15 | 77 | 1 |  |
| 76 | `XMLPrinter::PushText(float)` | 15 | 77 | 1 |  |
| 77 | `XMLPrinter::PushText(double)` | 15 | 77 | 1 |  |
| 78 | `XMLPrinter::PushAttribute(const char *, bool)` | 14 | 76 | 1 |  |
| 79 | `XMLPrinter::Visit(const XMLText &)` | 13 | 75 | 1 |  |
| 80 | `XMLPrinter::PushAttribute(const char *, unsigned int)` | 14 | 73 | 1 |  |
| 81 | `XMLPrinter::PushAttribute(const char *, uint64_t)` | 14 | 73 | 1 |  |
| 82 | `XMLPrinter::PushAttribute(const char *, int64_t)` | 14 | 73 | 1 |  |
| 83 | `XMLPrinter::PushAttribute(const char *, int)` | 14 | 73 | 1 |  |
| 84 | `XMLPrinter::PushAttribute(const char *, double)` | 14 | 73 | 1 |  |
| 85 | `XMLPrinter::Visit(const XMLDeclaration &)` | 14 | 46 | 1 |  |
| 86 | `XMLElement::BoolAttribute(const char *, bool) const` | 7 | 46 | 1 |  |
| 87 | `XMLElement::SetText(unsigned int)` | 10 | 42 | 1 |  |
| 88 | `XMLElement::SetText(uint64_t)` | 10 | 42 | 1 |  |
| 89 | `XMLElement::SetText(int64_t)` | 10 | 42 | 1 |  |
| 90 | `XMLElement::SetText(int)` | 10 | 42 | 1 |  |
| 91 | `XMLElement::SetText(float)` | 10 | 42 | 1 |  |
| 92 | `XMLElement::SetText(double)` | 10 | 42 | 1 |  |
| 93 | `XMLAttribute::BoolValue() const` | 6 | 42 | 1 |  |
| 94 | `XMLElement::IntAttribute(const char *, int) const` | 6 | 27 | 1 |  |
| 95 | `XMLElement::Int64Attribute(const char *, int64_t) const` | 6 | 27 | 1 |  |
| 96 | `XMLElement::QueryAttribute(const char *, unsigned int *) const` | 6 | 24 | 1 |  |
| 97 | `XMLElement::QueryAttribute(const char *, uint64_t *) const` | 6 | 24 | 1 |  |
| 98 | `XMLAttribute::IntValue() const` | 5 | 23 | 1 |  |
| 99 | `XMLAttribute::Int64Value() const` | 5 | 23 | 1 |  |
| 100 | `XMLDocument::RootElement()` | 5 | 20 | 1 |  |
| 101 | `XMLConstHandle::PreviousSiblingElement(const char *) const` | 5 | 20 | 1 |  |
| 102 | `XMLConstHandle::NextSiblingElement(const char *) const` | 5 | 20 | 1 |  |
| 103 | `XMLConstHandle::LastChildElement(const char *) const` | 5 | 20 | 1 |  |
| 104 | `XMLConstHandle::FirstChildElement(const char *) const` | 5 | 20 | 1 |  |
| 105 | `XMLAttribute::UnsignedValue() const` | 5 | 20 | 1 |  |
| 106 | `XMLAttribute::Unsigned64Value() const` | 5 | 20 | 1 |  |
| 107 | `XMLDocument::RootElement() const` | 4 | 19 | 1 |  |
| 108 | `XMLElement::FloatAttribute(const char *, float) const` | 5 | 14 | 1 |  |
| 109 | `XMLElement::DoubleAttribute(const char *, double) const` | 5 | 14 | 1 |  |
| 110 | `XMLAttribute::FloatValue() const` | 4 | 10 | 1 |  |
| 111 | `XMLAttribute::DoubleValue() const` | 4 | 10 | 1 |  |
| 112 | `XMLConstHandle::NextSibling() const` | 3 | 3 | 1 |  |
| 113 | `XMLConstHandle::FirstChild() const` | 3 | 3 | 1 |  |
| 114 | `XMLHandle::ToText()` | 2 | 2 | 1 |  |
| 115 | `XMLHandle::LastChild()` | 2 | 2 | 1 |  |
| 116 | `XMLHandle::FirstChild()` | 2 | 2 | 1 |  |
| 117 | `XMLConstHandle::ToUnknown() const` | 2 | 2 | 1 |  |
| 118 | `XMLConstHandle::ToText() const` | 2 | 2 | 1 |  |
| 119 | `XMLConstHandle::ToElement() const` | 2 | 2 | 1 |  |
| 120 | `XMLConstHandle::ToDeclaration() const` | 2 | 2 | 1 |  |
| 121 | `XMLUnknown::ToUnknown() const` | 1 | 1 | 1 |  |
| 122 | `XMLUnknown::ToUnknown()` | 1 | 1 | 1 |  |
| 123 | `XMLText::ToText() const` | 1 | 1 | 1 |  |
| 124 | `XMLText::ToText()` | 1 | 1 | 1 |  |
| 125 | `XMLPrinter::VisitExit(const XMLDocument &)` | 1 | 1 | 1 |  |
| 126 | `XMLNode::ToComment()` | 1 | 1 | 1 |  |
| 127 | `XMLNode::SetUserData(void *)` | 1 | 1 | 1 |  |
| 128 | `XMLNode::Parent()` | 1 | 1 | 1 |  |
| 129 | `XMLNode::NoChildren() const` | 1 | 1 | 1 |  |
| 130 | `XMLNode::LinkEndChild(XMLNode *)` | 1 | 1 | 1 |  |
| 131 | `XMLNode::GetUserData() const` | 1 | 1 | 1 |  |
| 132 | `XMLNode::GetLineNum() const` | 1 | 1 | 1 |  |
| 133 | `XMLNode::GetDocument() const` | 1 | 1 | 1 |  |
| 134 | `XMLHandle::operator=(const XMLHandle &)` | 1 | 1 | 1 |  |
| 135 | `XMLHandle::XMLHandle(const XMLHandle &)` | 1 | 1 | 1 |  |
| 136 | `XMLHandle::XMLHandle(XMLNode &)` | 1 | 1 | 1 |  |
| 137 | `XMLHandle::ToNode()` | 1 | 1 | 1 |  |
| 138 | `XMLHandle::ToElement()` | 1 | 1 | 1 |  |
| 139 | `XMLHandle::ToDeclaration()` | 1 | 1 | 1 |  |
| 140 | `XMLElement::ToElement() const` | 1 | 1 | 1 |  |
| 141 | `XMLDocument::ShallowEqual(const XMLNode *) const` | 1 | 1 | 1 |  |
| 142 | `XMLDocument::ShallowClone(XMLDocument *) const` | 1 | 1 | 1 |  |
| 143 | `XMLDocument::SetBOM(bool)` | 1 | 1 | 1 |  |
| 144 | `XMLDocument::ErrorName() const` | 1 | 1 | 1 |  |
| 145 | `XMLDocument::ErrorLineNum() const` | 1 | 1 | 1 |  |
| 146 | `XMLDocument::ErrorID() const` | 1 | 1 | 1 |  |
| 147 | `XMLDeclaration::ToDeclaration() const` | 1 | 1 | 1 |  |
| 148 | `XMLConstHandle::operator=(const XMLConstHandle &)` | 1 | 1 | 1 |  |
| 149 | `XMLConstHandle::XMLConstHandle(const XMLNode &)` | 1 | 1 | 1 |  |
| 150 | `XMLConstHandle::XMLConstHandle(const XMLConstHandle &)` | 1 | 1 | 1 |  |
| 151 | `XMLConstHandle::ToNode() const` | 1 | 1 | 1 |  |
| 152 | `XMLComment::ToComment() const` | 1 | 1 | 1 |  |
| 153 | `XMLComment::ToComment()` | 1 | 1 | 1 |  |
| 154 | `XMLAttribute::GetLineNum() const` | 1 | 1 | 1 |  |
| 155 | `XMLPrinter::PushText(const char *, bool)` | 12 | 74 | 0 |  |
| 156 | `XMLPrinter::PushAttribute(const char *, const char *)` | 11 | 70 | 0 |  |
| 157 | `XMLPrinter::OpenElement(const char *, bool)` | 15 | 63 | 0 |  |
| 158 | `XMLPrinter::PushHeader(bool, bool)` | 14 | 50 | 0 |  |
| 159 | `XMLPrinter::CloseElement(bool)` | 12 | 49 | 0 |  |
| 160 | `XMLElement::QueryBoolText(bool *) const` | 7 | 48 | 0 |  |
| 161 | `XMLPrinter::PushUnknown(const char *)` | 13 | 45 | 0 |  |
| 162 | `XMLPrinter::PushDeclaration(const char *)` | 13 | 45 | 0 |  |
| 163 | `XMLPrinter::PushComment(const char *)` | 13 | 45 | 0 |  |
| 164 | `XMLElement::QueryBoolAttribute(const char *, bool *) const` | 6 | 45 | 0 |  |
| 165 | `XMLAttribute::QueryBoolValue(bool *) const` | 5 | 41 | 0 |  |
| 166 | `XMLElement::SetText(const char *)` | 7 | 39 | 0 |  |
| 167 | `XMLUtil::ToBool(const char *, bool *)` | 4 | 37 | 0 |  |
| 168 | `XMLElement::QueryIntText(int *) const` | 6 | 29 | 0 |  |
| 169 | `XMLElement::QueryInt64Text(int64_t *) const` | 6 | 29 | 0 |  |
| 170 | `XMLElement::QueryUnsignedText(unsigned int *) const` | 6 | 26 | 0 |  |
| 171 | `XMLElement::QueryUnsigned64Text(uint64_t *) const` | 6 | 26 | 0 |  |
| 172 | `XMLElement::QueryIntAttribute(const char *, int *) const` | 5 | 26 | 0 |  |
| 173 | `XMLElement::QueryInt64Attribute(const char *, int64_t *) const` | 5 | 26 | 0 |  |
| 174 | `XMLElement::SetAttribute(const char *, const char *)` | 4 | 23 | 0 |  |
| 175 | `XMLElement::QueryUnsignedAttribute(const char *, unsigned int *) const` | 5 | 23 | 0 |  |
| 176 | `XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const` | 5 | 23 | 0 |  |
| 177 | `XMLNode::InsertFirstChild(XMLNode *)` | 1 | 22 | 0 |  |
| 178 | `XMLAttribute::QueryIntValue(int *) const` | 4 | 22 | 0 |  |
| 179 | `XMLAttribute::QueryInt64Value(int64_t *) const` | 4 | 22 | 0 |  |
| 180 | `XMLNode::PreviousSiblingElement(const char *)` | 4 | 19 | 0 |  |
| 181 | `XMLNode::NextSiblingElement(const char *)` | 4 | 19 | 0 |  |
| 182 | `XMLNode::LastChildElement(const char *)` | 4 | 19 | 0 |  |
| 183 | `XMLNode::FirstChildElement(const char *)` | 4 | 19 | 0 |  |
| 184 | `XMLAttribute::QueryUnsignedValue(unsigned int *) const` | 4 | 19 | 0 |  |
| 185 | `XMLAttribute::QueryUnsigned64Value(uint64_t *) const` | 4 | 19 | 0 |  |
| 186 | `XMLUtil::ToInt64(const char *, int64_t *)` | 3 | 18 | 0 |  |
| 187 | `XMLUtil::ToInt(const char *, int *)` | 3 | 18 | 0 |  |
| 188 | `XMLNode::PreviousSiblingElement(const char *) const` | 3 | 18 | 0 |  |
| 189 | `XMLNode::NextSiblingElement(const char *) const` | 3 | 18 | 0 |  |
| 190 | `XMLNode::LastChildElement(const char *) const` | 3 | 18 | 0 |  |
| 191 | `XMLNode::FirstChildElement(const char *) const` | 3 | 18 | 0 |  |
| 192 | `XMLElement::QueryFloatText(float *) const` | 5 | 16 | 0 |  |
| 193 | `XMLElement::QueryDoubleText(double *) const` | 5 | 16 | 0 |  |
| 194 | `XMLUtil::ToUnsigned64(const char *, uint64_t *)` | 3 | 15 | 0 |  |
| 195 | `XMLUtil::ToUnsigned(const char *, unsigned int *)` | 3 | 15 | 0 |  |
| 196 | `XMLDocument::Accept(XMLVisitor *) const` | 6 | 15 | 0 |  |
| 197 | `XMLElement::QueryFloatAttribute(const char *, float *) const` | 4 | 13 | 0 |  |
| 198 | `XMLElement::QueryDoubleAttribute(const char *, double *) const` | 4 | 13 | 0 |  |
| 199 | `XMLNode::DeepClone(XMLDocument *) const` | 4 | 12 | 0 |  |
| 200 | `XMLDocument::NewDeclaration(const char *)` | 3 | 9 | 0 |  |
| 201 | `XMLAttribute::QueryFloatValue(float *) const` | 3 | 9 | 0 |  |
| 202 | `XMLAttribute::QueryDoubleValue(double *) const` | 3 | 9 | 0 |  |
| 203 | `XMLUtil::IsPrefixHex(const char *)` | 1 | 7 | 0 |  |
| 204 | `XMLDocument::NewElement(const char *)` | 4 | 7 | 0 |  |
| 205 | `XMLElement::SetName(const char *, bool)` | 3 | 6 | 0 |  |
| 206 | `XMLDocument::NewUnknown(const char *)` | 3 | 6 | 0 |  |
| 207 | `XMLDocument::NewText(const char *)` | 3 | 6 | 0 |  |
| 208 | `XMLDocument::NewComment(const char *)` | 3 | 6 | 0 |  |
| 209 | `XMLAttribute::SetAttribute(bool)` | 3 | 6 | 0 |  |
| 210 | `XMLUtil::ToStr(bool, char *, int)` | 2 | 5 | 0 |  |
| 211 | `XMLUtil::ToFloat(const char *, float *)` | 2 | 5 | 0 |  |
| 212 | `XMLUtil::ToDouble(const char *, double *)` | 2 | 5 | 0 |  |
| 213 | `XMLNode::SetValue(const char *, bool)` | 2 | 5 | 0 |  |
| 214 | `XMLNode::GetDocument()` | 1 | 4 | 0 |  |
| 215 | `XMLDocument::ErrorStr() const` | 1 | 4 | 0 |  |
| 216 | `XMLAttribute::SetAttribute(unsigned int)` | 3 | 3 | 0 |  |
| 217 | `XMLAttribute::SetAttribute(uint64_t)` | 3 | 3 | 0 |  |
| 218 | `XMLAttribute::SetAttribute(int64_t)` | 3 | 3 | 0 |  |
| 219 | `XMLAttribute::SetAttribute(int)` | 3 | 3 | 0 |  |
| 220 | `XMLAttribute::SetAttribute(float)` | 3 | 3 | 0 |  |
| 221 | `XMLAttribute::SetAttribute(double)` | 3 | 3 | 0 |  |
| 222 | `XMLUtil::ToStr(unsigned int, char *, int)` | 2 | 2 | 0 |  |
| 223 | `XMLUtil::ToStr(uint64_t, char *, int)` | 2 | 2 | 0 |  |
| 224 | `XMLUtil::ToStr(int64_t, char *, int)` | 2 | 2 | 0 |  |
| 225 | `XMLUtil::ToStr(int, char *, int)` | 2 | 2 | 0 |  |
| 226 | `XMLUtil::ToStr(float, char *, int)` | 2 | 2 | 0 |  |
| 227 | `XMLUtil::ToStr(double, char *, int)` | 2 | 2 | 0 |  |
| 228 | `XMLVisitor::VisitExit(const XMLElement &)` | 1 | 1 | 0 |  |
| 229 | `XMLVisitor::VisitExit(const XMLDocument &)` | 1 | 1 | 0 |  |
| 230 | `XMLVisitor::VisitEnter(const XMLElement &, const XMLAttribute *)` | 1 | 1 | 0 |  |
| 231 | `XMLVisitor::VisitEnter(const XMLDocument &)` | 1 | 1 | 0 |  |
| 232 | `XMLVisitor::Visit(const XMLUnknown &)` | 1 | 1 | 0 |  |
| 233 | `XMLVisitor::Visit(const XMLText &)` | 1 | 1 | 0 |  |
| 234 | `XMLVisitor::Visit(const XMLDeclaration &)` | 1 | 1 | 0 |  |
| 235 | `XMLVisitor::Visit(const XMLComment &)` | 1 | 1 | 0 |  |
| 236 | `XMLNode::ToUnknown() const` | 1 | 1 | 0 |  |
| 237 | `XMLNode::ToUnknown()` | 1 | 1 | 0 |  |
| 238 | `XMLNode::ToText() const` | 1 | 1 | 0 |  |
| 239 | `XMLNode::ToText()` | 1 | 1 | 0 |  |
| 240 | `XMLNode::ToElement() const` | 1 | 1 | 0 |  |
| 241 | `XMLNode::ToDeclaration() const` | 1 | 1 | 0 |  |
| 242 | `XMLNode::ToComment() const` | 1 | 1 | 0 |  |
| 243 | `XMLNode::PreviousSibling() const` | 1 | 1 | 0 |  |
| 244 | `XMLNode::PreviousSibling()` | 1 | 1 | 0 |  |
| 245 | `XMLNode::Parent() const` | 1 | 1 | 0 |  |
| 246 | `XMLNode::NextSibling() const` | 1 | 1 | 0 |  |
| 247 | `XMLNode::NextSibling()` | 1 | 1 | 0 |  |
| 248 | `XMLNode::LastChild() const` | 1 | 1 | 0 |  |
| 249 | `XMLNode::FirstChild() const` | 1 | 1 | 0 |  |
| 250 | `XMLHandle::XMLHandle(XMLNode *)` | 1 | 1 | 0 |  |
| 251 | `XMLElement::QueryStringAttribute(const char *, const char **) const` | 1 | 1 | 0 |  |
| 252 | `XMLElement::FirstAttribute() const` | 1 | 1 | 0 |  |
| 253 | `XMLDocument::HasBOM() const` | 1 | 1 | 0 |  |
| 254 | `XMLConstHandle::XMLConstHandle(const XMLNode *)` | 1 | 1 | 0 |  |
| 255 | `XMLAttribute::SetAttribute(const char *)` | 1 | 1 | 0 |  |
| 256 | `XMLAttribute::Next() const` | 1 | 1 | 0 |  |
| 257 | `XMLDocument::SaveFile(const char *, bool)` | 15 | 71 | 0 | 파일 입출력 |
| 258 | `XMLDocument::SaveFile(FILE *, bool)` | 13 | 61 | 0 | 파일 입출력 |
| 259 | `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)` | 5 | 41 | 0 | 파일 입출력 |
