라이브러리: zlib
OSS-Fuzz 하네스 9개(official, official_checksum, official_compress, official_example_dict, official_example_flush, official_example_large, official_example_small, official_uncompress2, official_uncompress3)의 커버리지를 모두 합쳐도, 공개 API 88개 중 54개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `inflateBack(z_streamp, in_func, void *, out_func, void *)` — 새로 실행될 수 있는 코드 영역 524개
```
ZEXTERN int ZEXPORT inflateBack(z_streamp strm,
                                in_func in, void FAR *in_desc,
                                out_func out, void FAR *out_desc);
/*
     inflateBack() does a raw inflate with a single call using a call-back
   interface for input and output.  This is potentially more efficient than
   inflate() for file i/o applications, in that it avoids copying between the
   output and the sliding window by simply making the window itself the output
   buffer.  inflate() can be faster on modern CPUs when used with large
   buffers.  inflateBack() trusts the application to not change the output
   buffer passed by the output function, at least until inflateBack() returns.

     inflateBackInit() must be called first to allocate the internal state
   and to initialize the state with the user-provided window buffer.
   inflateBack() may then be used multiple times to inflate a complete, raw
   deflate stream with each call.  inflateBackEnd() is then called to free the
   allocated state.

     A raw deflate stream is one with no zlib or gzip header or trailer.
   This routine would normally be used in a utility that reads zip or gzip
   files and writes out uncompressed files.  The utility would decode the
   header and process the trailer on its own, hence this routine expects only
   the raw deflate stream to decompress.  This is different from the default
   behavior of inflate(), which expects a zlib header and trailer around the
   deflate stream.

     inflateBack() uses two subroutines supplied by the caller that are then
   called by inflateBack() for input and output.  inflateBack() calls those
   routines until it reads a complete deflate stream and writes out all of the
   uncompressed data, or until it encounters an error.  The function's
   parameters and return types are defined above in the in_func and out_func
   typedefs.  inflateBack() will call in(in_desc, &buf) which should return the
   number of bytes of provided input, and a pointer to that input in buf.  If
```

### 2. `deflateCopy(z_streamp, z_streamp)` — 새로 실행될 수 있는 코드 영역 66개
```
ZEXTERN int ZEXPORT deflateCopy(z_streamp dest,
                                z_streamp source);
/*
     Sets the destination stream as a complete copy of the source stream.

     This function can be useful when several compression strategies will be
   tried, for example when there are several ways of pre-processing the input
   data with a filter.  The streams that will be discarded should then be freed
   by calling deflateEnd.  Note that deflateCopy duplicates the internal
   compression state which can be quite large, so this strategy is slow and can
   consume lots of memory.

     deflateCopy returns Z_OK if success, Z_MEM_ERROR if there was not
   enough memory, Z_STREAM_ERROR if the source stream state was inconsistent
   (such as zalloc being Z_NULL).  msg is left unchanged in both source and
   destination.  If deflateCopy fails and dest is not Z_NULL, then dest->state
   is set to Z_NULL with dest otherwise unchanged, so that deflateEnd(dest) can
   be called safely, though dest is not a usable stream.
*/
```

### 3. `inflateCopy(z_streamp, z_streamp)` — 새로 실행될 수 있는 코드 영역 45개
```
ZEXTERN int ZEXPORT inflateCopy(z_streamp dest,
                                z_streamp source);
/*
     Sets the destination stream as a complete copy of the source stream.

     This function can be useful when randomly accessing a large stream.  The
   first pass through the stream can periodically record the inflate state,
   allowing restarting inflate at those points when randomly accessing the
   stream.

     inflateCopy returns Z_OK if success, Z_MEM_ERROR if there was not
   enough memory, Z_STREAM_ERROR if the source stream state was inconsistent
   (such as zalloc being Z_NULL).  msg is left unchanged in both source and
   destination.  If inflateCopy fails and dest is not Z_NULL, then dest->state
   is set to Z_NULL with dest otherwise unchanged, so that inflateEnd(dest) can
   be called safely, though dest is not a usable stream.
*/
```

### 4. `inflateBackInit_(z_streamp, int, unsigned char *, const char *, int)` — 새로 실행될 수 있는 코드 영역 38개
```
ZEXTERN int ZEXPORT inflateBackInit_(z_streamp strm, int windowBits,
                                     unsigned char FAR *window,
                                     const char *version,
                                     int stream_size);
```

### 5. `deflatePrime(z_streamp, int, int)` — 새로 실행될 수 있는 코드 영역 25개
```
ZEXTERN int ZEXPORT deflatePrime(z_streamp strm,
                                 int bits,
                                 int value);
/*
     deflatePrime() inserts bits in the deflate output stream.  The intent
   is that this function is used to start off the deflate output with the bits
   leftover from a previous deflate stream when appending to it.  As such, this
   function can only be used for raw deflate, and must be used before the first
   deflate() call after a deflateInit2() or deflateReset().  bits must be less
   than or equal to 16, and that many of the least significant bits of value
   will be inserted in the output.

     deflatePrime returns Z_OK if success, Z_BUF_ERROR if there was not enough
   room in the internal buffer to insert the bits, or Z_STREAM_ERROR if the
   source stream state was inconsistent.
*/
```

### 6. `zlibCompileFlags(void)` — 새로 실행될 수 있는 코드 영역 21개
```
ZEXTERN uLong ZEXPORT zlibCompileFlags(void);
/* Return flags indicating compile-time options.

    Type sizes, two bits each, 00 = 16 bits, 01 = 32, 10 = 64, 11 = other:
     1.0: size of uInt
     3.2: size of uLong
     5.4: size of voidpf (pointer)
     7.6: size of z_off_t

    Compiler, assembler, and debug options:
     8: ZLIB_DEBUG
     9: ASMV or ASMINF -- use ASM code
     10: ZLIB_WINAPI -- exported functions use the WINAPI calling convention
     11: 0 (reserved)

    One-time table building (smaller code, but not thread-safe if true):
     12: BUILDFIXED -- build static block decoding tables when needed
     13: DYNAMIC_CRC_TABLE -- build CRC calculation tables when needed
     14,15: 0 (reserved)

    Library content (indicates missing functionality):
     16: NO_GZCOMPRESS -- gz* functions cannot compress (to avoid linking
                          deflate code when not needed)
     17: NO_GZIP -- deflate can't write gzip streams, and inflate can't detect
                    and decode gzip streams (to avoid linking crc code)
     18-19: 0 (reserved)

    Operation variations (changes in library functionality):
     20: PKZIP_BUG_WORKAROUND -- slightly more permissive inflate
     21: FASTEST -- deflate algorithm with only one, lowest compression level
     22,23: 0 (reserved)
```

### 7. `inflatePrime(z_streamp, int, int)` — 새로 실행될 수 있는 코드 영역 20개
```
ZEXTERN int ZEXPORT inflatePrime(z_streamp strm,
                                 int bits,
                                 int value);
/*
     This function inserts bits in the inflate input stream.  The intent is to
   use inflatePrime() to start inflating at a bit position in the middle of a
   byte.  The provided bits will be used before any bytes are used from
   next_in.  This function should be used with raw inflate, before the first
   inflate() call, after inflateInit2() or inflateReset().  It can also be used
   after an inflate() return indicates the end of a deflate block or header
   when using Z_BLOCK.  bits must be less than or equal to 16, and that many of
   the least significant bits of value will be inserted in the input.  The
   other bits in value can be non-zero, and will be ignored.

     If bits is negative, then the input stream bit buffer is emptied.  Then
   inflatePrime() can be called again to put bits in the buffer.  This is used
   to clear out bits leftover after feeding inflate a block description prior
   to feeding inflate codes.

     inflatePrime returns Z_OK if success, or Z_STREAM_ERROR if the source
   stream state was inconsistent, or if bits is out of range.  If inflate was
   in the middle of processing a header, trailer, or stored block lengths, then
   it is possible for there to be only eight bits available in the bit buffer.
   In that case, bits > 8 is considered out of range.  However, when used as
   outlined above, there will always be 16 bits available in the buffer for
   insertion.  As noted in its documentation above, inflate records the number
   of bits in the bit buffer on return in data_type. 32 minus that is the
   number of bits available for insertion.  inflatePrime does not update
   data_type with the new number of bits in buffer.
*/
```

### 8. `deflateGetDictionary(z_streamp, Bytef *, uInt *)` — 새로 실행될 수 있는 코드 영역 18개
```
ZEXTERN int ZEXPORT deflateGetDictionary(z_streamp strm,
                                         Bytef *dictionary,
                                         uInt  *dictLength);
/*
     Returns the sliding dictionary being maintained by deflate.  dictLength is
   set to the number of bytes in the dictionary, and that many bytes are copied
   to dictionary.  dictionary must have enough space, where 32768 bytes is
   always enough.  If deflateGetDictionary() is called with dictionary equal to
   Z_NULL, then only the dictionary length is returned, and nothing is copied.
   Similarly, if dictLength is Z_NULL, then it is not set.

     deflateGetDictionary() may return a length less than the window size, even
   when more than the window size in input has been provided. It may return up
   to 258 bytes less in that case, due to how zlib's implementation of deflate
   manages the sliding window and lookahead for matches, where matches can be
   up to 258 bytes long. If the application needs the last window-size bytes of
   input, then that would need to be saved by the application outside of zlib.

     deflateGetDictionary returns Z_OK on success, or Z_STREAM_ERROR if the
   stream state is inconsistent.
*/
```

### 9. `inflateValidate(z_streamp, int)` — 새로 실행될 수 있는 코드 영역 16개
```
ZEXTERN int            ZEXPORT inflateValidate(z_streamp, int);
```

### 10. `inflateGetDictionary(z_streamp, Bytef *, uInt *)` — 새로 실행될 수 있는 코드 영역 16개
```
ZEXTERN int ZEXPORT inflateGetDictionary(z_streamp strm,
                                         Bytef *dictionary,
                                         uInt  *dictLength);
/*
     Returns the sliding dictionary being maintained by inflate.  dictLength is
   set to the number of bytes in the dictionary, and that many bytes are copied
   to dictionary.  dictionary must have enough space, where 32768 bytes is
   always enough.  If inflateGetDictionary() is called with dictionary equal to
   Z_NULL, then only the dictionary length is returned, and nothing is copied.
   Similarly, if dictLength is Z_NULL, then it is not set.

     inflateGetDictionary returns Z_OK on success, or Z_STREAM_ERROR if the
   stream state is inconsistent.
*/
```

## 참고: 기존 하네스 official.cc (고치지 마세요. include와 작성 방식만 참고)
```
// OSS-Fuzz 공식 하네스: oss-fuzz/projects/zlib/zlib_uncompress_fuzzer.cc 그대로 (zlib 커밋 71747d1).
// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "zlib.h"

static Bytef buffer[256 * 1024] = { 0 };

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
  if (Z_OK != uncompress(buffer, &buffer_length, data,
                         static_cast<uLong>(size))) {
    return 0;
  }
  return 0;
}

```