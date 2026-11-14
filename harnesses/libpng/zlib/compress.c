/* libpng가 쓰는 zlib 소스를 함께 빌드하기 위한 한 줄짜리 파일 (python3 scripts/exp.py fetch zlib 필요).
   이렇게 두면 zlib 코드는 링크되지만 libpng 커버리지 집계에는 들어가지 않는다. */
#include "../../../third_party/zlib/compress.c"
