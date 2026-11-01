# Fuzz Introspector와 비교 (TinyXML2 공식 하네스, 같은 커버리지)

Fuzz Introspector(FI, OSS-Fuzz가 쓰는 하네스 분석 도구, 커밋 8bc858d·2026-05-27)를 gapfuzz와 같은 입력으로 돌려 봤다.
입력: `third_party/tinyxml2`, `harnesses/official.cpp`, `out/repeat/official/r1`(120초 1회)의 커버리지.

## 실행할 수 있었던 범위

FI에는 두 가지 방식이 있다.

| 방식 | 필요한 것 | 이 환경 |
|---|---|---|
| LLVM 플러그인 방식 (OSS-Fuzz 기본) | FI 전용 LLVM 패스를 LLVM 소스와 함께 빌드 | **불가**: LLVM 개발 헤더 패키지를 받을 수 없음(패키지 서버 접근 불가) |
| 소스 분석 방식 (tree-sitter, 컴파일 불필요) | 파이썬 패키지 | **가능**: 파이썬 의존성을 GitHub 소스에서 빌드해 실행 (`scripts/run_fi.sh`) |

그래서 아래 정량 비교는 **소스 분석 방식의 FI**와의 비교다. OSS-Fuzz가 실제로 쓰는 LLVM 방식의 FI는 정확도가 더 높으므로,
그 방식과의 정량 비교는 최종 발표 전에 OSS-Fuzz 환경(도커)에서 다시 해야 한다.

## 결과 (소스 분석 방식 FI vs gapfuzz)

| 항목 | FI (소스 분석 방식) | gapfuzz |
|---|---|---|
| 하네스에서 닿을 수 있는 함수 | 3개 (C++ 메서드 호출을 거의 따라가지 못함) | 공개 API 303개를 분류 (호출 그래프는 clang AST로 구성) |
| 막힌 분기 목록 (fuzz blocker) | 0개 (분기 정보는 LLVM 방식에서만 나옴) | 20개 (각각 원인 판정) |
| 막힌 이유 | 없음 | 하네스가 고정한 인자, 부르지 않은 API, 직접 안 부른 공개 API 등 |
| 하네스에서 고칠 곳 | 없음 | 9곳 (사람 정답과 비교해 9/9 맞음) |
| 추천 | "더 퍼징할 함수" 1개 (`XMLElement::ParseDeep`) | 하네스 줄 번호 + 바꿀 인자 |

## LLVM 방식 FI와의 차이 (FI 공식 문서 기준)

FI의 LLVM 방식은 "어느 분기에서 막혔는지(fuzz blocker)와 그 뒤에 막힌 코드의 양"을 표로 보여 준다.
**왜 막혔는지는 사람이 콜 트리를 보고 찾는다.** FI 공식 사례 문서(`doc/CaseStudies.md`, jsonnet 사례)에는

> "Looking into the fuzz target call tree reveals that the argument of type `EvalKind` is always set to a static value (`REGULAR` in this case)."

라고, 사람이 콜 트리를 보고 "하네스가 인자를 상수로 고정했다"는 원인을 찾아낸 과정이 나온다.
gapfuzz는 이 단계(막힌 조건 → 하네스가 넘긴 인자 → 고칠 줄)를 자동으로 하고(`FIXED` 판정),
고친 뒤 실제로 열렸는지 다시 확인(`verify`)하는 것까지 한다. 이것이 FI와 겹치지 않는 부분이다.

## 한계

- LLVM 방식 FI와의 정량 비교는 하지 못했다 (위 이유).
- FI는 여러 언어·OSS-Fuzz 전체 프로젝트를 다루고, gapfuzz는 C/C++ 라이브러리 3개에서만 확인했다.
