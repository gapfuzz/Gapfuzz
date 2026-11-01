// 2021년 버그(9efb6b0에서 수정) 재현용: 파싱 오류가 나는 파일을 같은 문서에 두 번 LoadFile.
// 오류 처리 경로가 노드를 잘못된 함수로 지워 메모리 풀 집계가 어긋나고, 다음 LoadFile의 Clear()에서 assert 실패.
#include "tinyxml2.h"
#include <cstdint>
#include <cstdio>
#include <unistd.h>
using namespace tinyxml2;
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    char path[64];
    snprintf(path, sizeof path, "/tmp/gapfuzz_lf.%d", getpid());
    FILE *fp = fopen(path, "wb");
    fwrite(data, 1, size, fp);
    fclose(fp);
    XMLDocument doc;
    doc.LoadFile(path);
    doc.LoadFile(path);
    unlink(path);
    return 0;
}
