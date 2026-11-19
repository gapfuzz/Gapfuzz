# 제안 검증 — official-r1 → official_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | XMLDocument::Parse · nBytes | 적용 | 2 | 2 |
| 2 | XMLDocument::XMLDocument · whitespaceMode | 적용 | 1 | 1 |
| 3 | XMLDocument::Parse · xml | 미적용 | 1 | 0 |

**적용한 제안 기준: 막혀 있던 분기 3개 중 3개가 열림**

## 1. `XMLDocument::Parse(const char *, size_t)`의 2번째 인자 `nBytes`를 하네스가 고정합니다(13행에서 기본값) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `nBytes == 0` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XMLDocument::Parse(const char *, size_t)` 2463행 조건 `nBytes == static_cast<size_t>(-1)` (수정 전: 한 번도 거짓 아님)

## 2. `XMLDocument::XMLDocument(bool, Whitespace)`의 2번째 인자 `whitespaceMode`를 하네스가 고정합니다(12행에서 기본값) (필드 `_whitespaceMode`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `XMLDocument::Identify(char *, XMLNode **, bool)` 752행 조건 `WhitespaceMode() == PEDANTIC_WHITESPACE` (수정 전: 한 번도 참 아님)

## 3. `XMLDocument::Parse(const char *, size_t)`의 1번째 인자 `xml`에 하네스가 null을 넘긴 적이 없습니다(13행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `XMLDocument::Parse(const char *, size_t)` 2459행 조건 `!xml` (수정 전: 한 번도 참 아님)

