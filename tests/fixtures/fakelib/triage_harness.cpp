// 크래시 귀속(C) 테스트 하네스. 입력 첫 바이트로 일부러 다른 종류의 크래시를 낸다.
#include "fakelib.h"

#include <cstdint>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 2) return 0;
    switch (data[0]) {
    case 'O':   // ⓐ 라이브러리 결함: 라이브러리 안의 힙 오버플로
        fakelib::OverflowSum(data, size);
        break;
    case 'A':   // ⓓ 의도된 assert
        fakelib::CheckNot42(42);
        break;
    case 'U': { // ⓑ 하네스 버그: 금방 사라지는 문자열의 포인터를 넘김
        fakelib::Holder h;
        {
            std::string tmp(reinterpret_cast<const char *>(data), size);
            h.SetName(tmp.c_str());
        }
        h.NameLength();
        break;
    }
    case 'H': { // ⓑ 하네스 버그: 하네스 코드 자체의 스택 오버플로
        char buf[4];
        for (size_t i = 0; i < size; ++i) buf[i] = static_cast<char>(data[i]);
        fakelib::CheckNot42(buf[1]);
        break;
    }
    case 'T':   // ⓒ 리소스 상한: 무한 루프
        while (data[1] != 0xff) { }
        break;
    case 'M': { // ⓒ 리소스 상한: 3GB 할당
        char *p = fakelib::Alloc(size_t(3) << 30);
        delete[] p;
        break;
    }
    case 'D': { // ⓑ 하네스 버그: 해제 API로 지운 객체를 다시 씀 (해제는 라이브러리 안에서 일어남)
        fakelib::Buffer *b = fakelib::CreateBuffer(4);
        fakelib::DestroyBuffer(b);
        fakelib::BufferSum(b);
        break;
    }
    case 'F': { // ⓑ 하네스 버그: 같은 객체를 두 번 해제 요청
        fakelib::Buffer *b = fakelib::CreateBuffer(4);
        fakelib::DestroyBuffer(b);
        fakelib::DestroyBuffer(b);
        break;
    }
    case 'I':   // ⓐ 라이브러리 결함: 한 번의 API 호출 안에서 해제 후 사용 (규칙이 과하게 하네스 탓을 하지 않는지 확인)
        fakelib::InternalUseAfterFree(4);
        break;
    default:
        break;
    }
    return 0;
}
