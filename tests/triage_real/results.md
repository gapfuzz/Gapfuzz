# 실제 크래시로 본 크래시 귀속 정확도

사례 9개. 예전 규칙 6/9, 새 규칙 9/9.

| 사례 | 크래시 종류 | 정답 | 예전 규칙 | 새 규칙 (확신) | 정답 근거 |
|---|---|---|---|---|---|
| misuse_clear_then_use | ub: member call on address 0x521000000100 which does not point to an object of type  | HARNESS | ✗ UNCLEAR | ✓ HARNESS (강) | Clear() 뒤에 문서가 소유한 요소를 씀 (사용 규칙 위반) |
| misuse_delete_doc | ub: member call on address 0x521000000100 which does not point to an object of type  | HARNESS | ✗ UNCLEAR | ✓ HARNESS (강) | 문서를 delete한 뒤 그 요소를 씀 (사용 규칙 위반) |
| misuse_unterminated | heap-buffer-overflow | HARNESS | ✗ LIBRARY | ✓ HARNESS (약) | NUL 없는 버퍼를 길이 없이 넘김 |
| real_setvalue_uaf | heap-use-after-free | HARNESS | ✓ HARNESS | ✓ HARNESS (강) | 실제 퍼징에서 나온 크래시: SetValue(str, true)에 곧 사라질 문자열 |
| lib_deletenode_null | ub: member access within null pointer of type 'XMLNode' | LIBRARY | ✓ LIBRARY | ✓ LIBRARY (약) | 이슈 #1048, 커밋 aba13c5에서 라이브러리가 고침 |
| lib_cve_assert | deadly signal | ASSERT | ✓ ASSERT | ✓ ASSERT (강) | CVE-2024-50614/50615, 커밋 494735d에서 라이브러리가 고침. 같은 속성을 두 번 쓰면 파싱만 해도 닿음 (assert는 디버그 빌드에서만 켜짐) |
| lib_stack_overflow | stack-overflow | RESOURCE | ✓ RESOURCE | ✓ RESOURCE (강) | 깊은 중첩 재귀, 커밋 d946dda에서 깊이 제한 추가 |
| lib_assert_2021 | deadly signal | ASSERT | ✓ ASSERT | ✓ ASSERT (강) | 커밋 9efb6b0에서 라이브러리가 고친 assert 실패 (입력은 그 커밋의 테스트 파일 xmltest-5330.xml) |
| not_a_crash | 재현 안 됨 | UNCLEAR | ✓ UNCLEAR | ✓ UNCLEAR (약) | 정상 입력 (재현 안 됨) |
