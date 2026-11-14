// OSS-Fuzz 하네스: oss-fuzz/projects/zlib/zlib_uncompress2_fuzzer.cc 그대로.
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "zlib.h"

static Bytef buffer[256 * 1024] = { 0 };

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
  uLong buf_size = static_cast<uLong>(size);
  // Ignore return code.
  uncompress2(buffer, &buffer_length, data, &buf_size);
  return 0;
}
