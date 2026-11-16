// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 2,3를 OSS-Fuzz 하네스 official_xmltest2에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness_extra.py, 기록: samples/llm/combined/tinyxml2/official_xmltest2/).
// OSS-Fuzz 하네스: oss-fuzz/projects/tinyxml2/xmltest2.cpp. include 경로만 이 저장소에 맞게 바꿨다(tinyxml2/tinyxml2.h → tinyxml2.h).
/* Copyright 2024 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#include "tinyxml2.h"

#include <string>
#include <cstdio>
#include <cstdint>
#include <cstdlib>

#include <unistd.h>

using namespace tinyxml2;
using namespace std;

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
	// 앞쪽 2바이트는 제어용, 나머지는 기존처럼 XML 본문으로 쓴다.
	uint8_t ctrl_filename = 1; // [gapfuzz-llm] 기본값은 0이 아니므로 원래대로 유효한 파일명이 나온다
	uint8_t ctrl_nbytes = 0; // [gapfuzz-llm] Parse의 nBytes 선택용 제어 바이트
	size_t off = 0; // [gapfuzz-llm] 제어 바이트로 소비한 길이
	if (size > 0) { ctrl_filename = data[0]; off = 1; } // [gapfuzz-llm] 첫 바이트로 filename null 여부 결정
	if (size > 1) { ctrl_nbytes = data[1]; off = 2; } // [gapfuzz-llm] 둘째 바이트로 nBytes 결정(첫 바이트와 겹치지 않음)
	const uint8_t *payload = data + off; // [gapfuzz-llm] 제어 바이트를 제외한 본문
	size_t payload_size = size - off; // [gapfuzz-llm] 본문 길이

	char pathname[256];
	sprintf(pathname, "/tmp/libfuzzer.%d", getpid());
	FILE *fp = fopen(pathname, "wb");
	fwrite(payload, payload_size, 1, fp); // [gapfuzz-llm] 제어 바이트를 뺀 본문을 파일에 기록
  	fclose(fp);
    
	XMLDocument doc;
	const char *filename = (ctrl_filename % 8 == 0) ? nullptr : pathname; // [gapfuzz-llm] 가끔 nullptr를 넘겨 !filename 분기 도달
	doc.LoadFile(filename); // [gapfuzz-llm] filename이 nullptr일 수 있음(라이브러리가 오류로 처리)

	// [gapfuzz-llm] Parse(const char*, size_t) 호출 추가: nBytes를 퍼저 입력에서 선택
	string xml(reinterpret_cast<const char *>(payload), payload_size); // [gapfuzz-llm] NUL 종료가 보장되는 버퍼
	size_t nBytes;
	if (ctrl_nbytes % 4 == 0) {
		nBytes = static_cast<size_t>(-1); // [gapfuzz-llm] 원래 동작(strlen 사용) 경로도 계속 나오게 함
	} else {
		nBytes = static_cast<size_t>(ctrl_nbytes) % (payload_size + 1); // [gapfuzz-llm] 버퍼 길이를 넘지 않는 다양한 nBytes
	}
	XMLDocument doc2; // [gapfuzz-llm] Parse 전용 문서
	doc2.Parse(xml.c_str(), nBytes); // [gapfuzz-llm] nBytes 값이 _charBuffer 경로에 반영되도록 호출

    unlink(pathname);
	return 0;
}
