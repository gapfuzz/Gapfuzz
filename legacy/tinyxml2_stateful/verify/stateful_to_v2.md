# 제안 검증 — stateful-r1 → stateful_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | XMLComment::ShallowClone · document | 적용 | 5 | 5 |
| 2 | XMLDocument::Accept · visitor | 적용 | 4 | 4 |
| 3 | XMLDocument::Parse · nBytes | 적용 | 2 | 2 |
| 4 | XMLDocument::Print · streamer | 미적용 | 1 | 0 |
| 5 | XMLHandle::XMLHandle · node | 적용 | 1 | 1 |
| 6 | XMLPrinter::XMLPrinter · aposInAttributes | 적용 | 1 | 1 |
| 7 | XMLDocument::SetBOM · useBOM | 적용 | 1 | 1 |
| 8 | XMLConstHandle::XMLConstHandle · node | 미적용 | 1 | 0 |
| 9 | XMLDocument::Parse · xml | 미적용 | 1 | 0 |
| 10 | XMLDocument::DeleteNode · node | 미적용 | 1 | 0 |
| 11 | XMLDocument::XMLDocument · whitespaceMode | 미적용 | 1 | 0 |

**적용한 제안 기준: 막혀 있던 분기 14개 중 14개가 열림**

## 1. `XMLComment::ShallowClone(XMLDocument *) const`의 1번째 인자 `document`를 하네스가 고정합니다(161행에서 항상 같은 객체 `&doc`) → 퍼저 입력으로 바꾸세요 (같은 호출이 5개 구현 클래스에 영향: `XMLComment::ShallowClone`, `XMLDeclaration::ShallowClone`, `XMLElement::ShallowClone`, `XMLText::ShallowClone`, `XMLUnknown::ShallowClone`)
- 열림 (5/5) — `XMLText::ShallowClone(XMLDocument *) const` 1268행 조건 `!doc` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLComment::ShallowClone(XMLDocument *) const` 1317행 조건 `!doc` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLDeclaration::ShallowClone(XMLDocument *) const` 1366행 조건 `!doc` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLUnknown::ShallowClone(XMLDocument *) const` 1414행 조건 `!doc` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLElement::ShallowClone(XMLDocument *) const` 2112행 조건 `!doc` (수정 전: 한 번도 참 아님)

## 2. `XMLDocument::Accept(XMLVisitor *) const`의 1번째 인자 `visitor`를 하네스가 고정합니다(172행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요 (같은 호출이 2개 구현 클래스에 영향: `XMLDocument::Accept`, `XMLElement::Accept`)
- 열림 (5/5) — `XMLDocument::Accept(XMLVisitor *) const` 781행 조건 `visitor->VisitEnter( *this )` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `XMLDocument::Accept(XMLVisitor *) const` 783행 조건 `!node->Accept( visitor )` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLElement::Accept(XMLVisitor *) const` 2152행 조건 `visitor->VisitEnter( *this, _rootAttribute )` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `XMLElement::Accept(XMLVisitor *) const` 2154행 조건 `!node->Accept( visitor )` (수정 전: 한 번도 참 아님)

## 3. `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(44행에서 기본값, 233행에서 기본값) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `nBytes == 0` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLDocument::Parse(const char *, size_t)` 2463행 조건 `nBytes == static_cast<size_t>(-1)` (수정 전: 한 번도 거짓 아님)

## 4. `XMLDocument::Print(XMLPrinter *) const`의 1번째 인자 `streamer`를 하네스가 고정합니다(171행에서 항상 같은 객체 `&printer`) → 퍼저 입력으로 바꾸세요
- 여전히 막힘 (0/5) — `XMLDocument::Print(XMLPrinter *) const` 2488행 조건 `streamer` (수정 전: 한 번도 거짓 아님)

## 5. `XMLHandle::XMLHandle(XMLNode *)`의 1번째 인자 `node`를 하네스가 고정합니다(188행에서 항상 같은 객체 `&doc`) (필드 `_node`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요 (또는 `XMLHandle::XMLHandle(XMLNode &)`로도 이 값을 바꿀 수 있음)
- 열림 (5/5) — `XMLHandle::FirstChildElement(const char *)` 2075행 조건 `_node` (수정 전: 한 번도 거짓 아님)

## 6. `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)`의 4번째 인자 `aposInAttributes`를 하네스가 고정합니다(170행에서 기본값, 178행에서 기본값) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)` 2605행 조건 `(aposInAttributes == ESCAPE_APOS_CHARS_IN_ATTRIBUTES)` (수정 전: 한 번도 거짓 아님)

## 7. 하네스가 `XMLDocument::SetBOM(bool)`를 부르지 않아 1번째 인자 `useBOM` 값이 들어가지 않습니다 (필드 `_writeBOM`를 거쳐 조건에 쓰임) → 호출을 추가하세요
- 열림 (5/5) — `XMLPrinter::VisitEnter(const XMLDocument &)` 2973행 조건 `doc.HasBOM()` (수정 전: 한 번도 참 아님)

## 8. `XMLConstHandle::XMLConstHandle(const XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(190행) (필드 `_node`를 거쳐 조건에 쓰임) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `XMLConstHandle::LastChildElement(const char *) const` 2157행 조건 `_node` (수정 전: 한 번도 거짓 아님)

## 9. `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(44행, 233행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `!xml` (수정 전: 한 번도 참 아님)

## 10. `XMLDocument::DeleteNode(XMLNode *)`의 1번째 인자 `node`에 하네스가 null을 넘긴 적이 없습니다(150행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `XMLDocument::DeleteNode(XMLNode *)` 2333행 조건 `node == 0` (수정 전: 한 번도 참 아님)

## 11. `XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 `COLLAPSE_WHITESPACE`, `PRESERVE_WHITESPACE`, `기본값` 중에서만 고릅니다(42행, 46행) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 여전히 막힘 (0/5) — `XMLDocument::Identify(char *, XMLNode **, bool)` 752행 조건 `WhitespaceMode() == PEDANTIC_WHITESPACE` (수정 전: 한 번도 참 아님)

