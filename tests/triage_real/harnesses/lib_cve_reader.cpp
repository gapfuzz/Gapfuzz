// CVE-2024-50614/50615 재현용: 파싱 후 텍스트와 속성 값을 읽는 하네스.
// TinyXML2는 문자 참조(&#...;)를 값을 읽을 때(GetStr) 처리하므로, 파싱만 하는 하네스로는 이 코드에 닿지 않는다.
#include "tinyxml2.h"
#include <cstdint>
#include <string>
using namespace tinyxml2;
static void walk(const XMLElement *e) {
    for (; e; e = e->NextSiblingElement()) {
        (void)e->GetText();
        for (const XMLAttribute *a = e->FirstAttribute(); a; a = a->Next()) (void)a->Value();
        walk(e->FirstChildElement());
    }
}
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string s(reinterpret_cast<const char *>(data), size);
    XMLDocument doc;
    doc.Parse(s.c_str());
    walk(doc.RootElement());
    return 0;
}
