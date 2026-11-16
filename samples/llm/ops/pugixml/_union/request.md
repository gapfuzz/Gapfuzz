라이브러리: pugixml
OSS-Fuzz 하네스 2개(official, official_xpath)의 커버리지를 모두 합쳐도, 공개 API 349개 중 288개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `xml_document::save(std::basic_ostream<wchar_t> &, const char_t *, unsigned int) const` — 새로 실행될 수 있는 코드 영역 506개
```
		void save(std::basic_ostream<wchar_t>& stream, const char_t* indent = PUGIXML_TEXT("\t"), unsigned int flags = format_default) const;
```

### 2. `xml_text::operator=(bool)` — 새로 실행될 수 있는 코드 영역 151개
```
		xml_text& operator=(bool rhs);
```

### 3. `xml_document::load(std::basic_istream<wchar_t> &, unsigned int)` — 새로 실행될 수 있는 코드 영역 76개
```
		xml_parse_result load(std::basic_istream<wchar_t>& stream, unsigned int options = parse_default);
```

### 4. `xml_document::load(std::basic_istream<char> &, unsigned int, xml_encoding)` — 새로 실행될 수 있는 코드 영역 72개
```
		// Load document from stream.
		xml_parse_result load(std::basic_istream<char>& stream, unsigned int options = parse_default, xml_encoding encoding = encoding_auto);
```

### 5. `xml_text::as_ullong(unsigned long long) const` — 새로 실행될 수 있는 코드 영역 71개
```
		unsigned long long as_ullong(unsigned long long def = 0) const;
```

### 6. `xml_text::as_uint(unsigned int) const` — 새로 실행될 수 있는 코드 영역 71개
```
		unsigned int as_uint(unsigned int def = 0) const;
```

### 7. `xpath_node_set::sort(bool)` — 새로 실행될 수 있는 코드 영역 70개
```
		// Sort the collection in ascending/descending order by document order
		void sort(bool reverse = false);
```

### 8. `xml_node::remove_child(string_view_t)` — 새로 실행될 수 있는 코드 영역 67개
```
		bool remove_child(string_view_t name);
```

### 9. `xpath_variable_set::xpath_variable_set(const xpath_variable_set &)` — 새로 실행될 수 있는 코드 영역 66개
```
		// Copy constructor/assignment operator
		xpath_variable_set(const xpath_variable_set& rhs);
```

### 10. `xml_node::insert_copy_before(const xml_node &, const xml_node &)` — 새로 실행될 수 있는 코드 영역 56개
```
		xml_node insert_copy_before(const xml_node& proto, const xml_node& node);
```

## 참고: 기존 하네스 official.cpp (고치지 마세요. include와 작성 방식만 참고)
```
#include "pugixml.hpp"

#include <stdint.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size)
{
    pugi::xml_document doc;

	doc.load_buffer(Data, Size);
	doc.load_buffer(Data, Size, pugi::parse_minimal);
	doc.load_buffer(Data, Size, pugi::parse_full);

	return 0;
}

```