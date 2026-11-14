# LLM 하네스 수정 — tinyxml2/stateful, 제안 4

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::Print(XMLPrinter *) const`의 1번째 인자 `streamer`를 하네스가 고정합니다(171행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6133/5258 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix4/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -168,7 +168,7 @@
         }
         case 13: {  // 출력
             XMLPrinter printer(nullptr, fdp.ConsumeBool(), fdp.ConsumeIntegralInRange<int>(0, 4));
-            if (fdp.ConsumeBool()) doc.Print(&printer);
+            if (fdp.ConsumeBool()) doc.Print(fdp.ConsumeBool() ? &printer : nullptr);  // [gapfuzz-llm] streamer를 고정하지 않고 입력으로 &printer 또는 nullptr(문서상 허용, stdout 출력)을 골라 'streamer가 거짓'인 분기를 열기 위함
             else cur->Accept(&printer);
             printer.CStr();
             printer.CStrSize();
```
