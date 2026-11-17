# LLM 하네스 수정 — pugixml/official, 제안 2

- 모델: `claude-sonnet-5-5`
- 제안: 하네스가 `xml_node::xml_node(xml_node_struct *)`를 부르지 않아 1번째 인자 `p` 값이 들어가지 않습니다 (필드 `_root`를 거쳐 조건에 쓰임) → 호출을 추가하세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|
| 1 | 실패 | 0/1 | - | 1182/2012 |
| 2 | 통과 | 1/1 | - | 2023/2489 |

**채택 후보: 시도 2** (`harnesses/pugixml/llm/official_fix2/try2.cpp`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 2
@@ -10,5 +10,20 @@
 	doc.load_buffer(Data, Size, pugi::parse_minimal);
 	doc.load_buffer(Data, Size, pugi::parse_full);
 
+	uint8_t mode = Size > 0 ? Data[0] % 3 : 0; // [gapfuzz-llm] 입력 첫 바이트로 xml_node 생성자에 넘길 포인터 종류를 고름
+	pugi::xml_node_struct *p = NULL; // [gapfuzz-llm] 0이면 널 포인터(빈 노드)로 원래처럼 노드 없는 경우도 유지
+	if (mode == 1) p = doc.internal_object(); // [gapfuzz-llm] 문서 루트 구조체를 _root로 쓰는 경우를 추가
+	else if (mode == 2) p = doc.first_child().internal_object(); // [gapfuzz-llm] 파싱된 첫 자식 노드(없으면 널)를 _root로 쓰는 경우를 추가
+
+	try
+	{
+		pugi::xml_node node(p); // [gapfuzz-llm] 제안대로 xml_node(xml_node_struct*) 생성자 호출 (포인터는 doc 소유라 유효함)
+		node.first_child(); // [gapfuzz-llm] 생성된 노드의 _root를 실제로 사용
+		node.append_buffer(Data, Size); // [gapfuzz-llm] 생성한 노드의 _root로 append_buffer를 호출해 doc->extra_buffers 목록에 항목을 추가, 소멸 시 extra 루프가 참이 되게 함 (널/비요소 노드는 오류 상태만 반환)
+	}
+	catch (...)
+	{
+	}
+
 	return 0;
 }
```
