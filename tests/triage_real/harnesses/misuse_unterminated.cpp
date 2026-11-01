// 하네스 오용: 입력을 NUL 없이 복사한 버퍼를 길이 없이 Parse에 넘김.
// 라이브러리가 문자열 끝을 찾다가 버퍼 밖을 읽음(heap-buffer-overflow), 버퍼는 하네스가 할당 → 정답: 하네스 탓
#include "tinyxml2.h"
#include <cstdint>
#include <cstdlib>
#include <cstring>
using namespace tinyxml2;
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size == 0) return 0;
    char *buf = static_cast<char *>(malloc(size));
    memcpy(buf, data, size);                             // NUL 종료 없음
    XMLDocument doc;
    doc.Parse(buf);                                      // nBytes를 안 넘겨 strlen으로 길이를 잼
    free(buf);
    return 0;
}
