#include "fakelib.h"

#include <cassert>
#include <cstring>

namespace fakelib {

int OverflowSum(const unsigned char *data, size_t n) {
    unsigned char *buf = new unsigned char[n];
    for (size_t i = 0; i <= n; ++i)            // 버그: n+1번 씀
        buf[i] = data[i % n];
    int s = buf[0];
    delete[] buf;
    return s;
}

void CheckNot42(int x) {
    assert(x != 42);                            // 라이브러리가 가정한 불변 조건
}

char *Alloc(size_t n) {
    char *p = new char[n];
    p[0] = 1;
    return p;
}

size_t Holder::NameLength() const {
    return name_ ? std::strlen(name_) : 0;
}

int Widget::Level(int lvl) {
    if (lvl == 5) {                             // lvl: 하네스가 (cond ? 1 : 2)로만 넘김 → NARROW(선택지 제한)
        return 50;
    }
    return lvl;
}

int Widget::Run(const char *s, bool strict) {
    if (!s) {                                   // s: 하네스가 null을 넘긴 적 없음 → NARROW(null 미전달)
        return -1;
    }
    int score = 0;
    const char *q = s;                          // 지역 변수를 한 번 거침
    if (q[0] == 'y') {                          // q ← s: Run 1번째 인자 → VARIES (지역 변수 추적)
        score += 64;
    }
    if (mode_ == 2) {                           // mode_: 생성자 1번째 인자 → 하네스가 입력으로 바꿈(VARIES)
        score += 1;
    }
    if (verbose_) {                             // verbose_: 생성자 2번째 인자 → 하네스가 항상 기본값(FIXED)
        score += 2;
    }
    if (strict) {                               // strict: Run 2번째 인자 → 하네스가 항상 기본값(FIXED)
        score += 4;
    } else {
        score += 8;
    }
    if (HasLabel()) {                           // label_: SetLabel로만 설정 → 하네스가 안 부름(SETTER_NOT_CALLED)
        score += 16;
    }
    if (s[0] == 'x') {                          // s: Run 1번째 인자 → 하네스가 입력으로 바꿈(VARIES)
        score += 32;
    }
    return score;
}

}  // namespace fakelib

// ---- 생성·해제 API (크래시 귀속의 사용 규칙 위반 테스트용) ----
namespace fakelib {
struct Buffer {
    size_t n;
    int *data;
};

Buffer *CreateBuffer(size_t n) {
    Buffer *b = new Buffer{n, new int[n]()};
    return b;
}

void DestroyBuffer(Buffer *b) {
    delete[] b->data;
    delete b;
}

int BufferSum(const Buffer *b) {
    int s = 0;
    for (size_t i = 0; i < b->n; ++i) s += b->data[i];
    return s;
}

int InternalUseAfterFree(size_t n) {
    Buffer *b = CreateBuffer(n);
    DestroyBuffer(b);
    return BufferSum(b);    // 버그: 라이브러리가 스스로 해제한 객체를 다시 읽음
}
}  // namespace fakelib
