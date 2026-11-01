# gapfuzz — 하네스 갭 분석기

퍼징 하네스가 라이브러리의 무엇을 놓치고 있는지, **그 원인이 하네스의 어느 줄에 있는지** 찾아 주는 도구입니다.

- llvm-cov는 "몇 번째 줄이 실행 안 됨"까지만 알려줍니다.
- Fuzz Introspector는 "어느 함수·분기가 막혔는지"를 보여줍니다.
- gapfuzz는 거기서 한 걸음 더 가서 "하네스 161행이 항상 같은 객체를 넘겨서 이 분기 5개가 막혔다"처럼
  하네스 코드 수준의 원인과 고칠 곳을 알려 주고, 고친 뒤 실제로 열렸는지 검증합니다.
  크래시가 나면 그것이 하네스 탓인지 라이브러리 탓인지도 자동으로 가립니다.

TinyXML2로 시작해 pugixml, expat, cJSON, jsoncpp, json-c, zlib, libyaml까지 8개 라이브러리에 적용했습니다. 다른 라이브러리는 `targets/<이름>.json` 설정 파일 하나로 빌드·퍼징·분석을 돌릴 수 있습니다(`scripts/tgt.py`).

> **실험(라이브러리 6개 × 1시간 × 10회)은 [EXPERIMENTS.md](EXPERIMENTS.md)를 보세요.** 환경 맞추기(Docker), 라이브러리 고르기, 실행, 결과 올리기까지 명령어 순서대로 있습니다.

## 기능

| 명령 | 하는 일 |
|---|---|
| `analyze` | 공개 API를 4가지로 분류하고, 막힌 분기마다 **하네스 쪽 원인**을 찾아 "하네스에서 고칠 곳" 목록을 만든다 |
| `verify` | 고칠 곳을 적용한 하네스의 결과와 비교해, 막혀 있던 분기가 **실제로 열렸는지** 확인한다 |
| `triage` | 크래시를 다시 실행해 **하네스 버그 / 라이브러리 결함 / 리소스 상한 / assert**로 분류한다 |
| `diff` | 두 하네스의 API 분류를 비교한다 |
| `stats` | 반복 실행 결과의 중앙값·범위, Mann-Whitney U 검정, 분류 안정성, 그래프 |
| `dict` | 하네스로는 못 여는(입력 내용에 막힌) 분기의 조건식에서 **딕셔너리 후보**를 뽑는다 |
| `ops` | "호출 안 함" API를 **새로 실행될 코드 양으로 순위**를 매기고, 스테이트풀 하네스에 넣을 **연산 코드 초안**을 만든다 |

### 1) 공개 API 분류 (`analyze`)

| 분류 | 의미 | 다음 조치 |
|---|---|---|
| **호출 안 함** | 실행된 코드 어디에서도 이 API로 가는 호출 경로가 없음 | 하네스에 이 API(또는 상위 API) 호출 추가. 퍼징을 오래 돌려도 안 열림 |
| **조건에 막힘** | 실행된 함수 안에 이 API로 가는 호출이 있지만 그 줄까지 도달하지 못함 | 리포트가 가리키는 조건을 만족시키는 입력·상태 |
| **일부 분기 미실행** | API는 실행됐지만 안쪽 조건문이 한 방향으로만 감 | 아래 "하네스에서 고칠 곳" 참고 |
| **완전 도달** | 모든 영역과 분기가 실행됨 | 없음 |

### 2) 하네스에서 고칠 곳 — 막힌 조건의 원인 추적 (`analyze`에 포함)

한 방향으로만 간 조건문마다, 그 조건이 읽는 값이 어디서 오는지 거슬러 올라갑니다.

```
조건식  ──읽는 값──▶  함수 매개변수 ─────────────────────────┐
                     필드(또는 필드를 돌려주는 게터)            │
                        └─▶ 그 필드를 설정하는 생성자·대입문 ──▶ (API, 몇 번째 인자)
                                                               │
                                       하네스의 호출 지점에서 그 인자를 어떻게 넘기나?
```

| 판정 | 뜻 | 예 (TinyXML2 실제 결과) |
|---|---|---|
| **하네스가 인자를 고정** | 하네스가 항상 기본값·상수·같은 객체를 넘김 | 161행 `ShallowClone(&doc)` → `if (!doc)` 분기 5개가 한 번도 안 열림 |
| **값을 정하는 API를 안 부름** | 그 값을 바꾸는 설정 API를 하네스가 부르지 않음 | `SetBOM`을 안 불러서 `if (doc.HasBOM())`이 항상 거짓 |
| **값의 범위를 좁힘** | 하네스가 `cond ? A : B`처럼 몇 개 값 중에서만 고르거나, null 검사인데 null을 넘긴 적이 없음 | 42행이 공백 모드를 2가지 중에서만 골라 PEDANTIC 분기가 안 열림 |
| **인자는 바뀌지만 맞는 값이 안 나옴** | 하네스가 입력으로 바꾸고 있음 → 값 범위·딕셔너리 문제 | `InsertEndChild`의 "다른 문서 노드" 조건 |
| **공개 API를 직접 안 부름** | 공개 API인데 라이브러리 내부에서만 한 가지 방식으로 불림 (하네스는 직접 부르지 않음) | `Attribute(name, value)`의 `value`가 내부 호출에선 항상 null |
| **라이브러리 내부에서 정해짐** | 하네스가 아니라 라이브러리 내부 호출·입력 내용이 정함 | `ConvertUTF32ToUTF8`의 `input` (문자 참조 파싱에서 옴) |

처음 세 판정이 "하네스에서 고칠 곳"이 되고, 하네스 줄 단위로 묶여 리포트 맨 위에 나옵니다.
조건이 지역 변수를 한 번 거쳐도(`comment = compare->ToComment()`) 매개변수까지 따라갑니다.
하네스가 직접 부르지 않는 내부 함수의 매개변수이면, 실행된 라이브러리 내부 호출 지점을 따라 최대 8단계 거슬러 올라가
하네스가 값을 넘기는 공개 API의 인자까지 연결합니다(예: pugixml `load_buffer`의 `options` → `load_buffer_impl` → `xml_parser::parse` → …).
호출 지점마다 서로 다른 상수를 넘기면(예: `parse_minimal`, `parse_full`) "고정"이 아니라 "몇 개 값 중 선택(범위를 좁힘)"으로 판정합니다.
공개 API는 짧고 실제 처리가 내부 함수에 있는 라이브러리는 `--internal-branches`로 내부 함수의 막힌 분기를 가장 가까운 공개 API 아래에 모읍니다.
`switch`의 `case` 분기와 한 줄에 여러 조건이 있는 경우(`a || b || c`)도 조건 하나하나를 따로 봅니다.

### 3) 제안 검증 (`verify`)

수정 전 분석의 "고칠 곳"마다, 그 때문에 막혀 있던 분기가 수정 후에 양쪽으로 실행됐는지 확인합니다.
도구의 제안이 맞았는지 데이터로 보여 주는 단계입니다.

### 4) 크래시 원인 귀속 (`triage`)

크래시 입력을 여러 번 다시 실행해 sanitizer 리포트를 받고, 접근·해제·할당 스택에서
처음 나오는 "우리 코드" 프레임이 하네스인지 라이브러리인지 봅니다.

| 분류 | 판단 근거 |
|---|---|
| ⓐ 라이브러리 결함 의심 | 오류 지점과 할당·해제가 모두 라이브러리 코드. null 포인터 접근은 "약"(API가 null을 허용하는지 확인 필요) |
| ⓑ 하네스 버그 의심 | 하네스가 메모리를 해제했거나, 수명이 끝난 하네스 지역 변수를 씀, 하네스 코드 자체에서 오류, 하네스가 소멸자·Delete류 API로 해제를 요청한 객체를 다른 줄에서 다시 씀, 이미 소멸된 객체를 호출(UBSan vptr), 하네스가 준 버퍼를 라이브러리가 범위 밖으로 읽음(약) |
| ⓒ 리소스 상한 | timeout, out-of-memory, 스택 오버플로, 너무 큰 할당 |
| ⓓ 의도된 assert | 라이브러리의 assert가 실패 |
| 판단 보류 | 재현 안 됨, 근거가 엇갈림 |

같은 버그의 크래시는 서명(오류 종류 + 접근 스택 위쪽 3개의 함수:줄 + 해제 위치)으로 하나로 묶고, 재현 횟수(예: 3/3)를 함께 적습니다.
꼬리 호출 최적화로 스택 프레임이 사라지지 않도록 빌드에 `-fno-optimize-sibling-calls`를 넣습니다.

### 5) 딕셔너리 후보 (`dict`)

원인 추적에서 하네스로 고칠 수 없다고 나온 분기의 조건식에서 퍼저가 직접 만들기 어려운 값을 뽑아 libFuzzer 딕셔너리로 씁니다:
문자·문자열 상수, 같은 포인터의 연속 위치 비교를 이은 바이트 조합(예: BOM `EF BB BF`), 숫자 비교의 경계값(10진·16진 문자열).
이름 붙은 상수는 소스에서 정의를 찾아 값으로 바꾸고, 토큰마다 근거(파일:줄, 조건식)를 주석으로 남깁니다.

### 6) 호출 안 함 API 우선순위와 연산 초안 (`ops`)

"호출 안 함" API마다 호출 그래프로 닿는 아직 실행되지 않은 함수들의 코드 영역 수를 세어 순위를 매기고,
단순 타입 인자만 받는 API는 FuzzedDataProvider로 인자를 채운 `case` 블록을 만들어 스테이트풀 하네스 사본에 넣습니다.
가짜 크래시를 막는 생성 규칙: 노드를 받는 변경 API에는 항상 새로 만든 노드(순환 방지), 문자열에 null 금지,
전역 상태를 바꾸는 Set 계열에는 끝까지 살아 있는 문자열 상수, 크기 인자는 0–64, 파일 입출력·방문자 콜백·연산자는 생성하지 않음.
`scripts/run.sh`에 `HARNESS_SRC`를 주면 퍼징 중 크래시가 나왔을 때 자동으로 실행됩니다.

## 설치

실험 수치는 Ubuntu 24.04 + clang 18.1.3에서 냈습니다. 같은 숫자를 보려면 이 환경을 쓰세요(Docker 이미지 또는 Ubuntu 24.04/WSL2).

```bash
# 방법 A: Docker (Dockerfile 포함)
docker build -t gapfuzz .
docker run --rm -it --cap-add SYS_PTRACE -v "$PWD":/work gapfuzz bash

# 방법 B: Ubuntu 24.04 / WSL2
sudo apt install -y clang llvm libclang-rt-18-dev git python3 python3-scipy

python3 scripts/exp.py doctor                # 환경 점검
scripts/setup.sh                             # TinyXML2와 OSS-Fuzz 딕셔너리 받기
python3 scripts/exp.py fetch pugixml expat cjson jsoncpp json-c zlib libyaml   # 다른 라이브러리 (고정 커밋)
```

배포판에 따라 `clang`만 설치하면 libFuzzer/ASan 런타임(compiler-rt)이 빠질 수 있어서 `libclang-rt-*-dev`를 따로 설치합니다.
런타임이 없으면 `setup.sh`가 LLVM 소스에서 libFuzzer와 커버리지 런타임만 빌드하고, 이 경우 ASan 없이 빌드됩니다.
필수 Python 패키지는 없습니다(`stats`의 검정에는 scipy, 그래프에는 matplotlib가 있으면 씁니다).

## 사용법

```bash
L=third_party/tinyxml2

# 1) 빌드: 퍼징용(fuzz) + 커버리지용(cov) 바이너리
scripts/build.sh harnesses/stateful.cpp out/asan_stateful

# 2) 퍼징 → 커버리지 (120초, 공식 딕셔너리). 크래시가 나면 자동으로 원인 귀속
HARNESS_SRC=harnesses/stateful.cpp scripts/run.sh out/asan_stateful 120 dicts/xml.dict

# 3) 분석 → gap_report.html / gap_report.md / gap.json ("하네스에서 고칠 곳" 포함)
python3 -m gapfuzz analyze --name stateful --header $L/tinyxml2.h --source $L/tinyxml2.cpp \
    --harness harnesses/stateful.cpp --include harnesses/include \
    --coverage out/asan_stateful/coverage.json --out out/asan_stateful/gap

# 4) 반복 실험 (5회 × 120초, 같은 시드) → 통계
scripts/build.sh harnesses/official.cpp out/asan_official
scripts/repeat.sh 5 120 official stateful
python3 -m gapfuzz stats --base official --target stateful --secs 120 \
    --out out/repeat/stats.md --plot out/repeat/coverage_runs.png

# 5) 제안 적용 후 검증
python3 -m gapfuzz verify out/repeat/stateful/r1/gap/gap.json out/repeat/stateful_v2/r*/gap/gap.json \
    --applied 1,2,3,5,6,7 --out out/verify.md

# 6) 크래시 원인 귀속 (직접 돌릴 때)
python3 -m gapfuzz triage out/asan_stateful --binary out/asan_stateful/fuzz \
    --harness harnesses/stateful.cpp --harness-dir harnesses --lib-dir $L --out triage.md

# 7) 딕셔너리 후보 → 기존 딕셔너리와 합친 파일
python3 -m gapfuzz dict out/repeat/official/r*/gap/gap.json --source $L/tinyxml2.cpp --source $L/tinyxml2.h \
    --base dicts/xml.dict --merge --out dicts/xml_gapfuzz_official.dict

# 8) 호출 안 함 API 상위 15개의 연산 초안을 넣은 하네스 사본
python3 -m gapfuzz ops --header $L/tinyxml2.h --source $L/tinyxml2.cpp --harness harnesses/stateful_v3.cpp \
    --include harnesses/include --coverage out/repeat/stateful_v3/r1/coverage.json --top 15 \
    --out harnesses/stateful_auto.cpp --report samples/ops_stateful_v3.md

# 9) 장시간 실험 (중간에 끊겨도 다시 실행하면 이어서 돎)
python3 scripts/long_runs.py --trials 10 --secs 3600 --jobs 2 official stateful stateful_v3
#    24시간 실험: 한 번에 한 구간씩 돌고 끝나므로, 다 끝날 때까지 반복 실행 (진행 상황은 out/day/state.json)
python3 scripts/day_run.py --hours 24 --chunk-min 105 stateful stateful_v3

# 10) 버그 재발견 (scripts/setup.sh --extra로 옛 버전을 받은 뒤)
python3 scripts/bug_bench.py --bug del --secs 600 --trials 5 official stateful stateful_v3

# 11) 다른 라이브러리 (targets/pugixml.json, targets/cjson.json)
python3 scripts/tgt.py build pugixml official official_v2
python3 scripts/tgt.py repeat pugixml official official_v2 --trials 5 --secs 120

# 12) 독립 라벨링: 판정을 가린 시트 → 두 사람 일치도 → 합의 정답
python3 scripts/label_kit.py make out/repeat/official/r1/gap/gap.json out/repeat/stateful/r1/gap/gap.json --out labeling
python3 scripts/label_kit.py agree labeling/sheet_A.csv labeling/sheet_B.csv
python3 scripts/label_kit.py merge labeling/sheet_A.csv labeling/sheet_B.csv --out labeling/consensus.json
```

테스트: `tests/run_all.sh`
- `run_tests.sh` — 호출 경로 분류 (TinyXML2, 짧게 퍼징)
- `test_causes.sh` — 하네스 고정 인자·값 범위 좁힘·지역 변수 추적 (가짜 라이브러리, 결정적)
- `test_triage.sh` — 크래시 원인 귀속 11종 (가짜 라이브러리, 결정적)
- `triage_real/run.py` — 실제 TinyXML2 크래시 9건으로 크래시 귀속 정확도 측정 (`scripts/setup.sh --extra` 필요)

## 폴더 구성

```
gapfuzz/      ast_index.py  clang AST에서 함수·호출·인자·조건식·필드 쓰기 추출
              analyze.py    커버리지와 대조해 API 분류
              causes.py     막힌 조건 → 하네스 원인 추적, 고칠 곳 묶기
              verify.py     제안 적용 후 검증
              triage.py     크래시 원인 귀속
              stats.py      반복 실험 통계·그래프
              report.py     HTML/Markdown 리포트
              dictgen.py    입력 내용에 막힌 분기 → 딕셔너리 후보
              opgen.py      호출 안 함 API 우선순위와 연산 초안
harnesses/    official.cpp      OSS-Fuzz 공식 하네스와 동일 (Parse만 호출)
              official_v2.cpp   공식 하네스에 gapfuzz 제안 2개만 적용 (여전히 파싱만 함)
              stateful.cpp      트리 조작 연산을 입력으로 고르는 하네스
              stateful_v2.cpp   stateful.cpp에 gapfuzz의 제안 6개를 적용한 버전
              stateful_v3.cpp   v2에 '값의 범위를 좁힘' 제안 4개를 더 적용한 버전
              official_v3.cpp   official_v2에 '공개 API를 직접 안 부름' 제안 4개를 적용한 버전
              stateful_auto.cpp v3에 `ops`가 만든 연산 15개를 넣은 버전
              pugixml/ cjson/ jsoncpp/ zlib/ expat/ json-c/ libyaml/  각 라이브러리의 OSS-Fuzz 공식 하네스와 제안 적용판(official_v2)
targets/      pugixml.json  cjson.json  jsoncpp.json  zlib.json  expat.json  json-c.json  libyaml.json   범용 실행기 설정
scripts/      exp.py(팀 실험)  setup.sh  build.sh  run.sh  repeat.sh  long_runs.py(장시간 실험)  day_run.py·day_loop.sh(24시간 실험)  bug_bench.py(버그 재발견)
              export_site.py(사이트 데이터)  tgt.py(다른 라이브러리)  audit.py(판정 정확도)  label_kit.py(독립 라벨링)  run_fi.sh(Fuzz Introspector)
tests/        run_all.sh 외 테스트, fixtures/fakelib (테스트용 가짜 라이브러리), triage_real (실제 크래시 9건)
samples/      실험 결과 예시 (verify, repeat, llm/runs: Claude 수정 diff·보고서, day: 24시간 실험)
experiments/  targets/<라이브러리>.json  1시간 실험에서 확인할 "고칠 곳" 분기 목록
results/      팀 실험 결과 (회차마다 작은 JSON, scripts/exp.py가 만듦)
presentation/ 중간발표 (midterm.src.html → build_deck.py → midterm.html, midterm_backup.pdf)
site/         분석기 사이트 (index.src.html → build_site.py → index.html)
Dockerfile    실험 환경 (Ubuntu 24.04, clang 18.1.3)
```

`out/`(퍼징 산출물)과 `third_party/`(라이브러리 소스)는 git에 올리지 않습니다. 소스는 `scripts/setup.sh`와 `scripts/exp.py fetch`가 고정 커밋으로 받습니다.

## 실험 결과 (TinyXML2)

### 장시간 실험 (1시간 × 10회)

TinyXML2, 하네스마다 1시간 × 10회, 같은 회차는 같은 시드(`scripts/long_runs.py`, 2개씩 동시 실행, 다른 작업 없이). 값은 중앙값 [최솟값–최댓값].

| 하네스 | 라인 | 분기 | 크래시 |
|---|---|---|---|
| official | 38.13% [38.07–38.18] | 42.33% [41.99–42.40] | 0 |
| stateful | 77.51% [77.07–77.69] | 79.76% [78.80–80.30] | 0 |
| stateful_v3 (제안 10개 적용) | 78.46% [78.13–78.57] | 83.08% [82.61–83.56] | 0 |

- official → stateful: 하네스 설계의 효과. 라인·분기 모두 A12 = 1.00, p = 1.1e-05 (10 대 10 정확검정의 최솟값).
- stateful → stateful_v3: 도구 제안의 효과. 라인 +1.0%p, 분기 +3.3%p, 둘 다 A12 = 1.00, p = 1.1e-05. 2분 실험에서는 라인 차이가 유의하지 않았는데, 1시간이면 10회 모두 v3가 더 높다.
- 공개 API 분류: 일부 분기 미실행 36 → 22, 완전 도달 164 → 179.
- 상세: `samples/repeat/stats_long_official_stateful.md`, `samples/repeat/stats_long_stateful_v3.md` (그래프 `long_*.png`)

### 24시간 실험 (stateful vs stateful_v3, 각 1회)

오래 돌리면 도구 없이도 결국 같은 분기가 열리는지 확인하려고 두 하네스를 24시간씩 돌렸다(`scripts/day_run.py`, 하네스마다 CPU 1개).
이 환경은 작업 하나를 2시간까지만 돌릴 수 있어 10·20·30분 뒤 105분 구간으로 이어 붙였다. 코퍼스는 이어지지만 libFuzzer 내부 상태는 구간마다 초기화된다.

| 경과 | stateful 라인 / 분기 | stateful_v3 라인 / 분기 |
|---:|---|---|
| 10분 | 77.51% / 79.76% | 78.46% / 83.02% |
| 1시간 | 77.69% / 80.03% | 78.46% / 83.42% |
| 4.5시간 | 77.69% / 80.16% | 78.46% / 83.42% |
| 24시간 | 77.69% / 80.16% (분기 590/736) | 78.57% / 83.56% (분기 615/736) |

- stateful은 4.5시간 뒤로 더 오르지 않았고, 24시간 값(80.16%)이 v3의 첫 10분(83.02%)보다 낮다. 오래 돌리는 것으로는 못 여는 분기를 제안 적용이 연다.
- 크래시·타임아웃 0. 코퍼스 65,183개 vs 76,083개.
- 한계: 하네스마다 1회라 통계 검정은 없음(통계는 위 1시간 × 10회). 구간마다 libFuzzer 재시작.
- 상세: `samples/day/timeline.md`, `samples/day/timeline.json`


### 공식 하네스 vs 스테이트풀 하네스

| | 공식 (Parse만) | 스테이트풀 | |
|---|---:|---:|---|
| 라인 커버리지 | 37.96% [37.74–38.07] | 76.81% [75.85–76.96] | 5회 모두 스테이트풀이 높음, p=0.0079 |
| 함수 커버리지 | 26.04% | 71.61% | |
| 분기 커버리지 | 41.85% | 77.99% | |
| 공개 API 303개 중 호출 안 함 | 261 | 103 | |
| 크래시 | 0/5 | 0/5 | 하네스 버그 수정 후 |

공식 하네스의 미도달은 거의 전부 "호출 안 함"입니다. 조건에 막힌 게 아니라 하네스가 그 API를 부르지 않아서이고,
퍼징을 오래 돌려도 열리지 않습니다. API 분류는 5회 반복에서 303개 중 302개(공식), 303개(스테이트풀)가 매번 같았습니다.

### "하네스에서 고칠 곳" 제안과 검증

| 하네스 | 제안 수 | 5회 반복에서 매번 같은 제안 |
|---|---:|---|
| 공식 | 2 (+ 개선 후 1) | 예 — `XMLDocument`의 공백 처리 모드가 항상 기본값, `Parse`의 길이 인자가 항상 기본값 |
| 스테이트풀 | 7 | 예 |
| 스테이트풀 v2 (제안 6개 적용) | 1 | 예 — 일부러 적용하지 않은 1개만 남음 |

스테이트풀 하네스의 제안 7개 중 6개를 적용한 `stateful_v2.cpp`로 같은 실험을 반복하고 `verify`로 확인했습니다.

| # | 제안 (하네스 줄) | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | `ShallowClone(&doc)` 항상 같은 객체 (161행) | 적용 | 5 | 5 |
| 2 | `Accept(&printer)` 항상 같은 방문자 (172행) | 적용 | 4 | 4 |
| 3 | `Parse`의 `nBytes` 항상 기본값 (44·233행) | 적용 | 2 | 2 |
| 4 | `Print(&printer)` 항상 같은 객체 (171행) | **미적용** | 1 | 0 |
| 5 | `XMLHandle(&doc)` 항상 같은 객체 (188행) | 적용 | 1 | 1 |
| 6 | `XMLPrinter` 4번째 인자 항상 기본값 (170·178행) | 적용 | 1 | 1 |
| 7 | `SetBOM`을 부르지 않음 | 적용 | 1 | 1 |

**적용한 제안 6개로 막혀 있던 분기 14개가 모두 열렸고, 적용하지 않은 제안 4의 분기만 그대로 막혀 있었습니다.**
4번은 `Print(nullptr)`가 표준 출력으로 찍어 퍼징 로그를 어지럽혀서 일부러 빼 두었고, 결과적으로 대조군 역할을 했습니다.

| | 스테이트풀 | 스테이트풀 v2 | |
|---|---:|---:|---|
| 분기 커버리지 | 77.99% [76.63–78.53] | 78.80% [78.12–80.03] | p=0.032 |
| 함수 커버리지 | 71.61% | 71.88% | p=0.008 |
| 라인 커버리지 | 76.81% | 76.85% | p=0.31 (유의하지 않음) |
| 완전 도달 API | 163 | 173 | |
| 일부 분기 미실행 API | 37 | 28 | |

제안은 특정 분기를 겨냥하기 때문에 전체 라인 커버리지로는 차이가 거의 드러나지 않습니다.
그래서 "막혀 있던 그 분기가 열렸는가"를 직접 확인하는 `verify`가 필요합니다.

이후 판정 정확도 점검(아래)에서 "값의 범위를 좁힘" 판정을 추가하자 제안이 4개 더 나왔고(총 11개, 5회 반복 모두 동일),
이것까지 적용한 `stateful_v3.cpp`로 다시 확인했습니다.

| # | 새 제안 (하네스 줄) | 막혀 있던 분기 | 열림 |
|---:|---|---:|---:|
| 8 | `XMLConstHandle`에 null을 넘긴 적 없음 (190행) | 1 | 1 |
| 9 | `Parse`의 `xml`에 null을 넘긴 적 없음 (44·233행) | 1 | 1 |
| 10 | `DeleteNode`에 null을 넘긴 적 없음 (150행) | 1 | 1 |
| 11 | 공백 처리 모드를 2가지 중에서만 고름 (42행) | 1 | 1 |

**v3에서는 적용한 제안 10개로 막혀 있던 분기 18개가 모두 열렸고, 미적용 1개만 남았습니다.**

| | 스테이트풀 | 스테이트풀 v3 | |
|---|---:|---:|---|
| 분기 커버리지 | 77.99% [76.63–78.53] | 79.89% [79.89–79.89] | 5회 모두 높음, p=0.0079 |
| 함수 커버리지 | 71.61% | 71.88% | p=0.0079 |
| 라인 커버리지 | 76.81% | 76.88% | p=0.31 (유의하지 않음) |
| 완전 도달 API | 163 | 177 | |
| 일부 분기 미실행 API | 37 | 24 | |
| 크래시 | 0/5 | 0/5 | |

### 공식 하네스 제안 검증 (OSS-Fuzz 기여 후보)

공식 하네스에 제안 2개만 최소로 적용한 `official_v2.cpp`(여전히 파싱만 함)로 같은 실험을 했습니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | `Parse`의 `nBytes`가 항상 기본값 | 적용 | 2 | 2 (5/5회) |
| 2 | `XMLDocument`의 공백 처리 모드가 항상 기본값 | 적용 | 1 | 1 (5/5회) |
| 3 | `Parse`의 `xml`에 null을 넘긴 적 없음 (개선된 분석기가 새로 낸 제안) | 미적용 | 1 | 0 |

적용한 제안의 분기 3개가 모두 열렸고, 적용하지 않은 3번만 막혀 있었습니다.
전체 수치는 분기 커버리지 41.85% → 43.09%(p=0.095, 5회로는 유의하지 않음), 라인 커버리지는 차이 없음(p=0.55)입니다.
OSS-Fuzz에 제안한다면 "커버리지가 크게 오른다"가 아니라 **"지금까지 한 번도 시험되지 않던 공백 처리 모드(COLLAPSE·PEDANTIC)와 길이 지정 파싱 경로를 연다"**로 설명하는 것이 정확합니다.
입력 앞 2바이트를 옵션으로 쓰므로 기존 코퍼스와의 호환성은 따로 검토해야 합니다.

### 호출 안 함 API 연산 자동 생성 (`ops`)

`ops`가 v3의 "호출 안 함" API 102개 중 83개에 대해 연산 초안을 만들 수 있었고(나머지는 파일 입출력·방문자 콜백 등),
새로 실행될 코드 영역 수 상위 15개를 넣은 `stateful_auto.cpp`로 120초 × 5회를 돌렸습니다(`samples/repeat/stats_auto.md`, 순위표 `samples/ops_stateful_v3.md`).

| | 스테이트풀 v3 | v3 + 자동 생성 15개 | |
|---|---:|---:|---|
| 라인 커버리지 | 77.32% [76.59–77.91] | 80.60% [80.49–81.07] | 5회 모두 높음, p=0.0079 |
| 분기 커버리지 | 80.43% [79.08–81.79] | 84.51% [84.10–85.46] | 5회 모두 높음, p=0.0079 |
| 호출 안 함 API | 102 | 87 | 넣은 15개가 모두 실행됨 |
| 크래시 | 0/5 | 0/5 | 가짜 크래시 없음 |

생성 규칙을 만들면서 실제로 걸러 낸 위험: `XMLUtil::SetBoolSerialization(str, str)`은 넘긴 포인터를 전역에 저장하므로,
반복마다 사라지는 `str`을 넘기면 예전 `SetValue` 사례와 같은 하네스 버그가 됩니다. 전역 Set 계열에는 문자열 상수만 넘기도록 규칙을 추가했습니다.

