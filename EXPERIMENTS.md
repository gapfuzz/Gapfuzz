# 팀 실험: 라이브러리 6개 × 1시간 × 10회

공식 하네스와 "공식 하네스 + gapfuzz 수정"을 라이브러리마다 1시간씩 10번 돌려 비교합니다.
TinyXML2에서 한 1시간 × 10회 실험을 나머지 라이브러리에도 똑같이 하는 것입니다.

| 라이브러리 | 종류 | 걸리는 시간 (CPU 2개) |
|---|---|---|
| pugixml | XML, C++ | 약 11시간 |
| expat | XML, C | 약 11시간 |
| cjson | JSON, C | 약 11시간 |
| jsoncpp | JSON, C++ | 약 11시간 |
| json-c | JSON, C | 약 11시간 |
| zlib | 압축, C | 약 11시간 |

한 라이브러리는 **한 사람이 한 컴퓨터에서 끝까지** 돌립니다. 같은 회차의 두 하네스를 동시에 돌리기 때문에,
컴퓨터마다 속도가 달라도 한 라이브러리 안의 비교(공식 vs 수정)는 공평합니다.

---

## 1. 환경 맞추기 (처음 한 번)

커버리지 숫자는 컴파일러 버전에 따라 달라지므로 **모두 clang 18.1.3**을 씁니다. 둘 중 하나를 고르세요.

### 방법 A: Docker (권장, 가장 확실하게 같음)

Windows·macOS는 Docker Desktop, Linux는 Docker Engine을 설치한 뒤:

```bash
git clone https://github.com/<팀 계정>/gapfuzz.git
cd gapfuzz
docker build -t gapfuzz .                 # 처음 한 번, 몇 분 걸림

# 이후 모든 명령은 이 줄로 컨테이너 안에서 실행 (아래 문서의 "gf" 자리에 붙여 넣기)
docker run --rm -it --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -e GAPFUZZ_BY="본인 이름" -v "$PWD":/work gapfuzz bash
```

`--cap-add SYS_PTRACE`는 메모리 누수 검사(LeakSanitizer)가 컨테이너 안에서 동작하는 데 필요하고, `--user`는 만든 파일이 내 계정 소유가 되게 합니다
(Windows PowerShell에서는 `--user ... -e HOME=/tmp` 부분을 빼고, `$PWD` 대신 `${PWD}`를 쓰세요).
macOS(Apple 칩)에서는 x86 에뮬레이션이라 2~3배 느려지니, 가능하면 Windows/Linux 컴퓨터로 돌리세요.

### 방법 B: Ubuntu 24.04 (WSL2 포함)

Ubuntu 24.04 저장소의 clang이 정확히 18.1.3이라 Docker와 같은 결과가 나옵니다. 22.04 등 다른 버전은 안 됩니다.

```bash
sudo apt update
sudo apt install -y clang llvm libclang-rt-18-dev git python3 python3-scipy tmux
git clone https://github.com/<팀 계정>/gapfuzz.git
cd gapfuzz
git config user.name "본인 이름"
```

### 확인

```bash
python3 scripts/exp.py doctor
```

`clang ... 18.1.3`, `[doctor] 통과`가 나와야 합니다. 안 되면 실험을 시작하지 말고 팀 채팅에 결과를 올려 주세요.

---

## 2. 라이브러리 고르기

```bash
git pull
python3 scripts/exp.py libs              # 진행 상황과 담당자 확인
python3 scripts/exp.py claim expat       # 비어 있는 라이브러리 하나를 맡음 (자동으로 push)
```

`claim`은 `results/expat/OWNER.txt`에 이름을 적어 올립니다. 다른 사람이 먼저 맡았으면 거부되니 다른 라이브러리를 고르세요.
Docker 안에서는 git 로그인이 없을 수 있으니, `claim`과 `submit`은 **컨테이너 밖(내 컴퓨터 터미널)**에서 실행하는 게 편합니다.
컨테이너 밖에 Python이 없다면 `claim expat --no-push` 후 `git add results/expat && git commit -m "claim(expat)" && git push`로 대신합니다.

---

## 3. 실험 돌리기

```bash
python3 scripts/exp.py fetch expat       # 라이브러리 소스를 고정 커밋으로 받기 (third_party/)
tmux new -s exp                          # 터미널을 닫아도 계속 돌게
python3 scripts/exp.py run expat         # 1시간 × 10회, 두 하네스 = 약 11시간
# tmux에서 빠져나오기: Ctrl+B 누른 뒤 D / 다시 붙기: tmux attach -t exp
```

- **끊겨도 괜찮습니다.** 같은 명령을 다시 실행하면 결과 파일이 있는 회차는 건너뛰고 이어서 돕니다.
  다만 돌던 회차는 처음부터 다시 돌아요.
- **노트북은 절전 모드를 꺼 주세요.** 화면은 꺼져도 되지만 잠자기에 들어가면 그 회차가 멈춥니다.
- 하루에 다 못 돌리면 나눠도 됩니다: `run expat --trials 1-5` 오늘, `run expat --trials 6-10` 내일.
  회차 번호마다 시드가 정해져 있어서(회차 r의 시드 = 1000 + r) 나눠 돌려도 결과는 같습니다.
- `--jobs`는 바꾸지 마세요(기본 2). 동시에 도는 개수가 다르면 같은 라이브러리 안에서 조건이 달라집니다.
- 진행 상황은 `python3 scripts/exp.py libs`, 중간 결과는 `python3 scripts/exp.py report expat` 후 `results/expat/REPORT.md`.

---

## 4. 결과 올리기

```bash
python3 scripts/exp.py submit expat
```

`results/expat/` 안의 파일만 골라 커밋하고 `git pull --rebase` 후 push합니다. 다른 폴더의 파일이 staged 상태면 거부합니다.
다 끝나기 전에도 중간중간 올려도 됩니다(올라간 회차는 다시 돌지 않음).

### 왜 충돌이 안 나나

| 무엇 | 어디에 | git |
|---|---|---|
| 코퍼스, 커버리지, 바이너리, 크래시 입력 (수 GB) | `out/` | 올리지 않음 (`.gitignore`) |
| 라이브러리 소스 | `third_party/` | 올리지 않음, `fetch`가 고정 커밋으로 받음 |
| 회차마다 결과 요약 (약 4KB) | `results/<라이브러리>/<하네스>/rNN.json` | 올림 |
| 라이브러리별 보고서 | `results/<라이브러리>/REPORT.md` | 올림 (담당자만 만듦) |
| 담당자 표시 | `results/<라이브러리>/OWNER.txt` | 올림 |

각자 **자기 라이브러리 폴더만** 바꾸므로 서로 같은 파일을 건드리지 않습니다. 그래서 `pull --rebase`가 항상 깔끔하게 됩니다.
도구 코드(`gapfuzz/`, `scripts/`, `harnesses/`)는 실험 기간에 고치지 않습니다. `run`은 이 폴더에 커밋하지 않은 변경이 있으면 경고합니다.
전체 요약 `results/SUMMARY.md`는 정리하는 한 사람만 `python3 scripts/exp.py report --all`로 만듭니다.

### 결과 파일에 들어가는 것

```json
{"lib": "expat", "harness": "official_v2", "trial": 3, "secs": 3600, "seed": 1003,
 "coverage": {"branches": {"pct": 32.4, "covered": 1234, "count": 3810}, "lines": {...}, ...},
 "execs": 41234567, "corpus": 2310, "crashes": [], "triage": [],
 "targets": [{"fix": 1, "applied": true, "line": 1668, "opened": true}, ...],
 "by": "김지윤", "env": {"clang": "Ubuntu clang version 18.1.3 ...", "cpu": "...", "tool_commit": "abc1234"}}
```

`targets`는 2분 실험에서 도구가 "고칠 곳"으로 짚은 분기(`experiments/targets/<라이브러리>.json`)가 이 회차에 열렸는지입니다.
`applied: false`는 일부러 고치지 않은 대조군입니다. 보고서는 같은 회차끼리 짝지어 중앙값, A12, Mann-Whitney U 정확검정을 냅니다.

---

## 5. 문제가 생기면

| 증상 | 해결 |
|---|---|
| `doctor`에서 clang 버전이 18이 아님 | Docker를 쓰거나 Ubuntu 24.04에서 실행 |
| `libFuzzer/ASan으로 빌드 실패` | `sudo apt install libclang-rt-18-dev` |
| 컨테이너 안에서 `LeakSanitizer has encountered a fatal error` | `docker run`에 `--cap-add SYS_PTRACE`를 넣었는지 확인 |
| 크래시가 남 | 그대로 두세요. 자동으로 원인 귀속(triage)을 돌려 결과 파일에 판정을 남깁니다. 팀 채팅에 알려 주세요 |
| 디스크가 부족함 | 끝난 회차의 `out/targets/<라이브러리>/*/long3600/r*/corpus`는 지워도 됩니다 (결과는 `results/`에 있음) |
| `submit`에서 rebase 실패 | 다른 사람이 같은 라이브러리 폴더를 건드린 것입니다. 팀 채팅에서 담당을 확인하세요 |
