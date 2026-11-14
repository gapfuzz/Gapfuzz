// TinyXML2 공식 OSS-Fuzz 하네스 (projects/tinyxml2/xmltest.cpp)와 동일한 동작.
// 입력을 문자열로 바꿔 Parse 한 번만 호출한다.
#include "tinyxml2.h"
#include <stddef.h>
#include <stdint.h>
#include <string>

using namespace tinyxml2;

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string data_string(reinterpret_cast<const char *>(data), size);
    XMLDocument doc;
    doc.Parse(data_string.c_str());
    return 0;
}
