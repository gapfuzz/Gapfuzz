# 버그 재발견 실험 결과

- `deletenode_results.json`: #1048 DeleteNode(nullptr) (수정 커밋 aba13c5의 바로 앞 버전), 하네스마다 600초 × 5회
- `cve_results.json`: CVE-2024-50614/50615 (수정 커밋 494735d의 바로 앞 버전, `-DTINYXML2_DEBUG` 빌드), 하네스마다 600초 × 5회
- `deletenode_v3_triage.md`: v3가 찾은 크래시의 귀속 결과 (라이브러리 결함)
- `cve_input.xml`: CVE의 assert에 닿는 최소 입력. 같은 속성을 두 번 쓰면 파싱만 해도 문자 참조가 처리된다.
  디버그 빌드에서는 assert 실패, 일반 빌드(OSS-Fuzz와 같은 설정)에서는 ASan·UBSan 오류가 0건이다.

재현: `scripts/setup.sh --extra` 후 `python3 scripts/bug_bench.py --bug del ...`, `--bug cve ...` (README 참고)
