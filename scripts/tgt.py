#!/usr/bin/env python3
"""라이브러리 설정 파일(targets/<이름>.json)로 빌드·퍼징·커버리지·갭 분석을 돌리는 범용 실행기.

모든 라이브러리가 이 실행기를 쓴다(예전의 TinyXML2 전용 스크립트는 legacy/로 옮김).

  python3 scripts/tgt.py build   pugixml harnesses/pugixml/official.cpp
  python3 scripts/tgt.py repeat  pugixml --trials 5 --secs 120 official official_llm
  python3 scripts/tgt.py analyze pugixml official out/targets/pugixml/official/r1

설정 파일 항목
  lang       "c" 또는 "c++"            lib_dir   라이브러리 소스 디렉터리
  sources    lib_dir 안의 구현 파일들   header    공개 API 헤더 (lib_dir 기준, 문자열 또는 목록)
  include_dirs  추가 include 디렉터리 (lib_dir 기준)
  namespace  공개 API 네임스페이스 (C는 "")   internal_classes  공개 API에서 뺄 클래스
  dict       퍼징 딕셔너리                cflags    추가 컴파일 옵션
  harness_dir  하네스 디렉터리 (기본 harnesses/<이름>)
결과: out/targets/<이름>/<하네스>/{fuzz,cov}, 회차별 out/targets/<이름>/<하네스>/r<k>/
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ["-g", "-O1", "-fno-omit-frame-pointer", "-fno-optimize-sibling-calls"]


def load(name: str) -> dict:
    t = json.load(open(ROOT / "targets" / f"{name}.json"))
    t["lib"] = ROOT / t["lib_dir"]
    t["srcs"] = [t["lib"] / s for s in t["sources"]]
    t["headers"] = [t["lib"] / h for h in ([t["header"]] if isinstance(t["header"], str) else t["header"])]
    t["incs"] = [t["lib"]] + [t["lib"] / i for i in t.get("include_dirs", [])]
    return t


def harness_path(t: dict, h: str) -> Path:
    base = ROOT / t.get("harness_dir", f"harnesses/{t['name']}")
    for ext in (".cpp", ".c", ".cc"):
        p = base / f"{h}{ext}"
        if p.exists():
            return p
    raise SystemExit(f"하네스 없음: harnesses/{t['name']}/{h}.*")


def compile_cmds(t: dict, harness: Path, out: Path, mode: str) -> list[list[str]]:
    """퍼징용(fuzz) 또는 커버리지용(cov) 바이너리를 만드는 명령. C 파일은 clang, C++은 clang++로 컴파일."""
    san = ["-fsanitize=fuzzer,address,undefined"] if mode == "fuzz" else \
          ["-fsanitize=fuzzer", "-fprofile-instr-generate", "-fcoverage-mapping"]
    inc = [f"-I{d}" for d in t["incs"]] + [f"-I{ROOT / 'harnesses' / 'include'}"]
    objs, cmds = [], []
    for src in [*t["srcs"], harness]:
        cc = ["clang", "-std=gnu11"] if src.suffix == ".c" else ["clang++", "-std=c++17"]
        o = out / f"{mode}_{src.stem}.o"
        san_c = [x.replace("fuzzer,", "fuzzer-no-link,") if x.startswith("-fsanitize=fuzzer,") else
                 ("-fsanitize=fuzzer-no-link" if x == "-fsanitize=fuzzer" else x) for x in san]
        cmds.append([*cc, *BASE, *inc, *t.get("cflags", []), *san_c, "-c", str(src), "-o", str(o)])
        objs.append(str(o))
    cmds.append(["clang++", *BASE, *san, *objs, "-o", str(out / mode)])
    return cmds


def build(t: dict, h: str) -> Path:
    harness = harness_path(t, h)
    out = ROOT / "out" / "targets" / t["name"] / h
    out.mkdir(parents=True, exist_ok=True)
    for mode in ("fuzz", "cov"):
        for c in compile_cmds(t, harness, out, mode):
            subprocess.run(c, check=True)
    print(f"[tgt] build {t['name']}/{h} -> {out}")
    return out


def analyze(t: dict, h: str, d: Path) -> None:
    args = [sys.executable, "-m", "gapfuzz", "analyze", "--name", f"{t['name']}-{h}-{d.name}"]
    for x in t["headers"]:
        args += ["--header", str(x)]
    for x in t["srcs"]:
        args += ["--source", str(x)]
    for x in t["incs"]:
        args += ["--include", str(x)]
    for f in t.get("cflags", []):
        if f.startswith("-D"):
            args += ["--define", f[2:]]
    args += ["--harness", str(harness_path(t, h)), "--include", str(ROOT / "harnesses" / "include"),
            "--namespace", t["namespace"], "--coverage", str(d / "coverage.json"), "--out", str(d / "gap")]
    if (d / "args.json").exists():                 # argtrace 기록이 있으면 판정 근거로 쓴다
        args += ["--args", str(d / "args.json")]
    if t.get("internal_branches"):
        args.append("--internal-branches")
    if t.get("internal_classes") is not None:
        for c in t["internal_classes"]:
            args += ["--internal-class", c]
        if not t["internal_classes"]:
            args += ["--internal-class", "__none__"]
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def run_one(t: dict, h: str, r: int, secs: int, seed_base: int, nice: int, dict_path: str | None, sub: str = "") -> str:
    """sub: 결과 하위 폴더 (예: "long3600"). 비우면 out/targets/<이름>/<하네스>/r<k>."""
    b = ROOT / "out" / "targets" / t["name"] / h
    d = (b / sub if sub else b) / f"r{r}"
    subprocess.run(["rm", "-rf", str(d)], check=True)
    (d / "corpus").mkdir(parents=True)
    dct = dict_path or (str(ROOT / t["dict"]) if t.get("dict") else None)
    args = ["nice", "-n", str(nice), str(b / "fuzz"), f"-max_total_time={secs}", f"-seed={seed_base + r}",
            "-rss_limit_mb=2048", "-timeout=10", "-print_final_stats=1", f"-artifact_prefix={d}/", str(d / "corpus")]
    if dct:
        args.insert(-1, f"-dict={dct}")
    with open(d / "fuzz.log", "w") as log:
        subprocess.run(args, stdout=log, stderr=subprocess.STDOUT)
    env = dict(os.environ, LLVM_PROFILE_FILE=str(d / "cov-%p.profraw"))
    subprocess.run([str(b / "cov"), "-runs=0", str(d / "corpus")], env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    raws = [str(p) for p in d.glob("cov-*.profraw")]
    subprocess.run(["llvm-profdata", "merge", "-sparse", *raws, "-o", str(d / "cov.profdata")], check=True)
    files = [str(s) for s in t["srcs"]] + [str(x) for x in t["headers"]]
    with open(d / "coverage.json", "w") as f:
        subprocess.run(["llvm-cov", "export", "-format=text", f"-instr-profile={d / 'cov.profdata'}", str(b / "cov"), *files],
                       stdout=f, check=True)
    rep = subprocess.run(["llvm-cov", "report", f"-instr-profile={d / 'cov.profdata'}", str(b / "cov"), *files],
                         capture_output=True, text=True, check=True).stdout
    (d / "coverage_summary.txt").write_text(rep)
    analyze(t, h, d)
    tot = rep.strip().splitlines()[-1].split()
    crashes = sum(1 for f in os.listdir(d) if f.split("-")[0] in ("crash", "leak", "timeout", "oom"))
    line = f"[tgt] {time.strftime('%H:%M')} {t['name']}/{h} r{r}: lines {tot[9]} branches {tot[12]} crashes={crashes}"
    print(line, flush=True)
    return line


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("target"); b.add_argument("harnesses", nargs="+")
    rp = sub.add_parser("repeat"); rp.add_argument("target"); rp.add_argument("harnesses", nargs="+")
    rp.add_argument("--trials", type=int, default=5); rp.add_argument("--secs", type=int, default=120)
    rp.add_argument("--seed-base", type=int, default=1000); rp.add_argument("--nice", type=int, default=10)
    rp.add_argument("--dict")
    an = sub.add_parser("analyze"); an.add_argument("target"); an.add_argument("harness"); an.add_argument("dir")
    a = ap.parse_args()
    t = load(a.target)
    if a.cmd == "build":
        for h in a.harnesses:
            build(t, Path(h).stem if "/" in h else h)
    elif a.cmd == "repeat":
        for r in range(1, a.trials + 1):
            for h in a.harnesses:
                run_one(t, h, r, a.secs, a.seed_base, a.nice, a.dict)
    elif a.cmd == "analyze":
        analyze(t, a.harness, Path(a.dir))


if __name__ == "__main__":
    main()
