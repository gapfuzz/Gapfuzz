# 크래시 원인 귀속 — fuzz

- 바이너리: `/home/claude/gapfuzz/out/bugs/del/stateful_v3/fuzz`
- 크래시 입력 1개 → 서로 다른 크래시 1개 (스택 기준으로 묶음)
- 입력마다 3번씩 다시 실행해 재현 여부 확인

| 분류 | 개수 | 다음 조치 |
|---|---:|---|
| ⓐ 라이브러리 결함 의심 | 1 | 최소화·재현 후 라이브러리 개발자에게 보고 검토 |

## 1. ⓐ 라이브러리 결함 의심 (확신 강) — ub: member access within null pointer of type 'XMLNode'
- 판단 근거: 오류 지점과 메모리 할당·해제가 모두 라이브러리 코드
  - 오류 지점: `tinyxml2::XMLDocument::DeleteNode` @ third_party/tx_del/tinyxml2.cpp:2353 (library)
- 오류 스택(우리 코드만): `tinyxml2::XMLDocument::DeleteNode [library]` → `LLVMFuzzerTestOneInput [harness]`
- 재현: 3/3
- sanitizer 요약: `UndefinedBehaviorSanitizer: undefined-behavior /home/claude/gapfuzz/third_party/tx_del/tinyxml2.cpp:2353:15`
- 입력 파일 1개: `crash-0908d7e8b0bd89eec192d766ee100111a946a0f4`
- 다음 조치: 최소화·재현 후 라이브러리 개발자에게 보고 검토

