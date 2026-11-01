# 판정 정확도 점검 — official-r1

막힌 분기 20개를 사람이 소스와 대조해 단 정답과 비교했습니다.

| 지표 | 값 |
|---|---:|
| 판정 정확도 | 14/20 (70%) |
| 고칠 곳 정밀도 | 4/4 (100%) |
| 고칠 곳 재현율 | 4/10 (40%) |

| 도구 판정 \ 정답 | H (하네스) | I (입력) | D (방어) |
|---|---:|---:|---:|
| FIXED | 3 | 0 | 0 |
| NARROW | 1 | 0 | 0 |
| INTERNAL | 6 | 8 | 2 |

## 틀린 판정

- `XMLDocument::DeleteNode|2333|8` 조건 `node == 0` — 도구 INTERNAL, 정답 H: 하네스가 DeleteNode에 null을 넘긴 적 없음(150행)
- `XMLDocument::DeleteNode|2337|9` 조건 `node->_parent` — 도구 INTERNAL, 정답 H: 하네스가 DeleteNode를 직접 부르지 않음 → 트리에 연결된 노드를 지우면 열림 (라이브러리는 연결 안 된 노드만 지움)
- `XMLDocument::Clear|2233|9` 조건 `_unlinked.Size()` — 도구 INTERNAL, 정답 H: 하네스가 만든 노드를 항상 바로 연결함 → 연결하지 않은 노드를 남긴 채 Clear해야 열림
- `XMLElement::Attribute|1639|10` 조건 `!value` — 도구 INTERNAL, 정답 H: 하네스가 Attribute를 직접 부르지 않음 → 두 번째 인자(value)를 넘겨 부르면 열림 (내부 호출은 항상 null)
- `XMLNode::Value|856|10` 조건 `this->ToDocument()` — 도구 INTERNAL, 정답 H: 하네스가 문서 노드의 Value()를 부르지 않음 → doc.Value()를 부르면 열림
- `XMLNode::InsertEndChild|934|10` 조건 `addThis->_document != _document` — 도구 INTERNAL, 정답 H: 다른 문서(other)의 노드를 삽입해야 열림 — 도구 조언과 일치
