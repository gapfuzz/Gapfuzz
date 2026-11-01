# 제안 검증 — expat-official-r1 → expat-official_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | XML_ParserReset · encoding | 적용 | 1 | 1 |
| 2 | XML_ExternalEntityParserCreate · context | 적용 | 5 | 4 |
| 3 | XML_Parse · s | 적용 | 1 | 1 |
| 4 | XML_SetHashSalt16Bytes · entropy | 미적용 | 1 | 0 |

**적용한 제안 기준: 막혀 있던 분기 7개 중 6개가 열림**

## 1. `XML_ParserReset(XML_Parser, const XML_Char *)`의 2번째 인자 `encoding`를 하네스가 고정합니다(84행에서 항상 `0`) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `XML_ParserReset(XML_Parser, const XML_Char *)` 1668행 조건 `encodingName` (수정 전: 한 번도 참 아님)

## 2. `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)`의 2번째 인자 `context`를 하네스가 `"e1"`, `0` 중에서만 고릅니다(101행, 108행) (라이브러리 내부 `setContext`를 거쳐 조건에 쓰임) → 나머지 값도 나오게 하세요
- 여전히 막힘 (0/5) — `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8298행 조건 `context == NULL` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8306행 조건 `*s == CONTEXT_SEP` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8314행 조건 `*s != XML_T` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8345행 조건 `*context != CONTEXT_SEP` (수정 전: 한 번도 거짓 아님)
- 열림 (5/5) — `XML_ExternalEntityParserCreate(XML_Parser, const XML_Char *, const XML_Char *)` 8356행 조건 `*context != XML_T` (수정 전: 한 번도 참 아님)

## 3. `XML_Parse(XML_Parser, const char *, int, int)`의 2번째 인자 `s`에 하네스가 null을 넘긴 적이 없습니다(78행, 79행) → nullptr도 넘겨 보세요
- 열림 (5/5) — `XML_Parse(XML_Parser, const char *, int, int)` 2339행 조건 `(s == NULL)` (수정 전: 한 번도 참 아님)

## 4. `XML_SetHashSalt16Bytes(XML_Parser, const uint8_t *)`의 2번째 인자 `entropy`에 하네스가 null을 넘긴 적이 없습니다(71행) → nullptr도 넘겨 보세요
- 여전히 막힘 (0/5) — `XML_SetHashSalt16Bytes(XML_Parser, const uint8_t *)` 2316행 조건 `entropy == NULL` (수정 전: 한 번도 참 아님)

