// 고정 인자 탐지(A) 테스트 하네스.
//   - Widget w(1)          : mode는 상수, verbose는 기본값
//   - Widget w2(data[0]%2) : mode는 입력에 따라 바뀜 (그래도 2는 안 나옴)
//   - w.Run(s)             : strict는 항상 기본값
//   - SetLabel은 부르지 않음
//   - w.Level(cond ? 1 : 2) : lvl은 1, 2 중에서만 고름
//   - Run에 null을 넘기지 않음
#include "fakelib.h"

#include <cstdint>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size == 0) return 0;
    std::string s(reinterpret_cast<const char *>(data), size);
    fakelib::Widget w(1);
    w.Run(s.c_str());
    fakelib::Widget w2(data[0] % 2);
    w2.Run(s.c_str());
    w.Level(data[0] % 2 ? 1 : 2);
    return 0;
}
