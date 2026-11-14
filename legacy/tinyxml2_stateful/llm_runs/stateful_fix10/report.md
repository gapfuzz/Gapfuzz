# LLM 하네스 수정 — tinyxml2/stateful, 제안 10

- 모델: `claude-sonnet-5-5`
- 제안: `XMLDocument::DeleteNode(XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(150행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 통과 | 1/1 | - | 6131/5432 |

**채택 후보: 시도 1** (`harnesses/llm/stateful_fix10/try1.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -147,7 +147,7 @@
         case 10:  // 자식 하나 삭제 (cur 자신·조상은 건드리지 않음)
             if (XMLNode *c = NthChild(cur, fdp.ConsumeIntegralInRange<unsigned>(0, nchild))) {
                 if (fdp.ConsumeBool()) cur->DeleteChild(c);
-                else doc.DeleteNode(c);
+                else doc.DeleteNode(fdp.ConsumeBool() ? nullptr : c);  // [gapfuzz-llm] DeleteNode는 null을 허용하므로 입력에 따라 nullptr도 넘겨 'node == 0' 분기를 실행 (원래 자식 노드도 계속 전달)
             }
             break;
         case 11:  // 자식 전부 삭제
```
