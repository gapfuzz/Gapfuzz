// 하네스 오용: doc.Clear()로 문서 내용을 지운 뒤, 그 전에 받아 둔 요소의 이름을 읽음.
// Clear()가 문자 버퍼를 해제하므로 라이브러리 안(Name)에서 heap-use-after-free가 난다.
// 문서가 소유한 노드를 Clear 뒤에 쓰는 것은 TinyXML2 사용 규칙 위반 → 정답: 하네스 탓
#include "tinyxml2.h"
#include <cstdint>
#include <cstdio>
#include <string>
using namespace tinyxml2;
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string s(reinterpret_cast<const char *>(data), size);
    XMLDocument doc;
    doc.Parse(s.c_str());
    XMLElement *e = doc.RootElement();
    if (!e) return 0;
    doc.Clear();
    volatile size_t n = 0;
    for (const char *p = e->Name(); p && *p; ++p) n++;   // Name()이 해제된 버퍼를 읽음
    return 0;
}
