# 호출 안 함 API 우선순위 — pugixml/_union

'호출 안 함' API 288개. 추가 가능 274개, 제외 14개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `xml_document::save(std::basic_ostream<wchar_t> &, const char_t *, unsigned int) const` | 47 | 506 | 506 | 이번에 추가 |
| 2 | `xml_text::operator=(bool)` | 18 | 151 | 151 | 이번에 추가 |
| 3 | `xml_document::load(std::basic_istream<wchar_t> &, unsigned int)` | 22 | 76 | 76 | 이번에 추가 |
| 4 | `xml_document::load(std::basic_istream<char> &, unsigned int, xml_encoding)` | 22 | 76 | 72 | 이번에 추가 |
| 5 | `xml_text::as_ullong(unsigned long long) const` | 5 | 93 | 71 | 이번에 추가 |
| 6 | `xml_text::as_uint(unsigned int) const` | 5 | 93 | 71 | 이번에 추가 |
| 7 | `xpath_node_set::sort(bool)` | 18 | 70 | 70 | 이번에 추가 |
| 8 | `xml_node::remove_child(string_view_t)` | 14 | 89 | 67 | 이번에 추가 |
| 9 | `xpath_variable_set::xpath_variable_set(const xpath_variable_set &)` | 12 | 66 | 66 | 이번에 추가 |
| 10 | `xml_node::insert_copy_before(const xml_node &, const xml_node &)` | 15 | 143 | 56 | 이번에 추가 |
| 11 | `as_wide(const char *)` | 18 | 89 | 48 |  |
| 12 | `xml_node::first_element_by_path(const char_t *, char_t) const` | 5 | 45 | 45 |  |
| 13 | `xml_node::insert_copy_before(const xml_attribute &, const xml_attribute &)` | 17 | 118 | 40 |  |
| 14 | `xml_named_node_iterator::operator--(int)` | 10 | 35 | 35 |  |
| 15 | `xml_node::insert_child_after(string_view_t, const xml_node &)` | 17 | 132 | 34 |  |
| 16 | `xml_node::child_value(const char_t *) const` | 4 | 37 | 33 |  |
| 17 | `xml_node::traverse(xml_tree_walker &)` | 5 | 33 | 33 |  |
| 18 | `xml_node::remove_attribute(string_view_t)` | 13 | 78 | 32 |  |
| 19 | `xml_node::offset_debug() const` | 2 | 29 | 29 |  |
| 20 | `xml_document::operator=(xml_document &&) noexcept` | 3 | 29 | 29 |  |
| 21 | `xml_node::insert_move_before(const xml_node &, const xml_node &)` | 10 | 65 | 28 |  |
| 22 | `xml_node::find_child_by_attribute(const char_t *, const char_t *, const char_t *) const` | 1 | 25 | 25 |  |
| 23 | `xml_node::insert_attribute_after(string_view_t, const xml_attribute &)` | 17 | 103 | 23 |  |
| 24 | `xml_node::attribute(string_view_t, xml_attribute &) const` | 6 | 40 | 23 |  |
| 25 | `xml_node::attribute(const char_t *, xml_attribute &) const` | 3 | 30 | 23 |  |
| 26 | `xml_node::find_child_by_attribute(const char_t *, const char_t *) const` | 1 | 21 | 21 |  |
| 27 | `xml_node::insert_child_before(string_view_t, const xml_node &)` | 17 | 132 | 19 |  |
| 28 | `xml_node::insert_attribute_before(const char_t *, const xml_attribute &)` | 15 | 103 | 19 |  |
| 29 | `xml_parse_result::description() const` | 1 | 19 | 19 |  |
| 30 | `xml_attribute_iterator::operator--(int)` | 11 | 19 | 19 |  |
| 31 | `xml_node::prepend_child(string_view_t)` | 17 | 127 | 18 |  |
| 32 | `xml_node::insert_copy_after(const xml_attribute &, const xml_attribute &)` | 17 | 118 | 18 |  |
| 33 | `xml_node::path(char_t) const` | 11 | 18 | 18 |  |
| 34 | `xml_node::prepend_copy(const xml_attribute &)` | 16 | 106 | 17 |  |
| 35 | `xml_text::as_bool(bool) const` | 4 | 38 | 16 |  |
| 36 | `xml_node::insert_copy_after(const xml_node &, const xml_node &)` | 15 | 143 | 15 |  |
| 37 | `xml_node::insert_attribute_before(string_view_t, const xml_attribute &)` | 17 | 103 | 15 |  |
| 38 | `xml_node::insert_attribute_after(const char_t *, const xml_attribute &)` | 15 | 103 | 15 |  |
| 39 | `xml_node::set_value(string_view_t)` | 10 | 80 | 15 |  |
| 40 | `xml_node::set_value(const char_t *, size_t)` | 8 | 80 | 15 |  |
| 41 | `xml_node::set_value(const char_t *)` | 8 | 80 | 15 |  |
| 42 | `xml_node::insert_move_after(const xml_node &, const xml_node &)` | 10 | 65 | 15 |  |
| 43 | `xml_named_node_iterator::operator++(int)` | 9 | 15 | 15 |  |
| 44 | `xml_node::ensure_attribute(string_view_t)` | 19 | 113 | 14 |  |
| 45 | `xml_node::ensure_attribute(const char_t *)` | 15 | 91 | 14 |  |
| 46 | `xpath_query::evaluate_string(char_t *, size_t, const xpath_node &) const` | 5 | 14 | 14 |  |
| 47 | `as_utf8(const wchar_t *)` | 16 | 14 | 14 |  |
| 48 | `xml_text::operator=(unsigned long)` | 19 | 150 | 13 |  |
| 49 | `xml_text::operator=(unsigned long long)` | 19 | 150 | 13 |  |
| 50 | `xml_text::operator=(unsigned int)` | 19 | 150 | 13 |  |
| 51 | `xml_node::append_copy(const xml_attribute &)` | 15 | 102 | 13 |  |
| 52 | `xml_node::append_buffer(const void *, size_t, unsigned int, xml_encoding)` | 3 | 37 | 12 |  |
| 53 | `xml_node::previous_sibling(string_view_t) const` | 5 | 22 | 12 |  |
| 54 | `xml_node::next_sibling(string_view_t) const` | 5 | 22 | 12 |  |
| 55 | `xml_node_iterator::operator--(int)` | 9 | 19 | 12 |  |
| 56 | `xml_node::set_name(const char_t *, size_t)` | 8 | 76 | 11 |  |
| 57 | `xml_node::prepend_copy(const xml_node &)` | 15 | 138 | 10 |  |
| 58 | `xml_node::append_copy(const xml_node &)` | 14 | 134 | 10 |  |
| 59 | `xml_node::prepend_attribute(string_view_t)` | 16 | 91 | 10 |  |
| 60 | `xml_node::prepend_attribute(const char_t *)` | 14 | 91 | 10 |  |
| 61 | `xpath_node_set::operator=(xpath_node_set &&) noexcept` | 5 | 10 | 10 |  |
| 62 | `xml_node::remove_children()` | 8 | 57 | 9 |  |
| 63 | `xml_node::remove_attributes()` | 6 | 38 | 9 |  |
| 64 | `xml_text::get() const` | 3 | 31 | 9 |  |
| 65 | `xml_document::document_element() const` | 2 | 9 | 9 |  |
| 66 | `xml_text::operator=(float)` | 21 | 145 | 8 |  |
| 67 | `xml_text::as_llong(long long) const` | 5 | 93 | 8 |  |
| 68 | `xml_text::as_int(int) const` | 5 | 93 | 8 |  |
| 69 | `xml_text::as_float(float) const` | 5 | 30 | 8 |  |
| 70 | `xml_text::as_double(double) const` | 5 | 30 | 8 |  |
| 71 | `xml_node::children() const` | 4 | 8 | 8 |  |
| 72 | `xml_node::attributes() const` | 4 | 8 | 8 |  |
| 73 | `xml_node::print(std::basic_ostream<char> &, const char_t *, unsigned int, xml_encoding, unsigned int) const` | 46 | 484 | 7 |  |
| 74 | `xml_text::operator=(double)` | 21 | 145 | 7 |  |
| 75 | `xml_attribute::as_ullong(unsigned long long) const` | 3 | 71 | 7 |  |
| 76 | `xml_attribute::as_uint(unsigned int) const` | 3 | 71 | 7 |  |
| 77 | `xml_attribute::as_llong(long long) const` | 3 | 71 | 7 |  |
| 78 | `xml_attribute::as_int(int) const` | 3 | 71 | 7 |  |
| 79 | `xml_node::prepend_move(const xml_node &)` | 10 | 57 | 7 |  |
| 80 | `xml_node::append_move(const xml_node &)` | 9 | 53 | 7 |  |
| 81 | `xml_text::as_string(const char_t *) const` | 3 | 29 | 7 |  |
| 82 | `xml_attribute::as_bool(bool) const` | 2 | 16 | 7 |  |
| 83 | `xml_attribute::as_float(float) const` | 3 | 8 | 7 |  |
| 84 | `xml_attribute::as_double(double) const` | 3 | 8 | 7 |  |
| 85 | `xml_writer_stream::write(const void *, size_t)` | 4 | 7 | 7 |  |
| 86 | `xml_attribute::as_string(const char_t *) const` | 1 | 7 | 7 |  |
| 87 | `xpath_query::operator=(xpath_query &&) noexcept` | 3 | 6 | 6 |  |
| 88 | `xml_text::operator=(long)` | 19 | 150 | 5 |  |
| 89 | `xml_text::operator=(long long)` | 19 | 150 | 5 |  |
| 90 | `xml_text::operator=(int)` | 19 | 150 | 5 |  |
| 91 | `xml_node::ensure_child(string_view_t)` | 20 | 149 | 5 |  |
| 92 | `xml_text::operator=(string_view_t)` | 19 | 142 | 5 |  |
| 93 | `xml_text::operator=(const char_t *)` | 17 | 142 | 5 |  |
| 94 | `xml_node::ensure_child(const char_t *)` | 16 | 128 | 5 |  |
| 95 | `xml_attribute::operator=(bool)` | 10 | 79 | 5 |  |
| 96 | `xml_attribute::operator=(unsigned long)` | 11 | 78 | 5 |  |
| 97 | `xml_attribute::operator=(unsigned long long)` | 11 | 78 | 5 |  |
| 98 | `xml_attribute::operator=(unsigned int)` | 11 | 78 | 5 |  |
| 99 | `xml_attribute::operator=(long)` | 11 | 78 | 5 |  |
| 100 | `xml_attribute::operator=(long long)` | 11 | 78 | 5 |  |
| 101 | `xml_attribute::operator=(int)` | 11 | 78 | 5 |  |
| 102 | `xml_attribute::operator=(float)` | 13 | 73 | 5 |  |
| 103 | `xml_attribute::operator=(double)` | 13 | 73 | 5 |  |
| 104 | `xml_attribute::operator=(string_view_t)` | 11 | 70 | 5 |  |
| 105 | `xml_attribute::operator=(const char_t *)` | 9 | 70 | 5 |  |
| 106 | `xml_node::children(const char_t *) const` | 3 | 17 | 5 |  |
| 107 | `xpath_node::operator void (*)(pugi::xpath_node ***)() const` | 1 | 5 | 5 |  |
| 108 | `xml_text::set(float, int)` | 20 | 144 | 4 |  |
| 109 | `xml_text::set(double, int)` | 20 | 144 | 4 |  |
| 110 | `xml_text::set(const char_t *, size_t)` | 16 | 141 | 4 |  |
| 111 | `xml_attribute::set_value(float, int)` | 12 | 72 | 4 |  |
| 112 | `xml_attribute::set_value(double, int)` | 12 | 72 | 4 |  |
| 113 | `xml_attribute::set_value(const char_t *, size_t)` | 8 | 69 | 4 |  |
| 114 | `xml_attribute::set_name(const char_t *, size_t)` | 8 | 69 | 4 |  |
| 115 | `xpath_variable_set::operator=(const xpath_variable_set &)` | 12 | 66 | 4 |  |
| 116 | `xpath_variable_set::set(const char_t *, const char_t *)` | 3 | 13 | 4 |  |
| 117 | `xpath_variable_set::set(const char_t *, const xpath_node_set &)` | 3 | 12 | 4 |  |
| 118 | `xpath_variable_set::set(const char_t *, double)` | 2 | 8 | 4 |  |
| 119 | `xpath_variable_set::set(const char_t *, bool)` | 2 | 8 | 4 |  |
| 120 | `xpath_node_set::xpath_node_set(xpath_node_set &&) noexcept` | 5 | 8 | 4 |  |
| 121 | `xml_named_node_iterator::xml_named_node_iterator(const xml_node &, const char_t *)` | 3 | 8 | 4 |  |
| 122 | `xpath_variable_set::xpath_variable_set(xpath_variable_set &&) noexcept` | 1 | 4 | 4 |  |
| 123 | `xpath_variable_set::operator=(xpath_variable_set &&) noexcept` | 1 | 4 | 4 |  |
| 124 | `xpath_query::return_type() const` | 1 | 4 | 4 |  |
| 125 | `xpath_parse_result::description() const` | 1 | 4 | 4 |  |
| 126 | `xpath_node_set::xpath_node_set(const xpath_node_set &)` | 1 | 4 | 4 |  |
| 127 | `xml_node::next_sibling() const` | 1 | 4 | 4 |  |
| 128 | `xml_node::first_child() const` | 1 | 4 | 4 |  |
| 129 | `xml_text::operator void (*)(pugi::xml_text ***)() const` | 3 | 25 | 3 |  |
| 130 | `xml_node_iterator::xml_node_iterator(const xml_node &)` | 3 | 7 | 3 |  |
| 131 | `xpath_query::operator void (*)(pugi::xpath_query ***)() const` | 1 | 3 | 3 |  |
| 132 | `xpath_node_set::operator[](size_t) const` | 3 | 3 | 3 |  |
| 133 | `xpath_node::operator!() const` | 1 | 3 | 3 |  |
| 134 | `xml_object_range::xml_object_range(xml_node_iterator, xml_node_iterator)` | 3 | 3 | 3 |  |
| 135 | `xml_object_range::xml_object_range(xml_named_node_iterator, xml_named_node_iterator)` | 3 | 3 | 3 |  |
| 136 | `xml_object_range::xml_object_range(xml_attribute_iterator, xml_attribute_iterator)` | 4 | 3 | 3 |  |
| 137 | `xml_node_iterator::operator==(const xml_node_iterator &) const` | 1 | 3 | 3 |  |
| 138 | `xml_node_iterator::operator++(int)` | 7 | 3 | 3 |  |
| 139 | `xml_node_iterator::operator!=(const xml_node_iterator &) const` | 1 | 3 | 3 |  |
| 140 | `xml_node::text() const` | 2 | 3 | 3 |  |
| 141 | `xml_named_node_iterator::operator==(const xml_named_node_iterator &) const` | 1 | 3 | 3 |  |
| 142 | `xml_named_node_iterator::operator!=(const xml_named_node_iterator &) const` | 1 | 3 | 3 |  |
| 143 | `xml_attribute_iterator::xml_attribute_iterator(const xml_attribute &, const xml_node &)` | 3 | 3 | 3 |  |
| 144 | `xml_attribute_iterator::operator==(const xml_attribute_iterator &) const` | 1 | 3 | 3 |  |
| 145 | `xml_attribute_iterator::operator++(int)` | 9 | 3 | 3 |  |
| 146 | `xml_attribute_iterator::operator!=(const xml_attribute_iterator &) const` | 1 | 3 | 3 |  |
| 147 | `xml_tree_walker::xml_tree_walker()` | 1 | 2 | 2 |  |
| 148 | `xml_node_iterator::operator->() const` | 2 | 2 | 2 |  |
| 149 | `xml_node_iterator::operator*() const` | 2 | 2 | 2 |  |
| 150 | `xml_named_node_iterator::operator->() const` | 2 | 2 | 2 |  |
| 151 | `xml_named_node_iterator::operator*() const` | 2 | 2 | 2 |  |
| 152 | `xml_document::load(const char_t *, unsigned int)` | 2 | 2 | 2 |  |
| 153 | `xml_attribute_iterator::operator->() const` | 2 | 2 | 2 |  |
| 154 | `xml_attribute_iterator::operator*() const` | 2 | 2 | 2 |  |
| 155 | `xml_document::save(std::basic_ostream<char> &, const char_t *, unsigned int, xml_encoding) const` | 47 | 506 | 1 |  |
| 156 | `xml_node::print(std::basic_ostream<wchar_t> &, const char_t *, unsigned int, unsigned int) const` | 46 | 484 | 1 |  |
| 157 | `xml_node::insert_child_before(const char_t *, const xml_node &)` | 14 | 121 | 1 |  |
| 158 | `xml_node::insert_child_after(const char_t *, const xml_node &)` | 14 | 121 | 1 |  |
| 159 | `xml_node::prepend_child(const char_t *)` | 14 | 116 | 1 |  |
| 160 | `xml_document::reset(const xml_document &)` | 12 | 107 | 1 |  |
| 161 | `as_wide(const std::basic_string<char> &)` | 20 | 88 | 1 |  |
| 162 | `xml_node::remove_child(const char_t *)` | 11 | 79 | 1 |  |
| 163 | `xml_node::remove_attribute(const char_t *)` | 9 | 56 | 1 |  |
| 164 | `xml_document::xml_document(xml_document &&) noexcept` | 3 | 26 | 1 |  |
| 165 | `xml_text::operator!() const` | 3 | 23 | 1 |  |
| 166 | `xml_text::empty() const` | 3 | 23 | 1 |  |
| 167 | `xml_text::data() const` | 3 | 23 | 1 |  |
| 168 | `as_utf8(const std::basic_string<wchar_t> &)` | 18 | 9 | 1 |  |
| 169 | `xpath_variable_set::get(const char_t *) const` | 1 | 1 | 1 |  |
| 170 | `xpath_query::xpath_query(xpath_query &&) noexcept` | 3 | 1 | 1 |  |
| 171 | `xpath_query::xpath_query()` | 1 | 1 | 1 |  |
| 172 | `xpath_query::result() const` | 1 | 1 | 1 |  |
| 173 | `xpath_query::operator!() const` | 1 | 1 | 1 |  |
| 174 | `xpath_parse_result::operator bool() const` | 1 | 1 | 1 |  |
| 175 | `xpath_node_set::first() const` | 1 | 1 | 1 |  |
| 176 | `xpath_node_set::empty() const` | 1 | 1 | 1 |  |
| 177 | `xpath_exception::what() const noexcept` | 1 | 1 | 1 |  |
| 178 | `xpath_exception::result() const` | 1 | 1 | 1 |  |
| 179 | `xml_writer_file::write(const void *, size_t)` | 2 | 1 | 1 |  |
| 180 | `xml_text::xml_text()` | 1 | 1 | 1 |  |
| 181 | `xml_node_iterator::xml_node_iterator()` | 1 | 1 | 1 |  |
| 182 | `xml_node::select_single_node(const xpath_query &) const` | 1 | 1 | 1 |  |
| 183 | `xml_node::select_single_node(const char_t *, xpath_variable_set *) const` | 1 | 1 | 1 |  |
| 184 | `xml_node::select_nodes(const xpath_query &) const` | 1 | 1 | 1 |  |
| 185 | `xml_node::select_nodes(const char_t *, xpath_variable_set *) const` | 1 | 1 | 1 |  |
| 186 | `xml_node::select_node(const xpath_query &) const` | 1 | 1 | 1 |  |
| 187 | `xml_node::select_node(const char_t *, xpath_variable_set *) const` | 1 | 1 | 1 |  |
| 188 | `xml_node::operator>=(const xml_node &) const` | 1 | 1 | 1 |  |
| 189 | `xml_node::operator>(const xml_node &) const` | 1 | 1 | 1 |  |
| 190 | `xml_node::operator<=(const xml_node &) const` | 1 | 1 | 1 |  |
| 191 | `xml_node::hash_value() const` | 1 | 1 | 1 |  |
| 192 | `xml_node::empty() const` | 1 | 1 | 1 |  |
| 193 | `xml_named_node_iterator::xml_named_node_iterator()` | 1 | 1 | 1 |  |
| 194 | `xml_document::load_buffer_inplace_own(void *, size_t, unsigned int, xml_encoding)` | 1 | 1 | 1 |  |
| 195 | `xml_document::load_buffer_inplace(void *, size_t, unsigned int, xml_encoding)` | 1 | 1 | 1 |  |
| 196 | `xml_attribute_iterator::xml_attribute_iterator()` | 1 | 1 | 1 |  |
| 197 | `xml_attribute::operator>=(const xml_attribute &) const` | 1 | 1 | 1 |  |
| 198 | `xml_attribute::operator>(const xml_attribute &) const` | 1 | 1 | 1 |  |
| 199 | `xml_attribute::operator<=(const xml_attribute &) const` | 1 | 1 | 1 |  |
| 200 | `xml_attribute::operator<(const xml_attribute &) const` | 1 | 1 | 1 |  |
| 201 | `xml_attribute::hash_value() const` | 1 | 1 | 1 |  |
| 202 | `set_memory_management_functions(allocation_function, deallocation_function)` | 1 | 1 | 1 |  |
| 203 | `get_memory_deallocation_function()` | 1 | 1 | 1 |  |
| 204 | `get_memory_allocation_function()` | 1 | 1 | 1 |  |
| 205 | `xml_document::save(xml_writer &, const char_t *, unsigned int, xml_encoding) const` | 44 | 503 | 0 |  |
| 206 | `xml_node::print(xml_writer &, const char_t *, unsigned int, xml_encoding, unsigned int) const` | 43 | 481 | 0 |  |
| 207 | `xml_text::set(bool)` | 17 | 150 | 0 |  |
| 208 | `xml_text::set(unsigned long)` | 18 | 149 | 0 |  |
| 209 | `xml_text::set(unsigned long long)` | 18 | 149 | 0 |  |
| 210 | `xml_text::set(unsigned int)` | 18 | 149 | 0 |  |
| 211 | `xml_text::set(long)` | 18 | 149 | 0 |  |
| 212 | `xml_text::set(long long)` | 18 | 149 | 0 |  |
| 213 | `xml_text::set(int)` | 18 | 149 | 0 |  |
| 214 | `xml_text::set(float)` | 20 | 144 | 0 |  |
| 215 | `xml_text::set(double)` | 20 | 144 | 0 |  |
| 216 | `xml_text::set(string_view_t)` | 18 | 141 | 0 |  |
| 217 | `xml_text::set(const char_t *)` | 16 | 141 | 0 |  |
| 218 | `xml_node::append_child(string_view_t)` | 16 | 123 | 0 |  |
| 219 | `xml_node::insert_child_before(xml_node_type, const xml_node &)` | 13 | 120 | 0 |  |
| 220 | `xml_node::insert_child_after(xml_node_type, const xml_node &)` | 13 | 120 | 0 |  |
| 221 | `xml_node::prepend_child(xml_node_type)` | 13 | 115 | 0 |  |
| 222 | `xml_node::append_child(const char_t *)` | 13 | 112 | 0 |  |
| 223 | `xml_node::append_child(xml_node_type)` | 12 | 111 | 0 |  |
| 224 | `xml_node::append_attribute(string_view_t)` | 15 | 87 | 0 |  |
| 225 | `xml_node::append_attribute(const char_t *)` | 13 | 87 | 0 |  |
| 226 | `xml_attribute::set_value(bool)` | 9 | 78 | 0 |  |
| 227 | `xml_attribute::set_value(unsigned long)` | 10 | 77 | 0 |  |
| 228 | `xml_attribute::set_value(unsigned long long)` | 10 | 77 | 0 |  |
| 229 | `xml_attribute::set_value(unsigned int)` | 10 | 77 | 0 |  |
| 230 | `xml_attribute::set_value(long)` | 10 | 77 | 0 |  |
| 231 | `xml_attribute::set_value(long long)` | 10 | 77 | 0 |  |
| 232 | `xml_attribute::set_value(int)` | 10 | 77 | 0 |  |
| 233 | `xml_node::set_name(string_view_t)` | 10 | 76 | 0 |  |
| 234 | `xml_node::set_name(const char_t *)` | 8 | 76 | 0 |  |
| 235 | `xml_attribute::set_value(float)` | 12 | 72 | 0 |  |
| 236 | `xml_attribute::set_value(double)` | 12 | 72 | 0 |  |
| 237 | `xml_attribute::set_value(string_view_t)` | 10 | 69 | 0 |  |
| 238 | `xml_attribute::set_value(const char_t *)` | 8 | 69 | 0 |  |
| 239 | `xml_attribute::set_name(string_view_t)` | 10 | 69 | 0 |  |
| 240 | `xml_attribute::set_name(const char_t *)` | 8 | 69 | 0 |  |
| 241 | `xml_node::remove_child(const xml_node &)` | 9 | 66 | 0 |  |
| 242 | `xml_node::remove_attribute(const xml_attribute &)` | 8 | 55 | 0 |  |
| 243 | `xml_named_node_iterator::operator--()` | 5 | 34 | 0 |  |
| 244 | `xml_node::child_value() const` | 2 | 24 | 0 |  |
| 245 | `xml_node::child(string_view_t) const` | 5 | 22 | 0 |  |
| 246 | `xml_node::attribute(string_view_t) const` | 5 | 22 | 0 |  |
| 247 | `xml_node_iterator::operator--()` | 4 | 18 | 0 |  |
| 248 | `xml_attribute_iterator::operator--()` | 4 | 18 | 0 |  |
| 249 | `xml_named_node_iterator::operator++()` | 4 | 14 | 0 |  |
| 250 | `xml_node::previous_sibling(const char_t *) const` | 1 | 12 | 0 |  |
| 251 | `xml_node::next_sibling(const char_t *) const` | 1 | 12 | 0 |  |
| 252 | `xml_node::child(const char_t *) const` | 1 | 12 | 0 |  |
| 253 | `xpath_variable::set(const char_t *)` | 2 | 9 | 0 |  |
| 254 | `xpath_variable::set(const xpath_node_set &)` | 2 | 8 | 0 |  |
| 255 | `xml_node::previous_sibling() const` | 1 | 7 | 0 |  |
| 256 | `xml_node::last_child() const` | 1 | 7 | 0 |  |
| 257 | `xml_node::last_attribute() const` | 1 | 7 | 0 |  |
| 258 | `xml_attribute::previous_attribute() const` | 1 | 7 | 0 |  |
| 259 | `xml_node::begin() const` | 2 | 6 | 0 |  |
| 260 | `xml_node::attributes_begin() const` | 2 | 6 | 0 |  |
| 261 | `xpath_variable::set(double)` | 1 | 4 | 0 |  |
| 262 | `xpath_variable::set(bool)` | 1 | 4 | 0 |  |
| 263 | `xpath_node_set::operator=(const xpath_node_set &)` | 1 | 4 | 0 |  |
| 264 | `xml_node::end() const` | 2 | 4 | 0 |  |
| 265 | `xml_node::attributes_end() const` | 2 | 4 | 0 |  |
| 266 | `xml_writer_stream::xml_writer_stream(std::basic_ostream<wchar_t> &)` | 2 | 2 | 0 |  |
| 267 | `xml_writer_stream::xml_writer_stream(std::basic_ostream<char> &)` | 2 | 2 | 0 |  |
| 268 | `xml_node_iterator::operator++()` | 2 | 2 | 0 |  |
| 269 | `xml_attribute_iterator::operator++()` | 2 | 2 | 0 |  |
| 270 | `xpath_node_set::size() const` | 1 | 1 | 0 |  |
| 271 | `xml_tree_walker::end(xml_node &)` | 1 | 1 | 0 |  |
| 272 | `xml_tree_walker::begin(xml_node &)` | 1 | 1 | 0 |  |
| 273 | `xml_document::load_string(const char_t *, unsigned int)` | 1 | 1 | 0 |  |
| 274 | `xml_attribute::operator!() const` | 1 | 1 | 0 |  |
| 275 | `xml_document::save_file(const wchar_t *, const char_t *, unsigned int, xml_encoding) const` | 60 | 539 | 0 | 파일 입출력 |
| 276 | `xml_document::save_file(const char *, const char_t *, unsigned int, xml_encoding) const` | 54 | 519 | 0 | 파일 입출력 |
| 277 | `xml_document::load_file(const wchar_t *, unsigned int, xml_encoding)` | 19 | 56 | 0 | 파일 입출력 |
| 278 | `xml_document::load_file(const char *, unsigned int, xml_encoding)` | 12 | 36 | 0 | 파일 입출력 |
| 279 | `xml_writer_file::xml_writer_file(void *)` | 2 | 2 | 0 | 파일 입출력 |
| 280 | `xml_object_range::begin() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 281 | `xml_object_range::begin() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 282 | `xml_object_range::begin() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 283 | `xml_object_range::empty() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 284 | `xml_object_range::empty() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 285 | `xml_object_range::empty() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 286 | `xml_object_range::end() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 287 | `xml_object_range::end() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 288 | `xml_object_range::end() const` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
