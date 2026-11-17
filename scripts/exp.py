#!/usr/bin/env python3
"""팀 실험 실행기: 라이브러리를 골라 장시간 반복 실험을 돌리고, 작은 결과 파일만 evaluation/results/에 남긴다.

    python3 scripts/exp.py doctor                 # 환경 점검 (모두 같은 환경인지 확인)
    python3 scripts/exp.py libs                   # 라이브러리 목록, 진행 상황, 담당
    python3 scripts/exp.py claim expat            # 이 라이브러리를 맡는다고 표시하고 push
    python3 scripts/exp.py fetch expat            # 라이브러리 소스를 고정 커밋으로 받기
    python3 scripts/exp.py run expat              # 1시간 × 10회 (OSS-Fuzz vs gapfuzz 제안을 Claude가 고친 하네스)
    python3 scripts/exp.py run expat --trials 1-5 # 회차 일부만 (나머지는 나중에)
    python3 scripts/exp.py run expat --plan 24h   # 24시간 × 1회, 시간에 따른 커버리지 기록
    python3 scripts/exp.py report expat           # evaluation/results/expat/REPORT.md 만들기
    python3 scripts/exp.py submit expat           # evaluation/results/expat/만 커밋하고 push

설계
  - 한 라이브러리는 한 사람이 한 컴퓨터에서 돌린다. 같은 회차의 두 하네스를 동시에(CPU 2개) 돌려
    컴퓨터 속도 차이가 비교에 섞이지 않게 한다.
  - 큰 파일(코퍼스, 커버리지, 바이너리)은 out/에 남고 git에 올라가지 않는다(.gitignore).
    git에 올리는 것은 작은 JSON뿐이라(evaluation/results/<라이브러리>/1h/<하네스>/rNN.json,
    evaluation/results/<라이브러리>/24h/<하네스>.json), 서로 다른 라이브러리를
    맡은 사람끼리는 같은 파일을 건드리지 않아 충돌이 나지 않는다.
  - 이미 결과 파일이 있는 회차는 건너뛰므로, 중간에 끊겨도 같은 명령을 다시 실행하면 이어서 돈다.
    24시간 실험은 구간(10분, 20분, 30분, 그 뒤 1시간씩)이 끝날 때마다 커버리지를 재서 저장하므로,
    끊기면 마지막으로 끝난 구간 다음부터 같은 코퍼스로 이어서 돈다.
"""
import argparse
import concurrent.futures as cf
import importlib.util
import json
import os
import platform
import re
import socket
import subprocess
import sys
import tempfile
import time
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALUATION = ROOT / "evaluation"
RESULTS = Path(os.environ.get("GAPFUZZ_RESULTS", EVALUATION / "results"))   # 시험용으로 바꿀 수 있음
EXPECTED_CLANG_MAJOR = 18
LIBS = ["tinyxml2", "pugixml", "cjson", "jsoncpp", "zlib", "expat", "json-c"]   # OSS-Fuzz vs Claude 수정 비교 대상
BASE = os.environ.get("GAPFUZZ_BASE", "official")          # 비교 기준 하네스 (추가 실험 때만 바꿈)
FIXED = os.environ.get("GAPFUZZ_FIXED", "official_llm")   # gapfuzz 제안을 Claude API가 고치고 gapfuzz가 검증한 하네스 (scripts/make_llm_harness.py)
HARNESSES = [BASE, FIXED]
SEED_BASE = 1000                                                    # 회차 r의 시드 = 1000 + r (두 하네스 같음)

_spec = importlib.util.spec_from_file_location("tgt", ROOT / "scripts" / "tgt.py")
tg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tg)


# ------------------------------------------------------------------ 환경
def sh(cmd, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, **kw)
    except FileNotFoundError:                      # 도구가 설치되지 않음: 오류로 죽지 않고 '없음'으로 보고한다
        return subprocess.CompletedProcess(cmd, 127, "", f"{cmd[0]}: 설치되어 있지 않음")


def env_info() -> dict:
    def first(cmd):
        try:
            return sh(cmd).stdout.strip().splitlines()[0]
        except Exception:
            return ""
    cpu = ""
    try:
        cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "")
    except OSError:
        pass
    os_name = ""
    try:
        os_name = next((l.split("=", 1)[1].strip().strip('"') for l in open("/etc/os-release") if l.startswith("PRETTY_NAME=")), "")
    except OSError:
        pass
    return {
        "clang": first(["clang", "--version"]),
        "llvm_cov": first(["llvm-cov", "--version"]) if sh(["llvm-cov", "--version"]).returncode == 0 else "",
        "python": platform.python_version(),
        "os": os_name,
        "docker": Path("/.dockerenv").exists(),
        "cpu": cpu,
        "cores": os.cpu_count(),
        "tool_commit": first(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"]),
    }


def doctor(_a) -> int:
    e = env_info()
    ok = True
    print("[doctor] 환경")
    for k, v in e.items():
        print(f"  {k:12} {v}")
    m = re.search(r"clang version (\d+)\.", e["clang"])
    if not m or int(m.group(1)) != EXPECTED_CLANG_MAJOR:
        ok = False
        print(f"  ✗ clang {EXPECTED_CLANG_MAJOR}.x가 필요합니다 (팀 전원이 같은 버전이어야 커버리지 숫자를 비교할 수 있음)")
    for tool in ("llvm-cov", "llvm-profdata", "git"):
        if sh(["which", tool]).returncode != 0:
            ok = False
            print(f"  ✗ {tool} 없음")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "p.cpp"
        p.write_text('extern "C" int LLVMFuzzerTestOneInput(const char*,unsigned long){return 0;}\n')
        r = sh(["clang++", "-fsanitize=fuzzer,address,undefined", str(p), "-o", str(Path(d) / "p")])
        if r.returncode != 0:
            ok = False
            print("  ✗ libFuzzer/ASan으로 빌드 실패: libclang-rt-18-dev 설치 필요\n" + r.stderr[-400:])
        r = sh(["clang++", "-fsanitize=fuzzer", "-fprofile-instr-generate", "-fcoverage-mapping", str(p), "-o", str(Path(d) / "q")])
        if r.returncode != 0:
            ok = False
            print("  ✗ 커버리지 빌드 실패\n" + r.stderr[-400:])
    if (e["cores"] or 1) < 2:
        print("  ! CPU가 1개라 --jobs 1로 돌려야 하고 시간이 두 배 걸립니다")
    try:
        import scipy  # noqa: F401
    except ImportError:
        print("  · scipy 없음: 괜찮습니다 (통계는 내장 정확검정으로 계산)")
    print("[doctor] " + ("통과" if ok else "문제가 있습니다. README의 '팀 실험' 설치 절차를 확인하세요"))
    return 0 if ok else 1


# ------------------------------------------------------------------ 라이브러리
def target(lib: str) -> dict:
    p = ROOT / "targets" / f"{lib}.json"
    if not p.exists():
        raise SystemExit(f"모르는 라이브러리: {lib} (가능: {', '.join(LIBS)})")
    return tg.load(lib)


def fetch(a) -> int:
    for lib in a.libs:
        t = target(lib)
        d = ROOT / t["clone_dir"]
        if not d.exists():
            print(f"[fetch] {lib}: {t['repo']} 받는 중")
            r = sh(["git", "clone", "-q", t["repo"], str(d)])
            if r.returncode:
                raise SystemExit(r.stderr)
        head = sh(["git", "-C", str(d), "rev-parse", "HEAD"]).stdout.strip()
        if head != t["commit"]:
            sh(["git", "-C", str(d), "fetch", "-q", "origin", t["commit"]])
            r = sh(["git", "-C", str(d), "checkout", "-q", t["commit"]])
            if r.returncode:
                raise SystemExit(f"[fetch] {lib}: 커밋 {t['commit'][:10]}로 바꾸지 못함\n{r.stderr}")
        print(f"[fetch] {lib} @ {t['commit'][:10]} → {t['clone_dir']}")
    return 0


def plan_dir(secs: int) -> str:
    return f"{secs // 3600}h" if secs % 3600 == 0 else f"{secs}s"


def done_trials(lib: str, h: str, secs: int = 3600) -> list[int]:
    d = RESULTS / lib / plan_dir(secs) / h
    return sorted(int(p.stem[1:]) for p in d.glob("r*.json")) if d.exists() else []


def day_state(lib: str, h: str) -> dict:
    p = RESULTS / lib / "24h" / f"{h}.json"
    return json.load(open(p)) if p.exists() else {}


def all_libs() -> list[str]:
    """비교 대상 7개 + 하네스 전체 기준 실험만 하는 라이브러리(설정에 "ossfuzz" 목록이 있는 것)."""
    extra = []
    for p in sorted((ROOT / "targets").glob("*.json")):
        if p.stem.startswith("_") or p.stem in LIBS:
            continue
        try:
            if "ossfuzz" in json.load(open(p)):
                extra.append(p.stem)
        except ValueError:
            pass
    return LIBS + extra


def libs(_a) -> int:
    print(f"{'라이브러리':12} {'커밋':10}  {'하네스':>6}  {'1시간 × 10회':>14}  {'하네스 전체':>11}  {'24시간':>10}  소스       담당")
    for lib in all_libs():
        t = target(lib)
        have = (ROOT / t["clone_dir"]).exists()
        one = min(len(done_trials(lib, h)) for h in HARNESSES)
        day = min((day_state(lib, h).get("done_secs", 0) for h in HARNESSES)) / 3600
        ud = union_dir(lib, 3600) / "fixed"
        nu = len(list(ud.glob("r*.json"))) if ud.exists() else 0
        print(f"{lib:12} {t['commit'][:10]}  {len(tg.ossfuzz_harnesses(t)):>6}  {one:>11}/10  {nu:>8}/10  {day:>7.1f}/24  "
              f"{'받음' if have else 'fetch 필요':10} {owner_of(lib) or '-'}")
    return 0


# ------------------------------------------------------------------ 한 회차
def coverage_map(cov_json: Path) -> tuple[dict, dict]:
    data = json.load(open(cov_json))["data"][0]
    br = {}
    for f in data["files"]:
        for b in f["branches"]:
            k = (b[0], b[1])
            t, fl = br.get(k, (0, 0))
            br[k] = (t + b[4], fl + b[5])
    tot = data["totals"]
    cov = {k: {"pct": round(tot[k]["percent"], 3), "covered": tot[k]["covered"], "count": tot[k]["count"]}
           for k in ("lines", "branches", "functions", "regions")}
    return cov, br


def summarize_run(lib: str, h: str, r: int, secs: int, started: float, env: dict) -> dict:
    d = ROOT / "out" / "targets" / lib / h / f"long{secs}" / f"r{r}"
    cov, br = coverage_map(d / "coverage.json")
    log = (d / "fuzz.log").read_text(errors="replace")
    execs = re.findall(r"stat::number_of_executed_units:\s*(\d+)", log)
    crashes = sorted(p.name for p in d.iterdir() if p.name.split("-")[0] in ("crash", "leak", "timeout", "oom"))
    tg_path = EVALUATION / "experiments" / "targets" / f"{lib}.json"
    targets = []
    if tg_path.exists():
        for b in json.load(open(tg_path))["branches"]:
            side = 0 if b["never"] == "참" else 1
            seen = br.get((b["line"], b["col"]))
            targets.append({"fix": b["fix"], "applied": b["applied"], "line": b["line"],
                            "opened": bool(seen and seen[side] > 0)})
    triage = []
    if crashes:
        out_md = d / "triage.md"
        sh([sys.executable, "-m", "gapfuzz", "triage", "--binary", str(d.parent.parent / "fuzz"),
            "--harness", str(tg.harness_path(target(lib), h)), "--lib-dir", str(ROOT / target(lib)["lib_dir"]),
            "--name", f"{lib}-{h}-r{r}", "--root", str(ROOT), "--out", str(out_md), *[str(d / c) for c in crashes]], cwd=ROOT)
        tj = out_md.with_suffix(".json")
        if tj.exists():
            try:
                triage = [{"verdict": (c.get("verdict") or {}).get("cls"), "confidence": (c.get("verdict") or {}).get("confidence"),
                           "reason": (c.get("verdict") or {}).get("reason", "")[:200], "kind": c.get("kind"), "files": c.get("files", [])}
                          for c in json.load(open(tj)).get("crashes", [])]
            except Exception:
                triage = []
    return {
        "lib": lib, "harness": h, "trial": r, "secs": secs, "seed": SEED_BASE + r,
        "coverage": cov, "execs": int(execs[-1]) if execs else None,
        "corpus": len(os.listdir(d / "corpus")), "crashes": crashes, "triage": triage,
        "targets": targets,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(started)),
        "wall_secs": int(time.time() - started),
        "by": who_am_i(),
        "env": env,
    }


def who_am_i() -> str:
    return (os.environ.get("GAPFUZZ_BY") or sh(["git", "-C", str(ROOT), "config", "user.name"]).stdout.strip()
            or socket.gethostname())


def owner_of(lib: str) -> str:
    p = RESULTS / lib / "OWNER.txt"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def claim(a) -> int:
    lib = a.lib
    target(lib)
    me = who_am_i()
    g = lambda *c: sh(["git", "-C", str(ROOT), *c])
    if not a.no_push:
        g("pull", "--rebase", "--autostash")          # 다른 사람이 먼저 맡았는지 최신 상태로 확인
    cur = owner_of(lib)
    if cur and cur != me:
        raise SystemExit(f"[claim] {lib}는 이미 {cur} 님이 맡았습니다. 다른 라이브러리를 고르세요 (python3 scripts/exp.py libs)")
    p = RESULTS / lib / "OWNER.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(me + "\n", encoding="utf-8")
    print(f"[claim] {lib} 담당: {me}")
    if a.no_push:
        return 0
    rel = str(p.relative_to(ROOT))
    g("add", rel)
    if g("commit", "-m", f"claim({lib}): {me}").returncode != 0:
        return 0
    r = g("pull", "--rebase", "--autostash")
    if r.returncode:
        # 같은 순간에 다른 사람이 먼저 올림: 내 claim 커밋을 되돌리고 상대 것을 받는다
        g("rebase", "--abort")
        g("reset", "-q", "HEAD~1")
        p.unlink(missing_ok=True)
        g("pull", "--rebase", "--autostash")
        raise SystemExit(f"[claim] 방금 {owner_of(lib) or '다른 사람'} 님이 {lib}를 먼저 맡았습니다. 다른 라이브러리를 고르세요")
    r = g("push")
    print("[claim] push 완료" if r.returncode == 0 else "[claim] push 실패:\n" + r.stderr)
    return 0


def run_trial(lib: str, h: str, r: int, secs: int, env: dict) -> str:
    started = time.time()
    t = target(lib)
    tg.run_one(t, h, r, secs, SEED_BASE, 0, None, sub=f"long{secs}")
    res = summarize_run(lib, h, r, secs, started, env)
    out = RESULTS / lib / plan_dir(secs) / h / f"r{r:02d}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    opened = sum(x["opened"] for x in res["targets"] if x["applied"])
    total = sum(1 for x in res["targets"] if x["applied"])
    return (f"[run] {time.strftime('%m-%d %H:%M')} {lib}/{h} r{r:02d}: 분기 {res['coverage']['branches']['pct']:.2f}% "
            f"라인 {res['coverage']['lines']['pct']:.2f}% 겨냥 분기 {opened}/{total} 크래시 {len(res['crashes'])}")


def parse_range(s: str) -> list[int]:
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


# ------------------------------------------------------------------ 24시간 실험
DAY_SCHEDULE_MIN = [10, 20, 30] + [60] * 23          # 구간 길이(분). 합계 24시간. 앞쪽은 곡선을 촘촘히 보려고 짧게
DAY_SEED_BASE = 5000


def measure_corpus(lib: str, h: str, d: Path) -> dict:
    """코퍼스 전체를 커버리지 바이너리로 다시 실행해 라이브러리 소스의 커버리지와 겨냥 분기를 잰다."""
    t = target(lib)
    b = ROOT / "out" / "targets" / lib / h
    for f in d.glob("cov-*.profraw"):
        f.unlink()
    env = dict(os.environ, LLVM_PROFILE_FILE=str(d / "cov-%p.profraw"))
    subprocess.run([str(b / "cov"), "-runs=0", str(d / "corpus")], env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    raws = [str(p) for p in d.glob("cov-*.profraw")]
    subprocess.run(["llvm-profdata", "merge", "-sparse", *raws, "-o", str(d / "cov.profdata")], check=True)
    files = [str(x) for x in t["srcs"]] + [str(x) for x in t["headers"]]
    with open(d / "coverage.json", "w") as f:
        subprocess.run(["llvm-cov", "export", "-format=text", f"-instr-profile={d / 'cov.profdata'}", str(b / "cov"), *files],
                       stdout=f, check=True)
    cov, br = coverage_map(d / "coverage.json")
    targets = []
    tp = EVALUATION / "experiments" / "targets" / f"{lib}.json"
    if tp.exists():
        for x in json.load(open(tp))["branches"]:
            seen = br.get((x["line"], x["col"]))
            side = 0 if x["never"] == "참" else 1
            targets.append({"fix": x["fix"], "applied": x["applied"], "line": x["line"], "opened": bool(seen and seen[side] > 0)})
    crashes = sorted(p.name for p in d.iterdir() if p.name.split("-")[0] in ("crash", "leak", "timeout", "oom"))
    return {"coverage": cov, "targets": targets, "corpus": len(os.listdir(d / "corpus")), "crashes": crashes}


def day_one(lib: str, h: str, schedule: list[int], env: dict) -> str:
    t = target(lib)
    b = ROOT / "out" / "targets" / lib / h
    d = b / "day"
    out = RESULTS / lib / "24h" / f"{h}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    st = day_state(lib, h) or {"lib": lib, "harness": h, "schedule_min": schedule, "done_secs": 0, "chunks": 0,
                               "points": [], "by": who_am_i(), "env": env}
    if st["chunks"] and st["chunks"] < len(schedule) and not (d / "corpus").exists():
        raise RuntimeError(f"{lib}/{h}: 이어서 돌릴 코퍼스(out/targets/{lib}/{h}/day/corpus)가 없습니다. "
                           "처음 돌리던 컴퓨터에서 이어 주세요")
    if not st["chunks"]:
        subprocess.run(["rm", "-rf", str(d)], check=True)          # 결과가 없으면 이전 찌꺼기 없이 새로 시작
    (d / "corpus").mkdir(parents=True, exist_ok=True)
    dct = str(ROOT / t["dict"]) if t.get("dict") else None
    while st["chunks"] < len(schedule):
        k = st["chunks"]
        secs = schedule[k] * 60
        t0, runs = time.time(), 0
        with open(d / "fuzz.log", "a") as log:
            left = secs
            while left > 30 and runs < 50:                         # 크래시가 끝없이 반복되면 구간을 넘김
                runs += 1
                log.write(f"\n=== {time.strftime('%m-%d %H:%M')} 구간 {k + 1} 시작 (남은 {left}초) ===\n")
                log.flush()
                args = [str(b / "fuzz"), f"-max_total_time={left}", f"-seed={DAY_SEED_BASE + k * 100 + runs}",
                        "-rss_limit_mb=2048", "-timeout=10", f"-artifact_prefix={d}/", str(d / "corpus")]
                if dct:
                    args.insert(-1, f"-dict={dct}")
                subprocess.run(args, stdout=log, stderr=subprocess.STDOUT)   # 크래시로 멈추면 남은 시간만큼 다시
                left = secs - int(time.time() - t0)
            if runs >= 50:
                log.write("\n=== 크래시가 50번 반복되어 이 구간을 멈춥니다 ===\n")
        st["done_secs"] += secs
        st["chunks"] += 1
        m = measure_corpus(lib, h, d)
        m.update({"hours": round(st["done_secs"] / 3600, 3), "restarts": runs - 1,
                  "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
        st["points"].append(m)
        out.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        opened = sum(x["opened"] for x in m["targets"] if x["applied"])
        total = sum(1 for x in m["targets"] if x["applied"])
        print(f"[24h] {time.strftime('%m-%d %H:%M')} {lib}/{h} {m['hours']:.2f}시간: 분기 {m['coverage']['branches']['pct']:.2f}% "
              f"겨냥 분기 {opened}/{total} 크래시 {len(m['crashes'])}", flush=True)
    last = st["points"][-1] if st["points"] else {}
    if last.get("crashes") and not st.get("triage"):
        out_md = d / "triage.md"
        sh([sys.executable, "-m", "gapfuzz", "triage", "--binary", str(b / "fuzz"), "--harness", str(tg.harness_path(t, h)),
            "--lib-dir", str(ROOT / t["lib_dir"]), "--name", f"{lib}-{h}-24h", "--root", str(ROOT), "--out", str(out_md),
            *[str(d / c) for c in last["crashes"]]], cwd=ROOT)
        tj = out_md.with_suffix(".json")
        if tj.exists():
            st["triage"] = [{"verdict": (c.get("verdict") or {}).get("cls"), "confidence": (c.get("verdict") or {}).get("confidence"),
                             "reason": (c.get("verdict") or {}).get("reason", "")[:200], "files": c.get("files", [])}
                            for c in json.load(open(tj)).get("crashes", [])]
            out.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return f"[24h] {lib}/{h} 끝 ({st['done_secs'] / 3600:.1f}시간)"


def run_day(a, t: dict, env: dict) -> int:
    schedule = [int(x) for x in a.schedule.split(",")] if a.schedule else DAY_SCHEDULE_MIN
    left = {h: sum(schedule) * 60 - day_state(a.lib, h).get("done_secs", 0) for h in HARNESSES}
    if all(v <= 0 for v in left.values()):
        print(f"[24h] {a.lib}: 이미 끝났습니다 → python3 scripts/exp.py report {a.lib}")
        return 0
    print(f"[24h] {a.lib}: OSS-Fuzz와 Claude 수정본을 동시에 {sum(schedule) / 60:.1f}시간 (남은 시간 약 {max(left.values()) / 3600:.1f}시간). "
          "구간이 끝날 때마다 커버리지를 재서 evaluation/results/에 저장합니다.")
    for h in HARNESSES:
        tg.build(t, h)
    with cf.ThreadPoolExecutor(max_workers=len(HARNESSES)) as ex:
        for f in cf.as_completed([ex.submit(day_one, a.lib, h, schedule, env) for h in HARNESSES]):
            try:
                print(f.result(), flush=True)
            except Exception as e:
                print(f"[24h] 실패: {e!r}", flush=True)
    report_lib(a.lib)
    print(f"[24h] 결과 올리기: python3 scripts/exp.py submit {a.lib}")
    return 0


def run(a) -> int:
    t = target(a.lib)
    if not (ROOT / t["clone_dir"]).exists():
        raise SystemExit(f"먼저 소스를 받으세요: python3 scripts/exp.py fetch {a.lib}")
    if a.plan != "union" and a.lib not in LIBS:
        raise SystemExit(f"{a.lib}는 비교할 수정 하네스가 없습니다 (가능: {', '.join(LIBS)})")
    cur = owner_of(a.lib)
    if cur and cur != who_am_i() and not a.force:
        raise SystemExit(f"[run] {a.lib}는 {cur} 님 담당입니다. 정말 돌리려면 --force")
    env = env_info()
    m = re.search(r"clang version (\d+)\.", env["clang"])
    if not m or int(m.group(1)) != EXPECTED_CLANG_MAJOR:
        raise SystemExit(f"clang {EXPECTED_CLANG_MAJOR}.x가 아닙니다: {env['clang']}  (python3 scripts/exp.py doctor)")
    if env["tool_commit"] and sh(["git", "-C", str(ROOT), "status", "--porcelain", "--", "gapfuzz", "scripts", "harnesses", "targets"]).stdout.strip():
        print("[run] 주의: 도구·하네스 코드에 커밋하지 않은 변경이 있습니다. 결과가 팀원과 달라질 수 있습니다.")
    if a.plan == "union":
        return run_union(a, t, env)
    if not any((ROOT / "harnesses" / a.lib / f"{FIXED}{x}").exists() for x in (".c", ".cc", ".cpp")):
        raise SystemExit(f"[run] harnesses/{a.lib}/{FIXED}.* 가 없습니다. git pull로 받으세요 (만드는 법: scripts/make_llm_harness.py)")
    if a.plan == "24h":
        return run_day(a, t, env)
    trials = parse_range(a.trials)
    todo = [(h, r) for r in trials for h in HARNESSES if not (RESULTS / a.lib / plan_dir(a.secs) / h / f"r{r:02d}.json").exists()]
    if not todo:
        print(f"[run] {a.lib}: 요청한 회차가 모두 끝났습니다 → python3 scripts/exp.py report {a.lib}")
        return 0
    hours = len(todo) * a.secs / 3600 / max(a.jobs, 1)
    print(f"[run] {a.lib}: {len(todo)}개 실행 (회차 {a.trials}, 회당 {a.secs}초, 동시에 {a.jobs}개) → 약 {hours:.1f}시간")
    for h in HARNESSES:
        tg.build(t, h)
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(run_trial, a.lib, h, r, a.secs, env) for h, r in todo]
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # 한 회차가 실패해도 나머지는 계속
                print(f"[run] 실패: {e!r}", flush=True)
    report_lib(a.lib)
    print(f"[run] 끝. 결과 올리기: python3 scripts/exp.py submit {a.lib}")
    return 0


# ------------------------------------------------------------------ 하네스 전체 기준 실험 (--plan union)
def _has_harness(t: dict, h: str) -> bool:
    try:
        tg.harness_path(t, h)
        return True
    except SystemExit:
        return False


def union_sets(t: dict) -> tuple[list[str], list[str]]:
    """(기준 묶음, 적용 후 묶음).
    기준: 설정의 "ossfuzz" 목록(OSS-Fuzz 하네스 전부).
    적용 후: 각 하네스의 고친 버전이 있으면 그것(official → official_llm, 그 밖은 <이름>_llm), 없으면 원래 하네스 그대로,
             그리고 gapfuzz_ops(어느 하네스도 안 부르는 API를 부르는 새 하네스)가 있으면 추가.
    고치지 않은 하네스는 두 묶음이 같은 실행 기록을 같이 쓴다(다시 돌리지 않음)."""
    base = tg.ossfuzz_harnesses(t)
    fixed = []
    for h in base:
        cand = FIXED if h == BASE else f"{h}_llm"
        fixed.append(cand if _has_harness(t, cand) else h)
    if _has_harness(t, "gapfuzz_ops"):
        fixed.append("gapfuzz_ops")
    return base, fixed


def union_dir(lib: str, secs: int) -> Path:
    return RESULTS / lib / f"union_{plan_dir(secs)}"


def union_one(lib: str, t: dict, side: str, hs: list[str], r: int, secs: int, env: dict) -> dict:
    """한 회차의 한 묶음: 하네스들의 실행 기록을 합쳐 커버리지와 '어느 하네스도 안 부르는 API' 수를 잰다."""
    d = tg.union(t, hs, secs=secs, r=r, name=f"_union_{side}", sub=f"long{secs}")
    cov, _ = coverage_map(d / "coverage.json")
    res_apis = json.load(open(d / "gap" / "gap.json"))["results"]
    res = {"lib": lib, "side": side, "trial": r, "secs_per_harness": secs, "harnesses": hs,
           "total_cpu_hours": round(len(hs) * secs / 3600, 2), "coverage": cov, "apis": len(res_apis),
           "not_called": sum(1 for x in res_apis if x["category"] == "NOT_CALLED"),
           "fixes": len(json.load(open(d / "gap" / "gap.json"))["harness_fixes"]),
           "by": who_am_i(), "clang": env["clang"], "cpu": env["cpu"], "tool_commit": env["tool_commit"],
           "finished": time.strftime("%Y-%m-%d %H:%M")}
    out = union_dir(lib, secs) / side / f"r{r:02d}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return res


def run_union(a, t: dict, env: dict) -> int:
    base, fixed = union_sets(t)
    if len(base) == 1 and fixed == base:
        print(f"[run] {a.lib}: OSS-Fuzz 하네스가 하나뿐이고 고친 하네스도 없습니다. 기준만 잽니다.")
    allh = list(dict.fromkeys(base + fixed))
    trials = parse_range(a.trials)
    raw = lambda h, r: ROOT / "out" / "targets" / a.lib / h / f"long{a.secs}" / f"r{r}" / "cov.profdata"
    todo = [(h, r) for r in trials for h in allh if not raw(h, r).exists()]
    hours = len(todo) * a.secs / 3600 / max(a.jobs, 1)
    print(f"[run] {a.lib} (하네스 전체 기준): 기준 {len(base)}개 {base}")
    print(f"[run]   적용 후 {len(fixed)}개 {fixed}")
    print(f"[run]   새로 돌릴 것 {len(todo)}개 (하네스 {len(allh)}개 × 회차 {a.trials} 중 원본이 없는 것, 회당 {a.secs}초, 동시에 {a.jobs}개) → 약 {hours:.1f}시간")
    for h in allh:
        tg.build(t, h)
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(run_trial, a.lib, h, r, a.secs, env) for h, r in todo]
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:
                print(f"[run] 실패: {e!r}", flush=True)
    for r in trials:
        for side, hs in (("base", base), ("fixed", fixed)):
            if side == "fixed" and fixed == base:
                continue
            if not all(raw(h, r).exists() for h in hs):
                print(f"[run] r{r:02d} {side}: 아직 끝나지 않은 하네스가 있어 합치지 않습니다")
                continue
            x = union_one(a.lib, t, side, hs, r, a.secs, env)
            print(f"[run] r{r:02d} {'기준' if side == 'base' else '적용 후'} 합침: 분기 {x['coverage']['branches']['pct']:.2f}% "
                  f"라인 {x['coverage']['lines']['pct']:.2f}% 어느 하네스도 안 부르는 API {x['not_called']}/{x['apis']}", flush=True)
    union_report(a.lib, a.secs)
    print(f"[run] 끝. 결과: evaluation/results/{a.lib}/UNION.md  올리기: python3 scripts/exp.py submit {a.lib}")
    return 0


def union_report(lib: str, secs: int = 3600) -> None:
    d = union_dir(lib, secs)
    A = [json.load(open(p)) for p in sorted((d / "base").glob("r*.json"))] if (d / "base").exists() else []
    B = [json.load(open(p)) for p in sorted((d / "fixed").glob("r*.json"))] if (d / "fixed").exists() else []
    if not A:
        return
    br = lambda runs: [r["coverage"]["branches"]["pct"] for r in runs]
    ln = lambda runs: [r["coverage"]["lines"]["pct"] for r in runs]
    nc = lambda runs: sorted(r["not_called"] for r in runs)
    L = [f"# 하네스 전체 기준 실험 — {lib}", "",
         "라이브러리의 OSS-Fuzz 하네스를 모두 따로 돌린 뒤 커버리지를 합쳐서 비교합니다.",
         f"하네스마다 {secs}초씩, 같은 회차는 같은 시드. 값은 중앙값 [최솟값–최댓값].", "",
         f"- 기준: OSS-Fuzz 하네스 {len(A[0]['harnesses'])}개 ({', '.join(A[0]['harnesses'])}), 회차당 CPU {A[0]['total_cpu_hours']}시간"]
    if B:
        L.append(f"- 적용 후: 하네스 {len(B[0]['harnesses'])}개 ({', '.join(B[0]['harnesses'])}), 회차당 CPU {B[0]['total_cpu_hours']}시간")
    L += ["", "| | 회차 | 라인 | 분기 | 어느 하네스도 안 부르는 API |", "|---|---:|---|---|---|",
          f"| 기준 (OSS-Fuzz 전체) | {len(A)} | {_fmt(ln(A))} | {_fmt(br(A))} | {nc(A)[len(A) // 2]} / {A[0]['apis']} |"]
    if B:
        L.append(f"| 적용 후 (gapfuzz) | {len(B)} | {_fmt(ln(B))} | {_fmt(br(B))} | {nc(B)[len(B) // 2]} / {B[0]['apis']} |")
        L += ["", f"분기 커버리지: A12 = {a12(br(A), br(B)):.2f}, p = {mwu_p(br(A), br(B)):.2g} (Mann-Whitney U, 양측)"]
        if len(B[0]["harnesses"]) != len(A[0]["harnesses"]):
            L += ["", f"주의: 적용 후 쪽은 하네스가 {len(B[0]['harnesses']) - len(A[0]['harnesses'])}개 더 많아 회차당 총 퍼징 시간도 그만큼 깁니다."]
    (RESULTS / lib / "UNION.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ 통계
def a12(x: list[float], y: list[float]) -> float:
    """y가 x보다 클 확률 (Vargha-Delaney A12)."""
    if not x or not y:
        return float("nan")
    gt = sum(1 for xi in x for yi in y if yi > xi)
    eq = sum(1 for xi in x for yi in y if yi == xi)
    return (gt + 0.5 * eq) / (len(x) * len(y))


def mwu_p(x: list[float], y: list[float]) -> float:
    """Mann-Whitney U 양측 정확검정 (동점이 있으면 순열로 근사 없이 전부 셈, 표본 10개씩까지 빠름)."""
    n, m = len(x), len(y)
    if not n or not m:
        return float("nan")
    allv = x + y
    order = sorted(allv)
    rank = {}
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and order[j + 1] == order[i]:
            j += 1
        for k in range(i, j + 1):
            rank.setdefault(order[k], (i + j) / 2 + 1)
        i = j + 1
    ranks = [rank[v] for v in allv]
    obs = sum(ranks[:n])
    mean = n * (n + m + 1) / 2
    # 순위 합 분포를 동적 계획법으로: (뽑은 개수, 순위합*2) -> 경우의 수
    dist = {(0, 0): 1}
    for rk in ranks:
        r2 = int(round(rk * 2))
        nd = dict(dist)
        for (c, s), w in dist.items():
            if c < n:
                nd[(c + 1, s + r2)] = nd.get((c + 1, s + r2), 0) + w
        dist = nd
    total = comb(n + m, n)
    dev = abs(obs - mean)
    extreme = sum(w for (c, s), w in dist.items() if c == n and abs(s / 2 - mean) >= dev - 1e-9)
    return min(1.0, extreme / total)


def _fmt(v: list[float]) -> str:
    if not v:
        return "–"
    s = sorted(v)
    med = (s[len(s) // 2] if len(s) % 2 else (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2)
    return f"{med:.2f}% [{s[0]:.2f}–{s[-1]:.2f}]"


def load(lib: str, h: str, plan: str = "1h") -> list[dict]:
    d = RESULTS / lib / plan / h
    return [json.load(open(p)) for p in sorted(d.glob("r*.json"))] if d.exists() else []


def report_lib(lib: str) -> dict:
    A, B = load(lib, BASE), load(lib, FIXED)
    # 같은 회차끼리만 비교 (짝이 맞는 회차)
    common = sorted({r["trial"] for r in A} & {r["trial"] for r in B})
    A = [r for r in A if r["trial"] in common]
    B = [r for r in B if r["trial"] in common]
    L = [f"# {lib}: OSS-Fuzz 하네스 vs gapfuzz 제안을 Claude가 고친 하네스", ""]
    day = day_section(lib)
    if not common:
        L += ["## 1시간 × 10회", "", "아직 두 하네스가 모두 끝난 회차가 없습니다.", "", *day]
        (RESULTS / lib / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        return {}
    L += ["## 1시간 × 10회", ""]
    secs = sorted({r["secs"] for r in A + B})
    clangs = sorted({r["env"]["clang"] for r in A + B})
    cpus = sorted({r["env"]["cpu"] for r in A + B})
    L += [f"회차 {len(common)}개 ({', '.join(map(str, common))}), 회당 {', '.join(str(s) for s in secs)}초, 같은 회차는 같은 시드. "
          "커버리지는 라이브러리 소스만 집계.", "",
          "| 지표 | OSS-Fuzz | Claude 수정 | A12 | p (Mann-Whitney U, 양측 정확) |", "|---|---|---|---:|---:|"]
    stats = {}
    for key, ko in (("branches", "분기"), ("lines", "라인"), ("functions", "함수"), ("regions", "영역")):
        xa = [r["coverage"][key]["pct"] for r in A]
        xb = [r["coverage"][key]["pct"] for r in B]
        e, p = a12(xa, xb), mwu_p(xa, xb)
        stats[key] = {BASE: xa, FIXED: xb, "a12": e, "p": p}
        L.append(f"| {ko} | {_fmt(xa)} | {_fmt(xb)} | {e:.2f} | {p:.4g} |")
    L += ["", "값은 중앙값 [최솟값–최댓값]. A12는 무작위로 하나씩 뽑았을 때 수정본이 더 높을 확률(0.5면 차이 없음).", ""]

    tgt = [x for x in B[0]["targets"]] if B and B[0]["targets"] else []
    if tgt:
        L += ["## 제안이 겨냥한 분기", "", "회차마다 따로 셌습니다. 대조군은 일부러 적용하지 않은 제안의 분기입니다.", "",
              "| 하네스 | 겨냥한 분기(적용) 열린 수, 회차별 | 대조군 열린 수, 회차별 |", "|---|---|---|"]
        for name, runs in (("OSS-Fuzz", A), ("Claude 수정", B)):
            app = [sum(x["opened"] for x in r["targets"] if x["applied"]) for r in runs]
            ctl = [sum(x["opened"] for x in r["targets"] if not x["applied"]) for r in runs]
            n_app = sum(1 for x in runs[0]["targets"] if x["applied"])
            n_ctl = sum(1 for x in runs[0]["targets"] if not x["applied"])
            L.append(f"| {name} | {', '.join(f'{v}/{n_app}' for v in app)} | {', '.join(f'{v}/{n_ctl}' for v in ctl) if n_ctl else '–'} |")
        L.append("")
    L += ["## 크래시", "", "| 하네스 | 크래시가 난 회차 | 판정 |", "|---|---:|---|"]
    for name, runs in (("OSS-Fuzz", A), ("Claude 수정", B)):
        n = sum(1 for r in runs if r["crashes"])
        verdicts = sorted({f"{t['verdict']}({t['confidence']})" for r in runs for t in r["triage"]})
        L.append(f"| {name} | {n}/{len(runs)} | {', '.join(verdicts) or '–'} |")
    L += ["", "## 실행 환경", "",
          f"- clang: {'; '.join(clangs)}" + (" **(서로 다름: 비교에 주의)**" if len(clangs) > 1 else ""),
          f"- CPU: {'; '.join(cpus)}" + (" **(서로 다름)**" if len(cpus) > 1 else ""),
          f"- 실행한 사람: {', '.join(sorted({r['by'] for r in A + B}))}",
          f"- 실행 수 중앙값: OSS-Fuzz {sorted(r['execs'] or 0 for r in A)[len(A) // 2]:,}, 수정 {sorted(r['execs'] or 0 for r in B)[len(B) // 2]:,}", ""]
    L += day
    (RESULTS / lib / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return stats


def day_section(lib: str) -> list[str]:
    A, B = day_state(lib, BASE), day_state(lib, FIXED)
    if not A.get("points") and not B.get("points"):
        return []
    L = ["## 24시간 × 1회", "", "같은 코퍼스로 구간을 이어 붙여 24시간 돌리고, 구간이 끝날 때마다 코퍼스 전체로 커버리지를 쟀습니다. "
         "하네스마다 1회라 통계 검정은 없습니다(통계는 1시간 × 10회).", "",
         "| 경과 | OSS-Fuzz 분기 | 수정 분기 | OSS-Fuzz 라인 | 수정 라인 | 겨냥 분기(수정) |", "|---:|---:|---:|---:|---:|---:|"]
    pa, pb = A.get("points", []), B.get("points", [])
    for i in range(max(len(pa), len(pb))):
        x = pa[i] if i < len(pa) else None
        y = pb[i] if i < len(pb) else None
        hrs = (x or y)["hours"]
        cell = lambda p, k: f"{p['coverage'][k]['pct']:.2f}%" if p else ""
        tg_cell = (f"{sum(t['opened'] for t in y['targets'] if t['applied'])}/{sum(1 for t in y['targets'] if t['applied'])}"
                   if y and y["targets"] else "")
        L.append(f"| {f'{round(hrs * 60)}분' if hrs < 1 else f'{hrs:g}시간'} | {cell(x, 'branches')} | {cell(y, 'branches')} | {cell(x, 'lines')} | {cell(y, 'lines')} | {tg_cell} |")
    for name, s in (("OSS-Fuzz", A), ("수정", B)):
        if s.get("points"):
            last = s["points"][-1]
            tri = ", ".join(f"{t['verdict']}({t['confidence']})" for t in s.get("triage", [])) or "–"
            L.append(f"\n- {name}: 크래시 {len(last['crashes'])}개 (판정 {tri}), 코퍼스 {last['corpus']:,}개, 실행: {s.get('by', '')}")
    L.append("")
    return L


def report(a) -> int:
    targets = LIBS if a.all else [a.lib]
    rows = []
    for lib in targets:
        if not (load(lib, BASE) or load(lib, FIXED) or day_state(lib, BASE) or day_state(lib, FIXED)):
            continue
        st = report_lib(lib)
        print(f"[report] evaluation/results/{lib}/REPORT.md")
        if st:
            b = st["branches"]
            rows.append(f"| {lib} | {len(b[BASE])} | {_fmt(b[BASE])} | {_fmt(b[FIXED])} | {b['a12']:.2f} | {b['p']:.4g} |")
    if a.all:
        L = ["# 팀 실험 요약 (분기 커버리지)", "", "## 1시간 × 10회", "", "| 라이브러리 | 회차 | OSS-Fuzz | Claude 수정 | A12 | p |",
             "|---|---:|---|---|---:|---:|", *rows, "", "## 24시간 × 1회 (마지막 측정)", "",
             "| 라이브러리 | 경과 | OSS-Fuzz | Claude 수정 |", "|---|---:|---:|---:|"]
        for lib in LIBS:
            A, B = day_state(lib, BASE), day_state(lib, FIXED)
            if A.get("points") and B.get("points"):
                L.append(f"| {lib} | {min(A['done_secs'], B['done_secs']) / 3600:.1f}시간 | "
                         f"{A['points'][-1]['coverage']['branches']['pct']:.2f}% | {B['points'][-1]['coverage']['branches']['pct']:.2f}% |")
        (RESULTS / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("[report] evaluation/results/SUMMARY.md")
    return 0


# ------------------------------------------------------------------ 올리기
def submit(a) -> int:
    lib = a.lib
    union_report(lib)
    if not all(load(lib, h) for h in HARNESSES):          # 하네스 전체 기준 실험만 한 라이브러리 (예: libyaml)
        print(f"[submit] {lib}: {BASE}/{FIXED} 비교 결과가 없어 REPORT.md는 만들지 않습니다")
    else:
        report_lib(lib)
    path = f"evaluation/results/{lib}"
    g = lambda *c: sh(["git", "-C", str(ROOT), *c])
    if g("rev-parse", "--is-inside-work-tree").returncode:
        raise SystemExit("git 저장소가 아닙니다")
    staged_other = [f for f in g("diff", "--cached", "--name-only").stdout.split() if not f.startswith(path + "/")]
    if staged_other:
        raise SystemExit("evaluation/results/ 밖의 파일이 이미 staged 상태입니다. 실험 결과만 따로 올리도록 먼저 정리하세요:\n  " + "\n  ".join(staged_other))
    g("add", path)
    if not g("diff", "--cached", "--name-only", "--", path).stdout.strip():
        print("[submit] 올릴 새 결과가 없습니다")
        return 0
    nu = len(list((union_dir(lib, 3600) / "base").glob("r*.json"))) if (union_dir(lib, 3600) / "base").exists() else 0
    n = min(len(done_trials(lib, h)) for h in HARNESSES)
    dh = min(day_state(lib, h).get("done_secs", 0) for h in HARNESSES) / 3600
    who = who_am_i()
    msg = f"results({lib}): 1시간 {n}/10회, 24시간 {dh:.1f}/24시간" + (f", 하네스 전체 기준 {nu}회" if nu else "") + f" ({who})"
    r = g("commit", "-m", msg)
    if r.returncode:
        raise SystemExit(r.stderr or r.stdout)
    print(f"[submit] 커밋: {msg}")
    if a.no_push:
        return 0
    r = g("pull", "--rebase", "--autostash")
    if r.returncode:
        raise SystemExit("[submit] pull --rebase 실패. 다른 사람이 같은 evaluation/results/ 폴더를 고쳤는지 확인하세요\n" + r.stderr)
    r = g("push")
    if r.returncode:
        raise SystemExit("[submit] push 실패\n" + r.stderr)
    print("[submit] push 완료")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="gapfuzz 팀 실험 실행기")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="환경 점검")
    sub.add_parser("libs", help="라이브러리 목록, 진행 상황, 담당")
    c = sub.add_parser("claim", help="라이브러리를 맡기 (evaluation/results/<lib>/OWNER.txt를 올려 다른 사람과 겹치지 않게)")
    c.add_argument("lib")
    c.add_argument("--no-push", action="store_true")
    f = sub.add_parser("fetch", help="라이브러리 소스를 고정 커밋으로 받기")
    f.add_argument("libs", nargs="+")
    r = sub.add_parser("run", help="반복 실험 실행 (끊겨도 다시 실행하면 이어서)")
    r.add_argument("lib")
    r.add_argument("--trials", default="1-10", help="회차 범위 (예: 1-10, 1-5, 3,7)")
    r.add_argument("--secs", type=int, default=3600, help="회당 퍼징 시간(초)")
    r.add_argument("--jobs", type=int, default=2, help="동시에 돌릴 개수 (CPU 수 이하)")
    r.add_argument("--force", action="store_true", help="다른 사람이 맡은 라이브러리라도 실행")
    r.add_argument("--plan", choices=["1h", "24h", "union"], default="1h",
                   help="1h: 1시간 × 10회 (기본), 24h: 24시간 × 1회, union: OSS-Fuzz 하네스 전체를 각각 돌려 합친 커버리지로 비교")
    r.add_argument("--schedule", help=argparse.SUPPRESS)          # 시험용: 24h 구간 길이(분), 예: 1,1
    p = sub.add_parser("report", help="evaluation/results/<lib>/REPORT.md 만들기")
    p.add_argument("lib", nargs="?")
    p.add_argument("--all", action="store_true", help="모든 라이브러리 + evaluation/results/SUMMARY.md")
    s = sub.add_parser("submit", help="evaluation/results/<lib>/만 커밋하고 push")
    s.add_argument("lib")
    s.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if a.cmd == "report" and not a.all and not a.lib:
        ap.error("라이브러리 이름이나 --all을 주세요")
    return {"doctor": doctor, "libs": libs, "claim": claim, "fetch": fetch, "run": run, "report": report,
            "submit": submit}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
