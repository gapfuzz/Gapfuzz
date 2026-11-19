#!/usr/bin/env python3
"""라이브러리 설정 파일(targets/<이름>.json)로 빌드·퍼징·커버리지·갭 분석을 돌리는 범용 실행기.

모든 라이브러리가 이 실행기를 쓴다.

  python3 scripts/tgt.py build   pugixml harnesses/pugixml/official.cpp
  python3 scripts/tgt.py repeat  pugixml --trials 5 --secs 120 official official_llm
  python3 scripts/tgt.py analyze pugixml official out/targets/pugixml/official/r1
  python3 scripts/tgt.py union   zlib            # OSS-Fuzz 하네스 전체(설정의 "ossfuzz")의 커버리지를 합쳐서 분석

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


def analyze(t: dict, h: str, d: Path, label: str | None = None) -> None:
    """h: 호출 지점을 읽을 하네스. label: 리포트에 쓸 이름(합친 커버리지 분석 때 "_union")."""
    args = [sys.executable, "-m", "gapfuzz", "analyze", "--name", f"{t['name']}-{label or h}-{d.name}"]
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


def ossfuzz_harnesses(t: dict) -> list[str]:
    """이 라이브러리의 OSS-Fuzz 하네스 이름들. 설정의 "ossfuzz" 목록, 없으면 official 하나."""
    return list(t.get("ossfuzz") or ["official"])


def union(t: dict, harnesses: list[str] | None = None, secs: int = 120, r: int = 1, name: str = "_union", sub: str = "") -> Path:
    """OSS-Fuzz 하네스 여러 개의 커버리지를 하나로 합치고, 합친 결과로 갭 분석을 한다.

    하네스마다 따로 돌린 실행 기록(out/targets/<이름>/<하네스>/r<k>/cov.profdata)을 합쳐
    out/targets/<이름>/_union/r<k>/coverage.json 을 만든다. 실행 기록이 없는 하네스는 secs초로 먼저 돌린다.
    합친 커버리지에서 "호출 안 함"은 어느 하네스도 부르지 않는 API, "막힌 분기"는 모든 하네스를 합쳐도 한쪽으로만 간 분기다.

    한계: 호출 지점(인자 고정 여부)은 대표 하네스(목록의 첫 번째)의 소스만 읽는다. 다른 하네스 안에서 고정된 인자는
    그 하네스를 따로 분석해야 나온다(tgt.py analyze). 합친 분석의 '고칠 곳'은 "대표 하네스가 고정했고, 다른 하네스도 열지 못한 분기"다.
    """
    hs = harnesses or ossfuzz_harnesses(t)
    root = ROOT / "out" / "targets" / t["name"]
    rd = lambda h: (root / h / sub if sub else root / h) / f"r{r}"       # sub: 결과 하위 폴더 (팀 실험은 "long3600")
    for h in hs:
        b = root / h
        if not (b / "cov").exists():
            build(t, h)
        if not (rd(h) / "cov.profdata").exists():
            print(f"[tgt] {t['name']}/{h}: 실행 기록이 없어 {secs}초 퍼징부터 합니다", flush=True)
            run_one(t, h, r, secs, 1000, 10, None, sub=sub)
    d = (root / name / sub if sub else root / name) / f"r{r}"                     # name: 결과 폴더. 적용 후를 따로 합칠 때 다른 이름을 준다(예: _union_after)
    subprocess.run(["rm", "-rf", str(d)], check=True)
    d.mkdir(parents=True)
    subprocess.run(["llvm-profdata", "merge", "-sparse", *[str(rd(h) / "cov.profdata") for h in hs],
                    "-o", str(d / "cov.profdata")], check=True)
    bins = [str(root / hs[0] / "cov")] + [x for h in hs[1:] for x in ("-object", str(root / h / "cov"))]
    files = [str(s) for s in t["srcs"]] + [str(x) for x in t["headers"]]
    with open(d / "coverage.json", "w") as f:
        subprocess.run(["llvm-cov", "export", "-format=text", f"-instr-profile={d / 'cov.profdata'}", *bins, *files],
                       stdout=f, stderr=subprocess.DEVNULL, check=True)
    rep = subprocess.run(["llvm-cov", "report", f"-instr-profile={d / 'cov.profdata'}", *bins, *files],
                         capture_output=True, text=True, check=True).stdout
    (d / "coverage_summary.txt").write_text(rep)
    analyze(t, hs[0], d, label=name)

    # 하네스별로 어떤 API를 실행하는지 표로 남긴다
    per, total = {}, 0
    for h in hs:
        g = json.load(open(rd(h) / "gap" / "gap.json"))
        per[h] = {x["mangled"]: x["api"] for x in g["results"] if x["category"] != "NOT_CALLED"}
        total = len(g["results"])
    ug = json.load(open(d / "gap" / "gap.json"))
    never = [x["api"] for x in ug["results"] if x["category"] == "NOT_CALLED"]
    tot = rep.strip().splitlines()[-1].split()
    info = {"lib": t["name"], "harnesses": hs, "apis": total, "not_called_union": len(never),
            "not_called_each": {h: total - len(per[h]) for h in hs}, "lines": tot[9], "branches": tot[12],
            "reached_by": {api: [h for h in hs if m in per[h]] for h0 in hs for m, api in per[h0].items()}}
    json.dump(info, open(d / "union.json", "w"), ensure_ascii=False, indent=1)
    md = [f"# OSS-Fuzz 하네스 전체 기준 — {t['name']}", "",
          f"하네스 {len(hs)}개의 커버리지를 합쳤습니다 (회차 r{r}). 라인 {tot[9]}, 분기 {tot[12]}.", "",
          f"공개 API {total}개 중 **어느 하네스도 부르지 않는 것 {len(never)}개**.", "",
          "| 하네스 | 이 하네스만 볼 때 호출 안 함 |", "|---|---:|"]
    md += [f"| {h} | {total - len(per[h])} |" for h in hs] + [f"| **전부 합쳐서** | **{len(never)}** |", ""]
    (d / "union.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[tgt] union {t['name']} ({name}): 하네스 {len(hs)}개, 라인 {tot[9]} 분기 {tot[12]}, 어느 하네스도 안 부르는 API {len(never)}/{total} -> {d}")
    return d


def measure_dir(t: dict, h: str, d: Path) -> list[str]:
    """d/corpus 를 커버리지 바이너리로 다시 실행해 d 에 cov.profdata, coverage.json, 요약, 갭 분석을 만든다."""
    b = ROOT / "out" / "targets" / t["name"] / h
    for f in d.glob("cov-*.profraw"):
        f.unlink()
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
    return rep.strip().splitlines()[-1].split()


def snap_dir(t: dict, h: str, r: int, sub: str, at: int) -> Path:
    """실행 중 at초 시점의 코퍼스로 잰 결과가 놓이는 곳: out/targets/<이름>/<하네스>/<sub>/snap<at>/r<k>."""
    b = ROOT / "out" / "targets" / t["name"] / h
    return (b / sub if sub else b) / f"snap{at}" / f"r{r}"


def _copy_corpus(src: Path, dst: Path, keep=None) -> int:
    """코퍼스 파일을 하드 링크로 옮겨 담는다(용량을 더 쓰지 않음). 링크가 안 되는 파일 시스템이면 복사한다."""
    import shutil
    subprocess.run(["rm", "-rf", str(dst.parent)], check=True)
    dst.mkdir(parents=True)
    n = 0
    for f in list(os.scandir(src)):
        try:
            if keep is not None and not keep(f):
                continue
            try:
                os.link(f.path, dst / f.name)
            except OSError:
                shutil.copy2(f.path, dst / f.name)
            n += 1
        except FileNotFoundError:           # 퍼저가 방금 더 작은 입력으로 바꾸면서 지운 파일
            pass
    return n


def prefix_from_mtime(t: dict, h: str, r: int, sub: str, at: int, started: float) -> Path | None:
    """실행 중 스냅샷이 없는 예전 기록용 근사: 끝난 코퍼스에서 파일 시각이 시작 후 at초 이내인 입력만 골라 잰다.
    퍼저가 나중에 더 작은 입력으로 바꾼 것은 빠지므로 실제 at초 시점보다 낮게 나올 수 있다(method: "mtime")."""
    b = ROOT / "out" / "targets" / t["name"] / h
    d = (b / sub if sub else b) / f"r{r}"
    if not (d / "corpus").is_dir():
        return None
    sd = snap_dir(t, h, r, sub, at)
    n = _copy_corpus(d / "corpus", sd / "corpus", keep=lambda f: f.stat().st_mtime <= started + at)
    measure_dir(t, h, sd)
    json.dump({"secs": at, "method": "mtime", "files": n}, open(sd / "snap.json", "w"))
    return sd


def run_one(t: dict, h: str, r: int, secs: int, seed_base: int, nice: int, dict_path: str | None, sub: str = "",
            snaps: list[int] | None = None) -> str:
    """sub: 결과 하위 폴더 (예: "long3600"). 비우면 out/targets/<이름>/<하네스>/r<k>.
    snaps: 퍼징 시작 후 이 시각(초)들에 코퍼스를 그대로 찍어 두고, 끝난 뒤 그 시점의 커버리지를 따로 잰다
           (동일 계산량 비교용). 끝난 뒤 파일 시각으로 자르면 퍼저가 바꿔치기한 입력이 빠지므로 실행 중에 찍는다."""
    b = ROOT / "out" / "targets" / t["name"] / h
    d = (b / sub if sub else b) / f"r{r}"
    subprocess.run(["rm", "-rf", str(d)], check=True)
    (d / "corpus").mkdir(parents=True)
    dct = dict_path or (str(ROOT / t["dict"]) if t.get("dict") else None)
    args = ["nice", "-n", str(nice), str(b / "fuzz"), f"-max_total_time={secs}", f"-seed={seed_base + r}",
            "-rss_limit_mb=2048", "-timeout=10", "-print_final_stats=1", f"-artifact_prefix={d}/", str(d / "corpus")]
    if dct:
        args.insert(-1, f"-dict={dct}")
    taken = []
    with open(d / "fuzz.log", "w") as log:
        p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT)
        t0 = time.time()
        for at in sorted(set(snaps or [])):
            while p.poll() is None and time.time() - t0 < at:
                time.sleep(max(0.05, min(1.0, at - (time.time() - t0))))
            early = p.poll() is not None                     # 크래시 등으로 그 전에 끝났으면 마지막 코퍼스가 곧 그 시점의 코퍼스
            sd = snap_dir(t, h, r, sub, at)
            n = _copy_corpus(d / "corpus", sd / "corpus")
            taken.append((at, sd, {"secs": at, "method": "snapshot", "files": n, "ended_early": early,
                                   "taken_after_secs": round(time.time() - t0, 1)}))
        p.wait()
    tot = measure_dir(t, h, d)
    for at, sd, info in taken:
        measure_dir(t, h, sd)
        json.dump(info, open(sd / "snap.json", "w"))
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
    un = sub.add_parser("union", help="OSS-Fuzz 하네스 전체의 커버리지를 합쳐서 분석")
    un.add_argument("target"); un.add_argument("harnesses", nargs="*", help="합칠 하네스 (기본: 설정의 ossfuzz 목록)")
    un.add_argument("--secs", type=int, default=120, help="실행 기록이 없는 하네스를 돌릴 시간(초)")
    un.add_argument("--name", default="_union", help="결과 폴더 이름 (기본 _union). 적용 후를 합칠 때는 다른 이름을 준다")
    un.add_argument("--add", action="append", default=[], help="설정의 ossfuzz 목록에 더해 함께 합칠 하네스 (여러 번 가능, 예: gapfuzz_ops)")
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
    elif a.cmd == "union":
        union(t, (a.harnesses or ossfuzz_harnesses(t)) + a.add, a.secs, name=a.name)


if __name__ == "__main__":
    main()
