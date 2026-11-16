# 호출 안 함 API 우선순위 — zlib/_union

'호출 안 함' API 54개. 추가 가능 26개, 제외 28개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `inflateBack(z_streamp, in_func, void *, out_func, void *)` | 2 | 524 | 524 | 이번에 추가 |
| 2 | `deflateCopy(z_streamp, z_streamp)` | 2 | 66 | 66 | 이번에 추가 |
| 3 | `inflateCopy(z_streamp, z_streamp)` | 3 | 45 | 45 | 이번에 추가 |
| 4 | `inflateBackInit_(z_streamp, int, unsigned char *, const char *, int)` | 1 | 38 | 38 | 이번에 추가 |
| 5 | `deflatePrime(z_streamp, int, int)` | 1 | 25 | 25 | 이번에 추가 |
| 6 | `zlibCompileFlags(void)` | 1 | 21 | 21 | 이번에 추가 |
| 7 | `inflatePrime(z_streamp, int, int)` | 1 | 20 | 20 | 이번에 추가 |
| 8 | `deflateGetDictionary(z_streamp, Bytef *, uInt *)` | 2 | 18 | 18 | 이번에 추가 |
| 9 | `inflateValidate(z_streamp, int)` | 1 | 16 | 16 | 이번에 추가 |
| 10 | `inflateGetDictionary(z_streamp, Bytef *, uInt *)` | 2 | 16 | 16 | 이번에 추가 |
| 11 | `inflateBackEnd(z_streamp)` | 1 | 16 | 16 |  |
| 12 | `deflatePending(z_streamp, unsigned int *, int *)` | 1 | 16 | 16 |  |
| 13 | `inflateMark(z_streamp)` | 1 | 10 | 10 |  |
| 14 | `inflateGetHeader(z_streamp, gz_headerp)` | 1 | 10 | 10 |  |
| 15 | `deflateUsed(z_streamp, int *)` | 1 | 9 | 9 |  |
| 16 | `deflateSetHeader(z_streamp, gz_headerp)` | 1 | 8 | 8 |  |
| 17 | `zError(int)` | 1 | 7 | 7 |  |
| 18 | `inflateSyncPoint(z_streamp)` | 1 | 7 | 7 |  |
| 19 | `inflateUndermine(z_streamp, int)` | 1 | 6 | 6 |  |
| 20 | `deflateTune(z_streamp, int, int, int, int)` | 1 | 6 | 6 |  |
| 21 | `inflateCodesUsed(z_streamp)` | 1 | 4 | 4 |  |
| 22 | `zlibVersion(void)` | 1 | 2 | 2 |  |
| 23 | `compress_z(Bytef *, z_size_t *, const Bytef *, z_size_t)` | 1 | 2 | 2 |  |
| 24 | `compress(Bytef *, uLongf *, const Bytef *, uLong)` | 1 | 2 | 2 |  |
| 25 | `uncompress_z(Bytef *, z_size_t *, const Bytef *, z_size_t)` | 1 | 1 | 1 |  |
| 26 | `get_crc_table(void)` | 1 | 1 | 1 |  |
| 27 | `gzbuffer(gzFile, unsigned int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 28 | `gzclearerr(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 29 | `gzclose(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 30 | `gzclose_r(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 31 | `gzclose_w(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 32 | `gzdirect(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 33 | `gzdopen(int, const char *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 34 | `gzeof(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 35 | `gzerror(gzFile, int *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 36 | `gzflush(gzFile, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 37 | `gzfread(voidp, z_size_t, z_size_t, gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 38 | `gzfwrite(voidpc, z_size_t, z_size_t, gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 39 | `gzgetc(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 40 | `gzgetc_(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 41 | `gzgets(gzFile, char *, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 42 | `gzoffset(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 43 | `gzopen(const char *, const char *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 44 | `gzprintf(gzFile, const char *, ...)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 45 | `gzputc(gzFile, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 46 | `gzputs(gzFile, const char *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 47 | `gzread(gzFile, voidp, unsigned int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 48 | `gzrewind(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 49 | `gzseek(gzFile, long long, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 50 | `gzsetparams(gzFile, int, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 51 | `gztell(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 52 | `gzungetc(int, gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 53 | `gzvprintf(gzFile, const char *, struct __va_list_tag *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 54 | `gzwrite(gzFile, voidpc, unsigned int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
