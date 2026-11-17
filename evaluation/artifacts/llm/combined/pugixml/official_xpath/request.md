라이브러리: pugixml
하네스 파일: official_xpath.cpp

아래 제안 4개를 **모두 한 하네스에** 적용하세요.

## 제안 3
하네스가 `xml_node::attribute(const char_t *, xml_attribute &) const`를 부르지 않아 2번째 인자 `hint` 값이 들어가지 않습니다 (필드 `_attr`를 거쳐 조건에 쓰임) → 호출을 추가하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (18개)
- `xml_attribute::value() const` 5450행, 조건 `!_attr`가 퍼징 중 한 번도 '참'이 되지 않음
```
 5446  	}
 5447  
 5448  	PUGI_IMPL_FN const char_t* xml_attribute::value() const
 5449  	{
 5450> 		if (!_attr) return PUGIXML_TEXT("");
 5451  		const char_t* value = _attr->value;
 5452  		return value ? value : PUGIXML_TEXT("");
 5453  	}
 5454  
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8785행, 조건 `attr`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 8781  		}
 8782  
 8783  		xml_attribute_struct* attr = xnode.attribute().internal_object();
 8784  
 8785> 		if (attr)
 8786  		{
 8787  			if ((get_document(attr).header & xml_memory_page_contents_shared_mask) == 0)
 8788  			{
 8789  				if ((attr->header & impl::xml_memory_page_name_allocated_or_shared_mask) == 0) return attr->name;
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8787행, 조건 `(get_document(attr).header & xml_memory_page_contents_shared_mask) == 0`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 8783  		xml_attribute_struct* attr = xnode.attribute().internal_object();
 8784  
 8785  		if (attr)
 8786  		{
 8787> 			if ((get_document(attr).header & xml_memory_page_contents_shared_mask) == 0)
 8788  			{
 8789  				if ((attr->header & impl::xml_memory_page_name_allocated_or_shared_mask) == 0) return attr->name;
 8790  				if ((attr->header & impl::xml_memory_page_value_allocated_or_shared_mask) == 0) return attr->value;
 8791  			}
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8789행, 조건 `(attr->header & impl::xml_memory_page_name_allocated_or_shared_mask) == 0`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 8785  		if (attr)
 8786  		{
 8787  			if ((get_document(attr).header & xml_memory_page_contents_shared_mask) == 0)
 8788  			{
 8789> 				if ((attr->header & impl::xml_memory_page_name_allocated_or_shared_mask) == 0) return attr->name;
 8790  				if ((attr->header & impl::xml_memory_page_value_allocated_or_shared_mask) == 0) return attr->value;
 8791  			}
 8792  
 8793  			return NULL;
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8813행, 조건 `lhs.attribute()`가 퍼징 중 한 번도 '참'이 되지 않음
```
 8809  			// slow comparison
 8810  			xml_node ln = lhs.node(), rn = rhs.node();
 8811  
 8812  			// compare attributes
 8813> 			if (lhs.attribute() && rhs.attribute())
 8814  			{
 8815  				// shared parent
 8816  				if (lhs.parent() == rhs.parent())
 8817  				{
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8830행, 조건 `lhs.attribute()`가 퍼징 중 한 번도 '참'이 되지 않음
```
 8826  				// compare attribute parents
 8827  				ln = lhs.parent();
 8828  				rn = rhs.parent();
 8829  			}
 8830> 			else if (lhs.attribute())
 8831  			{
 8832  				// attributes go after the parent element
 8833  				if (lhs.parent() == rhs.node()) return false;
 8834  
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8837행, 조건 `rhs.attribute()`가 퍼징 중 한 번도 '참'이 되지 않음
```
 8833  				if (lhs.parent() == rhs.node()) return false;
 8834  
 8835  				ln = lhs.parent();
 8836  			}
 8837> 			else if (rhs.attribute())
 8838  			{
 8839  				// attributes go after the parent element
 8840  				if (rhs.parent() == lhs.node()) return true;
 8841  
```
- `xpath_query::evaluate_node_set(const xpath_node &) const` 9682행, 조건 `key`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 9678  					const void* attr = it->attribute().internal_object();
 9679  					const void* node = it->node().internal_object();
 9680  					const void* key = attr ? attr : node;
 9681  
 9682> 					if (key && hash_insert(hash_data, hash_size, key))
 9683  					{
 9684  						*write++ = *it;
 9685  					}
 9686  				}
```

## 제안 5
하네스가 `xpath_query::xpath_query(xpath_query &&) noexcept`를 부르지 않아 1번째 인자 `rhs` 값이 들어가지 않습니다 (필드 `_impl`를 거쳐 조건에 쓰임) → 호출을 추가하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (5개)
- `xpath_query::evaluate_boolean(const xpath_node &) const` 13509행, 조건 `!_impl`가 퍼징 중 한 번도 '참'이 되지 않음
```
13505  	}
13506  
13507  	PUGI_IMPL_FN bool xpath_query::evaluate_boolean(const xpath_node& n) const
13508  	{
13509> 		if (!_impl) return false;
13510  
13511  		impl::xpath_context c(n, 1, 1);
13512  		impl::xpath_stack_data sd;
13513  
```
- `xpath_query::evaluate_number(const xpath_node &) const` 13530행, 조건 `!_impl`가 퍼징 중 한 번도 '참'이 되지 않음
```
13526  	}
13527  
13528  	PUGI_IMPL_FN double xpath_query::evaluate_number(const xpath_node& n) const
13529  	{
13530> 		if (!_impl) return impl::gen_nan();
13531  
13532  		impl::xpath_context c(n, 1, 1);
13533  		impl::xpath_stack_data sd;
13534  
```
- `xpath_query::evaluate_string(const xpath_node &) const` 13552행, 조건 `!_impl`가 퍼징 중 한 번도 '참'이 되지 않음
```
13548  
13549  #ifndef PUGIXML_NO_STL
13550  	PUGI_IMPL_FN string_t xpath_query::evaluate_string(const xpath_node& n) const
13551  	{
13552> 		if (!_impl) return string_t();
13553  
13554  		impl::xpath_context c(n, 1, 1);
13555  		impl::xpath_stack_data sd;
13556  
```
- `xpath_query::evaluate_node_set(const xpath_node &) const` 13605행, 조건 `!root`가 퍼징 중 한 번도 '참'이 되지 않음
```
13601  
13602  	PUGI_IMPL_FN xpath_node_set xpath_query::evaluate_node_set(const xpath_node& n) const
13603  	{
13604  		impl::xpath_ast_node* root = impl::evaluate_node_set_prepare(static_cast<impl::xpath_query_impl*>(_impl));
13605> 		if (!root) return xpath_node_set();
13606  
13607  		impl::xpath_context c(n, 1, 1);
13608  		impl::xpath_stack_data sd;
13609  
```
- `xpath_query::evaluate_node(const xpath_node &) const` 13627행, 조건 `!root`가 퍼징 중 한 번도 '참'이 되지 않음
```
13623  
13624  	PUGI_IMPL_FN xpath_node xpath_query::evaluate_node(const xpath_node& n) const
13625  	{
13626  		impl::xpath_ast_node* root = impl::evaluate_node_set_prepare(static_cast<impl::xpath_query_impl*>(_impl));
13627> 		if (!root) return xpath_node();
13628  
13629  		impl::xpath_context c(n, 1, 1);
13630  		impl::xpath_stack_data sd;
13631  
```

## 제안 6
하네스가 `xpath_variable::set(const char_t *)`를 부르지 않아 1번째 인자 `value` 값이 들어가지 않습니다 (필드 `value`를 거쳐 조건에 쓰임) → 호출을 추가하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `xpath_variable::get_string() const` 13181행, 조건 `value`가 퍼징 중 한 번도 '참'이 되지 않음
```
13177  
13178  	PUGI_IMPL_FN const char_t* xpath_variable::get_string() const
13179  	{
13180  		const char_t* value = (_type == xpath_type_string) ? static_cast<const impl::xpath_variable_string*>(this)->value : NULL;
13181> 		return value ? value : PUGIXML_TEXT("");
13182  	}
13183  
13184  	PUGI_IMPL_FN const xpath_node_set& xpath_variable::get_node_set() const
13185  	{
```

## 제안 9
`xml_node::xml_node(xml_node_struct *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`impl::{익명}::xpath_ast_node::step_fill`, `impl::{익명}::xpath_ast_node::step_fill`, `impl::{익명}::xpath_ast_node::step_fill`)에서만 불립니다. 내부 호출은 1번째 인자 `p`를 한 가지 방식으로만 넘기므로 (필드 `_root`를 거쳐 조건에 쓰임) → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (16개)
- `xml_node::type() const` 5773행, 조건 `_root`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 5769  	}
 5770  
 5771  	PUGI_IMPL_FN xml_node_type xml_node::type() const
 5772  	{
 5773> 		return _root ? PUGI_IMPL_NODETYPE(_root) : node_null;
 5774  	}
 5775  
 5776  	PUGI_IMPL_FN const char_t* xml_node::value() const
 5777  	{
```
- `xml_node::value() const` 5778행, 조건 `!_root`가 퍼징 중 한 번도 '참'이 되지 않음
```
 5774  	}
 5775  
 5776  	PUGI_IMPL_FN const char_t* xml_node::value() const
 5777  	{
 5778> 		if (!_root) return PUGIXML_TEXT("");
 5779  		const char_t* value = _root->value;
 5780  		return value ? value : PUGIXML_TEXT("");
 5781  	}
 5782  
```
- `xml_node::attribute(const char_t *) const` 5799행, 조건 `!_root`가 퍼징 중 한 번도 '참'이 되지 않음
```
 5795  	}
 5796  
 5797  	PUGI_IMPL_FN xml_attribute xml_node::attribute(const char_t* name_) const
 5798  	{
 5799> 		if (!_root) return xml_attribute();
 5800  
 5801  		for (xml_attribute_struct* i = _root->first_attribute; i; i = i->next_attribute)
 5802  		{
 5803  			const char_t* iname = i->name;
```
- `xml_node::attribute(const char_t *) const` 5801행, 조건 `i`가 퍼징 중 한 번도 '참'이 되지 않음
```
 5797  	PUGI_IMPL_FN xml_attribute xml_node::attribute(const char_t* name_) const
 5798  	{
 5799  		if (!_root) return xml_attribute();
 5800  
 5801> 		for (xml_attribute_struct* i = _root->first_attribute; i; i = i->next_attribute)
 5802  		{
 5803  			const char_t* iname = i->name;
 5804  			if (iname && impl::strequal(name_, iname))
 5805  				return xml_attribute(i);
```
- `xml_node::root() const` 5996행, 조건 `_root`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 5992  	}
 5993  
 5994  	PUGI_IMPL_FN xml_node xml_node::root() const
 5995  	{
 5996> 		return _root ? xml_node(&impl::get_document(_root)) : xml_node();
 5997  	}
 5998  
 5999  	PUGI_IMPL_FN xml_text xml_node::text() const
 6000  	{
```
- `xml_document::reset()` 7680행, 조건 `extra`가 퍼징 중 한 번도 '참'이 되지 않음
```
 7676  			_buffer = NULL;
 7677  		}
 7678  
 7679  		// destroy extra buffers (note: no need to destroy linked list nodes, they're allocated using document allocator)
 7680> 		for (impl::xml_extra_buffer* extra = static_cast<impl::xml_document_struct*>(_root)->extra_buffers; extra; extra = extra->next)
 7681  		{
 7682  			if (extra->buffer) impl::xml_memory::deallocate(extra->buffer);
 7683  		}
 7684  
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8774행, 조건 `(get_document(node).header & xml_memory_page_contents_shared_mask) == 0`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 8770  		xml_node_struct* node = xnode.node().internal_object();
 8771  
 8772  		if (node)
 8773  		{
 8774> 			if ((get_document(node).header & xml_memory_page_contents_shared_mask) == 0)
 8775  			{
 8776  				if (node->name && (node->header & impl::xml_memory_page_name_allocated_or_shared_mask) == 0) return node->name;
 8777  				if (node->value && (node->header & impl::xml_memory_page_value_allocated_or_shared_mask) == 0) return node->value;
 8778  			}
```
- `xpath_query::evaluate_node(const xpath_node &) const` 8776행, 조건 `(node->header & impl::xml_memory_page_name_allocated_or_shared_mask) == 0`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 8772  		if (node)
 8773  		{
 8774  			if ((get_document(node).header & xml_memory_page_contents_shared_mask) == 0)
 8775  			{
 8776> 				if (node->name && (node->header & impl::xml_memory_page_name_allocated_or_shared_mask) == 0) return node->name;
 8777  				if (node->value && (node->header & impl::xml_memory_page_value_allocated_or_shared_mask) == 0) return node->value;
 8778  			}
 8779  
 8780  			return NULL;
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: pugixml 저장소 tests/fuzz_xpath.cpp (커밋 f0a3faa) 그대로.
   2  #include "../src/pugixml.hpp"
   3  #include "fuzzer/FuzzedDataProvider.h"
   4  
   5  #include <stdint.h>
   6  #include <string.h>
   7  #include <string>
   8  
   9  extern "C" int LLVMFuzzerTestOneInput(const uint8_t* Data, size_t Size)
  10  {
  11  	FuzzedDataProvider fdp(Data, Size);
  12  	std::string text = fdp.ConsumeRandomLengthString(1024);
  13  
  14  #ifndef PUGIXML_NO_EXCEPTIONS
  15  	try
  16  #endif
  17  	{
  18  		pugi::xpath_variable_set vars;
  19  		size_t var_count = fdp.ConsumeIntegralInRange<size_t>(0, 50);
  20  		std::vector<std::string> var_name_storage;
  21  		for (size_t i = 0; i < var_count; ++i)
  22  		{
  23  			var_name_storage.push_back(fdp.ConsumeRandomLengthString(128));
  24  
  25  			const int xpath_value_type_count = pugi::xpath_type_boolean + 1;
  26  			pugi::xpath_value_type value_type = static_cast<pugi::xpath_value_type>(fdp.ConsumeIntegralInRange(0, xpath_value_type_count));
  27  			vars.add(var_name_storage.back().c_str(), value_type);
  28  		}
  29  		pugi::xpath_query q(text.c_str(), &vars);
  30  
  31  		std::vector<uint8_t> xml_buffer = fdp.ConsumeBytes<uint8_t>(fdp.ConsumeIntegralInRange(0, 1024));
  32  		pugi::xml_document doc;
  33  		doc.load_buffer(xml_buffer.data(), xml_buffer.size(), pugi::parse_full);
  34  
  35  		q.evaluate_boolean(doc);
  36  		q.evaluate_number(doc);
  37  		q.evaluate_string(doc);
  38  		q.evaluate_node(doc);
  39  		q.evaluate_node_set(doc);
  40  	}
  41  #ifndef PUGIXML_NO_EXCEPTIONS
  42  	catch (pugi::xpath_exception&)
  43  	{
  44  	}
  45  #endif
  46  	return 0;
  47  }
```