라이브러리: zlib
하네스 파일: official.cc
지금 하네스는 공개 API 88개 중 74개를 한 번도 부르지 않습니다.

## 하네스에 추가할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `compress(Bytef *, uLongf *, const Bytef *, uLong)` — 새로 실행될 수 있는 코드 영역 1716개
```
ZEXTERN int ZEXPORT compress(Bytef *dest, uLongf *destLen,
                             const Bytef *source, uLong sourceLen);
```

### 2. `inflateBack(z_streamp, in_func, void *, out_func, void *)` — 새로 실행될 수 있는 코드 영역 524개
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

### 3. `deflateCopy(z_streamp, z_streamp)` — 새로 실행될 수 있는 코드 영역 66개
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

### 4. `deflateBound(z_streamp, uLong)` — 새로 실행될 수 있는 코드 영역 63개
```
ZEXTERN uLong ZEXPORT deflateBound(z_streamp strm, uLong sourceLen);
```

### 5. `deflateParams(z_streamp, int, int)` — 새로 실행될 수 있는 코드 영역 50개
```
ZEXTERN int ZEXPORT deflateParams(z_streamp strm,
                                  int level,
                                  int strategy);
/*
     Dynamically update the compression level and compression strategy.  The
   interpretation of level and strategy is as in deflateInit2().  This can be
   used to switch between compression and straight copy of the input data, or
   to switch to a different kind of input data requiring a different strategy.
   If the compression approach (which is a function of the level) or the
   strategy is changed, and if there have been any deflate() calls since the
   state was initialized or reset, then the input available so far is
   compressed with the old level and strategy using deflate(strm, Z_BLOCK).
   There are three approaches for the compression levels 0, 1..3, and 4..9
   respectively.  The new level and strategy will take effect at the next call
   of deflate().

     If a deflate(strm, Z_BLOCK) is performed by deflateParams(), and it does
   not have enough output space to complete, then the parameter change will not
   take effect.  In this case, deflateParams() can be called again with the
   same parameters and more output space to try again.

     In order to assure a change in the parameters on the first try, the
   deflate stream should be flushed using deflate() with Z_BLOCK or other flush
   request until strm.avail_out is not zero, before calling deflateParams().
   Then no more input data should be provided before the deflateParams() call.
   If this is done, the old level and strategy will be applied to the data
   compressed before deflateParams(), and the new level and strategy will be
   applied to the data compressed after deflateParams().

     deflateParams returns Z_OK on success, Z_STREAM_ERROR if the source stream
   state was inconsistent or if a parameter was invalid, or Z_BUF_ERROR if
   there was not enough output space to complete the compression of the
   available input data before a change in the strategy or approach.  Note that
```

### 6. `inflateCopy(z_streamp, z_streamp)` — 새로 실행될 수 있는 코드 영역 45개
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

### 7. `inflateSync(z_streamp)` — 새로 실행될 수 있는 코드 영역 44개
```
ZEXTERN int ZEXPORT inflateSync(z_streamp strm);
/*
     Skips invalid compressed data until a possible full flush point (see above
   for the description of deflate with Z_FULL_FLUSH) can be found, or until all
   available input is skipped.  No output is provided.

     inflateSync searches for a 00 00 FF FF pattern in the compressed data.
   All full flush points have this pattern, but not all occurrences of this
   pattern are full flush points.

     inflateSync returns Z_OK if a possible full flush point has been found,
   Z_BUF_ERROR if no more input was provided, Z_DATA_ERROR if no flush point
   has been found, or Z_STREAM_ERROR if the stream structure was inconsistent.
   In the success case, the application may save the current value of total_in
   which indicates where valid compressed data was found.  In the error case,
   the application may repeatedly call inflateSync, providing more input each
   time, until success or end of the input data.
*/
```

### 8. `deflateSetDictionary(z_streamp, const Bytef *, uInt)` — 새로 실행될 수 있는 코드 영역 40개
```
ZEXTERN int ZEXPORT deflateSetDictionary(z_streamp strm,
                                         const Bytef *dictionary,
                                         uInt  dictLength);
/*
     Initializes the compression dictionary from the given byte sequence
   without producing any compressed output.  When using the zlib format, this
   function must be called immediately after deflateInit, deflateInit2 or
   deflateReset, and before any call of deflate.  When doing raw deflate, this
   function must be called either before any call of deflate, or immediately
   after the completion of a deflate block, i.e. after all input has been
   consumed and all output has been delivered when using any of the flush
   options Z_BLOCK, Z_PARTIAL_FLUSH, Z_SYNC_FLUSH, or Z_FULL_FLUSH.  The
   compressor and decompressor must use exactly the same dictionary (see
   inflateSetDictionary).

     The dictionary should consist of strings (byte sequences) that are likely
   to be encountered later in the data to be compressed, with the most commonly
   used strings preferably put towards the end of the dictionary.  Using a
   dictionary is most useful when the data to be compressed is short and can be
   predicted with good accuracy; the data can then be compressed better than
   with the default empty dictionary.

     Depending on the size of the compression data structures selected by
   deflateInit or deflateInit2, a part of the dictionary may in effect be
   discarded, for example if the dictionary is larger than the window size
   provided in deflateInit or deflateInit2.  Thus the strings most likely to be
   useful should be put at the end of the dictionary, not at the front.  In
   addition, the current implementation of deflate will use at most the window
   size minus 262 bytes of the provided dictionary.

     Upon return of this function, strm->adler is set to the Adler-32 value
   of the dictionary; the decompressor may later use this value to determine
   which dictionary has been used by the compressor.  (The Adler-32 value
```

### 9. `inflateBackInit_(z_streamp, int, unsigned char *, const char *, int)` — 새로 실행될 수 있는 코드 영역 38개
```
ZEXTERN int ZEXPORT inflateBackInit_(z_streamp strm, int windowBits,
                                     unsigned char FAR *window,
                                     const char *version,
                                     int stream_size);
```

### 10. `adler32_combine(uLong, uLong, long long)` — 새로 실행될 수 있는 코드 영역 27개
```
   ZEXTERN uLong ZEXPORT adler32_combine(uLong, uLong, z_off_t);
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 공식 하네스: oss-fuzz/projects/zlib/zlib_uncompress_fuzzer.cc 그대로 (zlib 커밋 71747d1).
   2  // Copyright 2015 The Chromium Authors. All rights reserved.
   3  // Use of this source code is governed by a BSD-style license that can be
   4  // found in the LICENSE file.
   5  
   6  #include <stddef.h>
   7  #include <stdint.h>
   8  #include <string.h>
   9  
  10  #include "zlib.h"
  11  
  12  static Bytef buffer[256 * 1024] = { 0 };
  13  
  14  // Entry point for LibFuzzer.
  15  extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  16    uLongf buffer_length = static_cast<uLongf>(sizeof(buffer));
  17    if (Z_OK != uncompress(buffer, &buffer_length, data,
  18                           static_cast<uLong>(size))) {
  19      return 0;
  20    }
  21    return 0;
  22  }
```