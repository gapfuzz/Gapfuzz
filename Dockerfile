# gapfuzz 실험 환경: 팀원 모두 같은 컴파일러(clang 18.1.3)와 도구로 돌리기 위한 이미지
#   docker build -t gapfuzz .
#   docker run --rm -it --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp -e GAPFUZZ_BY="이름" -v "$PWD":/work gapfuzz python3 scripts/exp.py doctor
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1
# Ubuntu 24.04 저장소의 clang/llvm은 18.1.3으로 고정되어 있다 (doctor가 버전을 확인)
RUN apt-get update && apt-get install -y --no-install-recommends \
        clang llvm libclang-rt-18-dev \
        git ca-certificates python3 python3-scipy tmux \
    && rm -rf /var/lib/apt/lists/*
# 마운트한 저장소를 다른 사용자 id로 열어도 git이 거부하지 않게
RUN git config --system --add safe.directory '*'
WORKDIR /work
CMD ["bash"]
