# LLM 하네스 수정 — tinyxml2/official, 제안 5

- 모델: `claude-sonnet-5-5`
- 제안: `XMLElement::Attribute(const char *, const char *) const`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLElement::ParseAttributes`)에서만 불립니다. 내부 호출은 2번째 인자 `value`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1265/1558 |

**채택 후보: 시도 1** (`harnesses/llm/official_fix5/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -11,5 +11,20 @@
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
     doc.Parse(data_string.c_str());
+    try { // [gapfuzz-llm] 라이브러리/std 예외가 하네스 크래시로 이어지지 않도록 보호
+        const XMLElement *root = doc.RootElement(); // [gapfuzz-llm] Attribute를 직접 부를 대상 요소를 얻음
+        const XMLAttribute *attr = root ? root->FirstAttribute() : 0; // [gapfuzz-llm] 실제 존재하는 속성 이름을 쓰기 위해 첫 속성을 얻음
+        if (root && attr) { // [gapfuzz-llm] name은 null이면 안 되므로 속성이 있을 때만 호출
+            unsigned mode = size > 0 ? (data[0] % 3) : 0; // [gapfuzz-llm] 입력 앞 바이트로 value 전달 방식을 고름
+            const char *value = 0; // [gapfuzz-llm] mode 0: value가 null인 기존 경로
+            if (mode == 1) {
+                value = attr->Value(); // [gapfuzz-llm] mode 1: 속성값과 같은 값을 넘겨 StringEqual 참 경로 도달
+            } else if (mode == 2) {
+                value = data_string.c_str(); // [gapfuzz-llm] mode 2: 입력 문자열(대개 다른 값)을 넘겨 !value 거짓 및 불일치 경로 도달
+            }
+            (void)root->Attribute(attr->Name(), value); // [gapfuzz-llm] Attribute(name, value)를 직접 호출해 1639행 분기를 퍼징
+        }
+    } catch (...) { // [gapfuzz-llm] 예외는 무시하고 계속 진행
+    }
     return 0;
 }
```
