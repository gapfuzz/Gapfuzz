// official_v2.cpp에 gapfuzz의 새 판정 'DIRECT_CALL'(라이브러리만 부르는 공개 API를 하네스가 직접 안 부름) 제안 4개를 적용한 버전.
// 파싱 뒤에 라이브러리가 내부에서만 부르던 공개 API 4개를 하네스가 직접, 라이브러리와 다른 방식으로 부른다.
//   [제안 3] XMLNode::Value()를 문서 객체에서 부른 적 없음          → doc.Value()
//   [제안 4] XMLElement::Attribute(name, value)의 value가 내부에선 항상 null → 값을 넘겨 부름
//   [제안 5] XMLNode::InsertEndChild에 다른 문서의 노드를 넘긴 적 없음  → 다른 문서의 노드를 넘김
//   [제안 6] XMLDocument::DeleteNode에 null·트리에 연결된 노드를 넘긴 적 없음 → 입력 비트로 둘 중 하나
// 입력 구조는 official_v2와 같다: [옵션 1바이트][길이 비율 1바이트][XML 문자열]
#include "tinyxml2.h"

#include <cstddef>
#include <cstdint>
#include <string>

using namespace tinyxml2;

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 2) return 0;
    const uint8_t opt = data[0];
    const uint8_t ratio = data[1];
    std::string data_string(reinterpret_cast<const char *>(data + 2), size - 2);

    static const Whitespace kModes[] = {PRESERVE_WHITESPACE, COLLAPSE_WHITESPACE, PEDANTIC_WHITESPACE};
    XMLDocument doc(true, kModes[opt % 3]);                                    // [제안 1]

    if (opt & 0x80) {                                                         // [제안 2]
        const size_t n = data_string.size() * ratio / 255;                    // 0 ~ 문자열 길이
        doc.Parse(data_string.c_str(), n);
    } else {
        doc.Parse(data_string.c_str());
    }

    (void)doc.Value();                                                        // [제안 3]
    XMLElement *root = doc.RootElement();
    if (root) {
        if (const XMLAttribute *a = root->FirstAttribute())                   // [제안 4]
            (void)root->Attribute(a->Name(), (opt & 0x08) ? a->Value() : "");
        XMLDocument other;                                                    // [제안 5]
        other.Parse("<o/>");
        if (opt & 0x10) (void)root->InsertEndChild(other.RootElement());
        if (opt & 0x20) doc.DeleteNode(root->FirstChild());                   // [제안 6] 트리에 연결된 노드
    }
    if (opt & 0x40) doc.DeleteNode(nullptr);                                  // [제안 6] null
    return 0;
}
