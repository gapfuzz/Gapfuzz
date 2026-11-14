/* gapfuzz argtrace: 하네스가 라이브러리를 부르는 지점에서 실제로 넘어간 인자 값을 기록한다.
 *
 * `python3 -m gapfuzz argtrace`가 하네스 사본의 인자 식을 GAPFUZZ_ARG_*(번호, 식)으로 감싸고 이 헤더를 끼워 넣는다.
 * 감싼 식은 값을 그대로 돌려주므로 하네스 동작은 바뀌지 않는다. 프로그램이 끝날 때 환경 변수
 * GAPFUZZ_ARGTRACE_OUT 이 가리키는 파일에 "번호 호출수 넘침여부 값…" 을 한 줄씩 쓴다.
 * 값 표기: i:<정수>  f:<실수>  p:null / p:nonnull (포인터는 null 여부만)  o (그 밖의 객체: 값은 기록하지 않음)
 */
#ifndef GAPFUZZ_ARGTRACE_H
#define GAPFUZZ_ARGTRACE_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef GAPFUZZ_ARGTRACE_N
#define GAPFUZZ_ARGTRACE_N 1
#endif
#define GAPFUZZ_AT_MAXV 16   /* 지점마다 기억하는 서로 다른 값의 최대 개수. 넘으면 '여러 값'으로만 표시 */

struct gapfuzz_at_slot {
  unsigned long long count;
  int n, overflow;
  char kind[GAPFUZZ_AT_MAXV];
  long long val[GAPFUZZ_AT_MAXV];
};
static struct gapfuzz_at_slot gapfuzz_at[GAPFUZZ_ARGTRACE_N];

static void gapfuzz_at_dump(void) {
  const char *path = getenv("GAPFUZZ_ARGTRACE_OUT");
  FILE *f;
  int i, k;
  if (!path || !(f = fopen(path, "w"))) return;
  for (i = 0; i < GAPFUZZ_ARGTRACE_N; i++) {
    struct gapfuzz_at_slot *s = &gapfuzz_at[i];
    if (!s->count) continue;
    fprintf(f, "%d %llu %d", i, s->count, s->overflow);
    for (k = 0; k < s->n; k++) {
      if (s->kind[k] == 'i') fprintf(f, " i:%lld", s->val[k]);
      else if (s->kind[k] == 'p') fprintf(f, " %s", s->val[k] ? "p:nonnull" : "p:null");
      else if (s->kind[k] == 'f') { double d; memcpy(&d, &s->val[k], sizeof d); fprintf(f, " f:%.9g", d); }
      else fprintf(f, " o");
    }
    fputc('\n', f);
  }
  fclose(f);
}

static inline void gapfuzz_at_rec(int id, char kind, long long v) {
  static int registered;
  struct gapfuzz_at_slot *s;
  int k;
  if (!registered) { registered = 1; atexit(gapfuzz_at_dump); }
  if (id < 0 || id >= GAPFUZZ_ARGTRACE_N) return;
  s = &gapfuzz_at[id];
  s->count++;
  for (k = 0; k < s->n; k++)
    if (s->kind[k] == kind && s->val[k] == v) return;
  if (s->n == GAPFUZZ_AT_MAXV) { s->overflow = 1; return; }
  s->kind[s->n] = kind;
  s->val[s->n++] = v;
}

static inline long long gapfuzz_at_bits(double d) { long long v = 0; memcpy(&v, &d, sizeof d); return v; }

#ifdef __cplusplus
#include <cstddef>
#include <type_traits>
#include <utility>
template <class T> static inline T &&gapfuzz_arg(int id, T &&v) {
  typedef typename std::decay<T>::type D;
  if constexpr (std::is_integral<D>::value || std::is_enum<D>::value) gapfuzz_at_rec(id, 'i', (long long)v);
  else if constexpr (std::is_floating_point<D>::value) gapfuzz_at_rec(id, 'f', gapfuzz_at_bits((double)v));
  else if constexpr (std::is_pointer<D>::value) gapfuzz_at_rec(id, 'p', v != nullptr);
  else if constexpr (std::is_null_pointer<D>::value) gapfuzz_at_rec(id, 'p', 0);
  else gapfuzz_at_rec(id, 'o', 0);
  return std::forward<T>(v);
}
#define GAPFUZZ_ARG_I(id, e) gapfuzz_arg(id, (e))
#define GAPFUZZ_ARG_P(id, e) gapfuzz_arg(id, (e))
#define GAPFUZZ_ARG_F(id, e) gapfuzz_arg(id, (e))
#define GAPFUZZ_ARG_O(id, e) gapfuzz_arg(id, (e))
#else
#define GAPFUZZ_ARG_I(id, e) __extension__({ __auto_type gf_v_ = (e); gapfuzz_at_rec(id, 'i', (long long)gf_v_); gf_v_; })
#define GAPFUZZ_ARG_P(id, e) __extension__({ __auto_type gf_v_ = (e); gapfuzz_at_rec(id, 'p', gf_v_ != 0); gf_v_; })
#define GAPFUZZ_ARG_F(id, e) __extension__({ __auto_type gf_v_ = (e); gapfuzz_at_rec(id, 'f', gapfuzz_at_bits((double)gf_v_)); gf_v_; })
#endif
#endif
