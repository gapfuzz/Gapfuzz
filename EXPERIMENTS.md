# 실험: OSS-Fuzz 하네스 vs Claude가 고친 하네스

## 무엇을 실험하나

라이브러리마다 하네스 두 개를 같은 컴퓨터에서, 같은 시간 동안, 같은 시드로 나란히 돌려 비교합니다.

| 하네스 | 파일 | 설명 |
|---|---|---|
| OSS-Fuzz | `harnesses/<라이브러리 이름>/official.*` | OSS-Fuzz에 등록된 원래 하네스 (고치지 않음) |
| Claude 수정 | `harnesses/<라이브러리 이름>/official_llm.*` | gapfuzz가 짚은 "하네스에서 고칠 곳"을 Claude API가 고치고, gapfuzz가 검사해 통과한 하네스 |

`official_llm`은 이미 저장소에 들어 있습니다. **팀원은 API 키가 필요 없고 `git pull`만 하면 됩니다.**

gapfuzz는 OSS-Fuzz 하네스를 분석해 "하네스의 이 부분 때문에 라이브러리 분기가 막혔으니 이렇게 고쳐라"라는 제안을 냅니다
(예: zlib에서 "`inflate`를 하네스가 직접 부르지 않아 `flush` 값이 한 가지뿐 → 직접 불러 다른 값을 넘겨라").
라이브러리마다 이 제안들 대부분을 Claude에게 맡기고, 한 개씩은 **일부러 맡기지 않고 대조군으로 남겼습니다.**
맡긴 제안의 분기는 열리고 대조군의 분기는 안 열려야, 열린 이유가 "오래 돌려서 운 좋게"가 아니라 "제안대로 고쳐서"라고 말할 수 있습니다.

| 라이브러리 | Claude에게 맡긴 제안 | 대조군 (일부러 안 맡김) | 짧은 검사(60초 × 2회)에서 겨냥 분기 열림 |
|---|---:|---:|---:|
| pugixml | 3개 | 1개 | 30/33 |
| cjson | 4개 | 1개 | 7/7 |
| jsoncpp | 2개 | 1개 | 7/8 |
| zlib | 3개 | 1개 | 11/11 |
| expat | 3개 | 1개 | 6/7 |
| json-c | 4개 | 1개 | 4/5 |
| tinyxml2 | 6개 | 1개 | `official_llm` 만든 뒤 채움 (`scripts/make_llm_harness.py tinyxml2`) |

제안 내용과 Claude가 바꾼 코드는 `samples/llm/combined/<라이브러리 이름>/report.md`, 만든 방법은 `scripts/make_llm_harness.py`에 있습니다.

실험은 두 가지입니다. 짧은 검사에서 열린 분기가 **오래 돌려도 효과가 유지되는지** 확인합니다.

| 실험 | 무엇을 보나 | 명령 | 걸리는 시간 |
|---|---|---|---|
| 1시간 × 10회 | 차이가 우연이 아닌지 (통계 검정) | `run <라이브러리 이름>` | 약 10시간 |
| 24시간 × 1회 | OSS-Fuzz 하네스가 오래 돌리면 따라잡는지 (시간에 따른 곡선) | `run <라이브러리 이름> --plan 24h` | 약 24.5시간 |

---

## 팀 규칙 (꼭 지키기)

1. **실험 전에 `claim`으로 라이브러리를 맡습니다.** 한 라이브러리는 한 사람이 한 컴퓨터에서 끝까지 돌립니다.
2. **결과는 `python3 scripts/exp.py submit <라이브러리 이름>`으로만 올립니다.** `git add -A`는 쓰지 마세요.
3. **실험 기간에는 공용 파일을 고치지 않습니다.** `gapfuzz/`, `scripts/`, `harnesses/`, `EXPERIMENTS.md`, `README.md`가 공용 파일입니다. 고칠 일이 있으면 팀 채팅에 먼저 말하고 한 사람만 고칩니다.
4. 두 실험은 한 컴퓨터에서 **차례로** 돌립니다(1시간 × 10회 → 24시간). 동시에 돌리면 같은 실행 파일을 다시 빌드해서 실험이 깨질 수 있습니다.

> 문서의 `<라이브러리 이름>` 자리에는 내가 맡은 라이브러리를 넣으세요: `tinyxml2`, `pugixml`, `expat`, `cjson`, `jsoncpp`, `json-c`, `zlib` 중 하나.
> 꺾쇠(`< >`)까지 지우고 넣어야 합니다. 예: `python3 scripts/exp.py run expat`

---

## 전체 흐름 (Windows + WSL + Docker)

아래는 Windows(WSL)에서 Docker로 실제로 실행한 순서 그대로입니다. Ubuntu 24.04라면 Docker 없이 해도 됩니다([맨 아래](#docker-없이-ubuntu-2404)).

```
[WSL]        저장소 받기 → Docker 설치 → Docker 켜기 → 이미지 빌드 → claim
[tmux 안]    컨테이너 들어가기
[컨테이너]   doctor → fetch → run (1시간 × 10회, 약 10시간)
[WSL 새 탭]  submit
[컨테이너]   run --plan 24h (약 24.5시간)
[WSL 새 탭]  submit
```

> 명령을 어디서 실행하는지가 중요합니다. 프롬프트로 구분하세요.
> - `user@DESKTOP-...:~/gapfuzz$` → **WSL** (컨테이너 밖). git 로그인이 있어서 `claim`, `submit`은 여기서.
> - `ubuntu@a2f7005cea61:/work$` 같은 모양 → **컨테이너 안**. `doctor`, `fetch`, `run`은 여기서.

---

## 0. 저장소 받기, 내 Ubuntu 버전 확인

WSL 터미널에서:

```bash
cd ~
git clone https://github.com/gapfuzz/Gapfuzz.git gapfuzz
cd gapfuzz
lsb_release -a
```

- **24.04가 아니거나(26.04 등) 잘 모르겠으면** 1번부터 순서대로 진행합니다(권장).
- `Ubuntu 24.04`면 [Docker 없이](#docker-없이-ubuntu-2404)로 해도 됩니다.
- macOS나 Docker Desktop은 3번부터 같습니다. 단 Apple 칩 Mac은 2~3배 느려지니 가능하면 Windows/Linux 컴퓨터로 돌리세요.

이미 받아 둔 저장소가 있으면 `cd ~/gapfuzz && git pull`로 최신 상태를 받습니다.

---

## 1. Docker 설치 (처음 한 번)

```bash
sudo apt update
sudo apt install -y docker.io tmux
sudo usermod -aG docker $USER        # 내 계정을 docker 그룹에 추가
```

`sudo`가 묻는 비밀번호는 **WSL Ubuntu를 설치할 때 정한 리눅스 계정 비밀번호**입니다(Windows 비밀번호와 다를 수 있음).
입력해도 화면에 아무것도 안 보이는 게 정상입니다.

> 비밀번호를 잊었으면 Windows **PowerShell**에서 `wsl -u root` → `passwd <내 리눅스 아이디>` → `exit`.
> 리눅스 아이디는 프롬프트 `user@DESKTOP-...`의 `@` 앞부분입니다.

그룹 추가가 적용되도록 **WSL 창을 닫았다가 다시 엽니다.**

---

## 2. Docker 켜기 (WSL을 새로 켤 때마다)

WSL은 보통 systemd가 꺼져 있어서 `systemctl start docker`, `service docker start`가 안 됩니다. Docker를 직접 띄웁니다.

```bash
sudo sh -c 'nohup dockerd > /var/log/dockerd.log 2>&1 &'
sleep 5
docker info | head -12
```

`Server:` 아래에 정보가 나오면 켜진 것입니다.

| 이런 메시지가 나오면 | 해결 |
|---|---|
| `failed to connect to the docker API ... no such file or directory` | Docker가 안 켜진 것. 위 `dockerd` 명령 실행 |
| `System has not been booted with systemd` | 정상. `systemctl` 대신 위 `dockerd` 명령 사용 |
| `permission denied while trying to connect to the docker API` | 그룹 권한이 아직 적용 안 됨. `newgrp docker` 실행 후 `cd ~/gapfuzz` (또는 WSL 창을 닫았다 열기) |
| `newgrp docker`가 `Password:`를 물음 | 그룹에 안 들어가 있는 것. `Ctrl+C` → `sudo usermod -aG docker $USER` → WSL 창 닫았다 열기 |
| `dockerd`를 켰는데도 안 됨 | `sudo tail -20 /var/log/dockerd.log`로 원인 확인. `iptables` 에러면 `sudo update-alternatives --set iptables /usr/sbin/iptables-legacy` 후 다시 켜기 |

> 매번 켜기 귀찮으면(선택): `printf '[boot]\nsystemd=true\n' | sudo tee -a /etc/wsl.conf` → PowerShell에서 `wsl --shutdown` → WSL 다시 열기.
> 이후 Docker가 자동으로 켜집니다. **실험이 돌고 있지 않을 때만** 하세요(`wsl --shutdown`은 모든 작업을 끕니다).

---

## 3. 이미지 빌드 (처음 한 번, 몇 분)

```bash
cd ~/gapfuzz
docker build -t gapfuzz .
```

마지막에 `Successfully tagged gapfuzz:latest`가 나오면 성공입니다.
`DEPRECATED: The legacy builder is deprecated` 경고는 무시해도 됩니다.

---

## 4. 라이브러리 맡기 (WSL에서)

```bash
cd ~/gapfuzz
git pull
git config user.name                                  # 지금 설정된 git 이름 확인 (비어 있으면 git config user.name "이름")
python3 scripts/exp.py libs                           # 진행 상황과 담당자 확인. 담당자가 '-'인 것을 고름
python3 scripts/exp.py claim <라이브러리 이름>        # 하나를 맡음 (GitHub에 자동 push)
```

`claim`은 **git 이름**으로 `results/<라이브러리 이름>/OWNER.txt`에 담당자를 적어 올립니다. 다른 사람이 먼저 맡았으면 거부되니 다른 라이브러리를 고르세요.

> WSL에서 `python3 scripts/exp.py run ...`을 실행하면 `FileNotFoundError: ... 'llvm-cov'` 에러가 납니다.
> WSL에는 clang 도구가 없어서 그런 것이니, `run`은 꼭 **컨테이너 안에서** 하세요.

---

## 5. tmux 켜고 컨테이너 들어가기

tmux를 **먼저** 켜고 그 안에서 컨테이너에 들어가야, 창에서 빠져나와도 실험이 계속 돕니다.

```bash
cd ~/gapfuzz
tmux new -s exp
docker run --rm -it --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -e GAPFUZZ_BY="$(git config user.name)" -v "$PWD":/work gapfuzz bash
```

- `GAPFUZZ_BY`에는 git 이름이 자동으로 들어갑니다. 그대로 복사해서 쓰면 됩니다.
  다른 이름을 넣으면 `run`이 `[run] <라이브러리 이름>는 <git 이름> 님 담당입니다. 정말 돌리려면 --force`라며 멈춥니다.
  본인이 맡은 게 맞다면 `run <라이브러리 이름> --force`로 실행해도 됩니다.
- `--cap-add SYS_PTRACE`는 메모리 누수 검사가 컨테이너 안에서 동작하는 데 필요합니다.
- 프롬프트가 `ubuntu@<숫자와 글자>:/work$`로 바뀌면 컨테이너 안입니다. `/work`가 WSL의 `~/gapfuzz`와 같은 폴더입니다.

---

## 6. 환경 확인, 소스 받기, 1시간 × 10회 실행 (컨테이너 안)

```bash
python3 scripts/exp.py doctor
```

이렇게 나와야 합니다. 안 되면 실험을 시작하지 말고 팀 채팅에 화면을 올려 주세요.

```
[doctor] 환경
  clang        Ubuntu clang version 18.1.3 (1ubuntu1)
  llvm_cov     Ubuntu LLVM version 18.1.3
  os           Ubuntu 24.04.5 LTS
  docker       True
  ...
[doctor] 통과
```

```bash
python3 scripts/exp.py fetch <라이브러리 이름>        # 라이브러리 소스를 고정 커밋으로 받기 (third_party/)
python3 scripts/exp.py run <라이브러리 이름>
```

정상이면:

```
[run] <라이브러리 이름>: 20개 실행 (회차 1-10, 회당 3600초, 동시에 2개) → 약 10.0시간
[tgt] build <라이브러리 이름>/official -> /work/out/targets/<라이브러리 이름>/official
[tgt] build <라이브러리 이름>/official_llm -> /work/out/targets/<라이브러리 이름>/official_llm
```

그 뒤 **1시간 동안 아무 출력이 없는 게 정상**입니다(첫 회차 퍼징 중). 1시간마다 이런 줄이 2개씩 찍힙니다.

```
[run] 11-02 15:57 <라이브러리 이름>/official r01: 분기 ...% 라인 ...% 겨냥 분기 0/.. 크래시 0
[run] 11-02 15:57 <라이브러리 이름>/official_llm r01: 분기 ...% 라인 ...% 겨냥 분기 ../.. 크래시 0
```

### tmux에서 빠져나오기 / 다시 붙기

- 빠져나오기: `Ctrl+B`를 누르고 손을 뗀 뒤 `D` → 실험은 계속 돔
- 다시 붙기: WSL에서 `tmux attach -t exp`

### 돌리는 동안 지킬 것

- **WSL 창은 닫지 말고 최소화만.** 창을 모두 닫으면 WSL이 꺼지면서 실험도 멈출 수 있습니다.
- **Windows 절전 끄기:** 설정 → 시스템 → 전원 → "절전 모드로 전환"을 "안 함". 노트북이면 충전기를 연결하고 덮개를 닫아도 안 꺼지게 설정.
- `--jobs`는 바꾸지 마세요(기본 2). 같은 회차의 두 하네스를 동시에 돌려야 비교가 공평합니다.
- 하루에 다 못 돌리면 나눠도 됩니다: `run <라이브러리 이름> --trials 1-5`, 다음에 `--trials 6-10`. 회차마다 시드가 정해져 있어(회차 r의 시드 = 1000 + r) 결과는 같습니다.

### 중간에 끊겼다면

2번(Docker 켜기) → 5번(tmux, 컨테이너) → `python3 scripts/exp.py run <라이브러리 이름>`을 다시 하면 됩니다.
결과 파일이 있는 회차는 건너뛰고, 돌던 회차만 처음부터 다시 돕니다.

---

## 7. 결과 올리기 (WSL에서)

`[run] 끝. 결과 올리기: python3 scripts/exp.py submit <라이브러리 이름>`가 나오면 끝난 것입니다.
컨테이너 안에는 GitHub 로그인이 없으니, **WSL 창에 새 탭**을 열어서 올립니다.

```bash
cd ~/gapfuzz
python3 scripts/exp.py submit <라이브러리 이름>
```

`results/<라이브러리 이름>/` 안의 파일만 골라 커밋하고, `git pull --rebase` 후 push합니다. 다 끝나기 전에 중간 결과를 올려도 됩니다.

---

## 8. 24시간 실험 (컨테이너 안)

1시간 × 10회가 **끝나고 submit한 뒤에** 시작합니다. `tmux attach -t exp`로 원래 창에 돌아가서(컨테이너가 아직 열려 있음):

```bash
python3 scripts/exp.py run <라이브러리 이름> --plan 24h
```

컨테이너를 이미 나왔다면 5번처럼 `tmux new -s day` → `docker run ...`으로 다시 들어가서 실행합니다.

```
[24h] <라이브러리 이름>: OSS-Fuzz와 Claude 수정본을 동시에 24.0시간 (남은 시간 약 24.0시간). 구간이 끝날 때마다 커버리지를 재서 results/에 저장합니다.
[24h] 11-03 01:20 <라이브러리 이름>/official 0.17시간: 분기 ...% 겨냥 분기 ../.. 크래시 0
...
```

- 10분, 20분, 30분, 그 뒤 1시간마다 한 줄씩 찍힙니다. 이것이 시간에 따른 곡선이 됩니다.
- 끊기면 같은 명령을 다시 실행하면 마지막으로 끝난 구간 다음부터 이어 돕니다. 단 **같은 컴퓨터에서** 이어야 합니다(코퍼스가 `out/`에 있음).
- 중간에 WSL 새 탭에서 `submit`으로 지금까지의 곡선을 올려도 됩니다. 끝나면 7번처럼 `submit`.

---

## 9. 결과 보기

```bash
python3 scripts/exp.py report <라이브러리 이름>       # results/<라이브러리 이름>/REPORT.md 생성
cat results/<라이브러리 이름>/REPORT.md
```

끝난 회차까지만 집계합니다. 보고서에서 볼 것:

| 항목 | 뜻 | 효과가 있다고 말할 수 있는 기준 |
|---|---|---|
| 분기 커버리지 중앙값 | 10회 결과의 가운데 값 | Claude 수정이 더 높음 |
| A12 | Claude 수정 한 회가 OSS-Fuzz 한 회보다 높을 확률 | 0.5면 차이 없음, **0.71 이상이면 큰 차이** |
| p (Mann-Whitney U) | 차이가 우연일 가능성 | **0.05 미만** |
| 겨냥 분기 | 도구가 짚은 분기가 회차마다 열렸는지 | Claude 수정에서 열리고, OSS-Fuzz 하네스와 대조군에서는 안 열림 |
| 24시간 표 | 시간대별 두 하네스의 커버리지 | 24시간이 지나도 OSS-Fuzz 하네스가 따라잡지 못함 |

모두 submit한 뒤 **정리 담당 한 사람만** `python3 scripts/exp.py report --all`로 전체 요약 `results/SUMMARY.md`를 만듭니다.

---

## 한 장 요약

```bash
# [WSL] 컴퓨터를 켤 때마다
sudo sh -c 'nohup dockerd > /var/log/dockerd.log 2>&1 &'

# [WSL] 처음 한 번
cd ~/gapfuzz && git pull && docker build -t gapfuzz .
python3 scripts/exp.py claim <라이브러리 이름>

# [WSL] 실험 시작
tmux new -s exp
docker run --rm -it --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -e GAPFUZZ_BY="$(git config user.name)" -v "$PWD":/work gapfuzz bash

# [컨테이너]
python3 scripts/exp.py doctor
python3 scripts/exp.py fetch <라이브러리 이름>
python3 scripts/exp.py run <라이브러리 이름>               # 약 10시간
# Ctrl+B, D 로 빠져나오기 / tmux attach -t exp 로 다시 붙기

# [WSL 새 탭] 끝나면
python3 scripts/exp.py submit <라이브러리 이름>

# [컨테이너] 그다음
python3 scripts/exp.py run <라이브러리 이름> --plan 24h    # 약 24.5시간

# [WSL 새 탭] 끝나면
python3 scripts/exp.py submit <라이브러리 이름>
```

---

## Docker 없이 (Ubuntu 24.04)

Ubuntu 24.04(WSL 포함) 저장소의 clang이 정확히 18.1.3이라 Docker와 같은 결과가 나옵니다. 다른 버전은 안 됩니다.

```bash
sudo apt update
sudo apt install -y clang llvm libclang-rt-18-dev git python3 python3-scipy tmux
cd ~/gapfuzz
python3 scripts/exp.py doctor                 # [doctor] 통과 확인
python3 scripts/exp.py claim <라이브러리 이름>
python3 scripts/exp.py fetch <라이브러리 이름>
tmux new -s exp
python3 scripts/exp.py run <라이브러리 이름>
```

컨테이너가 없으므로 모든 명령을 같은 터미널에서 실행합니다. 나머지(빠져나오기, submit, 24시간, 결과 보기)는 위와 같습니다.

---

## 결과 파일과 충돌이 안 나는 이유

| 무엇 | 어디에 | git |
|---|---|---|
| 코퍼스, 커버리지, 바이너리, 크래시 입력 (수 GB) | `out/` | 올리지 않음 (`.gitignore`) |
| 라이브러리 소스 | `third_party/` | 올리지 않음, `fetch`가 고정 커밋으로 받음 |
| 1시간 회차마다 결과 요약 (약 4KB) | `results/<라이브러리>/1h/<하네스>/rNN.json` | 올림 |
| 24시간 실험의 구간별 측정값 (수십 KB) | `results/<라이브러리>/24h/<하네스>.json` | 올림 |
| 라이브러리별 보고서 | `results/<라이브러리>/REPORT.md` | 올림 (담당자만 만듦) |
| 담당자 표시 | `results/<라이브러리>/OWNER.txt` | 올림 |

각자 **자기 라이브러리 폴더만** 바꾸므로 서로 같은 파일을 건드리지 않습니다. 그래서 `submit`의 `pull --rebase`가 항상 깔끔하게 됩니다.
`run`은 도구 코드에 커밋하지 않은 변경이 있으면 경고합니다.

### 결과 파일에 들어가는 것

```json
{"lib": "expat", "harness": "official_llm", "trial": 3, "secs": 3600, "seed": 1003,
 "coverage": {"branches": {"pct": 32.4, "covered": 1234, "count": 3810}, "lines": {...}, ...},
 "execs": 41234567, "corpus": 2310, "crashes": [], "triage": [],
 "targets": [{"fix": 1, "applied": true, "line": 1668, "opened": true}, ...],
 "by": "이름", "env": {"clang": "Ubuntu clang version 18.1.3 ...", "cpu": "...", "tool_commit": "abc1234"}}
```

`targets`는 도구가 "고칠 곳"으로 짚은 분기(`experiments/targets/<라이브러리>.json`)가 이 회차에 열렸는지입니다. `applied: false`는 Claude에게 맡기지 않은 대조군입니다.
24시간 결과 파일은 `points` 목록에 구간마다 `{"hours": 2.0, "coverage": {...}, "targets": [...], "corpus": 31200, "crashes": [], "restarts": 0}`가 쌓입니다.

---

## 그 밖의 문제

| 증상 | 해결 |
|---|---|
| `run`이 `harnesses/<라이브러리>/official_llm.* 가 없습니다` | `git pull`로 최신 저장소를 받으세요 |
| `doctor`에서 clang 버전이 18이 아님 | Docker를 쓰거나 Ubuntu 24.04에서 실행 |
| `libFuzzer/ASan으로 빌드 실패` | `sudo apt install libclang-rt-18-dev` (Docker면 이미지 다시 빌드) |
| 컨테이너 안에서 `LeakSanitizer has encountered a fatal error` | `docker run`에 `--cap-add SYS_PTRACE`를 넣었는지 확인 |
| 크래시가 남 | 그대로 두세요. 자동으로 원인 귀속(triage)을 돌려 결과 파일에 판정을 남깁니다. 팀 채팅에 알려 주세요 |
| 디스크가 부족함 | 끝난 회차의 `out/targets/<라이브러리>/*/long3600/r*/corpus`는 지워도 됩니다(결과는 `results/`에 있음). `*/day/`는 24시간이 끝난 뒤에만 지우세요 |
| 24시간을 다시 실행했더니 "이어서 돌릴 코퍼스가 없습니다" | `day/` 폴더가 지워졌거나 다른 컴퓨터입니다. 처음부터 다시 하려면 `results/<라이브러리>/24h/`를 지우고 실행하세요 |
| `submit`에서 rebase 실패 | 다른 사람이 같은 폴더나 공용 파일을 건드린 것입니다. 팀 채팅에서 확인하세요 |

## 새 하네스 `gapfuzz_ops` 만들기 (하네스 전체 기준 실험 전에, 한 사람이 한 번)

`gapfuzz_ops`는 "OSS-Fuzz 하네스를 전부 합쳐도 한 번도 불리지 않는 공개 API"를 부르는 새 하네스입니다. 라이브러리마다 하나씩 있고,
하네스 전체 기준 실험의 적용 후 묶음에 들어갑니다. **이 파일이 없는 채로 실험을 돌리면 API를 추가한 효과가 빠진 실험이 됩니다.**

- 한 사람이 11개를 모두 만들어 커밋합니다. 다른 팀원은 `git pull`로 받아서 씁니다. 각자 따로 만들면 서로 다른 하네스로 실험하게 됩니다.
- Claude는 돌릴 때마다 다른 코드를 냅니다. **커밋한 뒤에는 다시 만들지 않습니다.** (스크립트는 이미 있는 라이브러리를 건너뜁니다.)
- Claude API 키가 필요하고 비용이 듭니다. 키는 환경 변수로만 넘기고 파일·채팅·커밋에 적지 않습니다.

### 만드는 조건 (다시 만들 때 같게 맞출 값)

| 항목 | 값 | 바꾸는 법 |
|---|---|---|
| 모델 | `claude-sonnet-5-5` | 환경 변수 `GAPFUZZ_MODEL` 또는 `--model` |
| 요청할 API 수 | 순위 상위 10개 | `--top` |
| 검사 퍼징 | 60초 × 2회 | `--secs`, `--trials` |
| 다시 묻는 횟수 | 최대 3번 | `--tries` |
| 출력 상한 / 생각 분량 | 64000 토큰 / medium | `GAPFUZZ_MAX_TOKENS`, `GAPFUZZ_EFFORT` |
| 진단 | OSS-Fuzz 하네스마다 120초 × 1회를 합침 | `tgt.py union --secs` |

기존 `official_llm` 하네스도 `claude-sonnet-5-5`로 만들었습니다(`samples/llm/`의 기록). 한 묶음 안의 하네스를 같은 모델로 맞추기 위해 `gapfuzz_ops`도 같은 모델을 씁니다. 모델을 바꾸려면 `official_llm`도 다시 만들고 그 실험도 다시 돌려야 합니다.

### 1. 준비 (WSL)

```bash
cd ~/gapfuzz
git pull
git status            # working tree clean 이어야 함
tmux new -s ops
```

### 2. 키를 넣고 컨테이너 들어가기 (WSL, tmux 안)

```bash
read -s ANTHROPIC_API_KEY      # 키를 붙여 넣고 Enter. 화면에는 아무것도 안 보입니다
export ANTHROPIC_API_KEY
docker run --rm -it --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -e ANTHROPIC_API_KEY -v "$PWD":/work gapfuzz bash
```

### 3. 어떤 API가 뽑히는지 먼저 보기 (컨테이너 안, 키를 쓰지 않음)

```bash
python3 scripts/exp.py fetch <라이브러리 이름>
python3 -m gapfuzz llmops <라이브러리 이름> --union --list
```

표의 "이번에 추가"가 붙은 줄이 Claude에게 요청할 API입니다.

### 4. 만들기 (컨테이너 안)

```bash
bash scripts/make_gapfuzz_ops.sh                 # 11개 전부. 하네스가 적은 라이브러리부터
bash scripts/make_gapfuzz_ops.sh cjson           # 하나만 먼저 해 볼 때
```

라이브러리마다 이 순서로 돕니다: 소스 받기 → OSS-Fuzz 하네스 전부를 120초씩 돌려 합침 → 안 불리는 API 순위 → Claude에게 요청
→ 컴파일, 60초 × 2회 퍼징, 요청한 API가 실행됐는지, 크래시가 하네스 탓인지 검사 → 실패하면 이유를 돌려주고 다시(최대 3번) → 통과하면 저장.

- 하나가 실패해도 다음 라이브러리로 넘어갑니다. 끝에 요약이 나옵니다.
- 걸리는 시간은 라이브러리당 10~40분(하네스 수에 따라)입니다. `Ctrl+B, D`로 빠져나오고 `tmux attach -t ops`로 다시 붙습니다.

### 5. 결과 확인

| 파일 | 내용 |
|---|---|
| `harnesses/<라이브러리 이름>/gapfuzz_ops.*` | 통과한 새 하네스. 첫 줄에 만든 모델이 적혀 있음 |
| `samples/llm/ops/<라이브러리 이름>/_union/report.md` | 시도별 결과표(실행된 API, 크래시 귀속, 토큰 수)와 모델 이름 |
| `samples/llm/ops/<라이브러리 이름>/_union/request.md` | Claude에게 보낸 요청 전문 |
| `samples/llm/ops/<라이브러리 이름>/_union/ranking.md` | 안 불리는 API 순위표 |
| `out/ops_logs/<라이브러리 이름>.log` | 실행 로그 (커밋하지 않음) |

만들어진 하네스는 **사람이 읽어 봅니다.** 검사 통과는 "컴파일되고, 요청한 API가 실행되고, 60초 안에 하네스 탓 크래시가 없다"는 뜻입니다.

1. `// [gapfuzz-ops]` 블록마다 인자가 `data`/`size`에서 나오는가 (상수면 안 됨)
2. 초기화 → 사용 → 해제 순서가 맞는가, 반환값을 확인하는가
3. `report.md` 끝에 Claude가 적은 "뺀 API와 이유"

3번 다 실패한 라이브러리는 `gapfuzz_ops` 없이 실험하고, 그 사실과 `report.md`의 실패 이유를 결과에 적습니다. 통과할 때까지 조건을 바꿔 가며 다시 돌리지 않습니다.

효과를 짧게 미리 보려면(120초 × 1회, 참고용):

```bash
python3 scripts/tgt.py union <라이브러리 이름>                                          # 기준
python3 scripts/tgt.py union <라이브러리 이름> --add gapfuzz_ops --name _union_after    # 새 하네스를 더했을 때
```

### 6. 커밋 (WSL)

```bash
git add harnesses/*/gapfuzz_ops.* samples/llm/ops
git status --short        # gapfuzz_ops 파일과 samples/llm/ops 아래 기록만 보여야 함
git commit -m "gapfuzz_ops: 새 하네스 (claude-sonnet-5-5, top 10, 검사 60초 × 2회, 최대 3번)"
git push
```

커밋 메시지에 모델과 조건을 적어 둡니다. 이 커밋 뒤로는 `gapfuzz_ops`를 바꾸지 않습니다.

### 이름이 비슷한 예전 파일

`harnesses/zlib/official_ops.cc`, `harnesses/tinyxml2/official_llm_ops.cpp`처럼 이름 끝에 `_ops`가 붙은 파일은 예전 방식(하네스 하나에 호출을 끼워 넣음)의 결과물입니다.
하네스 전체 기준 실험에는 들어가지 않습니다. 실험에 들어가는 것은 `gapfuzz_ops` 하나입니다.

---

## 추가 하네스 고치기 (`<하네스 이름>_llm`, 선택, 한 사람이 한 번)

`official_llm`은 대표 하네스(`official`) 하나만 고친 것입니다. 이 단계는 **나머지 OSS-Fuzz 하네스도** 같은 방식으로 고쳐
`official_compress_llm`처럼 `<하네스 이름>_llm`으로 저장합니다. 있으면 하네스 전체 기준 실험의 적용 후 묶음에 자동으로 들어갑니다.

- **고친 하네스 하나마다 팀 실험이 1시간 × 10회씩 늘어납니다.** 시간이 모자라면 이 단계를 건너뛰어도 실험은 성립합니다(그 하네스는 원본 그대로 묶음에 들어감).
- `gapfuzz_ops`와 같은 규칙입니다: 한 사람이 만들어 커밋하고, 커밋한 뒤에는 다시 만들지 않습니다. 모델도 같게 둡니다(`claude-sonnet-5-5`).

### 어떤 제안을 맡기나 (사람이 고르지 않고 규칙으로)

| 규칙 | 내용 | 이유 |
|---|---|---|
| 1. 하네스 전체 기준 | 겨냥한 분기가 OSS-Fuzz 하네스 전체를 합친 커버리지에서도 막혀 있는 제안만 | 다른 하네스가 이미 여는 분기는 고칠 이유가 없음 |
| 2. 한 번만 | 같은 분기를 여러 하네스가 겨냥하면 `ossfuzz` 목록에서 앞선 하네스 하나에만. `official_llm`이 맡은 분기는 빼고 시작 | 같은 분기를 여러 번 고쳐도 합친 커버리지는 늘지 않고 실험 시간만 늚 |

맡길 제안이 없는 하네스는 고친 버전을 만들지 않습니다.

### 1. 무엇을 맡길지 먼저 보기 (컨테이너 안, 키를 쓰지 않음)

```bash
python3 scripts/make_llm_harness_extra.py <라이브러리 이름> --list
python3 scripts/make_llm_harness_extra.py --all --primary --list      # 11개 전부, 마지막 줄에 늘어나는 실험 시간
```

하네스마다 제안별로 "맡김 / 다른 하네스가 이미 엶 / 앞선 하네스가 맡음"이 나옵니다.

### 2. 만들기 (컨테이너 안, `ANTHROPIC_API_KEY` 필요: 위 절의 2번과 같은 방법)

```bash
python3 scripts/make_llm_harness_extra.py <라이브러리 이름>              # 한 라이브러리
python3 scripts/make_llm_harness_extra.py --all                          # 11개 전부
python3 scripts/make_llm_harness_extra.py --all --primary                # + official_llm이 없는 라이브러리는 대표 하네스도
```

- `--primary`: `official_llm`이 아직 없는 라이브러리(`http-parser`, `libucl`, `yyjson`)의 대표 하네스도 같은 규칙으로 고쳐 `official_llm`을 만듭니다.
  기존 7개 라이브러리의 `official_llm`은 사람이 고른 제안으로 만든 것이라 건드리지 않습니다. `libyaml`의 대표 하네스는 고칠 곳이 없습니다.
- 검사는 `official_llm`을 만들 때와 같습니다: 컴파일 → 60초 × 2회 퍼징 → 겨냥한 분기가 하나라도 열렸나 → 크래시가 하네스 탓인가. 실패하면 이유를 돌려주고 최대 3번.
- 이미 `<하네스 이름>_llm`이 있으면 건너뜁니다.

### 3. 결과 확인과 커밋

| 파일 | 내용 |
|---|---|
| `harnesses/<라이브러리 이름>/<하네스 이름>_llm.*` | 통과한 하네스. 첫 줄에 모델과 적용한 제안 번호 |
| `samples/llm/combined/<라이브러리 이름>/<하네스 이름>/report.md` | 시도별 결과(열린 분기, 크래시 귀속, 토큰 수) |
| `samples/llm/combined/EXTRA.md` | 전체 요약표 |

`best.diff`로 무엇이 바뀌었는지 읽어 봅니다. 통과하지 못한 하네스는 고친 버전 없이 원본으로 실험하고, 그 사실을 결과에 적습니다.

```bash
git add harnesses/*/*_llm.* samples/llm/combined        # WSL에서
git status --short
git commit -m "추가 하네스 수정 <하네스 이름>_llm (claude-sonnet-5-5, 하네스 전체 기준으로 막힌 분기만, 분기당 한 하네스)"
git push
```

### 알아둘 한계

- 대표 하네스의 `official_llm`은 사람이 제안을 골랐고(대조군 포함), 추가 하네스는 위 규칙으로 골랐습니다. 고르는 방식이 다르다는 점을 결과에 적습니다.
- 규칙 2는 "앞선 하네스가 그 분기를 실제로 연다"고 가정합니다. 앞선 하네스의 수정이 그 분기를 못 열어도 뒤 하네스에 다시 맡기지 않습니다.
- "null을 넘긴 적이 없음" 같은 제안은 그 인자에 null이 금지돼 있을 수 있습니다. Claude에게 금지된 인자는 넘기지 말라고 지시하고 크래시 귀속으로 거르지만, `best.diff`에서 직접 확인하세요.

---

## 하네스 전체 기준 실험 (`--plan union`)

라이브러리에 OSS-Fuzz 하네스가 여러 개 있으면, 하네스 하나만 비교해서는 "다른 하네스가 이미 하는 일"이 섞입니다.
이 실험은 하네스를 **모두 따로 돌린 뒤 커버리지를 합쳐서** 비교합니다. 한 라이브러리는 한 사람이 전부 돌립니다(합치려면 원본 기록이 한 컴퓨터에 있어야 함).

먼저 위의 "새 하네스 `gapfuzz_ops` 만들기"(와, 하기로 했다면 "추가 하네스 고치기")가 끝나 `harnesses/<라이브러리 이름>/gapfuzz_ops.*`가 저장소에 있어야 합니다(`git pull`).
대상 라이브러리는 11개입니다: `cjson`, `jsoncpp`, `http-parser`, `expat`, `pugixml`, `tinyxml2`, `libucl`, `yyjson`, `json-c`, `zlib`, `libyaml`.

```bash
python3 scripts/exp.py run <라이브러리 이름> --plan union --secs 60 --trials 1-2    # 먼저 짧게: 끝까지 도는지 확인 (15분쯤)
python3 scripts/exp.py run <라이브러리 이름> --plan union                          # 하네스마다 1시간 × 10회
python3 scripts/exp.py run <라이브러리 이름> --plan union --jobs 3                 # 동시에 3개
python3 scripts/exp.py submit <라이브러리 이름>
```

- 실행하면 처음에 두 묶음의 하네스 목록이 나옵니다. **적용 후 목록에 `gapfuzz_ops`가 있는지 확인하고** 진행합니다.
- 짧게 돌린 결과(`results/<라이브러리 이름>/60s`, `union_60s`, `UNION.md`)는 확인 후 지웁니다. 올리지 않습니다.
- `--jobs`는 "물리 코어 수 − 1"과 "(메모리 GB − 2) ÷ 2" 중 작은 값 이하로 줍니다(기본 2). WSL 안에서 `lscpu`, `free -g`로 보이는 값 기준입니다.
  퍼저 하나가 코어 하나를 계속 쓰고 메모리를 최대 2GB까지 씁니다. 더 높이면 서로 느려져 커버리지가 낮게 나옵니다.
- 실행 순서는 회차 먼저입니다(1회차의 모든 하네스 → 2회차 …). 중간에 멈춰도 끝난 회차까지는 비교할 수 있습니다.

| 묶음 | 들어가는 하네스 |
|---|---|
| 기준 | 설정(`targets/<이름>.json`)의 `"ossfuzz"` 목록 전부 |
| 적용 후 | 각 하네스의 고친 버전이 있으면 그것(`official` → `official_llm`, 그 밖은 `<이름>_llm`), 없으면 원래 하네스. 여기에 `gapfuzz_ops`(새 하네스)가 있으면 추가 |

- 고치지 않은 하네스는 두 묶음이 같은 실행 기록을 같이 씁니다. 다시 돌리지 않습니다.
- 이미 `--plan 1h`로 돌린 `official`, `official_llm`의 원본(`out/targets/<이름>/<하네스>/long3600/`)이 남아 있으면 그대로 씁니다.
- 끊겨도 다시 실행하면 원본이 없는 것만 이어서 돕니다.

결과 파일

| 위치 | 내용 |
|---|---|
| `results/<이름>/1h/<하네스>/rNN.json` | 하네스별 회차 결과 (기존과 같은 형식) |
| `results/<이름>/union_1h/base/rNN.json` | 회차별 기준 묶음을 합친 결과: 하네스 목록, 커버리지, 어느 하네스도 안 부르는 API 수 |
| `results/<이름>/union_1h/fixed/rNN.json` | 회차별 적용 후 묶음을 합친 결과 |
| `results/<이름>/UNION.md` | 요약표 (중앙값, A12, p) |

걸리는 시간은 "새로 돌릴 하네스 수 × 회차 × 1시간 ÷ 동시에 돌리는 수"입니다. 실행하면 맨 처음에 예상 시간이 나옵니다.
적용 후 쪽에 `gapfuzz_ops`가 들어가면 하네스가 하나 더 많아 총 퍼징 시간도 1시간 더 깁니다. `UNION.md`에 이 점이 표시됩니다.
