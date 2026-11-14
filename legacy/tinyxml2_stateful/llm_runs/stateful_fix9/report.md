# LLM 하네스 수정 — tinyxml2/stateful, 제안 9

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(44행, 233행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6177/5586 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix9/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -41,7 +41,7 @@
 
     XMLDocument doc(fdp.ConsumeBool(), fdp.ConsumeBool() ? COLLAPSE_WHITESPACE : PRESERVE_WHITESPACE);
     std::string xml = fdp.ConsumeRandomLengthString(4096);
-    doc.Parse(xml.c_str());
+    doc.Parse(fdp.ConsumeIntegralInRange<int>(0, 15) == 0 ? nullptr : xml.c_str());  // [gapfuzz-llm] Parse의 xml 인자에 nullptr(!xml 분기)도 가끔 전달하도록 입력에서 선택
 
     XMLDocument other;          // DeepClone / 다른 문서 간 동작 확인용
     XMLNode *cur = &doc;
@@ -230,7 +230,7 @@
         case 20:  // 문서 비우고 다시 파싱
             doc.Clear();
             cur = &doc;
-            if (fdp.ConsumeBool()) doc.Parse(str);
+            if (fdp.ConsumeBool()) doc.Parse(fdp.ConsumeIntegralInRange<int>(0, 15) == 0 ? nullptr : str);  // [gapfuzz-llm] 재파싱에서도 xml 인자에 nullptr(!xml 분기)를 가끔 전달
             break;
         default:  // 루트 요소·형 변환 조회
             doc.RootElement();
```
