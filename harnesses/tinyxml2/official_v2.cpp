// TinyXML2 공식 OSS-Fuzz 하네스(xmltest.cpp)에 gapfuzz 제안 2개만 적용한 버전.
// 여전히 '파싱만' 하는 하네스이며, 바뀐 것은 아래 두 인자뿐이다.
//   [제안 1] XMLDocument의 공백 처리 모드가 항상 기본값(PRESERVE)  → 입력 첫 바이트로 3가지 중 선택
//   [제안 2] Parse의 길이 인자(nBytes)가 항상 기본값(문자열 끝까지) → 입력 첫 바이트로 기본값 또는 0~전체 길이 선택
//
// 입력 구조: [옵션 1바이트][길이 비율 1바이트][XML 문자열]
// OSS-Fuzz에 제안할 때 기존 코퍼스와의 호환성은 따로 고려해야 한다(입력 앞 2바이트가 옵션으로 쓰임).
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
    return 0;
}
