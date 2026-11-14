#include <stddef.h>
#include <stdint.h>
#include "extlib.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  ext_ctx *c = ext_new();
  if (!c) return 0;
  /* level은 코드로는 변수지만, 입력이 1MB를 넘지 않는 한 항상 1이다 */
  int level = size > 1000000 ? 9 : 1;
  ext_feed(c, (const char *)data, size, level);
  ext_free(c);
  return 0;
}
