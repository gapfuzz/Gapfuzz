# 호출 안 함 API 우선순위 — jsoncpp/_union

'호출 안 함' API 213개. 추가 가능 211개, 제외 2개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `Reader::parse(const std::string &, Value &, bool)` | 299 | 406 | 406 | 이번에 추가 |
| 2 | `StyledWriter::write(const Value &)` | 269 | 385 | 385 | 이번에 추가 |
| 3 | `Value::isConvertibleTo(ValueType) const` | 88 | 119 | 99 | 이번에 추가 |
| 4 | `StyledStreamWriter::write(OStream &, const Value &)` | 271 | 385 | 98 | 이번에 추가 |
| 5 | `Value::resize(ArrayIndex)` | 119 | 61 | 58 | 이번에 추가 |
| 6 | `operator<<(OStream &, const Value &)` | 102 | 55 | 52 | 이번에 추가 |
| 7 | `Path::Path(const String &, const PathArgument &, const PathArgument &, const PathArgument &, const PathArgument &, const PathArgument &)` | 125 | 51 | 51 | 이번에 추가 |
| 8 | `Value::compare(const Value &) const` | 37 | 52 | 45 | 이번에 추가 |
| 9 | `as() const` | 79 | 66 | 42 | 이번에 추가 |
| 10 | `Value::operator!=(const Value &) const` | 27 | 41 | 34 | 이번에 추가 |
| 11 | `FastWriter::write(const Value &)` | 218 | 297 | 29 |  |
| 12 | `Value::members()` | 13 | 24 | 24 |  |
| 13 | `Value::removeMember(const String &)` | 119 | 35 | 22 |  |
| 14 | `Value::operator[](const StaticString &)` | 120 | 34 | 21 |  |
| 15 | `Reader::getFormatedErrorMessages() const` | 50 | 21 | 21 |  |
| 16 | `Path::resolve(const Value &, const Value &) const` | 106 | 45 | 19 |  |
| 17 | `Value::insert(ArrayIndex, const Value &)` | 75 | 22 | 19 |  |
| 18 | `Path::resolve(const Value &) const` | 106 | 45 | 18 |  |
| 19 | `StreamWriterBuilder::validate(Value *) const` | 39 | 26 | 17 |  |
| 20 | `Value::findIntegral(const String &) const` | 9 | 19 | 17 |  |
| 21 | `Value::removeMember(const char *)` | 118 | 28 | 15 |  |
| 22 | `Value::append(const Value &)` | 113 | 28 | 15 |  |
| 23 | `as() const` | 75 | 19 | 15 |  |
| 24 | `as() const` | 76 | 21 | 14 |  |
| 25 | `ValueIteratorBase::key() const` | 12 | 15 | 12 |  |
| 26 | `Value::demand(const char *, const char *)` | 73 | 15 | 12 |  |
| 27 | `Value::removeIndex(ArrayIndex, Value *)` | 71 | 13 | 12 |  |
| 28 | `Path::make(Value &) const` | 7 | 11 | 11 |  |
| 29 | `Value::operator[](int) const` | 95 | 31 | 10 |  |
| 30 | `ValueIteratorBase::operator-(const SelfType &) const` | 5 | 10 | 10 |  |
| 31 | `Reader::pushError(const Value &, const String &, const Value &)` | 95 | 10 | 10 |  |
| 32 | `Value::findString(const String &) const` | 7 | 9 | 8 |  |
| 33 | `Value::findBool(const String &) const` | 7 | 9 | 8 |  |
| 34 | `Value::findInt(const String &) const` | 9 | 21 | 7 |  |
| 35 | `Value::findUInt64(const String &) const` | 9 | 19 | 7 |  |
| 36 | `Value::findInt64(const String &) const` | 9 | 19 | 7 |  |
| 37 | `Value::findNumeric(const String &) const` | 8 | 14 | 7 |  |
| 38 | `Value::findDouble(const String &) const` | 7 | 13 | 7 |  |
| 39 | `Value::findNull(const String &) const` | 7 | 9 | 7 |  |
| 40 | `Value::findUInt(const String &) const` | 6 | 8 | 7 |  |
| 41 | `Value::findObject(const String &) const` | 6 | 8 | 7 |  |
| 42 | `Value::findArray(const String &) const` | 6 | 8 | 7 |  |
| 43 | `Reader::pushError(const Value &, const String &)` | 95 | 8 | 6 |  |
| 44 | `Value::toStyledString() const` | 116 | 26 | 5 |  |
| 45 | `Value::get(std::string_view, const Value &) const` | 4 | 5 | 5 |  |
| 46 | `Value::get(ArrayIndex, const Value &) const` | 95 | 25 | 4 |  |
| 47 | `Value::back()` | 17 | 18 | 4 |  |
| 48 | `operator>>(IStream &, Value &)` | 71 | 4 | 4 |  |
| 49 | `ValueIteratorBase::memberName() const` | 5 | 4 | 4 |  |
| 50 | `ValueIteratorBase::index() const` | 5 | 4 | 4 |  |
| 51 | `StyledStreamWriter::StyledStreamWriter(String)` | 2 | 4 | 4 |  |
| 52 | `Reader::Reader()` | 3 | 4 | 4 |  |
| 53 | `ValueMembersIterator::operator++(int)` | 7 | 4 | 3 |  |
| 54 | `Value::back() const` | 11 | 5 | 2 |  |
| 55 | `ValueMembersView::end() const` | 4 | 3 | 2 |  |
| 56 | `ValueMembersIterator::operator==(const ValueMembersIterator &) const` | 2 | 2 | 2 |  |
| 57 | `ValueIterator::operator=(const SelfType &)` | 3 | 2 | 2 |  |
| 58 | `ValueIterator::ValueIterator(const ValueConstIterator &)` | 2 | 2 | 2 |  |
| 59 | `ValueConstMembersView::end() const` | 4 | 2 | 2 |  |
| 60 | `ValueConstMembersIterator::operator++(int)` | 8 | 2 | 2 |  |
| 61 | `ValueConstIterator::ValueConstIterator(const ValueIterator &)` | 2 | 2 | 2 |  |
| 62 | `Value::members() const` | 4 | 2 | 2 |  |
| 63 | `Value::copy(const Value &)` | 2 | 2 | 2 |  |
| 64 | `Reader::getStructuredErrors() const` | 98 | 2 | 2 |  |
| 65 | `Reader::Reader(const Features &)` | 2 | 2 | 2 |  |
| 66 | `Reader::parse(IStream &, Value &, bool)` | 300 | 406 | 1 |  |
| 67 | `valueToQuotedString(const char *)` | 64 | 83 | 1 |  |
| 68 | `as() const` | 79 | 64 | 1 |  |
| 69 | `as() const` | 80 | 56 | 1 |  |
| 70 | `Value::operator>=(const Value &) const` | 36 | 45 | 1 |  |
| 71 | `Value::operator<=(const Value &) const` | 36 | 45 | 1 |  |
| 72 | `as() const` | 75 | 19 | 1 |  |
| 73 | `Value::front()` | 13 | 16 | 1 |  |
| 74 | `is() const` | 4 | 14 | 1 |  |
| 75 | `is() const` | 4 | 12 | 1 |  |
| 76 | `is() const` | 4 | 12 | 1 |  |
| 77 | `Value::getString(std::string_view *) const` | 5 | 12 | 1 |  |
| 78 | `Value::removeMember(std::string_view, Value *)` | 49 | 10 | 1 |  |
| 79 | `Value::removeMember(std::string_view)` | 49 | 10 | 1 |  |
| 80 | `Value::removeMember(const char *, Value *)` | 48 | 10 | 1 |  |
| 81 | `is() const` | 2 | 6 | 1 |  |
| 82 | `Value::get(const char *, const Value &) const` | 3 | 5 | 1 |  |
| 83 | `Value::get(const String &, const Value &) const` | 5 | 5 | 1 |  |
| 84 | `ValueIterator::operator--(int)` | 7 | 4 | 1 |  |
| 85 | `Value::Value(std::string_view)` | 6 | 4 | 1 |  |
| 86 | `ValueMembersView::begin() const` | 4 | 3 | 1 |  |
| 87 | `ValueMembersIterator::operator*() const` | 7 | 3 | 1 |  |
| 88 | `ValueIterator::operator++(int)` | 4 | 3 | 1 |  |
| 89 | `ValueConstMembersIterator::operator*() const` | 7 | 3 | 1 |  |
| 90 | `ValueConstIterator::operator--(int)` | 9 | 3 | 1 |  |
| 91 | `Value::front() const` | 7 | 3 | 1 |  |
| 92 | `Value::Value(Value &&) noexcept` | 3 | 3 | 1 |  |
| 93 | `is() const` | 2 | 2 | 1 |  |
| 94 | `is() const` | 2 | 2 | 1 |  |
| 95 | `ValueIterator::operator->() const` | 6 | 2 | 1 |  |
| 96 | `ValueConstMembersView::begin() const` | 4 | 2 | 1 |  |
| 97 | `ValueConstMembersIterator::operator==(const ValueConstMembersIterator &) const` | 2 | 2 | 1 |  |
| 98 | `ValueConstIterator::operator=(const ValueIteratorBase &)` | 3 | 2 | 1 |  |
| 99 | `ValueConstIterator::operator->() const` | 6 | 2 | 1 |  |
| 100 | `Value::operator bool() const` | 2 | 2 | 1 |  |
| 101 | `valueToString(UInt)` | 1 | 1 | 1 |  |
| 102 | `valueToString(Int)` | 1 | 1 | 1 |  |
| 103 | `swap(Value &, Value &)` | 1 | 1 | 1 |  |
| 104 | `is() const` | 1 | 1 | 1 |  |
| 105 | `as() const` | 1 | 1 | 1 |  |
| 106 | `as() const` | 1 | 1 | 1 |  |
| 107 | `as() const` | 1 | 1 | 1 |  |
| 108 | `ValueMembersIterator::operator!=(const ValueMembersIterator &) const` | 1 | 1 | 1 |  |
| 109 | `ValueConstMembersIterator::operator!=(const ValueConstMembersIterator &) const` | 1 | 1 | 1 |  |
| 110 | `ValueConstIterator::operator++(int)` | 5 | 1 | 1 |  |
| 111 | `Value::setComment(const char *, size_t, CommentPlacement)` | 1 | 1 | 1 |  |
| 112 | `Value::setComment(const char *, CommentPlacement)` | 2 | 1 | 1 |  |
| 113 | `Value::operator[](std::string_view) const` | 3 | 1 | 1 |  |
| 114 | `Value::operator[](std::string_view)` | 3 | 1 | 1 |  |
| 115 | `Value::isMember(std::string_view) const` | 3 | 1 | 1 |  |
| 116 | `Value::isMember(const char *) const` | 2 | 1 | 1 |  |
| 117 | `StyledWriter::StyledWriter()` | 2 | 1 | 1 |  |
| 118 | `StreamWriterBuilder::operator[](const String &)` | 1 | 1 | 1 |  |
| 119 | `StaticString::operator const char *() const` | 1 | 1 | 1 |  |
| 120 | `Reader::good() const` | 3 | 1 | 1 |  |
| 121 | `FastWriter::omitEndingLineFeed()` | 1 | 1 | 1 |  |
| 122 | `FastWriter::enableYAMLCompatibility()` | 1 | 1 | 1 |  |
| 123 | `FastWriter::dropNullPlaceholders()` | 1 | 1 | 1 |  |
| 124 | `FastWriter::FastWriter()` | 2 | 1 | 1 |  |
| 125 | `Exception::what() const noexcept` | 3 | 1 | 1 |  |
| 126 | `CharReaderBuilder::strictMode(Value *)` | 1 | 1 | 1 |  |
| 127 | `CharReaderBuilder::operator[](const String &)` | 1 | 1 | 1 |  |
| 128 | `CharReaderBuilder::ecma404Mode(Value *)` | 1 | 1 | 1 |  |
| 129 | `CharReader::getStructuredErrors() const` | 9 | 1 | 1 |  |
| 130 | `Reader::parse(const char *, const char *, Value &, bool)` | 287 | 405 | 0 |  |
| 131 | `valueToQuotedString(const char *, size_t)` | 63 | 83 | 0 |  |
| 132 | `Value::asInt() const` | 78 | 65 | 0 |  |
| 133 | `Value::asLargestInt() const` | 79 | 64 | 0 |  |
| 134 | `Value::asInt64() const` | 78 | 63 | 0 |  |
| 135 | `Value::asLargestUInt() const` | 80 | 56 | 0 |  |
| 136 | `Value::asUInt64() const` | 79 | 55 | 0 |  |
| 137 | `Value::operator>(const Value &) const` | 36 | 45 | 0 |  |
| 138 | `Value::operator<(const Value &) const` | 35 | 44 | 0 |  |
| 139 | `Value::operator==(const Value &) const` | 26 | 40 | 0 |  |
| 140 | `StreamWriterBuilder::newStreamWriter() const` | 25 | 37 | 0 |  |
| 141 | `Value::append(Value &&)` | 112 | 27 | 0 |  |
| 142 | `Value::operator[](ArrayIndex) const` | 94 | 21 | 0 |  |
| 143 | `Value::insert(ArrayIndex, Value &&)` | 74 | 21 | 0 |  |
| 144 | `Value::getMemberNames() const` | 138 | 21 | 0 |  |
| 145 | `Value::findValue(const String &) const` | 8 | 20 | 0 |  |
| 146 | `Value::clear()` | 94 | 20 | 0 |  |
| 147 | `Value::asCString() const` | 75 | 20 | 0 |  |
| 148 | `Reader::getFormattedErrorMessages() const` | 49 | 20 | 0 |  |
| 149 | `Value::findValue(const String &) const` | 8 | 18 | 0 |  |
| 150 | `Value::findValue(const String &) const` | 8 | 18 | 0 |  |
| 151 | `Value::findValue(const String &) const` | 8 | 18 | 0 |  |
| 152 | `Value::asFloat() const` | 74 | 18 | 0 |  |
| 153 | `Value::asDouble() const` | 74 | 18 | 0 |  |
| 154 | `StreamWriterBuilder::StreamWriterBuilder()` | 79 | 17 | 0 |  |
| 155 | `StreamWriterBuilder::setDefaults(Value *)` | 77 | 16 | 0 |  |
| 156 | `Value::Value(const char *)` | 76 | 15 | 0 |  |
| 157 | `Value::isInt() const` | 3 | 13 | 0 |  |
| 158 | `Value::findValue(const String &) const` | 7 | 13 | 0 |  |
| 159 | `Value::end()` | 6 | 13 | 0 |  |
| 160 | `Value::begin()` | 6 | 13 | 0 |  |
| 161 | `Value::findValue(const String &) const` | 6 | 12 | 0 |  |
| 162 | `Value::isUInt64() const` | 3 | 11 | 0 |  |
| 163 | `Value::isIntegral() const` | 3 | 11 | 0 |  |
| 164 | `Value::isInt64() const` | 3 | 11 | 0 |  |
| 165 | `Value::getString(const char **, const char **) const` | 3 | 11 | 0 |  |
| 166 | `Value::removeMember(const String &, Value *)` | 50 | 10 | 0 |  |
| 167 | `Value::removeMember(const char *, const char *, Value *)` | 46 | 9 | 0 |  |
| 168 | `Value::findValue(const String &) const` | 6 | 8 | 0 |  |
| 169 | `Value::findValue(const String &) const` | 6 | 8 | 0 |  |
| 170 | `Value::findValue(const String &) const` | 6 | 8 | 0 |  |
| 171 | `Value::findValue(const String &) const` | 5 | 7 | 0 |  |
| 172 | `Value::findValue(const String &) const` | 5 | 7 | 0 |  |
| 173 | `Value::findValue(const String &) const` | 5 | 7 | 0 |  |
| 174 | `Value::isNumeric() const` | 2 | 6 | 0 |  |
| 175 | `Value::operator[](const String &) const` | 5 | 5 | 0 |  |
| 176 | `Value::isDouble() const` | 1 | 5 | 0 |  |
| 177 | `Value::getComment(CommentPlacement) const` | 14 | 5 | 0 |  |
| 178 | `valueToString(bool)` | 1 | 4 | 0 |  |
| 179 | `Value::hasComment(CommentPlacement) const` | 16 | 4 | 0 |  |
| 180 | `Value::get(const char *, const char *, const Value &) const` | 1 | 4 | 0 |  |
| 181 | `Value::Value(const StaticString &)` | 4 | 4 | 0 |  |
| 182 | `ValueIterator::ValueIterator()` | 2 | 3 | 0 |  |
| 183 | `Value::Value(const char *, const char *)` | 3 | 3 | 0 |  |
| 184 | `PathArgument::PathArgument(const char *)` | 1 | 3 | 0 |  |
| 185 | `PathArgument::PathArgument(String)` | 2 | 3 | 0 |  |
| 186 | `PathArgument::PathArgument(ArrayIndex)` | 1 | 3 | 0 |  |
| 187 | `ValueMembersView::ValueMembersView(ValueIterator, ValueIterator)` | 3 | 2 | 0 |  |
| 188 | `ValueMembersIterator::operator++()` | 2 | 2 | 0 |  |
| 189 | `ValueMembersIterator::ValueMembersIterator(const ValueIterator &)` | 3 | 2 | 0 |  |
| 190 | `ValueIterator::operator--()` | 4 | 2 | 0 |  |
| 191 | `ValueIterator::operator*() const` | 6 | 2 | 0 |  |
| 192 | `ValueConstIterator::operator--()` | 4 | 2 | 0 |  |
| 193 | `StreamWriter::StreamWriter()` | 1 | 2 | 0 |  |
| 194 | `StaticString::StaticString(const char *)` | 1 | 2 | 0 |  |
| 195 | `writeString(const StreamWriter::Factory &, const Value &)` | 68 | 1 | 0 |  |
| 196 | `parseFromStream(const CharReader::Factory &, IStream &, Value *, String *)` | 70 | 1 | 0 |  |
| 197 | `ValueIteratorBase::operator==(const SelfType &) const` | 1 | 1 | 0 |  |
| 198 | `ValueIterator::operator++()` | 1 | 1 | 0 |  |
| 199 | `ValueIterator::ValueIterator(const ValueIterator &)` | 2 | 1 | 0 |  |
| 200 | `ValueConstMembersView::ValueConstMembersView(ValueConstIterator, ValueConstIterator)` | 3 | 1 | 0 |  |
| 201 | `ValueConstMembersIterator::operator++()` | 1 | 1 | 0 |  |
| 202 | `ValueConstMembersIterator::ValueConstMembersIterator(const ValueConstIterator &)` | 3 | 1 | 0 |  |
| 203 | `Value::isValidIndex(ArrayIndex) const` | 1 | 1 | 0 |  |
| 204 | `Value::isString() const` | 1 | 1 | 0 |  |
| 205 | `Value::isBool() const` | 1 | 1 | 0 |  |
| 206 | `Value::getOffsetStart() const` | 1 | 1 | 0 |  |
| 207 | `Value::getOffsetLimit() const` | 1 | 1 | 0 |  |
| 208 | `Value::find(const String &) const` | 4 | 1 | 0 |  |
| 209 | `Value::copyPayload(const Value &)` | 1 | 1 | 0 |  |
| 210 | `StaticString::c_str() const` | 1 | 1 | 0 |  |
| 211 | `PathArgument::PathArgument()` | 1 | 1 | 0 |  |
| 212 | `ValueConstMembersIterator::ValueConstMembersIterator()` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 213 | `ValueMembersIterator::ValueMembersIterator()` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
