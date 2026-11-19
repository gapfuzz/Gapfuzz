# 제안 검증 — pugixml-official-r1 → pugixml-official_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | xml_document::load_buffer · encoding | 적용 | 5 | 4 |
| 2 | xml_node::xml_node · p | 미적용 | 1 | 0 |
| 3 | xml_document::load_buffer · options | 적용 | 26 | 24 |
| 4 | xml_document::load_buffer · contents | 적용 | 2 | 1 |

**적용한 제안 기준: 막혀 있던 분기 33개 중 29개가 열림**

## 1. `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 4번째 인자 `encoding`를 하네스가 고정합니다(9행에서 기본값, 10행에서 기본값, 11행에서 기본값) (라이브러리 내부 `impl::{익명}::load_buffer_impl` → `impl::{익명}::get_buffer_encoding`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2106행 조건 `encoding == encoding_wchar` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2109행 조건 `encoding == encoding_utf16` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2112행 조건 `encoding == encoding_utf32` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2115행 조건 `encoding != encoding_auto` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 4864행 조건 `!impl::convert_buffer(buffer, length, buffer_encoding, contents, size, is_mutable)` (수정 전: 한 번도 참 아님)

## 2. 하네스가 `xml_node::xml_node(xml_node_struct *)`를 부르지 않아 1번째 인자 `p` 값이 들어가지 않습니다 (필드 `_root`를 거쳐 조건에 쓰임) → 호출을 추가하세요
- 여전히 막힘 (0/5) — `xml_document::reset()` 7680행 조건 `extra` (수정 전: 한 번도 참 아님)

## 3. `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 3번째 인자 `options`를 하네스가 `기본값`, `parse_minimal`, `parse_full` 중에서만 고릅니다(9행, 10행, 11행) (라이브러리 내부 `impl::{익명}::load_buffer_impl` → `impl::{익명}::xml_parser::parse` → `impl::{익명}::xml_parser::parse_tree` → `impl::{익명}::get_strconv_pcdata`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2800행 조건 `case 1` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2801행 조건 `case 2` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2803행 조건 `case 4` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2804행 조건 `case 5` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2805행 조건 `case 6` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2806행 조건 `case 7` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2807행 조건 `default` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2969행 조건 `case 1` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2970행 조건 `case 2` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2971행 조건 `case 3` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2972행 조건 `case 4` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2973행 조건 `case 5` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2974행 조건 `case 6` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2976행 조건 `case 8` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2977행 조건 `case 9` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2978행 조건 `case 10` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2979행 조건 `case 11` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2980행 조건 `case 12` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2981행 조건 `case 13` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2982행 조건 `case 14` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2983행 조건 `case 15` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2984행 조건 `default` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 3515행 조건 `!PUGI_IMPL_OPTSET` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 3525행 조건 `!PUGI_IMPL_OPTSET` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 3642행 조건 `!PUGI_IMPL_OPTSET` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 4855행 조건 `(options & parse_fragment)` (수정 전: 한 번도 참 아님)

## 4. `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)`의 1번째 인자 `contents`에 하네스가 null을 넘긴 적이 없습니다(9행, 10행, 11행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 2138행 조건 `contents` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `xml_document::load_buffer(const void *, size_t, unsigned int, xml_encoding)` 4844행 조건 `!contents` (수정 전: 한 번도 참 아님)

