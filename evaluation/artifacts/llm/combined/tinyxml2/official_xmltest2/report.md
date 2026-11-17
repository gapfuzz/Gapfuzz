# LLM 하네스 수정 — tinyxml2/official_xmltest2, 제안 2,3

- 모델: `claude-sonnet-5-5`
- 제안: 하네스가 `XMLDocument::Parse(const char *, size_t)`를 부르지 않아 2번째 인자 `nBytes` 값이 들어가지 않습니다 (필드 `_charBuffer`를 거쳐 조건에 쓰임) → 호출을 추가하세요
- 제안: `XMLDocument::LoadFile(const char *)`의 1번째 인자 `filename`에 하네스가 null을 넘긴 적이 없습니다(35행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 1/2 | 2: 0/1, 3: 1/1 | - | 2169/2872 |
| 2 | 통과 | 1/2 | 2: 0/1, 3: 1/1 | - | 4056/3030 |

**채택 후보: 시도 1** (`harnesses/tinyxml2/llm/official_xmltest2_combined/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -25,14 +25,35 @@
 
 // Entry point for LibFuzzer.
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
+	// 앞쪽 2바이트는 제어용, 나머지는 기존처럼 XML 본문으로 쓴다.
+	uint8_t ctrl_filename = 1; // [gapfuzz-llm] 기본값은 0이 아니므로 원래대로 유효한 파일명이 나온다
+	uint8_t ctrl_nbytes = 0; // [gapfuzz-llm] Parse의 nBytes 선택용 제어 바이트
+	size_t off = 0; // [gapfuzz-llm] 제어 바이트로 소비한 길이
+	if (size > 0) { ctrl_filename = data[0]; off = 1; } // [gapfuzz-llm] 첫 바이트로 filename null 여부 결정
+	if (size > 1) { ctrl_nbytes = data[1]; off = 2; } // [gapfuzz-llm] 둘째 바이트로 nBytes 결정(첫 바이트와 겹치지 않음)
+	const uint8_t *payload = data + off; // [gapfuzz-llm] 제어 바이트를 제외한 본문
+	size_t payload_size = size - off; // [gapfuzz-llm] 본문 길이
+
 	char pathname[256];
 	sprintf(pathname, "/tmp/libfuzzer.%d", getpid());
 	FILE *fp = fopen(pathname, "wb");
-	fwrite(data, size, 1, fp);
+	fwrite(payload, payload_size, 1, fp); // [gapfuzz-llm] 제어 바이트를 뺀 본문을 파일에 기록
   	fclose(fp);
     
 	XMLDocument doc;
-	doc.LoadFile(pathname);
+	const char *filename = (ctrl_filename % 8 == 0) ? nullptr : pathname; // [gapfuzz-llm] 가끔 nullptr를 넘겨 !filename 분기 도달
+	doc.LoadFile(filename); // [gapfuzz-llm] filename이 nullptr일 수 있음(라이브러리가 오류로 처리)
+
+	// [gapfuzz-llm] Parse(const char*, size_t) 호출 추가: nBytes를 퍼저 입력에서 선택
+	string xml(reinterpret_cast<const char *>(payload), payload_size); // [gapfuzz-llm] NUL 종료가 보장되는 버퍼
+	size_t nBytes;
+	if (ctrl_nbytes % 4 == 0) {
+		nBytes = static_cast<size_t>(-1); // [gapfuzz-llm] 원래 동작(strlen 사용) 경로도 계속 나오게 함
+	} else {
+		nBytes = static_cast<size_t>(ctrl_nbytes) % (payload_size + 1); // [gapfuzz-llm] 버퍼 길이를 넘지 않는 다양한 nBytes
+	}
+	XMLDocument doc2; // [gapfuzz-llm] Parse 전용 문서
+	doc2.Parse(xml.c_str(), nBytes); // [gapfuzz-llm] nBytes 값이 _charBuffer 경로에 반영되도록 호출
 
     unlink(pathname);
 	return 0;
```
