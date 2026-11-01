# 판정 정확도 점검 — stateful-r1

막힌 분기 61개를 사람이 소스와 대조해 단 정답과 비교했습니다.

| 지표 | 값 |
|---|---:|
| 판정 정확도 | 44/61 (72%) |
| 고칠 곳 정밀도 | 15/15 (100%) |
| 고칠 곳 재현율 | 15/41 (37%) |

| 도구 판정 \ 정답 | H (하네스) | I (입력) | D (방어) |
|---|---:|---:|---:|
| FIXED | 14 | 0 | 0 |
| SETTER_NOT_CALLED | 1 | 0 | 0 |
| VARIES | 9 | 0 | 0 |
| INTERNAL | 17 | 15 | 5 |

## 틀린 판정

- `XMLComment::ShallowEqual|1329|14` 조건 `comment` — 도구 INTERNAL, 정답 H: 하네스가 복제본과 원본만 비교(163행) → 종류가 다른 노드와 비교해야 열림
- `XMLComment::ShallowEqual|1329|25` 조건 `XMLUtil::StringEqual( comment->Value(), Value() )` — 도구 INTERNAL, 정답 H: 위와 같음 (값이 다른 노드와 비교)
- `XMLDeclaration::ShallowEqual|1378|14` 조건 `declaration` — 도구 INTERNAL, 정답 H: 위와 같음
- `XMLDeclaration::ShallowEqual|1378|29` 조건 `XMLUtil::StringEqual( declaration->Value(), Value() )` — 도구 INTERNAL, 정답 H: 위와 같음
- `XMLDocument::Clear|2233|9` 조건 `_unlinked.Size()` — 도구 INTERNAL, 정답 H: 하네스가 만든 노드를 항상 바로 연결함 → 연결하지 않은 노드를 남긴 채 Clear해야 열림
- `XMLElement::ShallowEqual|2127|10` 조건 `other` — 도구 INTERNAL, 정답 H: 위와 같음
- `XMLElement::ShallowEqual|2127|19` 조건 `XMLUtil::StringEqual( other->Name(), Name() )` — 도구 INTERNAL, 정답 H: 위와 같음
- `XMLElement::ShallowEqual|2132|22` 조건 `b` — 도구 INTERNAL, 정답 H: 속성 개수가 다른 요소와 비교해야 열림
- `XMLElement::ShallowEqual|2133|18` 조건 `!XMLUtil::StringEqual( a->Value(), b->Value() )` — 도구 INTERNAL, 정답 H: 속성 값이 다른 요소와 비교해야 열림
- `XMLElement::ShallowEqual|2139|14` 조건 `a` — 도구 INTERNAL, 정답 H: 속성 개수가 다른 요소와 비교해야 열림
- `XMLElement::ShallowEqual|2139|19` 조건 `b` — 도구 INTERNAL, 정답 H: 위와 같음
- `XMLNode::PreviousSiblingElement|1070|14` 조건 `element` — 도구 INTERNAL, 정답 H: 하네스가 첫 번째 자식 요소에서만 호출(197행) → 앞 형제 요소가 있는 노드에서 호출해야 열림
- `XMLPrinter::VisitEnter|2983|10` 조건 `element.Parent()` — 도구 INTERNAL, 정답 H: 하네스가 트리에 연결된 노드만 출력 → 부모 없는 요소를 출력해야 열림
- `XMLText::ShallowEqual|1281|14` 조건 `text` — 도구 INTERNAL, 정답 H: 하네스가 복제본과 원본만 비교 → 다른 노드와 비교해야 열림
- `XMLText::ShallowEqual|1281|22` 조건 `XMLUtil::StringEqual( text->Value(), Value() )` — 도구 INTERNAL, 정답 H: 위와 같음
- `XMLUnknown::ShallowEqual|1426|14` 조건 `unknown` — 도구 INTERNAL, 정답 H: 위와 같음
- `XMLUnknown::ShallowEqual|1426|25` 조건 `XMLUtil::StringEqual( unknown->Value(), Value() )` — 도구 INTERNAL, 정답 H: 위와 같음
