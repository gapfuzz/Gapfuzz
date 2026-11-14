#!/usr/bin/env bash
# Fuzz Introspector(소스 분석 방식)를 TinyXML2 공식 하네스에 돌린다. 결과는 samples/compare_fuzz_introspector.md 참고.
#
# 사용법: scripts/run_fi.sh [회차 디렉터리, 기본 out/repeat/official/r1]
#   - FI와 tree-sitter 문법들을 GitHub에서 받아 제자리 빌드한다 (pypi 접근이 막힌 환경용)
#   - cxxfilt, rust_demangler는 작은 대체 모듈(c++filt 호출)을 쓴다
#   결과: out/fi/out/{summary.json, branch-blockers.json, result.json}
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="${1:-$ROOT/out/repeat/official/r1}"
W="$ROOT/out/fi"; D="$W/deps"
mkdir -p "$D"

clone() { [ -d "$D/$(basename "$1")" ] || git clone -q --depth 1 --branch "$2" "https://github.com/$1.git" "$D/$(basename "$1")"; }
[ -d "$D/fuzz-introspector" ] || git clone -q --depth 1 https://github.com/ossf/fuzz-introspector.git "$D/fuzz-introspector"
clone tree-sitter/py-tree-sitter v0.23.2 && git -C "$D/py-tree-sitter" submodule -q update --init --depth 1
for g in cpp:v0.23.4 c:v0.23.4 python:v0.23.6 go:v0.23.4 java:v0.23.5 rust:v0.23.2; do clone "tree-sitter/tree-sitter-${g%%:*}" "${g##*:}"; done
clone tqdm/tqdm v4.66.5 && echo '__version__ = "4.66.5"' > "$D/tqdm/tqdm/_dist_ver.py"
for d in py-tree-sitter tree-sitter-cpp tree-sitter-c tree-sitter-python tree-sitter-go tree-sitter-java tree-sitter-rust; do
    (cd "$D/$d" && python3 setup.py -q build_ext --inplace >/dev/null 2>&1)
done
mkdir -p "$D/shim/cxxfilt"
cat > "$D/shim/cxxfilt/__init__.py" <<'EOF'
import subprocess
class InvalidName(Exception): pass
def demangle(name, external_only=True):
    return subprocess.run(["c++filt", name], capture_output=True, text=True).stdout.strip() or name
EOF
echo 'def demangle(name): return name' > "$D/shim/rust_demangler.py"
PP="$D/shim:$D/tqdm:$D/py-tree-sitter:$D/fuzz-introspector/src"
for g in cpp c python go java rust; do PP="$PP:$D/tree-sitter-$g/bindings/python"; done
export PYTHONPATH="$PP"

rm -rf "$W/src" "$W/out"; mkdir -p "$W/src"
cp "$ROOT"/third_party/tinyxml2/tinyxml2.{h,cpp} "$W/src/"
cp "$ROOT/harnesses/official.cpp" "$W/src/official_fuzzer.cpp"
llvm-cov show -instr-profile="$RUN/cov.profdata" -object="$RUN/cov" -line-coverage-gt=0 \
    -show-branches=count -show-expansions > "$W/src/official_fuzzer.covreport"
cd "$W"
python3 "$D/fuzz-introspector/src/main.py" full --target-dir src --language c++ --out-dir out --name tinyxml2 > fi_full.log 2>&1 || true
cp src/* out/
(cd out && python3 "$D/fuzz-introspector/src/main.py" report --target-dir . --language c-cpp --name tinyxml2 > ../fi_report.log 2>&1 || true)
echo "[fi] -> $W/out/summary.json, branch-blockers.json"
