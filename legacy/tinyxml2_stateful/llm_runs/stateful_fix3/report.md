# LLM 하네스 수정 — tinyxml2/stateful, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(44행에서 기본값, 233행에서 기본값) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 2개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 2/2 | - | 6457/5975 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix3/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -41,7 +41,8 @@
 
     XMLDocument doc(fdp.ConsumeBool(), fdp.ConsumeBool() ? COLLAPSE_WHITESPACE : PRESERVE_WHITESPACE);
     std::string xml = fdp.ConsumeRandomLengthString(4096);
-    doc.Parse(xml.c_str());
+    const size_t nBytes = fdp.ConsumeBool() ? static_cast<size_t>(-1) : fdp.ConsumeIntegralInRange<size_t>(0, xml.size());  // [gapfuzz-llm] nBytes를 퍼저 입력에서 고름(-1=원래 기본값, 0 포함, 실제 버퍼 길이 이하로 제한)
+    doc.Parse(xml.c_str(), nBytes);  // [gapfuzz-llm] nBytes 고정(기본값) 대신 퍼저가 고른 값을 전달해 nBytes==0 및 nBytes!=-1 분기 도달
 
     XMLDocument other;          // DeepClone / 다른 문서 간 동작 확인용
     XMLNode *cur = &doc;
@@ -230,7 +231,7 @@
         case 20:  // 문서 비우고 다시 파싱
             doc.Clear();
             cur = &doc;
-            if (fdp.ConsumeBool()) doc.Parse(str);
+            if (fdp.ConsumeBool()) doc.Parse(str, fdp.ConsumeBool() ? static_cast<size_t>(-1) : fdp.ConsumeIntegralInRange<size_t>(0, s.size()));  // [gapfuzz-llm] nBytes를 퍼저 입력에서 고름(-1=원래 기본값, 0 포함, s 길이 이하로 제한해 버퍼 초과 읽기 방지)
             break;
         default:  // 루트 요소·형 변환 조회
             doc.RootElement();
```
