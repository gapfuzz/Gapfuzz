/* 확장 판정(CALLBACK, STATE, ASSERT, 실행 중 관찰) 시험용 가짜 C 라이브러리 */
#ifndef EXTLIB_H
#define EXTLIB_H
#include <stddef.h>
typedef struct ext_ctx ext_ctx;
typedef void (*ext_item_fn)(void *user, const char *s, size_t n);

ext_ctx *ext_new(void);
void ext_free(ext_ctx *c);
/* 항목을 만날 때마다 불릴 콜백을 등록한다 */
void ext_set_handler(ext_ctx *c, ext_item_fn fn, void *user);
/* 다음 ext_feed가 이어 붙이기 모드로 동작하게 한다 */
void ext_mark_dirty(ext_ctx *c);
int ext_feed(ext_ctx *c, const char *data, size_t size, int level);
#endif
