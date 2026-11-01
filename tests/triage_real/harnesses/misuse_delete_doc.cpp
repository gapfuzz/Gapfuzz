// 하네스 오용: 문서를 delete한 뒤 그 문서의 요소를 사용.
// 소멸자가 노드 메모리 풀을 해제하므로 라이브러리 안에서 heap-use-after-free → 정답: 하네스 탓
#include "tinyxml2.h"
#include <cstdint>
#include <string>
using namespace tinyxml2;
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string s(reinterpret_cast<const char *>(data), size);
    XMLDocument *doc = new XMLDocument();
    doc->Parse(s.c_str());
    XMLElement *e = doc->RootElement();
    delete doc;
    if (e) (void)e->FirstChildElement("x");             // 해제된 노드를 사용
    return 0;
}
