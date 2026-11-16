라이브러리: tinyxml2
하네스 파일: official_xmltest2.cpp

아래 제안 2개를 **모두 한 하네스에** 적용하세요.

## 제안 2
하네스가 `XMLDocument::Parse(const char *, size_t)`를 부르지 않아 2번째 인자 `nBytes` 값이 들어가지 않습니다 (필드 `_charBuffer`를 거쳐 조건에 쓰임) → 호출을 추가하세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XMLDocument::LoadFile(FILE *)` 2413행, 조건 `read != size`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2409      const size_t size = static_cast<size_t>(filelength);
 2410      TIXMLASSERT( _charBuffer == 0 );
 2411      _charBuffer = new char[size+1];
 2412      const size_t read = fread( _charBuffer, 1, size, fp );
 2413>     if ( read != size ) {
 2414          SetError( XML_ERROR_FILE_READ_ERROR, 0, 0 );
 2415          return _errorID;
 2416      }
 2417  
```

## 제안 3
`XMLDocument::LoadFile(const char *)`의 1번째 인자 `filename`에 하네스가 null을 넘긴 적이 없습니다(35행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `XMLDocument::LoadFile(const char *)` 2354행, 조건 `!filename`가 퍼징 중 한 번도 '참'이 되지 않음
```
 2350  
 2351  
 2352  XMLError XMLDocument::LoadFile( const char* filename )
 2353  {
 2354>     if ( !filename ) {
 2355          TIXMLASSERT( false );
 2356          SetError( XML_ERROR_FILE_COULD_NOT_BE_OPENED, 0, "filename=<null>" );
 2357          return _errorID;
 2358      }
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 하네스: oss-fuzz/projects/tinyxml2/xmltest2.cpp. include 경로만 이 저장소에 맞게 바꿨다(tinyxml2/tinyxml2.h → tinyxml2.h).
   2  /* Copyright 2024 Google LLC
   3  Licensed under the Apache License, Version 2.0 (the "License");
   4  you may not use this file except in compliance with the License.
   5  You may obtain a copy of the License at
   6        http://www.apache.org/licenses/LICENSE-2.0
   7  Unless required by applicable law or agreed to in writing, software
   8  distributed under the License is distributed on an "AS IS" BASIS,
   9  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  10  See the License for the specific language governing permissions and
  11  limitations under the License.
  12  */
  13  
  14  #include "tinyxml2.h"
  15  
  16  #include <string>
  17  #include <cstdio>
  18  #include <cstdint>
  19  #include <cstdlib>
  20  
  21  #include <unistd.h>
  22  
  23  using namespace tinyxml2;
  24  using namespace std;
  25  
  26  // Entry point for LibFuzzer.
  27  extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
  28  	char pathname[256];
  29  	sprintf(pathname, "/tmp/libfuzzer.%d", getpid());
  30  	FILE *fp = fopen(pathname, "wb");
  31  	fwrite(data, size, 1, fp);
  32    	fclose(fp);
  33      
  34  	XMLDocument doc;
  35  	doc.LoadFile(pathname);
  36  
  37      unlink(pathname);
  38  	return 0;
  39  }
```