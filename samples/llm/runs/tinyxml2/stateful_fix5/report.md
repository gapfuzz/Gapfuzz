# LLM 하네스 수정 — tinyxml2/stateful, 제안 5

- 모델: `claude-sonnet-5-5`
- 제안: `XMLHandle::XMLHandle(XMLNode *)`의 1번째 인자 `node`를 하네스가 고정합니다(188행에서 항상 같은 객체 `&doc`) (필드 `_node`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요 (또는 `XMLHandle::XMLHandle(XMLNode &)`로도 이 값을 바꿀 수 있음)
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6281/5528 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix5/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -185,7 +185,7 @@
             break;
         }
         case 15: {  // 핸들 탐색
-            XMLHandle h(&doc);
+            XMLHandle h(fdp.ConsumeBool() ? static_cast<XMLNode *>(&doc) : (fdp.ConsumeBool() ? cur : static_cast<XMLNode *>(nullptr)));  // [gapfuzz-llm] 핸들 노드가 항상 &doc라 _node가 거짓이 되지 않았으므로 &doc·cur·nullptr(XMLHandle이 허용하는 빈 핸들)를 입력으로 고름
             h.FirstChildElement(fdp.ConsumeBool() ? str : nullptr).FirstChild().NextSiblingElement().ToElement();
             XMLConstHandle ch(cur);
             ch.LastChildElement().PreviousSibling().ToNode();
```
