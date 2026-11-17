# LLM 하네스 수정 — tinyxml2/official, 제안 6

- 모델: `claude-sonnet-5-5`
- 제안: `XMLNode::Value() const`를 `XMLDocument` 객체에서 부른 적이 없습니다(조건 `this->ToDocument()`가 한쪽으로만 감) → 하네스가 `XMLDocument` 객체에서 이 API를 불러 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 1185/870 |

**채택 후보: 시도 1** (`harnesses/llm/official_fix6/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -11,5 +11,6 @@
     std::string data_string(reinterpret_cast<const char *>(data), size);
     XMLDocument doc;
     doc.Parse(data_string.c_str());
+    const char *doc_value = doc.Value(); (void)doc_value; // [gapfuzz-llm] XMLDocument 객체에서 Value()를 호출해 ToDocument()가 참이 되는 분기(null 반환)를 실행. 반환값은 역참조하지 않음
     return 0;
 }
```
