# LLM 하네스 수정 — expat/official_parsebuffer, 제안 3

- 모델: `claude-sonnet-5-5`
- 제안: `XML_SetHashSalt16Bytes(XML_Parser, const uint8_t *)`의 2번째 인자 `entropy`에 하네스가 null을 넘긴 적이 없습니다(72행) → nullptr도 넘겨 보세요
- 겨냥한 분기: 1개

| 시도 | 결과 | 열림 | 제안별 열림 | 크래시 귀속 | 토큰(입력/출력) |
|---:|---|---:|---|---|---|
| 1 | 통과 | 1/1 | 3: 1/1 | - | 3406/2263 |

**채택 후보: 시도 1** (`harnesses/expat/llm/official_parsebuffer_combined/try1.c`). 사람이 읽고 넣으세요.

```diff
--- 수정 전
+++ 시도 1
@@ -69,7 +69,9 @@
   uint8_t entropy[16];
   memcpy(entropy, &first, sizeof(first));
   memcpy(entropy + sizeof(first), &second, sizeof(second));
-  XML_SetHashSalt16Bytes(p, entropy);
+  // 입력 첫 바이트의 최하위 비트가 1이면 entropy에 NULL을 넘기고, 아니면 기존 값을 넘김
+  // (XML_SetHashSalt16Bytes는 NULL entropy를 문서상 허용하며 XML_FALSE를 반환함)
+  XML_SetHashSalt16Bytes(p, (data[0] & 1) ? NULL : entropy); // [gapfuzz-llm] entropy == NULL 분기를 도달시키기 위해 입력 첫 바이트로 NULL을 고르게 함
   (void)sip24_valid;
 
   XML_SetUserData(p, p);
```
