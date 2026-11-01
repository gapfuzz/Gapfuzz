// 회귀 테스트용 하네스: BLOCKED 판정 검증
// 입력 길이는 libFuzzer -max_len(기본 4096)을 넘지 못하므로 아래 if 문은 절대 참이 되지 않는다.
// 분석기는 XMLDocument::Print 와 그 아래(XMLPrinter::OpenElement 등)를
// "호출 경로 있음 · 조건에 막힘"으로 분류하고, 막힌 지점으로 이 파일의 if 블록을 가리켜야 한다.
#include "tinyxml2.h"
#include <cstddef>
#include <cstdint>
#include <string>

using namespace tinyxml2;

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string s(reinterpret_cast<const char *>(data), size);
    XMLDocument doc;
    doc.Parse(s.c_str());
    if (size > 1000000) {
        XMLPrinter printer;
        doc.Print(&printer);   // BLOCKED_SITE
    }
    return 0;
}
