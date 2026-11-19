# 제안 검증 — official_v2-r1 → official_v3-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | XMLDocument::Parse · xml | 미적용 | 1 | 0 |
| 2 | XMLDocument::DeleteNode · node | 적용 | 2 | 2 |
| 3 | XMLElement::Attribute · value | 적용 | 1 | 1 |
| 4 | XMLNode::Value | 적용 | 1 | 1 |
| 5 | XMLNode::InsertEndChild · addThis | 적용 | 1 | 1 |

**적용한 제안 기준: 막혀 있던 분기 5개 중 5개가 열림**

## 1. `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(27행, 29행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `!xml` (수정 전: 한 번도 참 아님)

## 2. `XMLDocument::DeleteNode(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLDocument::Clear`, `XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `node`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 열림 (5/5) — `XMLDocument::DeleteNode(XMLNode *)` 2333행 조건 `node == 0` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLDocument::DeleteNode(XMLNode *)` 2337행 조건 `node->_parent` (수정 전: 한 번도 참 아님)

## 3. `XMLElement::Attribute(const char *, const char *) const`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLElement::ParseAttributes`)에서만 불립니다. 내부 호출은 2번째 인자 `value`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 값(null 포함)을 넘겨 보세요
- 열림 (5/5) — `XMLElement::Attribute(const char *, const char *) const` 1639행 조건 `!value` (수정 전: 한 번도 거짓 아님)

## 4. `XMLNode::Value() const`를 `XMLDocument` 객체에서 부른 적이 없습니다(조건 `this->ToDocument()`가 한쪽으로만 감) → 하네스가 `XMLDocument` 객체에서 이 API를 불러 보세요
- 열림 (5/5) — `XMLNode::Value() const` 856행 조건 `this->ToDocument()` (수정 전: 한 번도 참 아님)

## 5. `XMLNode::InsertEndChild(XMLNode *)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`XMLNode::ParseDeep`)에서만 불립니다. 내부 호출은 1번째 인자 `addThis`를 한 가지 방식으로만 넘기므로 → 하네스가 직접 불러 다른 상태의 객체(트리에 연결된 노드, 다른 문서의 노드, null 등)를 넘겨 보세요
- 열림 (5/5) — `XMLNode::InsertEndChild(XMLNode *)` 934행 조건 `addThis->_document != _document` (수정 전: 한 번도 참 아님)

