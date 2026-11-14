# LLM 하네스 수정 — tinyxml2/stateful, 제안 8

- 모델: `claude-sonnet-5-5`
- 제안: `XMLConstHandle::XMLConstHandle(const XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(190행) (필드 `_node`를 거쳐 조건에 쓰임) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6244/5151 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix8/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -187,7 +187,7 @@
         case 15: {  // 핸들 탐색
             XMLHandle h(&doc);
             h.FirstChildElement(fdp.ConsumeBool() ? str : nullptr).FirstChild().NextSiblingElement().ToElement();
-            XMLConstHandle ch(cur);
+            XMLConstHandle ch(fdp.ConsumeBool() ? cur : nullptr);  // [gapfuzz-llm] XMLConstHandle의 null 노드 분기(_node가 거짓)를 타도록 입력에 따라 nullptr도 전달
             ch.LastChildElement().PreviousSibling().ToNode();
             break;
         }
```
