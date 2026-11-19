# 실험: OSS-Fuzz 하네스 전체 vs gapfuzz를 적용한 하네스

이 디렉터리는 Gapfuzz의 효과를 평가하고 결과를 재현하기 위한 자료입니다. 일반적인 도구 사용법은 루트 [README](../README.md)와 [상세 문서](../docs/DETAILS.md)를 보세요.

이 디렉터리는 Gapfuzz의 효과를 평가하고 결과를 재현하기 위한 자료입니다. 일반적인 도구 사용법은 루트 [README](../README.md)와 [상세 문서](../docs/DETAILS.md)를 보세요.

## 무엇을 실험하나

라이브러리마다 **하네스 묶음 두 개**를 같은 컴퓨터에서, 같은 시간 동안, 같은 시드로 돌려 비교합니다.

### 하네스 이름

| 이름 | 뜻 | 만든 곳 |
| --- | --- | --- |
| `official_<이름>` | OSS-Fuzz의 하네스 (예: `official_compress`) | OSS-Fuzz |
| `official_<이름>_llm` | 나머지 하네스를 같은 방식으로 고친 것 (있는 것만) | Claude + gapfuzz 검사 |
| `gapfuzz_ops` | 어느 OSS-Fuzz 하네스도 부르지 않는 공개 API를 부르는 새 하네스 | Claude + gapfuzz 검사 |

### 대상 라이브러리

| 라이브러리 | OSS-Fuzz 하네스 |
| --- | --: |
| `cjson` | 1 |
| `jsoncpp` | 1 |
| `expat` | 2 |
| `pugixml` | 2 |
| `http-parser` | 2 |
| `libucl` | 2 |
| `tinyxml2` | 2 |
| `yyjson` | 3 |
| `json-c` | 4 |
| `zlib` | 9 |
| `libyaml` | 9 |

## 전체 순서

```
A. 하네스 만들기      준비 담당 한 사람만, 한 번
     gapfuzz_ops (라이브러리마다 1개)
     official_<이름>_llm, 없는 official_llm (선택)
     커밋하고 push

B. 실험               각자 맡은 라이브러리
     git pull → claim → 짧게 확인 → run --plan union → submit
```

**A가 push되기 전에 B를 시작하지 않습니다.** `gapfuzz_ops`가 없는 채로 돌리면 "안 부르던 API를 부르게 한 효과"가 빠진 실험이 됩니다.

> 명령을 어디서 실행하는지가 중요합니다. 프롬프트로 구분하세요.
>
> - `user@DESKTOP-...:~/gapfuzz$` → **WSL** (컨테이너 밖). git 로그인이 있어서 `claim`, `submit`, `git`은 여기서.
> - `ubuntu@a2f7005cea61:/work$` 같은 모양 → **컨테이너 안**. `doctor`, `fetch`, `run`, 하네스 만들기는 여기서.

> 문서의 `<라이브러리 이름>` 자리에는 위 표의 이름을 넣으세요. 꺾쇠(`< >`)까지 지우고 넣어야 합니다. 예: `python3 scripts/exp.py claim expat`

## 팀 규칙 (꼭 지키기)

1. **실험 전에 `claim`으로 라이브러리를 맡습니다.** 한 라이브러리는 한 사람이 한 컴퓨터에서 끝까지 돌립니다(커버리지를 합치려면 실행 기록이 한 컴퓨터에 있어야 함). 전에 `official`/`official_llm`을 돌린 라이브러리는 그 사람이 그 컴퓨터에서 이어서 하는 것이 가장 빠릅니다.
2. **결과는 `python3 scripts/exp.py submit <라이브러리 이름>`으로만 올립니다.** `git add -A`는 쓰지 마세요.
3. **실험 기간에는 공용 파일을 고치지 않습니다.** `gapfuzz/`, `scripts/`, `harnesses/`, `targets/`, `evaluation/README.md`, `README.md`가 공용 파일입니다. 특히 **한 번 push된 `gapfuzz_ops`와 `*_llm` 하네스는 다시 만들지 않습니다.** Claude는 돌릴 때마다 다른 코드를 내므로, 다시 만들면 앞 회차와 다른 하네스가 됩니다.
4. 한 컴퓨터에서 `run`을 동시에 두 개 띄우지 않습니다. 같은 실행 파일을 다시 빌드해서 실험이 깨질 수 있습니다.
5. 한 라이브러리는 처음부터 끝까지 **같은 `--jobs` 값**으로 돌리고, 그 값을 팀 채팅에 적어 둡니다(결과 파일에는 기록되지 않음).

---

# 환경 준비 (처음 한 번)

아래는 Windows(WSL)에서 Docker로 실제로 실행한 순서 그대로입니다. Ubuntu 24.04라면 Docker 없이 해도 됩니다(문서 뒤쪽의 [Docker 없이 (Ubuntu 24.04)](#docker-없이-ubuntu-2404) 절).

## 0. 저장소 받기, 내 Ubuntu 버전 확인

WSL 터미널에서:

```bash
cd ~
git clone https://github.com/gapfuzz/Gapfuzz.git gapfuzz
cd gapfuzz
lsb_release -a
```

- **24.04가 아니거나(26.04 등) 잘 모르겠으면** 1번부터 순서대로 진행합니다(권장).
- macOS나 Docker Desktop은 3번부터 같습니다. 단 Apple 칩 Mac은 2~3배 느려지니 가능하면 Windows/Linux 컴퓨터로 돌리세요.

이미 받아 둔 저장소가 있으면 `cd ~/gapfuzz && git pull`로 최신 상태를 받습니다.

## 1. Docker 설치

```bash
sudo apt update
sudo apt install -y docker.io tmux
sudo usermod -aG docker $USER        # 내 계정을 docker 그룹에 추가
```

`sudo`가 묻는 비밀번호는 **WSL Ubuntu를 설치할 때 정한 리눅스 계정 비밀번호**입니다(Windows 비밀번호와 다를 수 있음). 입력해도 화면에 아무것도 안 보이는 게 정상입니다.

> 비밀번호를 잊었으면 Windows **PowerShell**에서 `wsl -u root` → `passwd <내 리눅스 아이디>` → `exit`. 리눅스 아이디는 프롬프트 `user@DESKTOP-...`의 `@` 앞부분입니다.

그룹 추가가 적용되도록 **WSL 창을 닫았다가 다시 엽니다.**

## 2. Docker 켜기 (WSL을 새로 켤 때마다)

WSL은 보통 systemd가 꺼져 있어서 `systemctl start docker`, `service docker start`가 안 됩니다. Docker를 직접 띄웁니다.

```bash
sudo sh -c 'nohup dockerd > /var/log/dockerd.log 2>&1 &'
sleep 5
docker info | head -12
```

`Server:` 아래에 정보가 나오면 켜진 것입니다.

| 이런 메시지가 나오면 | 해결 |
| --- | --- |
| `failed to connect to the docker API ... no such file or directory` | Docker가 안 켜진 것. 위 `dockerd` 명령 실행 |
| `System has not been booted with systemd` | 정상. `systemctl` 대신 위 `dockerd` 명령 사용 |
| `permission denied while trying to connect to the docker API` | 그룹 권한이 아직 적용 안 됨. `newgrp docker` 실행 후 `cd ~/gapfuzz` (또는 WSL 창을 닫았다 열기) |
| `newgrp docker`가 `Password:`를 물음 | 그룹에 안 들어가 있는 것. `Ctrl+C` → `sudo usermod -aG docker $USER` → WSL 창 닫았다 열기 |
| `dockerd`를 켰는데도 안 됨 | `sudo tail -20 /var/log/dockerd.log`로 원인 확인. `iptables` 에러면 `sudo update-alternatives --set iptables /usr/sbin/iptables-legacy` 후 다시 켜기 |

> 매번 켜기 귀찮으면(선택): `printf '[boot]\nsystemd=true\n' | sudo tee -a /etc/wsl.conf` → PowerShell에서 `wsl --shutdown` → WSL 다시 열기. 이후 Docker가 자동으로 켜집니다. **실험이 돌고 있지 않을 때만** 하세요(`wsl --shutdown`은 모든 작업을 끕니다).

## 3. 이미지 빌드 (몇 분)

```bash
cd ~/gapfuzz
docker build -t gapfuzz .
```

마지막에 `Successfully tagged gapfuzz:latest`가 나오면 성공입니다. `DEPRECATED: The legacy builder is deprecated` 경고는 무시해도 됩니다.

---

# 실험 돌리기

```
[WSL]        Docker 켜기 → git pull → claim
[tmux 안]    컨테이너 들어가기
[컨테이너]   doctor → fetch → 짧게 확인 → run --plan union
[WSL 새 탭]  submit
```

## 4. 라이브러리 맡기 (WSL에서)

```bash
cd ~/gapfuzz
git pull                                              # 준비 담당이 만든 하네스를 받음
ls harnesses/<라이브러리 이름>/                        # gapfuzz_ops.* 가 있는지 확인
git config user.name                       # 지금 설정된 git 이름 확인 (비어 있으면 git config user.name "이름")
python3 scripts/exp.py libs                           # 진행 상황과 담당자 확인. 담당자가 '-'인 것을 고름
python3 scripts/exp.py claim <라이브러리 이름>        # 하나를 맡음 (GitHub에 자동 push)
```

`claim`은 **git 이름**으로 `evaluation/results/<라이브러리 이름>/OWNER.txt`에 담당자를 적어 올립니다. 다른 사람이 먼저 맡았으면 거부되니 다른 라이브러리를 고르세요. 전에 이미 맡았던 라이브러리는 다시 `claim`하지 않아도 됩니다.

> WSL에서 `python3 scripts/exp.py run ...`을 실행하면 `FileNotFoundError: ... 'llvm-cov'` 에러가 납니다. WSL에는 clang 도구가 없어서 그런 것이니, `run`은 꼭 **컨테이너 안에서** 하세요.

## 5. tmux 켜고 컨테이너 들어가기

tmux를 **먼저** 켜고 그 안에서 컨테이너에 들어가야, 창에서 빠져나와도 실험이 계속 돕니다.

```bash
cd ~/gapfuzz
tmux new -s exp
docker run --rm -it --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -e GAPFUZZ_BY="$(git config user.name)" -v "$PWD":/work gapfuzz bash
```

- `GAPFUZZ_BY`에는 git 이름이 자동으로 들어갑니다. 그대로 복사해서 쓰면 됩니다. 다른 이름을 넣으면 `run`이 `[run] <라이브러리 이름>는 <git 이름> 님 담당입니다. 정말 돌리려면 --force`라며 멈춥니다.
- `--cap-add SYS_PTRACE`는 메모리 누수 검사가 컨테이너 안에서 동작하는 데 필요합니다.
- 프롬프트가 `ubuntu@<숫자와 글자>:/work$`로 바뀌면 컨테이너 안입니다. `/work`가 WSL의 `~/gapfuzz`와 같은 폴더입니다.

## 6. 환경 확인, 소스 받기, 짧게 확인 (컨테이너 안)

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
python3 scripts/exp.py fetch <라이브러리 이름>   # 라이브러리 소스를 고정 커밋으로 받기 (third_party/)
python3 scripts/exp.py run <라이브러리 이름> --plan union --secs 60 --trials 1-2    # 짧게: 끝까지 도는지 확인 (15분쯤)
```

처음에 두 묶음의 하네스 목록이 나옵니다. **"적용 후" 목록에 `gapfuzz_ops`가 있는지 확인합니다.** 없으면 멈추고 4번의 `git pull`부터 다시 봅니다.

```
[run] <라이브러리 이름> (하네스 전체 기준): 기준 N개 ['official', ...]
[run]   적용 후 M개 ['official_llm', ..., 'gapfuzz_ops']
[run]   새로 돌릴 것 K개 (...) → 약 X시간
```

마지막에 `[run] 끝. 결과: evaluation/results/<라이브러리 이름>/UNION.md`가 나오면 정상입니다. 짧게 돌린 결과는 지웁니다(올리지 않음).

```bash
rm -rf evaluation/results/<라이브러리 이름>/60s evaluation/results/<라이브러리 이름>/union_60s evaluation/results/<라이브러리 이름>/UNION.md
```

## 7. 실험: 하네스마다 1시간 × 10회 (컨테이너 안)

```bash
python3 scripts/exp.py run <라이브러리 이름> --plan union --jobs <숫자>
```

### `--jobs` 정하기

`--jobs`는 한 번에 같이 돌릴 퍼징 개수입니다. 퍼징 하나가 CPU 코어 1개와 메모리 2GB를 쓰므로, 내 컴퓨터가 감당할 수 있는 만큼만 줍니다.

**1. 코어 수와 메모리 보기** (WSL이나 컨테이너 안에서)

```bash
lscpu | grep "Core(s) per socket"     # 코어 수
free -g | grep Mem                     # 첫 번째 숫자가 메모리(GB)
```

**2. 두 숫자를 구해서 작은 쪽을 씁니다**

- 코어 기준: 코어 수 − 1
- 메모리 기준: (메모리 − 2) ÷ 2, 소수점은 버림

| 코어 | 메모리 | 코어 기준 | 메모리 기준 | `--jobs` |
| --- | --- | --- | --- | --- |
| 4 | 8GB | 3 | 3 | 3 |
| 6 | 9GB | 5 | 3 | 3 |
| 8 | 16GB | 7 | 7 | 7 |
| 8 | 62GB | 7 | 30 | 7 |

잘 모르겠으면 `--jobs`를 빼고 실행합니다. 그러면 2개씩 돕니다.

- 계산한 값보다 크게 주지 않습니다. 서로 느려져 커버리지가 낮게 나오거나, 메모리가 모자라 실행이 죽습니다.
- 숫자가 커도 결과는 같습니다. 퍼징 하나는 똑같이 1시간이고, 전체가 끝나는 시각만 빨라집니다.

### 도는 순서

- 회차 먼저입니다: 1회차의 모든 하네스 → 2회차의 모든 하네스 → …. 중간에 멈춰도 끝난 회차까지는 비교할 수 있습니다.
- 이미 `official`, `official_llm`을 1시간 × 10회 돌린 기록(`out/targets/<라이브러리 이름>/<하네스>/long3600/`)이 있으면 그대로 씁니다.
- 고치지 않은 하네스는 두 묶음이 같은 실행 기록을 같이 씁니다. 다시 돌리지 않습니다.
- 회차마다 시드가 정해져 있습니다(회차 r의 시드 = 1000 + r). 나눠 돌려도 결과는 같습니다: `--trials 1-5`, 다음에 `--trials 6-10`.

처음 1시간은 출력이 없는 것이 정상입니다. 실행이 끝날 때마다 한 줄씩, 한 회차가 다 끝나면 합친 결과가 찍힙니다.

```
[run] 11-20 15:57 <라이브러리 이름>/official_compress r01: 분기 ...% 라인 ...% 겨냥 분기 ../.. 크래시 0
[run] r01 기준 합침: 분기 ...% 라인 ...% 어느 하네스도 안 부르는 API ../..
[run] r01 적용 후 합침: 분기 ...% 라인 ...% 어느 하네스도 안 부르는 API ../..
```

### tmux에서 빠져나오기 / 다시 붙기

- 빠져나오기: `Ctrl+B`를 누르고 손을 뗀 뒤 `D` → 실험은 계속 돔
- 다시 붙기: WSL에서 `tmux attach -t exp`

### 돌리는 동안 지킬 것

- **WSL 창은 닫지 말고 최소화만.** 창을 모두 닫으면 WSL이 꺼지면서 실험도 멈출 수 있습니다.
- **Windows 절전 끄기:** 설정 → 시스템 → 전원 → "절전 모드로 전환"을 "안 함". 노트북이면 충전기를 연결하고 덮개를 닫아도 안 꺼지게 설정.
- 그 컴퓨터로 게임, 영상 편집 같은 무거운 작업을 하지 않습니다. 코어를 뺏겨 결과가 흔들립니다.

### 중간에 끊겼다면

2번(Docker 켜기) → 5번(tmux, 컨테이너) → 7번의 `run` 명령을 **같은 `--jobs`로** 다시 실행합니다. 끝난 실행은 건너뛰고, 돌던 실행만 처음부터 다시 돕니다. 같은 컴퓨터에서 이어야 합니다(실행 기록이 `out/`에 있음).

## 8. 결과 올리기 (WSL에서)

`[run] 끝. 결과: evaluation/results/<라이브러리 이름>/UNION.md  올리기: python3 scripts/exp.py submit <라이브러리 이름>`가 나오면 끝난 것입니다. 컨테이너 안에는 GitHub 로그인이 없으니, **WSL 창에 새 탭**을 열어서 올립니다.

```bash
cd ~/gapfuzz
python3 scripts/exp.py submit <라이브러리 이름>
```

올린 뒤 GitHub에서 `evaluation/results/<라이브러리 이름>/union_1h/`와 `UNION.md`가 보이는지 확인합니다.

## 9. 결과 보기

```bash
cat evaluation/results/<라이브러리 이름>/UNION.md       # 묶음 대 묶음 (run과 submit이 자동으로 만듦)
cat evaluation/results/<라이브러리 이름>/REPORT.md      # official 대 official_llm (submit이 만듦. official_llm이 있는 라이브러리만)
```

| 항목 | 뜻 | 효과가 있다고 말할 수 있는 기준 |
| --- | --- | --- |
| 분기 커버리지 중앙값 [최소–최대] | 10회 결과의 가운데 값과 범위 | 적용 후가 더 높음 |
| 어느 하네스도 안 부르는 API | 묶음 전체가 한 번도 실행하지 않은 공개 API 수 | 적용 후가 더 적음 |
| A12 | 적용 후 한 회가 기준 한 회보다 높을 확률 | 0.5면 차이 없음, **0.71 이상이면 큰 차이** |
| p (Mann-Whitney U) | 차이가 우연일 가능성 | **0.05 미만** |
| 겨냥 분기 (`REPORT.md`) | 도구가 짚은 분기가 회차마다 열렸는지 | `official_llm`에서 열리고, `official`과 대조군에서는 안 열림 |

읽을 때 주의할 점:

- 적용 후 묶음은 `gapfuzz_ops`만큼 하네스가 하나 더 많아 회차당 총 퍼징 시간이 1시간 깁니다. `UNION.md`에 이 문장이 자동으로 들어갑니다.
- 크래시가 난 실행은 거기서 퍼징이 멈춰 커버리지가 낮게 나옵니다. 회차 결과의 `crashes`, `triage`를 함께 봅니다.
- 라이브러리끼리 % 숫자를 직접 비교하지 않습니다. 같은 라이브러리 안에서 기준과 적용 후를 비교합니다.

하네스별 숫자를 한 표로 보려면: `python3 scripts/cov_table.py <라이브러리 이름> official official_llm gapfuzz_ops --sub long3600`

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
python3 scripts/exp.py run <라이브러리 이름> --plan union --secs 60 --trials 1-2    # 짧게 확인, 적용 후 목록에 gapfuzz_ops가 있는지
rm -rf evaluation/results/<라이브러리 이름>/60s evaluation/results/<라이브러리 이름>/union_60s evaluation/results/<라이브러리 이름>/UNION.md
python3 scripts/exp.py run <라이브러리 이름> --plan union --jobs 3                 # 본 실험
# Ctrl+B, D 로 빠져나오기 / tmux attach -t exp 로 다시 붙기

# [WSL 새 탭] 끝나면
python3 scripts/exp.py submit <라이브러리 이름>
```

## 보조 실험: 24시간 × 1회

"OSS-Fuzz 하네스를 오래 돌리면 따라잡는 것 아니냐"를 보는 실험입니다. `official`과 `official_llm` 두 개만 24시간 동안 나란히 돌리고, 구간마다 커버리지를 재서 시간에 따른 곡선을 만듭니다. 하네스 전체 기준이 아니며, `official_llm`이 있는 라이브러리에서만 됩니다. 7번이 **끝나고 submit한 뒤에** 시작합니다.

```bash
python3 scripts/exp.py run <라이브러리 이름> --plan 24h     # 컨테이너 안, 약 24.5시간
```

- 10분, 20분, 30분, 그 뒤 1시간마다 한 줄씩 찍힙니다.
- 끊기면 같은 명령을 다시 실행하면 마지막으로 끝난 구간 다음부터 이어 돕니다. **같은 컴퓨터에서** 이어야 합니다.
- 끝나면 8번처럼 `submit`합니다. `REPORT.md`의 24시간 표에서, 24시간이 지나도 `official`이 따라잡지 못하는지 봅니다.

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
python3 scripts/exp.py run <라이브러리 이름> --plan union --jobs 3
```

컨테이너가 없으므로 모든 명령을 같은 터미널에서 실행합니다. 나머지(짧게 확인, 빠져나오기, submit, 결과 보기)는 위와 같습니다.

## 결과 파일과 충돌이 안 나는 이유

| 무엇 | 어디에 | git |
| --- | --- | --- |
| 코퍼스, 커버리지, 바이너리, 크래시 입력 (수 GB) | `out/` | 올리지 않음 (`.gitignore`) |
| 라이브러리 소스 | `third_party/` | 올리지 않음, `fetch`가 고정 커밋으로 받음 |
| 하네스별 회차 결과 (약 4KB) | `evaluation/results/<라이브러리>/1h/<하네스>/rNN.json` | 올림 |
| 회차별 기준 묶음을 합친 결과 | `evaluation/results/<라이브러리>/union_1h/base/rNN.json` | 올림 |
| 회차별 적용 후 묶음을 합친 결과 | `evaluation/results/<라이브러리>/union_1h/fixed/rNN.json` | 올림 |
| 묶음 비교 요약 (중앙값, A12, p) | `evaluation/results/<라이브러리>/UNION.md` | 올림 |
| `official` 대 `official_llm` 보고서 | `evaluation/results/<라이브러리>/REPORT.md` | 올림 |
| 24시간 실험의 구간별 측정값 | `evaluation/results/<라이브러리>/24h/<하네스>.json` | 올림 |
| 담당자 표시 | `evaluation/results/<라이브러리>/OWNER.txt` | 올림 |

각자 **자기 라이브러리 폴더만** 바꾸므로 서로 같은 파일을 건드리지 않습니다. 그래서 `submit`의 `pull --rebase`가 항상 깔끔하게 됩니다. `run`은 도구 코드에 커밋하지 않은 변경이 있으면 경고합니다.

### 결과 파일에 들어가는 것

하네스별 회차 결과(`1h/<하네스>/rNN.json`):

```json
{"lib": "expat", "harness": "official_llm", "trial": 3, "secs": 3600, "seed": 1003,
 "coverage": {"branches": {"pct": 32.4, "covered": 1234, "count": 3810}, "lines": {...}, ...},
 "execs": 41234567, "corpus": 2310, "crashes": [], "triage": [],
 "targets": [{"fix": 1, "applied": true, "line": 1668, "opened": true}, ...],
 "by": "이름", "env": {"clang": "Ubuntu clang version 18.1.3 ...", "cpu": "...", "tool_commit": "abc1234"}}
```

`targets`는 도구가 대표 하네스에서 "고칠 곳"으로 짚은 분기(`evaluation/experiments/targets/<라이브러리>.json`)가 이 회차에 열렸는지입니다. `applied: false`는 Claude에게 맡기지 않은 대조군입니다. 묶음 결과(`union_1h/{base,fixed}/rNN.json`)에는 그 회차에 합친 하네스 목록, 합친 커버리지, 어느 하네스도 안 부르는 API 수, 회차당 총 퍼징 시간이 들어갑니다.

## 참고: `official_llm`은 어떻게 만들었나

gapfuzz는 OSS-Fuzz 대표 하네스를 분석해 "하네스의 이 부분 때문에 라이브러리 분기가 막혔으니 이렇게 고쳐라"라는 제안을 냅니다(예: zlib에서 "`inflate`를 하네스가 직접 부르지 않아 `flush` 값이 한 가지뿐 → 직접 불러 다른 값을 넘겨라"). 라이브러리마다 이 제안들 대부분을 Claude에게 맡기고, 한 개씩은 **일부러 맡기지 않고 대조군으로 남겼습니다.** 맡긴 제안의 분기는 열리고 대조군의 분기는 안 열려야, 열린 이유가 "오래 돌려서 운 좋게"가 아니라 "제안대로 고쳐서"라고 말할 수 있습니다.

| 라이브러리 | Claude에게 맡긴 제안 | 대조군 (일부러 안 맡김) | 짧은 검사(60초 × 2회)에서 겨냥 분기 열림 |
| --- | --: | --: | --: |
| pugixml | 3개 | 1개 | 30/33 |
| cjson | 4개 | 1개 | 7/7 |
| jsoncpp | 2개 | 1개 | 7/8 |
| zlib | 3개 | 1개 | 11/11 |
| expat | 3개 | 1개 | 6/7 |
| json-c | 4개 | 1개 | 4/5 |
| tinyxml2 | 6개 | 1개 | `evaluation/artifacts/llm/combined/tinyxml2/report.md` 참고 |

제안 내용과 Claude가 바꾼 코드는 `evaluation/artifacts/llm/combined/<라이브러리 이름>/report.md`, 만든 방법은 `scripts/make_llm_harness.py`에 있습니다. 나머지 하네스를 고친 `official_<이름>_llm`은 대조군 없이 규칙으로 제안을 골랐습니다. 고르는 방식이 다르다는 점을 결과에 적습니다.

## 그 밖의 문제

| 증상 | 해결 |
| --- | --- |
| "적용 후" 목록에 `gapfuzz_ops`가 없음 | `git pull`로 최신 저장소를 받으세요. 그래도 없으면 하네스가 아직 push되지 않은 것입니다 |
| `run`이 `<라이브러리 이름>는 ... 님 담당입니다` | 다른 사람이 맡은 라이브러리입니다. 본인이 맞다면 5번의 `GAPFUZZ_BY`를 확인하세요 |
| `doctor`에서 clang 버전이 18이 아님 | Docker를 쓰거나 Ubuntu 24.04에서 실행 |
| `libFuzzer/ASan으로 빌드 실패` | `sudo apt install libclang-rt-18-dev` (Docker면 이미지 다시 빌드) |
| 컨테이너 안에서 `LeakSanitizer has encountered a fatal error` | `docker run`에 `--cap-add SYS_PTRACE`를 넣었는지 확인 |
| 크래시가 남 | 그대로 두세요. 자동으로 원인 귀속(triage)을 돌려 결과 파일에 판정을 남깁니다. 팀 채팅에 알려 주세요 |
| 디스크가 부족함 | 끝난 회차의 `out/targets/<라이브러리>/*/long3600/r*/corpus`는 지워도 됩니다(`cov.profdata`는 남겨야 합칠 수 있음). `*/day/`는 24시간이 끝난 뒤에만 지우세요 |
| 24시간을 다시 실행했더니 "이어서 돌릴 코퍼스가 없습니다" | `day/` 폴더가 지워졌거나 다른 컴퓨터입니다. 처음부터 다시 하려면 `evaluation/results/<라이브러리>/24h/`를 지우고 실행하세요 |
| `submit`에서 rebase 실패 | 다른 사람이 같은 폴더나 공용 파일을 건드린 것입니다. 팀 채팅에서 확인하세요 |
