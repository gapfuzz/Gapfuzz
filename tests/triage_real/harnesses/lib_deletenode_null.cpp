// 라이브러리 버그 #1048 (aba13c5에서 수정): DeleteNode(nullptr)가 세그폴트.
// 유지보수자가 라이브러리 쪽에 null 검사를 넣어 고쳤으므로 → 정답: 라이브러리 탓
#include "tinyxml2.h"
#include <cstdint>
#include <string>
using namespace tinyxml2;
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string s(reinterpret_cast<const char *>(data), size);
    XMLDocument doc;
    doc.Parse(s.c_str());
    doc.DeleteNode(doc.RootElement());                   // 파싱 실패면 RootElement()가 null
    return 0;
}
