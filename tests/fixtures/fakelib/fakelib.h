// 테스트용 가짜 라이브러리. 일부러 버그와 상태 의존 분기를 넣어 두었다.
#pragma once
#include <cstddef>

namespace fakelib {

// ---- 크래시 귀속(C) 테스트용 ----
int OverflowSum(const unsigned char *data, size_t n);   // 라이브러리 버그: 힙 버퍼 오버플로
void CheckNot42(int x);                                  // assert(x != 42)
char *Alloc(size_t n);                                   // 입력이 정한 크기를 그대로 할당

// 생성·해제 API가 따로 있는 힙 객체 (해제 뒤 사용·두 번 해제는 사용 규칙 위반)
struct Buffer;
Buffer *CreateBuffer(size_t n);
void DestroyBuffer(Buffer *b);
int BufferSum(const Buffer *b);
int InternalUseAfterFree(size_t n);                      // 라이브러리 버그: 한 번의 호출 안에서 해제 후 사용

// 문자열을 복사하지 않고 포인터만 기억하는 클래스 (TinyXML2의 SetValue(str, true)와 같은 규칙)
class Holder {
public:
    void SetName(const char *s) { name_ = s; }
    size_t NameLength() const;
private:
    const char *name_ = nullptr;
};

// ---- 고정 인자 탐지(A) 테스트용 ----
class Widget {
public:
    explicit Widget(int mode = 0, bool verbose = false) : mode_(mode), verbose_(verbose) {}
    int Run(const char *s, bool strict = true);
    int Level(int lvl);
    void SetLabel(const char *label) { label_ = label; }
    bool HasLabel() const { return label_ != nullptr; }
private:
    int mode_;
    bool verbose_;
    const char *label_ = nullptr;
};

}  // namespace fakelib
