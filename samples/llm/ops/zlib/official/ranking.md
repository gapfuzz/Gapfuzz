# 호출 안 함 API 우선순위 — zlib/official

'호출 안 함' API 74개. 추가 가능 46개, 제외 28개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `compress(Bytef *, uLongf *, const Bytef *, uLong)` | 46 | 1716 | 1716 | 이번에 추가 |
| 2 | `inflateBack(z_streamp, in_func, void *, out_func, void *)` | 2 | 524 | 524 | 이번에 추가 |
| 3 | `deflateCopy(z_streamp, z_streamp)` | 3 | 114 | 66 | 이번에 추가 |
| 4 | `deflateBound(z_streamp, uLong)` | 3 | 111 | 63 | 이번에 추가 |
| 5 | `deflateParams(z_streamp, int, int)` | 36 | 1558 | 50 | 이번에 추가 |
| 6 | `inflateCopy(z_streamp, z_streamp)` | 3 | 45 | 45 | 이번에 추가 |
| 7 | `inflateSync(z_streamp)` | 2 | 44 | 44 | 이번에 추가 |
| 8 | `deflateSetDictionary(z_streamp, const Bytef *, uInt)` | 12 | 225 | 40 | 이번에 추가 |
| 9 | `inflateBackInit_(z_streamp, int, unsigned char *, const char *, int)` | 1 | 38 | 38 | 이번에 추가 |
| 10 | `adler32_combine(uLong, uLong, long long)` | 2 | 27 | 27 | 이번에 추가 |
| 11 | `inflateSetDictionary(z_streamp, const Bytef *, uInt)` | 1 | 26 | 26 |  |
| 12 | `crc32_combine(uLong, uLong, long long)` | 6 | 26 | 26 |  |
| 13 | `deflatePrime(z_streamp, int, int)` | 4 | 84 | 25 |  |
| 14 | `zlibCompileFlags(void)` | 1 | 21 | 21 |  |
| 15 | `inflatePrime(z_streamp, int, int)` | 1 | 20 | 20 |  |
| 16 | `deflateGetDictionary(z_streamp, Bytef *, uInt *)` | 3 | 66 | 18 |  |
| 17 | `deflatePending(z_streamp, unsigned int *, int *)` | 2 | 64 | 16 |  |
| 18 | `inflateValidate(z_streamp, int)` | 1 | 16 | 16 |  |
| 19 | `inflateGetDictionary(z_streamp, Bytef *, uInt *)` | 2 | 16 | 16 |  |
| 20 | `inflateBackEnd(z_streamp)` | 1 | 16 | 16 |  |
| 21 | `inflateMark(z_streamp)` | 1 | 10 | 10 |  |
| 22 | `inflateGetHeader(z_streamp, gz_headerp)` | 1 | 10 | 10 |  |
| 23 | `deflateUsed(z_streamp, int *)` | 2 | 57 | 9 |  |
| 24 | `deflateSetHeader(z_streamp, gz_headerp)` | 2 | 56 | 8 |  |
| 25 | `compressBound(uLong)` | 2 | 8 | 8 |  |
| 26 | `zError(int)` | 1 | 7 | 7 |  |
| 27 | `inflateSyncPoint(z_streamp)` | 1 | 7 | 7 |  |
| 28 | `deflateTune(z_streamp, int, int, int, int)` | 2 | 54 | 6 |  |
| 29 | `inflateUndermine(z_streamp, int)` | 1 | 6 | 6 |  |
| 30 | `inflateCodesUsed(z_streamp)` | 1 | 4 | 4 |  |
| 31 | `compress_z(Bytef *, z_size_t *, const Bytef *, z_size_t)` | 45 | 1715 | 2 |  |
| 32 | `zlibVersion(void)` | 1 | 2 | 2 |  |
| 33 | `crc32_combine_gen(long long)` | 4 | 21 | 1 |  |
| 34 | `uncompress_z(Bytef *, z_size_t *, const Bytef *, z_size_t)` | 1 | 1 | 1 |  |
| 35 | `get_crc_table(void)` | 1 | 1 | 1 |  |
| 36 | `compress2(Bytef *, uLongf *, const Bytef *, uLong, int)` | 45 | 1714 | 0 |  |
| 37 | `compress2_z(Bytef *, z_size_t *, const Bytef *, z_size_t, int)` | 44 | 1713 | 0 |  |
| 38 | `deflate(z_streamp, int)` | 35 | 1508 | 0 |  |
| 39 | `deflateInit_(z_streamp, int, const char *, int)` | 16 | 289 | 0 |  |
| 40 | `deflateInit2_(z_streamp, int, int, int, int, int, const char *, int)` | 15 | 284 | 0 |  |
| 41 | `deflateReset(z_streamp)` | 13 | 156 | 0 |  |
| 42 | `deflateResetKeep(z_streamp)` | 10 | 145 | 0 |  |
| 43 | `deflateBound_z(z_streamp, z_size_t)` | 2 | 107 | 0 |  |
| 44 | `deflateEnd(z_streamp)` | 2 | 71 | 0 |  |
| 45 | `crc32_combine_op(uLong, uLong, uLong)` | 2 | 15 | 0 |  |
| 46 | `compressBound_z(z_size_t)` | 1 | 4 | 0 |  |
| 47 | `gzbuffer(gzFile, unsigned int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 48 | `gzclearerr(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 49 | `gzclose(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 50 | `gzclose_r(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 51 | `gzclose_w(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 52 | `gzdirect(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 53 | `gzdopen(int, const char *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 54 | `gzeof(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 55 | `gzerror(gzFile, int *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 56 | `gzflush(gzFile, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 57 | `gzfread(voidp, z_size_t, z_size_t, gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 58 | `gzfwrite(voidpc, z_size_t, z_size_t, gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 59 | `gzgetc(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 60 | `gzgetc_(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 61 | `gzgets(gzFile, char *, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 62 | `gzoffset(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 63 | `gzopen(const char *, const char *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 64 | `gzprintf(gzFile, const char *, ...)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 65 | `gzputc(gzFile, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 66 | `gzputs(gzFile, const char *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 67 | `gzread(gzFile, voidp, unsigned int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 68 | `gzrewind(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 69 | `gzseek(gzFile, long long, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 70 | `gzsetparams(gzFile, int, int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 71 | `gztell(gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 72 | `gzungetc(int, gzFile)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 73 | `gzvprintf(gzFile, const char *, struct __va_list_tag *)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
| 74 | `gzwrite(gzFile, voidpc, unsigned int)` | 1 | 0 | 0 | 구현이 빌드에 없음 (선언만 있거나 매크로·인라인) |
