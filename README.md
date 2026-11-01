# gapfuzz — 하네스 갭 분석기

퍼징 하네스가 라이브러리의 무엇을 놓치고 있는지, **그 원인이 하네스의 어느 줄에 있는지** 찾아 주는 도구입니다.

- llvm-cov는 "몇 번째 줄이 실행 안 됨"까지만 알려줍니다.
- Fuzz Introspector는 "어느 함수·분기가 막혔는지"를 보여줍니다.
- gapfuzz는 거기서 한 걸음 더 가서 **"하네스 161행이 항상 같은 객체를 넘겨서 이 분기 5개가 막혔다"**처럼
  하네스 코드 수준의 원인과 고칠 곳을 알려 주고, 고친 뒤 실제로 열렸는지 검증합니다.
  크래시가 나면 그것이 하네스 탓인지 라이브러리 탓인지도 자동으로 가립니다.

TinyXML2로 시작해 pugixml, expat, cJSON, jsoncpp, json-c, zlib, libyaml까지 8개 라이브러리에 적용했습니다. 다른 라이브러리는 `targets/<이름>.json` 설정 파일 하나로 빌드·퍼징·분석을 돌릴 수 있습니다(`scripts/tgt.py`).

> **팀 실험(라이브러리 6개 × 1시간 × 10회)은 [EXPERIMENTS.md](EXPERIMENTS.md)를 보세요.** 환경 맞추기(Docker), 라이브러리 고르기, 실행, 결과 올리기까지 명령어 순서대로 있습니다.

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

실험 수치는 **Ubuntu 24.04 + clang 18.1.3**에서 냈습니다. 같은 숫자를 보려면 이 환경을 쓰세요(Docker 이미지 또는 Ubuntu 24.04/WSL2).

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

### 짧은 실험 (120초 × 5회)

조건: 하네스마다 120초 × 5회, 같은 회차는 같은 퍼저 시드, OSS-Fuzz `xml.dict`, ASan+UBSan.
커버리지는 라이브러리 소스(`tinyxml2.cpp`, `tinyxml2.h`)만 집계. 값은 중앙값 [최솟값–최댓값].
자세한 표와 그래프는 `samples/repeat/`.

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

### 딕셔너리 후보 (`dict`)

공식 하네스의 "라이브러리 내부" 판정 분기에서 토큰 22개를 뽑아 OSS-Fuzz `xml.dict`에 더하고, 다른 시드(2000+회차)로 120초 × 5회 비교했습니다(`samples/repeat/stats_dict.md`).

- 겨냥한 분기 중 BOM 검사(400·401행)는 기존 딕셔너리로 5회 중 2~3회 막혔지만 새 딕셔너리로는 5회 모두 열렸고, 425행은 1회 열렸습니다.
- 470행은 열리지 않았고, 539행은 앞 검사 때문에 도달 불가능한 방어 코드라 열리지 않는 것이 맞습니다.
- 전체 분기 커버리지는 42.13% → 42.40%로 통계적으로 유의하지 않습니다(p=0.095). **겨냥한 분기 몇 개를 여는 정도의 작은 효과**입니다.

### 버그 재발견

이미 고쳐진 버그가 있는 TinyXML2 옛 버전(버그를 고친 커밋의 바로 앞)을 꺼내, 하네스마다 600초 × 5회 퍼징해 처음 찾기까지 걸린 시간을 쟀습니다(`scripts/bug_bench.py`, 결과 `out/bugs/*/results.json`).

| 버그 | 성격 | 공식 | 스테이트풀 | 스테이트풀 v3 |
|---|---|---|---|---|
| #1048 `DeleteNode(nullptr)` 세그폴트 (aba13c5에서 수정) | 공식 하네스가 부르지 않는 API, null 인자 | 0/5 | 0/5 | **5/5, 1초 이하** |
| CVE-2024-50614/50615 문자 참조 assert (494735d에서 수정) | Parse 경로, assert (디버그 빌드에서 측정) | **5/5, 5–18초** | 0/5 (다른 assert에 먼저 걸림) | 빌드 불가 (그 시점 API에 없는 옵션 사용) |

- v3의 null 전달은 도구의 "null을 넘긴 적 없음" 제안을 적용한 것이고, 이 제안은 버그 재발견 실험 전에 나왔습니다. 크래시 귀속은 이 크래시를 "라이브러리 결함"으로 분류했습니다(유지보수자가 라이브러리를 고친 것과 일치).
- CVE는 하네스가 아니라 **빌드 설정의 사각지대**였습니다. TinyXML2의 assert는 `TINYXML2_DEBUG`를 정의해야 켜지는데 OSS-Fuzz의 빌드(`projects/tinyxml2/build.sh`, Makefile 사용)는 정의하지 않습니다. 같은 입력(`<a b="&#x111111111;" b="1"/>`)을 일반 빌드에 넣으면 ASan·UBSan 오류가 0건입니다.
- 스테이트풀 하네스는 디버그 빌드에서 빈 이름 요소를 출력하는 경로의 다른 assert(`StrPair::GetStr`의 `_end`)에 매번 먼저 걸렸습니다.
- 검토했지만 뺀 버그: `TIXML_VSCPRINTF`의 null format(e48a131)은 protected 함수라 공개 API로 닿지 않고, 2021년 assert(9efb6b0)는 `LoadFile`을 두 번 불러야 드러나 세 하네스 모두 닿지 않습니다.

### 다른 라이브러리: pugixml, cJSON

OSS-Fuzz 공식 하네스(pugixml `tests/fuzz_parse.cpp`, cJSON `fuzzing/cjson_read_fuzzer.c`)를 분석하고, "고칠 곳" 제안을 적용한 `official_v2`로 120초 × 5회 비교했습니다(`samples/verify/`, `samples/repeat/stats_pugixml.md`, `stats_cjson.md`).

| 라이브러리 | 공개 API | 고칠 곳 | 적용 | 막혀 있던 분기 열림 | 대조군 | 분기 커버리지 |
|---|---:|---:|---:|---:|---:|---|
| pugixml (C++) | 349 | 4 | 3 | **29/33** | 0/1 | 17.44% → 20.19% (5회 모두, p=0.0079) |
| cJSON (C) | 78 | 5 | 4 | **5/7** | 0/1 | 44.97% → 45.45% (p=0.15, 유의하지 않음) |

- pugixml의 가장 큰 제안: 공식 하네스는 비트 플래그인 파싱 옵션을 기본·`parse_minimal`·`parse_full` 세 조합으로만 시험해, 내부 파서의 분기 26개가 막혀 있었습니다. 옵션을 입력으로 고르게 하자 24개가 열렸습니다.
- 적용 과정에서 TinyXML2에서는 드러나지 않던 분석기 한계를 고쳤습니다: 공개 API가 짧고 처리가 내부 함수에 있는 구조(`--internal-branches`, 다단계 인자 추적), 이름 붙은 const 상수, C 언어(네임스페이스 없음, C 모드 AST).
- cJSON에서 안 열린 2개는 도구의 오판입니다. `cJSON_ParseWithOpts(NULL)`은 함수 첫 줄의 null 검사에서 돌아가므로 안쪽 `ParseWithLengthOpts`의 null 검사에는 닿지 않습니다. 다단계 추적이 경로의 앞선 조건을 고려하지 않는 한계입니다.

### jsoncpp, zlib (2026-10-30 추가)

같은 절차로 두 라이브러리를 더 붙였습니다(`targets/jsoncpp.json`, `targets/zlib.json`). 공개 API가 헤더 여러 개, 구현이 소스 여러 개로 나뉜 구조라
`analyze`의 `--header`·`--source`를 여러 번 받도록 고쳤습니다. 하네스는 OSS-Fuzz 공식(jsoncpp `src/test_lib_json/fuzz.cpp`, zlib `zlib_uncompress_fuzzer.cc`)입니다.

| 라이브러리 | 적용한 제안 | 막혀 있던 분기 중 열림 | 대조군 | 분기 커버리지 (2분 × 5회 중앙값) |
|---|---:|---:|---:|---|
| jsoncpp (C++) | 2 | 6/8 | 0/1 | 28.44% → 29.06% (p = 0.0079) |
| zlib (C) | 3 | 9/11 | 0/1 | 18.98% → 21.06% (p = 0.0079) |

- 새 판정 DIRECT_CALL이 TinyXML2를 보고 만든 뒤 처음 보는 두 라이브러리에서도 나왔고 맞았습니다(zlib `inflate`의 `flush`: 7/7 열림, jsoncpp `Value(Int)`).
- zlib에서 안 열린 2개는 도구의 오판입니다. `uncompress`가 내부에서 만드는 지역 변수(`sourceLen`)를 하네스 인자 탓으로 묶었고, `destLen == NULL`은 값이 아니라 null을 넘겨야 열립니다.
- jsoncpp에 제안을 처음 적용했을 때 매 실행이 즉시 죽었습니다. 음수 `stackLimit`에 `newCharReader`가 `Json::LogicError`를 던졌는데 하네스가 받지 않은 것입니다.
  크래시 귀속에 **잡히지 않은 C++ 예외** 규칙을 추가해 "하네스 버그(확신 강)"로 판정하게 했고(예전에는 "의도된 assert"), 하네스를 고쳐 다시 돌렸습니다(`samples/triage_jsoncpp/`).
- 결과: `samples/verify/{jsoncpp,zlib}_official_to_v2.md`, `samples/repeat/stats_{jsoncpp,zlib}.md`.

**라이브러리 5개 합계: 적용한 제안 28개가 겨냥한 분기 85개 중 75개가 열림, 적용하지 않은 제안의 분기는 7개 중 0개.**

### expat, json-c, libyaml (2026-11-01 추가)

OSS-Fuzz 공식 하네스(expat `xml_parse_fuzzer.c`, json-c `tokener_parse_ex_fuzzer.cc`, libyaml `libyaml_parser_fuzzer.c`)로 같은 절차를 밟았습니다.
expat·json-c는 cmake가 만드는 설정 헤더가 필요해 `harnesses/<이름>/cfg/`에 넣었고, 빌드와 같은 `-D` 정의를 AST 분석에도 넘기도록 `analyze --define`을 추가했습니다.

| 라이브러리 | 적용한 제안 | 막혀 있던 분기 중 열림 | 대조군 | 분기 커버리지 (2분 × 5회 중앙값) |
|---|---:|---:|---:|---|
| expat (C) | 3 | 6/7 | 0/1 | 31.01% → 32.43% (p = 0.016) |
| json-c (C) | 4 | 4/5 | 0/2 | 41.12% → 41.39% (p = 0.55, 차이 없음) |
| libyaml (C) | – | 고칠 곳 0개 | – | 37.4% (공개 API 50개 중 44개를 호출 안 함) |

- **새 라이브러리에서 오판이 드러났고 규칙 두 개로 고쳤습니다.** 처음 분석에서 "고칠 곳"이 겨냥한 분기가 libyaml 169개, expat 19개였는데
  대부분 "하네스가 `&parser`를 항상 같은 객체로 넘김" 탓으로 묶여 있었습니다. 실제로는 ① 메모리 할당 실패·크기 넘침을 처리하는 분기이거나
  ② 라이브러리가 상태를 쌓는 객체의 필드에 달린 분기였습니다. 둘 다 하네스 인자를 바꿔도 열리지 않습니다.
  - 새 판정 `ALLOC_FAIL`: 실패 쪽이 한 번도 안 간 조건이 `SIZE_MAX`·`INT_MAX` 넘침 검사이거나, 조건이 부르는 함수가 결국 `malloc`·`realloc`(또는 `…_malloc` 래퍼)을 부르거나, 할당 래퍼 함수 안의 실패 검사일 때. 고칠 곳에서 뺍니다.
  - 상태 객체 규칙: 조건이 매개변수를 `p->필드`나 다른 함수의 인자로만 쓰고(포인터 값 자체는 안 봄), 그 타입이 가상 함수 없는 구조체면 "같은 객체" 판정을 내리지 않습니다.
    가상 함수가 있는 객체(TinyXML2 `XMLVisitor`)는 다른 구현을 넘기면 동작이 바뀌므로 그대로 둡니다.
  - 기존 5개 라이브러리 9개 하네스를 다시 분석해 **고칠 곳 목록이 하나도 바뀌지 않음**을 확인했습니다. 판정 정확도 숫자도 그대로입니다.
- **libyaml은 고칠 곳이 0개**입니다. 공식 하네스가 파싱 이벤트만 읽고 끝나서, 빠진 것은 하네스 줄의 인자가 아니라 로더·에미터·문서 API를 아예 부르지 않는 것입니다(호출 안 함 44/50).
- **json-c 크래시 귀속 사례 2번째**: 제안 5(`json_object_array_shrink`에 음수)를 그대로 넣자 매 실행이 `json_abort`로 죽었습니다.
  크래시 귀속에 "하네스가 직접 부른 공개 API가 입구의 인자 검사에서 명시적으로 abort" 규칙을 더해 **하네스 버그(확신 중)**로 판정하게 했고(예전에는 "의도된 assert"),
  하네스가 0 이상만 넘기도록 고쳤습니다. 그래서 이 제안이 겨냥한 `empty_slots < 0` 분기는 열 수 없습니다. 도구가 "열면 라이브러리가 종료하는 분기"를 아직 가려내지 못하는 한계입니다(`samples/triage_json-c/`).
- 결과: `samples/verify/{expat,json-c}_official_to_v2.md`, `samples/repeat/stats_{expat,json-c}.md`.

**제안을 적용한 라이브러리 7개 합계: 적용한 제안 35개가 겨냥한 분기 97개 중 85개가 열림, 적용하지 않은 제안의 분기는 10개 중 0개.**

**안정성** (`scripts/stability.py` → `samples/verify/stability.md`, 기존 결과만으로 계산):
- 겨냥한 분기는 수정 전 대표 1회(r1)만이 아니라 **5회 모두에서 막혀 있었다** (공식 하네스 기준 76/76).
- 열린 분기는 **5회 모두 열렸다** (85/85). 안 열린 분기와 대조군은 5회 모두 안 열렸다. 1–4회만 열린 "운 좋은" 분기는 0개.
- 한계: 회당 120초로 짧고, TinyXML2 밖 라이브러리는 장시간 실험을 하지 않았다. 정답 판단(어떤 분기가 막혔나)은 도구 자신의 커버리지 기준이다.

### 최신 버전에서 새 버그 찾기

라이브러리 3개 최신 버전을 제안 반영 하네스로 1시간씩 퍼징(`scripts/hunt.sh`): TinyXML2(stateful_auto) 2,308만 회, pugixml(official_v2) 6,096만 회,
cJSON(official_v2) 8,852만 회 실행, **크래시 0건**. 새 버그는 없었고, 하네스 쪽 가짜 크래시도 없었습니다(`samples/bugs/hunt_latest.md`).

## LLM(Claude API)으로 하네스 수정 (`gapfuzz llmfix`)

사람이 하네스를 고쳐 쓰던 단계를 Claude API에 맡기고, 결과를 gapfuzz가 검사합니다(`gapfuzz/llmfix.py`).

```bash
export ANTHROPIC_API_KEY=...                       # 키는 환경 변수로만 읽고 파일에 남기지 않음
python3 -m gapfuzz llmfix zlib official --list      # 고칠 곳 목록
python3 -m gapfuzz llmfix zlib official --fix 4     # 제안 4를 Claude에게 맡기고 검사
python3 -m gapfuzz llmfix zlib official --fix 4 --mock a.cpp,b.cpp   # 키 없이 흐름 시험
python3 scripts/llm_eval.py                         # 라이브러리 5개의 고칠 곳 전체 평가 → samples/llm/
```

흐름: 하네스 코드·제안·막힌 라이브러리 분기 코드·규칙을 보냄 → 고친 하네스 전체를 받음 → 컴파일 → 60초 × 2회 퍼징 →
겨냥한 분기가 열렸나(verify) → 크래시 귀속(triage). 실패하면 컴파일 오류, 아직 막힌 분기, "하네스 버그" 판정 근거를 같은 대화로 돌려주고
최대 3번까지 다시 받습니다. 통과한 수정안은 `out/llm/<라이브러리>/<하네스>_fix<번호>/`에 diff와 보고서로 남고, 사람이 읽고 넣습니다.

**평가 (claude-sonnet-5-5, 라이브러리 7개, `samples/llm/summary.md`)**

| 지표 | 값 |
|---|---|
| 통과한 제안 | 44/45 (첫 시도 42) |
| 겨냥한 분기 중 열림 | 100/108 |
| 사람도 적용한 제안 35개 | 사람 85/97, Claude 89/97 |
| 걸러 낸 실패 | 컴파일 실패 1번(다음 시도에 고침), 하네스 탓 크래시 0번 |
| 토큰 | 입력 약 21만, 출력 약 18만 |

- Claude 쪽 검사는 60초 × 2회, 사람 쪽은 120초 × 5회라 Claude에게 불리한 조건입니다. 대신 Claude는 검사 결과를 보고 최대 3번 다시 고쳤습니다.
- cJSON `ParseWithOpts(NULL)`: 사람이 못 연 분기(앞선 null 검사가 먼저 걸러 냄)를, 아직 막혔다는 피드백을 받은 Claude가 안쪽 `ParseWithLengthOpts`를 직접 불러 열었습니다.
- 유일한 실패는 json-c `json_object_array_shrink`의 `empty_slots < 0` 분기입니다. 세 번 모두 Claude가 "음수는 `json_abort`로 프로세스를 끝내는 잘못된 인자"라며 넘기지 않았고, 사람도 같은 이유로 열지 않았습니다(도구가 '열면 종료되는 분기'를 아직 못 가려냄).
- 하네스와 라이브러리 일부 코드가 Anthropic으로 전송됩니다. 비공개 코드는 `call_claude`를 로컬 모델 호출로 바꿔 끼우면 됩니다.
- 후보 하네스는 `harnesses/<라이브러리>/llm/` 아래에 생깁니다.

## 사이트

`site/`는 프로젝트 소개 겸 결과 탐색 페이지입니다. 라이브러리 이름을 입력하면 분석해 둔 결과(공개 API 분류, 막힌 분기와 원인, 고칠 곳, 고친 뒤 검증)를 보여 주고,
직접 돌린 `gap.json`을 올려 같은 화면으로 볼 수도 있습니다. 브라우저 안에서 빌드·퍼징은 하지 않습니다.

```bash
python3 scripts/export_site.py                       # site/data.json
python3 site/build_site.py <PretendardVariable.ttf> <Outfit[wght].ttf>   # site/index.html (파일 하나)
```

## 판정 정확도 점검

막힌 분기마다 사람이 TinyXML2 소스와 하네스를 직접 읽고 정답을 달아, 도구의 원인 판정과 비교했습니다
(`samples/audit/`, 재현: `python3 scripts/audit.py <gap.json> samples/audit/audit_labels.json`).

정답은 H(하네스를 고치면 열림), I(입력 내용으로 열어야 함), D(하네스로 열 수 없는 방어 분기) 세 가지입니다.

| 대상 | 판정 정확도 | 고칠 곳 정밀도 | 고칠 곳 재현율 |
|---|---:|---:|---:|
| 스테이트풀, 개선 전 | 72% (44/61) | 100% (15/15) | 37% (15/41) |
| 스테이트풀, 개선 후 | 98% (60/61) | 100% (19/19) | 46% (19/41) |
| **공식 하네스 (개선에 쓰지 않은 데이터)** | **70% (14/20)** | **100% (4/4)** | **40% (4/10)** |
| 스테이트풀, DIRECT_CALL 추가 후 | 100% (61/61) | 100% (20/20) | 49% (20/41) |
| 공식 하네스, DIRECT_CALL 추가 후 (*이 데이터를 보고 만든 규칙*) | 95% (19/20) | 100% (9/9) | 90% (9/10) |

- **정밀도는 두 하네스 모두 100%**: "고칠 곳"이라고 한 것은 모두 실제로 하네스를 고치면 열리는 분기였습니다.
- **재현율은 40% 안팎**: 하네스로 열 수 있는 분기의 절반 넘게는 "고칠 곳" 목록에 오르지 않습니다.
  그중 상당수는 "인자는 바뀌지만 맞는 값이 안 나옴"으로 분류되어 조언은 맞게 나오지만 목록에서는 빠집니다.
- 점검에서 찾은 두 패턴(지역 변수를 거친 값, 값의 범위를 좁힌 인자)을 고쳐 스테이트풀 정확도가 72% → 97%로 올랐습니다.
  다만 **같은 데이터를 보며 고친 수치라 낙관적**이고, 개선에 쓰지 않은 공식 하네스의 70%가 더 현실적인 값입니다.
- 남은 오판은 두 종류입니다.
  1. 하네스의 **동작 순서**에 달린 경우 — 예: 하네스가 노드를 만들면 항상 바로 트리에 붙여서 `Clear`의 "연결 안 된 노드" 분기가 안 열림.
  2. ~~하네스가 **직접 부르지 않는 공개 API**를 라이브러리가 내부에서만 정해진 방식으로 부르는 경우~~ — 새 판정 `DIRECT_CALL`로 해결(아래).

### 새 판정: DIRECT_CALL (라이브러리만 부르는 공개 API를 하네스가 직접 안 부름)

공식 하네스 점검에서 틀린 6개 중 5개가 같은 유형이었습니다. 공개 API인데 하네스는 한 번도 직접 부르지 않고, 라이브러리가 내부에서만
한 가지 방식으로 부릅니다(예: `Attribute(name, value)`의 `value`는 내부 호출에서 항상 null, `DeleteNode`에는 항상 트리에서 떨어진 노드).
판정 조건(`gapfuzz/causes.py` `_direct_callable`, `receiver_type_cause`):
- 공개 API이고, 하네스에 그 API의 호출 지점이 없고, 라이브러리 내부 호출로는 실행되며
- 내부 호출 지점이 그 인자를 모두 상수·기본값으로 넘기거나, 인자가 라이브러리 객체(노드 등)의 포인터·참조일 때
  (문자열·바이트·정수 포인터처럼 입력 내용을 담는 인자는 제외 → 입력으로 열어야 하는 분기를 잘못 고칠 곳으로 내지 않음)
- 또는 조건이 `this->ToDocument()`처럼 받는 객체의 실제 타입 검사일 때 → 그 타입 객체에서 부르라고 제안

이 규칙은 공식 하네스 점검 결과를 보고 만들었으므로 위 95%·90%는 낙관적입니다. 그래서 **제안대로 하네스를 고쳐 실제로 열리는지** 따로 확인했습니다.
`harnesses/official_v3.cpp`(official_v2 + DIRECT_CALL 제안 4개 적용, 120초 × 5회):

| 제안 | 막혀 있던 분기 | 열림 |
|---|---:|---:|
| `DeleteNode`를 직접 불러 null·트리에 연결된 노드 넘기기 | 2 | 2 |
| `Attribute(name, value)`에 value 넘기기 | 1 | 1 |
| `Value()`를 문서 객체에서 부르기 | 1 | 1 |
| `InsertEndChild`에 다른 문서의 노드 넘기기 | 1 | 1 |
| (대조군) 적용 안 한 제안: `Parse`에 null 넘기기 | 1 | 0 |

라인 38.2% → 40.1%, 분기 43.1% → 45.4% (5회 모두, p = 0.0079). pugixml·cJSON에서는 이 판정이 한 번도 나오지 않아 오탐도 없었습니다.
상세: `samples/verify/official_v2_to_v3.md`, `samples/repeat/stats_official_v2_vs_v3.md`, `samples/audit/audit_*_direct_call.md`.
- 정답 라벨은 도구 개발자(이 저장소 작성자)가 달았습니다. `scripts/label_kit.py`로 도구 판정을 가린 시트(`labeling/`)를 만들어 두었고,
  팀원 두 명이 독립적으로 단 정답의 일치도(Cohen's kappa)와 합의 정답으로 다시 잴 예정입니다.
- 표본이 작습니다. "고칠 곳 정밀도 100%"는 23개(4 + 19) 중 틀린 것이 없었다는 뜻으로 읽어야 합니다.

### 크래시 귀속 정확도: 실제 크래시 9건

TinyXML2 실제 크래시 9건으로 쟀습니다(`tests/triage_real/`, 결과 `tests/triage_real/results.md`). 정답은 실제로 누가 고쳤는지로 정했습니다.

| 종류 | 건수 | 예전 규칙 | 지금 규칙 |
|---|---:|---:|---:|
| 하네스 오용 (Clear·delete 뒤 사용, NUL 없는 버퍼, SetValue 임시 문자열) | 4 | 1 | 4 |
| 라이브러리가 커밋으로 고친 버그 (DeleteNode null, CVE assert, 깊은 중첩 스택 오버플로, 2021년 assert) | 4 | 4 | 4 |
| 크래시 아님 | 1 | 1 | 1 |

예전 규칙은 NUL 없는 버퍼를 넘긴 하네스 버그를 **라이브러리 결함으로 잘못 분류**했고(새 ASan 할당 머리말을 못 읽음), Clear·delete 뒤 사용 2건은 UBSan 메모 줄 때문에 스택을 못 읽어 판단 보류였습니다.
TinyXML2는 노드를 자체 메모리 풀로 관리해 ASan이 해제를 못 보므로, 지운 노드를 쓰는 하네스 버그는 UBSan의 vptr 검사로 드러납니다.
"해제 API로 지운 객체를 다시 씀" 규칙은 메모리 풀 때문에 TinyXML2 실제 데이터에는 나오지 않아, 힙 객체를 쓰는 가짜 라이브러리 사례(`test_triage.sh`의 D·F·I)로 검증했습니다.

### 크래시 사례: 하네스 버그

ASan을 처음 켰을 때 스테이트풀 하네스에서 `XMLPrinter::Write`의 heap-use-after-free가 잡혔습니다.
`triage`는 이것을 **ⓑ 하네스 버그 의심(확신 강, 3/3 재현)**으로 분류하고, 근거로 해제 위치가 하네스 236행(임시 문자열 소멸)임을 보여 줍니다.

- 원인: `SetValue(str, staticMem=true)`는 문자열을 복사하지 않고 포인터만 저장합니다(`SetInternedStr`).
  하네스가 반복마다 사라지는 임시 문자열을 넘겨, 이후 출력할 때 해제된 메모리를 읽었습니다.
- 수정: `staticMem=true`일 때는 프로그램 끝까지 살아 있는 정적 문자열만 넘김.
- 검증: 크래시 입력 2개(같은 크래시로 묶임)가 수정 전에는 재현되고, 수정 후에는 정상 실행됩니다.
  입력과 수정 전 하네스, 분류 결과는 `samples/harness_bug_crashes/`에 있습니다.

퍼징 크래시를 바로 라이브러리 버그로 보고하면 안 되는 이유를 보여 주는 사례입니다.

## 관련 도구와의 차이

OSS-Fuzz의 **Fuzz Introspector**는 하네스별 정적 도달성과 실행 커버리지를 비교하고, 커버리지를 막는 분기(fuzz blocker)를
막는 코드 양 순으로 보여 줍니다. 새로 노릴 함수 추천, 하네스 초안 생성, 딕셔너리 생성, 실행 결과 비교도 합니다.
"어디가 막혔나"를 보여 주는 진단 범위는 Fuzz Introspector가 훨씬 넓고 성숙합니다.

| | Fuzz Introspector | gapfuzz |
|---|---|---|
| 알려주는 것 | 어느 함수·분기가 막혔나 | 하네스의 **어느 줄, 어느 인자** 때문에 막혔나 |
| 막힌 원인 판단 | 위치까지 제시, 원인은 사용자가 판단 | 고정 인자 / 안 부른 설정 API / 값 범위 / 직접 안 부른 공개 API / 라이브러리 내부로 자동 분류 |
| 결과물 | 진단 리포트, 새 하네스 템플릿 | 기존 하네스의 수정 목록 + 적용 후 검증 |
| 크래시 | 다루지 않음 | 하네스 버그 vs 라이브러리 결함 자동 귀속 |
| 실행 환경 | LLVM LTO 계측, OSS-Fuzz 인프라(Docker) | clang + llvm-cov만, Docker 불필요 |
| 분석 단위 | 프로젝트의 모든 함수 | 헤더의 공개 API |

참고로 Fuzz Introspector의 fuzz blocker 결과 위에서 원인을 분류하려는 연구(FuzzGauge, Purdue 석사논문, 2025)가 있습니다.
gapfuzz의 원인 추적은 하네스 호출 지점의 인자까지 내려간다는 점이 다릅니다.
같은 하네스·같은 커버리지에 Fuzz Introspector를 직접 돌려 봤습니다(`scripts/run_fi.sh`, 결과 `samples/compare_fuzz_introspector.md`).
이 환경에서는 LLVM 방식(OSS-Fuzz 기본)은 빌드할 수 없어 **소스 분석 방식**만 돌렸고, 그 방식은 TinyXML2에서 하네스가 닿는 함수 3개, 막힌 분기 0개를 보고했습니다.
FI 공식 사례 문서(jsonnet)에도 "콜 트리를 보면 인자가 항상 상수로 고정돼 있다"는 원인을 사람이 찾는 과정이 나오며, 이 단계를 gapfuzz가 자동화합니다.
LLVM 방식과의 정량 비교는 Docker 환경에서 다시 해야 합니다(`python3 infra/helper.py introspector tinyxml2 --seconds=120`).

참고
- Fuzz Introspector 문서: https://fuzz-introspector.readthedocs.io/
- OSS-Fuzz 연동 안내: https://google.github.io/oss-fuzz/advanced-topics/fuzz-introspector/
- FuzzGauge: https://hammer.purdue.edu/articles/thesis/_b_FuzzGauge_A_method_to_automatically_determine_reasons_for_a_fuzz_blocker_b_/28541426

## 한계

- **원인 추적은 짧은 데이터 흐름까지**입니다. 조건이 읽는 매개변수·필드(게터 포함), 한 번 거친 지역 변수, 필드를 설정하는 생성자·대입문,
  그리고 라이브러리 내부 호출을 통한 매개변수 전달까지 봅니다. 포인터 별칭, 하네스의 **호출 순서·상태**에 달린 조건은 못 봅니다.
- **다단계 추적은 경로의 앞선 조건을 고려하지 않습니다.** 바깥 함수가 먼저 null을 거르면 안쪽의 null 검사에는 닿지 않는데도 제안할 수 있습니다(cJSON 사례).
- **"고칠 곳" 재현율**은 DIRECT_CALL 추가 전 공식 하네스 40%, 추가 후 90%(규칙을 만든 데이터라 낙관적)입니다. 스테이트풀은 49%로, "인자는 바뀌지만 맞는 값이 안 나옴"(VARIES)이 목록에서 빠지기 때문입니다. 목록에 오른 29개는 틀린 것이 없었지만 표본이 작고, 정답을 도구 작성자가 달았습니다.
- **"하네스가 인자를 고정"은 하네스 쪽 사실**이고, 그 인자를 바꾸면 반드시 열린다는 보장은 아닙니다. 그래서 `verify`로 확인합니다.
- **매크로로 만든 조건**은 AST 위치가 맞지 않아 "출처 불명"이 되기 쉽습니다(pugixml 막힌 분기 99개 중 14개).
- **도달 불가능한 방어 코드**를 따로 가려내지 않습니다(TinyXML2 539·544행). 이런 분기는 "라이브러리 내부"로 남습니다.
- **딕셔너리 후보**는 조건식의 상수·경계값만 봅니다. 여러 조건을 함께 만족해야 하는 입력(예: 같은 속성 두 번 + 8자리 이상 문자 참조)은 만들지 못합니다.
- **연산 초안**은 TinyXML2의 클래스별 객체 얻는 방법을 표로 갖고 있어 다른 라이브러리에는 그 표를 새로 써야 합니다. 단순 타입 인자만 채웁니다.
- **가상 함수**는 이름·시그니처가 같은 부모 메서드로 근사 연결합니다. 함수 포인터 호출은 추적하지 않습니다.
- **공개 API 판정**은 헤더 위치와 public 접근 지정자 기준입니다. 문서상 내부용 클래스는 `--internal-class`로 제외합니다
  (기본: StrPair, DynArray, MemPool, MemPoolT). 순수 가상 함수와 소멸자는 제외합니다. 오버로드와 const/비const 버전은 서로 다른 API로 셉니다.
- **크래시 귀속은 "의심"**입니다. API 문서의 사용 규칙(예: 이 인자는 null 금지)은 읽지 못하므로 null 접근은 약한 판정으로 둡니다.
  실제 데이터는 9건뿐입니다. `--harness`에는 바이너리를 빌드할 때 쓴 하네스 경로를 줘야 합니다.
- `build.sh`는 시스템에 compiler-rt가 있으면 ASan+UBSan을 켭니다. 없으면 ASan 없이 빌드해 메모리 오류를 크래시로 잡지 못합니다.
- 퍼징 실험은 2코어 클라우드 환경에서 돌렸습니다. 장시간 실험은 다른 작업과 동시에 돌리지 않았습니다.

## 다음 단계

- 팀원 독립 라벨링으로 판정 정확도와 일치도(kappa) 재측정 (`scripts/label_kit.py`)
- Fuzz Introspector LLVM 방식(OSS-Fuzz Docker)과 사례별 비교 (소스 분석 방식은 완료)
- 호출 순서·상태 의존 분기, 앞선 조건으로 막히는 경로를 원인 추적에 추가하고 연산 자동 생성을 확장
- OSS-Fuzz 기여: pugixml 파싱 옵션 개선안, TinyXML2 하네스 개선안과 assert를 켠 빌드 제안
- 24시간 실험
