# 호출 안 함 API 추가 — pugixml/_union

- 모델: `claude-sonnet-5-5`
- 수정 전: 공개 API 349개 중 호출 안 함 288개, 라인 44.07% · 분기 43.39%
- 추가를 요청한 API 10개: `xml_document::save`, `xml_text::operator=`, `xml_document::load`, `xml_document::load`, `xml_text::as_ullong`, `xml_text::as_uint`, `xpath_node_set::sort`, `xml_node::remove_child`, `xpath_variable_set::xpath_variable_set`, `xml_node::insert_copy_before`

| 시도 | 결과 | 실행된 API | 호출 안 함 | 라인 | 분기 | 사라진 API | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | 통과 | 10/10 | 249 | 49.01% | 44.3% | 0 | - | 2422/13917 |

수정 전 수치는 진단 때(기본 120초 × 1회), 시도별 수치는 검사 퍼징(짧음)의 중앙값이라 길이가 다릅니다. 정식 비교는 같은 조건의 긴 실험으로 하세요.

**채택: 시도 1** → `harnesses/pugixml/gapfuzz_ops.cpp`. 사람이 읽고 쓰세요.

```diff
--- 수정 전
+++ 시도 1
@@ -0,0 +1,359 @@
+#include "pugixml.hpp"
+
+#include <stdint.h>
+#include <stddef.h>
+
+#include <algorithm>
+#include <exception>
+#include <istream>
+#include <ostream>
+#include <sstream>
+#include <string>
+
+namespace
+{
+	typedef std::basic_string<pugi::char_t> str_t;
+
+	// 입력 한도와 반복 한도
+	const size_t kMaxInput = 64 * 1024;
+	const size_t kMaxOps = 16;
+	const size_t kOpBytes = 9; // 연산 코드 1바이트 + 인자 8바이트
+	const size_t kHeader = 3;  // 파싱 옵션, 저장 플래그, 연산 개수
+
+	// 바이트 배열 일부를 char_t 문자열로 복사 (char/wchar 모드 모두 동작)
+	str_t make_slice(const uint8_t* p, size_t n, unsigned off, unsigned len, unsigned maxlen)
+	{
+		str_t s;
+		if (n == 0) return s;
+		size_t o = off % (n + 1);
+		size_t l = std::min<size_t>(len % (maxlen + 1), n - o);
+		for (size_t i = 0; i < l; ++i) s.push_back(static_cast<pugi::char_t>(p[o + i]));
+		return s;
+	}
+
+	// 문서 순서(깊이 우선)로 idx번째 노드를 고른다. 단계 수에 상한을 둔다.
+	pugi::xml_node pick_node(const pugi::xml_document& doc, unsigned idx)
+	{
+		pugi::xml_node n = doc.first_child();
+		unsigned steps = idx % 4096;
+		for (unsigned i = 0; i < steps && n; ++i)
+		{
+			if (n.first_child())
+			{
+				n = n.first_child();
+			}
+			else
+			{
+				while (n && !n.next_sibling()) n = n.parent();
+				if (n) n = n.next_sibling();
+			}
+		}
+		return n;
+	}
+
+	// 저장 출력 크기 추정용 워커
+	struct CostWalker : pugi::xml_tree_walker
+	{
+		size_t cost;
+		size_t ilen;
+		CostWalker(size_t l) : cost(0), ilen(l) {}
+		bool for_each(pugi::xml_node&)
+		{
+			cost += static_cast<size_t>(depth()) * ilen + 1;
+			return cost < 2000000;
+		}
+	};
+
+	// 노드 개수 제한용 워커
+	struct CountWalker : pugi::xml_tree_walker
+	{
+		int n;
+		CountWalker() : n(0) {}
+		bool for_each(pugi::xml_node&) { return ++n < 2000; }
+	};
+
+	const pugi::xml_encoding kEncodings[] = {
+		pugi::encoding_auto, pugi::encoding_utf8, pugi::encoding_utf16_le, pugi::encoding_utf16_be,
+		pugi::encoding_utf16, pugi::encoding_utf32_le, pugi::encoding_utf32_be, pugi::encoding_utf32,
+		pugi::encoding_wchar, pugi::encoding_latin1};
+
+	unsigned parse_opts_from(uint8_t b)
+	{
+		unsigned o = pugi::parse_minimal;
+		if (b & 0x01) o |= pugi::parse_pi;
+		if (b & 0x02) o |= pugi::parse_comments;
+		if (b & 0x04) o |= pugi::parse_cdata;
+		if (b & 0x08) o |= pugi::parse_ws_pcdata;
+		if (b & 0x10) o |= pugi::parse_escapes;
+		if (b & 0x20) o |= pugi::parse_eol;
+		if (b & 0x40) o |= pugi::parse_wconv_attribute;
+		if (b & 0x80) o |= pugi::parse_declaration;
+		return o;
+	}
+
+	unsigned save_flags_from(uint8_t b)
+	{
+		unsigned f = 0;
+		if (b & 0x01) f |= pugi::format_indent;
+		if (b & 0x02) f |= pugi::format_raw;
+		if (b & 0x04) f |= pugi::format_no_declaration;
+		if (b & 0x08) f |= pugi::format_no_escapes;
+		if (b & 0x10) f |= pugi::format_no_empty_element_tags;
+		if (b & 0x20) f |= pugi::format_skip_control_chars;
+		if (b & 0x40) f |= pugi::format_attribute_single_quote;
+		if (b & 0x80) f |= pugi::format_write_bom;
+		return f;
+	}
+
+	// 파싱 실패 시 문서를 비우고 더 쓰지 않는다
+	void load_or_reset(pugi::xml_document& doc, const pugi::xml_parse_result& r)
+	{
+		if (!r) doc.reset();
+	}
+}
+
+extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
+{
+	if (size > kMaxInput) size = kMaxInput;
+	if (size < kHeader + kOpBytes) return 0;
+
+	const unsigned parse_opts = parse_opts_from(data[0]);
+	const unsigned save_flags = save_flags_from(data[1]);
+	size_t nops = data[2] % kMaxOps + 1;
+	nops = std::min(nops, (size - kHeader) / kOpBytes);
+	if (nops == 0) return 0;
+
+	const uint8_t* ops = data + kHeader;
+	const size_t header = kHeader + nops * kOpBytes;
+	const uint8_t* payload = data + header;
+	const size_t plen = size - header;
+
+	volatile unsigned long long sink = 0;
+
+	try
+	{
+		pugi::xml_document doc;
+
+		// 준비: 입력 본문을 문서로 파싱
+		{
+			pugi::xml_parse_result r = doc.load_buffer(payload, plen, parse_opts);
+			load_or_reset(doc, r);
+		}
+
+		for (size_t i = 0; i < nops; ++i)
+		{
+			const uint8_t* op = ops + i * kOpBytes;
+			const uint8_t* a = op + 1;
+			const unsigned arg16 = a[0] | (a[1] << 8);
+
+			switch (op[0] % 9)
+			{
+			case 0:
+			{
+				// [gapfuzz-ops] xml_document::save(std::basic_ostream<wchar_t> &, const char_t *, unsigned int) const
+				static const pugi::char_t* const indents[] = {PUGIXML_TEXT("\t"), PUGIXML_TEXT(" "), PUGIXML_TEXT("  "), PUGIXML_TEXT("")};
+				const pugi::char_t* indent = indents[a[2] % 4];
+				size_t ilen = (a[2] % 4 == 0 || a[2] % 4 == 1) ? 1 : (a[2] % 4 == 2 ? 2 : 0);
+				unsigned flags = save_flags ^ (a[3] & (pugi::format_indent | pugi::format_raw | pugi::format_no_declaration));
+
+				// 출력 크기 상한(1MB 미만)을 지키기 위해 비용 추정 후 초과하면 raw로 저장
+				CostWalker w(ilen);
+				doc.traverse(w);
+				if (w.cost > 100000) flags |= pugi::format_raw;
+
+				std::wostringstream os;
+				doc.save(os, indent, flags);
+				sink += os.str().size();
+				break;
+			}
+			case 1:
+			{
+				// [gapfuzz-ops] xml_document::load(std::basic_istream<char> &, unsigned int, xml_encoding)
+				size_t off = plen ? (arg16 % (plen + 1)) : 0;
+				std::string bytes(reinterpret_cast<const char*>(payload) + off, plen - off);
+				std::istringstream is(bytes);
+				pugi::xml_encoding enc = kEncodings[a[2] % (sizeof(kEncodings) / sizeof(kEncodings[0]))];
+				unsigned o = parse_opts_from(a[3]);
+				pugi::xml_parse_result r = doc.load(is, o, enc);
+				load_or_reset(doc, r);
+				break;
+			}
+			case 2:
+			{
+				// [gapfuzz-ops] xml_document::load(std::basic_istream<wchar_t> &, unsigned int)
+				size_t off = plen ? (arg16 % (plen + 1)) : 0;
+				std::wstring ws;
+				for (size_t k = off; k < plen; ++k) ws.push_back(static_cast<wchar_t>(payload[k]));
+				std::wistringstream is(ws);
+				unsigned o = parse_opts_from(a[3]);
+				pugi::xml_parse_result r = doc.load(is, o);
+				load_or_reset(doc, r);
+				break;
+			}
+			case 3:
+			{
+				// [gapfuzz-ops] xml_text::operator=(bool)
+				pugi::xml_node n = pick_node(doc, arg16);
+				if (n)
+				{
+					pugi::xml_text t = n.text();
+					t = ((a[2] & 1) != 0);
+					sink += t.as_bool() ? 1 : 0;
+				}
+				break;
+			}
+			case 4:
+			{
+				pugi::xml_node n = pick_node(doc, arg16);
+				if (n)
+				{
+					// 준비: 절반은 입력 조각을 텍스트로 넣어 숫자 변환 경로를 다양하게 만든다
+					if (a[2] & 1)
+					{
+						str_t s = make_slice(payload, plen, a[3] | (a[4] << 8), a[5], 40);
+						n.text().set(s.c_str());
+					}
+					unsigned def32 = a[4] | (a[5] << 8) | (a[6] << 16) | (static_cast<unsigned>(a[7]) << 24);
+					unsigned long long def64 = (static_cast<unsigned long long>(def32) << 32) | def32;
+
+					// [gapfuzz-ops] xml_text::as_ullong(unsigned long long) const
+					sink += n.text().as_ullong(def64);
+
+					// [gapfuzz-ops] xml_text::as_uint(unsigned int) const
+					sink += n.text().as_uint(def32);
+				}
+				break;
+			}
+			case 5:
+			{
+				// 컨텍스트 노드와 쿼리를 입력에서 고른다
+				pugi::xml_node ctx = pick_node(doc, arg16);
+				if (!ctx) ctx = doc;
+				str_t q = make_slice(payload, plen, a[2] | (a[3] << 8), a[4], 96);
+
+				pugi::xpath_node_set ns;
+				try
+				{
+					pugi::xpath_query query(q.c_str());
+					if (query.return_type() == pugi::xpath_type_node_set)
+						ns = query.evaluate_node_set(pugi::xpath_node(ctx));
+				}
+				catch (const pugi::xpath_exception&)
+				{
+					ns = doc.select_nodes(PUGIXML_TEXT("//node()"));
+				}
+
+				// [gapfuzz-ops] xpath_node_set::sort(bool)
+				ns.sort((a[5] & 1) != 0);
+				sink += ns.size();
+				if (!ns.empty()) sink += ns.first().node() ? 1 : 0;
+				break;
+			}
+			case 6:
+			{
+#ifdef PUGIXML_HAS_STRING_VIEW
+				pugi::xml_node n = pick_node(doc, arg16);
+				if (n)
+				{
+					// 절반은 실제 자식 이름을 사용해 삭제 경로에 도달하게 한다
+					str_t name;
+					if (a[2] & 1)
+						name = n.first_child() ? str_t(n.first_child().name()) : str_t();
+					else
+						name = make_slice(payload, plen, a[3] | (a[4] << 8), a[5], 32);
+
+					// [gapfuzz-ops] xml_node::remove_child(string_view_t)
+					pugi::string_view_t view(name.data(), name.size());
+					sink += n.remove_child(view) ? 1 : 0;
+				}
+#endif
+				break;
+			}
+			case 7:
+			{
+				// 준비: 변수 집합 구성 (이름과 타입이 유효할 때만 사용)
+				pugi::xpath_variable_set vars;
+				pugi::xpath_variable* v0 = vars.add(PUGIXML_TEXT("v0"), pugi::xpath_type_boolean);
+				pugi::xpath_variable* v1 = vars.add(PUGIXML_TEXT("v1"), pugi::xpath_type_number);
+				pugi::xpath_variable* v2 = vars.add(PUGIXML_TEXT("v2"), pugi::xpath_type_string);
+				pugi::xpath_variable* v3 = vars.add(PUGIXML_TEXT("v3"), pugi::xpath_type_node_set);
+				if (!v0 || !v1 || !v2 || !v3) break;
+
+				str_t sv = make_slice(payload, plen, a[2] | (a[3] << 8), a[4], 32);
+				v0->set((a[5] & 1) != 0);
+				v1->set(static_cast<double>(static_cast<int>(a[6]) - 128) * a[7]);
+				v2->set(sv.c_str());
+				pugi::xpath_node_set all = doc.select_nodes(PUGIXML_TEXT("//*"));
+				v3->set(all);
+
+				// [gapfuzz-ops] xpath_variable_set::xpath_variable_set(const xpath_variable_set &)
+				pugi::xpath_variable_set copy(vars);
+
+				// 복사본에서 값을 다시 바꿔도 원본은 영향을 받지 않아야 한다
+				copy.set(PUGIXML_TEXT("v1"), static_cast<double>(a[6]));
+
+				static const pugi::char_t* const exprs[] = {
+					PUGIXML_TEXT("$v0"), PUGIXML_TEXT("$v1 + 1"), PUGIXML_TEXT("string-length($v2)"),
+					PUGIXML_TEXT("count($v3)"), PUGIXML_TEXT("//*[name()=$v2]"), PUGIXML_TEXT("$v3[1]")};
+				const pugi::char_t* e = exprs[a[5] % (sizeof(exprs) / sizeof(exprs[0]))];
+				try
+				{
+					pugi::xpath_query query(e, &copy);
+					switch (query.return_type())
+					{
+					case pugi::xpath_type_node_set:
+						sink += query.evaluate_node_set(doc).size();
+						break;
+					case pugi::xpath_type_number:
+						sink += static_cast<unsigned long long>(query.evaluate_number(doc) > 0);
+						break;
+					case pugi::xpath_type_string:
+					{
+						pugi::char_t buf[256];
+						sink += query.evaluate_string(buf, 256, doc);
+						break;
+					}
+					default:
+						sink += query.evaluate_boolean(doc) ? 1 : 0;
+						break;
+					}
+				}
+				catch (const pugi::xpath_exception&)
+				{
+				}
+				break;
+			}
+			case 8:
+			{
+				pugi::xml_node proto = pick_node(doc, arg16);
+				pugi::xml_node where = pick_node(doc, a[2] | (a[3] << 8));
+				if (!proto || !where) break;
+				pugi::xml_node parent = where.parent();
+				if (!parent) break;
+
+				// 자기 조상을 자기 안에 복사하면 끝없이 커질 수 있으므로 제외
+				bool bad = (proto.type() == pugi::node_document);
+				for (pugi::xml_node p = parent; p && !bad; p = p.parent())
+					if (p == proto) bad = true;
+				if (bad) break;
+
+				// 복사 대상 크기 제한 (문서가 폭발적으로 커지는 것을 방지)
+				CountWalker cw;
+				proto.traverse(cw);
+				if (cw.n >= 2000) break;
+
+				// [gapfuzz-ops] xml_node::insert_copy_before(const xml_node &, const xml_node &)
+				pugi::xml_node res = parent.insert_copy_before(proto, where);
+				if (res) sink += static_cast<unsigned>(res.type());
+				break;
+			}
+			}
+		}
+	}
+	catch (const std::exception&)
+	{
+		// 라이브러리가 던지는 예외(xpath_exception, bad_alloc 등)는 무시
+	}
+
+	return 0;
+}
```
