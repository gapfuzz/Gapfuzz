# LLM 하네스 수정 — tinyxml2/stateful, 제안 6

- 모델: `claude-sonnet-5-5`
- 제안: `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)`의 4번째 인자 `aposInAttributes`를 하네스가 고정합니다(170행에서 기본값, 178행에서 기본값) → 퍼저 입력으로 바꾸세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 컴파일 실패 | -/- | - | 6339/5960 |
| 2 | 통과 | 1/1 | - | 11895/6404 |

**채택 후보: 시도 2** (`harnesses/llm/stateful_fix6/try2.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -167,7 +167,7 @@
             break;
         }
         case 13: {  // 출력
-            XMLPrinter printer(nullptr, fdp.ConsumeBool(), fdp.ConsumeIntegralInRange<int>(0, 4));
+            XMLPrinter printer(nullptr, fdp.ConsumeBool(), fdp.ConsumeIntegralInRange<int>(0, 4), fdp.ConsumeBool() ? XMLPrinter::ESCAPE_APOS_CHARS_IN_ATTRIBUTES : XMLPrinter::DONT_ESCAPE_APOS_CHARS_IN_ATTRIBUTES);  // [gapfuzz-llm] 작은따옴표 이스케이프 여부(aposInAttributes)가 기본값으로 고정되어 거짓 분기를 못 탔으므로 입력에서 고르게 함(열거형은 XMLPrinter 안에 선언됨)
             if (fdp.ConsumeBool()) doc.Print(&printer);
             else cur->Accept(&printer);
             printer.CStr();
@@ -175,7 +175,7 @@
             break;
         }
         case 14: {  // XMLPrinter 직접 사용
-            XMLPrinter printer(nullptr, fdp.ConsumeBool());
+            XMLPrinter printer(nullptr, fdp.ConsumeBool(), 0, fdp.ConsumeBool() ? XMLPrinter::ESCAPE_APOS_CHARS_IN_ATTRIBUTES : XMLPrinter::DONT_ESCAPE_APOS_CHARS_IN_ATTRIBUTES);  // [gapfuzz-llm] depth는 기본값 0을 유지하고 aposInAttributes만 입력에서 고르게 함(열거형은 XMLPrinter 안에 선언됨)
             printer.PushHeader(fdp.ConsumeBool(), fdp.ConsumeBool());
             printer.OpenElement(str, fdp.ConsumeBool());
             printer.PushAttribute("a", fdp.ConsumeIntegral<int>());
```
