# LLM 하네스 수정 — tinyxml2/stateful, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::Accept(XMLVisitor *) const`의 1번째 인자 `visitor`를 하네스가 고정합니다(172행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요 (같은 호출이 2개 구현 클래스에 영향: `XMLDocument::Accept`, `XMLElement::Accept`)
- 겨냥한 분기: 4개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 4/4 | - | 6923/6721 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix2/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -34,6 +34,25 @@
     return n;
 }
 
+// 퍼저 입력의 비트마스크로 각 방문 결과(true/false)를 정하는 방문자  // [gapfuzz-llm] VisitEnter가 false, Accept가 false를 돌려주는 분기를 열기 위해 입력 기반 방문자 추가
+class FuzzVisitor : public XMLVisitor {
+public:
+    explicit FuzzVisitor(uint32_t mask) : mask_(mask), idx_(0) {}
+    bool VisitEnter(const XMLDocument &) override { return Next(); }
+    bool VisitExit(const XMLDocument &) override { return Next(); }
+    bool VisitEnter(const XMLElement &, const XMLAttribute *) override { return Next(); }
+    bool VisitExit(const XMLElement &) override { return Next(); }
+    bool Visit(const XMLDeclaration &) override { return Next(); }
+    bool Visit(const XMLText &) override { return Next(); }
+    bool Visit(const XMLComment &) override { return Next(); }
+    bool Visit(const XMLUnknown &) override { return Next(); }
+
+private:
+    bool Next() { return ((mask_ >> (idx_++ & 31u)) & 1u) != 0; }
+    uint32_t mask_;
+    unsigned idx_;
+};
+
 }  // namespace
 
 extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
@@ -169,7 +188,11 @@
         case 13: {  // 출력
             XMLPrinter printer(nullptr, fdp.ConsumeBool(), fdp.ConsumeIntegralInRange<int>(0, 4));
             if (fdp.ConsumeBool()) doc.Print(&printer);
-            else cur->Accept(&printer);
+            else {  // [gapfuzz-llm] 방문자를 printer 고정에서 입력으로 고르게 변경
+                FuzzVisitor fuzzVisitor(fdp.ConsumeIntegral<uint32_t>());  // [gapfuzz-llm] 입력 비트마스크로 방문 결과를 정하는 방문자 생성
+                XMLVisitor *visitor = fdp.ConsumeBool() ? static_cast<XMLVisitor *>(&printer) : &fuzzVisitor;  // [gapfuzz-llm] 원래의 printer도 계속 선택될 수 있게 유지
+                cur->Accept(visitor);  // [gapfuzz-llm] 고정된 &printer 대신 입력으로 고른 visitor 전달 (null 아님)
+            }
             printer.CStr();
             printer.CStrSize();
             break;
```
