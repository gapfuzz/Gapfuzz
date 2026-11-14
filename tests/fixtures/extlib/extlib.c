#include "extlib.h"
#include <stdlib.h>

/* 라이브러리 자체 어서션 (TinyXML2의 TIXMLASSERT, pugixml의 PUGI_IMPL_ASSERT 같은 것) */
#define EXT_ASSERT(x) do { if (!(x)) abort(); } while (0)

struct ext_ctx {
  ext_item_fn on_item;
  void *user;
  int dirty;
  int total;
};

ext_ctx *ext_new(void) { return (ext_ctx *)calloc(1, sizeof(ext_ctx)); }
void ext_free(ext_ctx *c) { free(c); }

void ext_set_handler(ext_ctx *c, ext_item_fn fn, void *user) {
  c->on_item = fn;
  c->user = user;
}

void ext_mark_dirty(ext_ctx *c) { c->dirty = 1; }

int ext_feed(ext_ctx *c, const char *data, size_t size, int level) {
  int r = 0;
  EXT_ASSERT(size < 100000);
  if (c->on_item)
    c->on_item(c->user, data, size);
  if (c->dirty)
    r += 1;
  if (level > 5)
    r += 2;
  c->total += (int)size;
  return r;
}
