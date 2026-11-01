// pugixml 공식 하네스(tests/fuzz_parse.cpp)에 gapfuzz 제안을 적용한 버전.
//   제안 1 (적용): load_buffer의 encoding을 기본값으로 고정 → 입력 3번째 바이트로 고름
//   제안 2 (미적용, 대조군): xml_node(xml_node_struct*) 생성자 — 내부용이라 하네스에서 쓰지 않음
//   제안 3 (적용): options를 기본값·parse_minimal·parse_full 중에서만 고름 → 입력 1·2번째 바이트로 플래그 조합
//   제안 4 (적용): contents에 null을 넘긴 적 없음 → 가끔 nullptr도 넘김
// 기존 세 가지 호출은 그대로 둔다 (원래 하네스가 보던 것을 잃지 않도록).
#include "pugixml.hpp"

#include <stdint.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size)
{
    if (Size < 3) return 0;
    unsigned int options = (Data[0] | (Data[1] << 8)) & 0x7fff;          // parse_* 플래그 15비트
    pugi::xml_encoding encoding = static_cast<pugi::xml_encoding>(Data[2] % 10);
    const uint8_t *body = Data + 3;
    size_t n = Size - 3;

    pugi::xml_document doc;
    doc.load_buffer(body, n, options, encoding);
    if (Data[2] & 0x80) doc.load_buffer(nullptr, n, options, encoding);

    doc.load_buffer(body, n);
    doc.load_buffer(body, n, pugi::parse_minimal);
    doc.load_buffer(body, n, pugi::parse_full);
    return 0;
}
