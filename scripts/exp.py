#!/usr/bin/env python3
"""팀 실험 실행기: 라이브러리를 골라 장시간 반복 실험을 돌리고, 작은 결과 파일만 results/에 남긴다.

    python3 scripts/exp.py doctor                 # 환경 점검 (모두 같은 환경인지 확인)
    python3 scripts/exp.py libs                   # 라이브러리 목록, 진행 상황, 담당
    python3 scripts/exp.py claim expat            # 이 라이브러리를 맡는다고 표시하고 push
    python3 scripts/exp.py fetch expat            # 라이브러리 소스를 고정 커밋으로 받기
    python3 scripts/exp.py run expat              # 1시간 × 10회 (공식 vs 공식 + gapfuzz 수정)
    python3 scripts/exp.py run expat --trials 1-5 # 회차 일부만 (나머지는 다른 사람이나 나중에)
    python3 scripts/exp.py report expat           # results/expat/REPORT.md 만들기
    python3 scripts/exp.py submit expat           # results/expat/만 커밋하고 push

설계
  - 한 라이브러리는 한 사람이 한 컴퓨터에서 돌린다. 같은 회차의 두 하네스를 동시에(CPU 2개) 돌려
    컴퓨터 속도 차이가 비교에 섞이지 않게 한다.
  - 큰 파일(코퍼스, 커버리지, 바이너리)은 out/에 남고 git에 올라가지 않는다(.gitignore).
    git에 올리는 것은 회차마다 1KB 남짓한 results/<라이브러리>/<하네스>/rNN.json뿐이라, 서로 다른 라이브러리를
    맡은 사람끼리는 같은 파일을 건드리지 않아 충돌이 나지 않는다.
  - 이미 결과 파일이 있는 회차는 건너뛰므로, 중간에 끊겨도 같은 명령을 다시 실행하면 이어서 돈다.
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
RESULTS = Path(os.environ.get("GAPFUZZ_RESULTS", ROOT / "results"))   # 시험용으로 바꿀 수 있음
EXPECTED_CLANG_MAJOR = 18
LIBS = ["pugixml", "cjson", "jsoncpp", "zlib", "expat", "json-c"]   # 공식 vs 공식 + gapfuzz 수정 비교 대상
HARNESSES = ["official", "official_v2"]
SEED_BASE = 1000                                                    # 회차 r의 시드 = 1000 + r (두 하네스 같음)

_spec = importlib.util.spec_from_file_location("tgt", ROOT / "scripts" / "tgt.py")
tg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tg)


# ------------------------------------------------------------------ 환경
def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


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


def done_trials(lib: str, h: str) -> list[int]:
    d = RESULTS / lib / h
    return sorted(int(p.stem[1:]) for p in d.glob("r*.json")) if d.exists() else []


def libs(_a) -> int:
    print(f"{'라이브러리':10} {'커밋':10}  " + "  ".join(f"{h:>12}" for h in HARNESSES) + "  소스       담당")
    for lib in LIBS:
        t = target(lib)
        have = (ROOT / t["clone_dir"]).exists()
        cols = "  ".join(f"{len(done_trials(lib, h)):>9}/10" for h in HARNESSES)
        print(f"{lib:10} {t['commit'][:10]}  {cols}  {'받음' if have else 'fetch 필요':10} {owner_of(lib) or '-'}")
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
    tg_path = ROOT / "experiments" / "targets" / f"{lib}.json"
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
    out = RESULTS / lib / h / f"r{r:02d}.json"
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


def run(a) -> int:
    t = target(a.lib)
    if not (ROOT / t["clone_dir"]).exists():
        raise SystemExit(f"먼저 소스를 받으세요: python3 scripts/exp.py fetch {a.lib}")
    if a.lib not in LIBS:
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
    trials = parse_range(a.trials)
    todo = [(h, r) for r in trials for h in HARNESSES if not (RESULTS / a.lib / h / f"r{r:02d}.json").exists()]
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


def load(lib: str, h: str) -> list[dict]:
    d = RESULTS / lib / h
    return [json.load(open(p)) for p in sorted(d.glob("r*.json"))] if d.exists() else []


def report_lib(lib: str) -> dict:
    A, B = load(lib, "official"), load(lib, "official_v2")
    # 같은 회차끼리만 비교 (짝이 맞는 회차)
    common = sorted({r["trial"] for r in A} & {r["trial"] for r in B})
    A = [r for r in A if r["trial"] in common]
    B = [r for r in B if r["trial"] in common]
    L = [f"# {lib}: 공식 하네스 vs 공식 + gapfuzz 수정", ""]
    if not common:
        L.append("아직 두 하네스가 모두 끝난 회차가 없습니다.")
        (RESULTS / lib / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        return {}
    secs = sorted({r["secs"] for r in A + B})
    clangs = sorted({r["env"]["clang"] for r in A + B})
    cpus = sorted({r["env"]["cpu"] for r in A + B})
    L += [f"회차 {len(common)}개 ({', '.join(map(str, common))}), 회당 {', '.join(str(s) for s in secs)}초, 같은 회차는 같은 시드. "
          "커버리지는 라이브러리 소스만 집계.", "",
          "| 지표 | 공식 | + gapfuzz 수정 | A12 | p (Mann-Whitney U, 양측 정확) |", "|---|---|---|---:|---:|"]
    stats = {}
    for key, ko in (("branches", "분기"), ("lines", "라인"), ("functions", "함수"), ("regions", "영역")):
        xa = [r["coverage"][key]["pct"] for r in A]
        xb = [r["coverage"][key]["pct"] for r in B]
        e, p = a12(xa, xb), mwu_p(xa, xb)
        stats[key] = {"official": xa, "official_v2": xb, "a12": e, "p": p}
        L.append(f"| {ko} | {_fmt(xa)} | {_fmt(xb)} | {e:.2f} | {p:.4g} |")
    L += ["", "값은 중앙값 [최솟값–최댓값]. A12는 무작위로 하나씩 뽑았을 때 수정본이 더 높을 확률(0.5면 차이 없음).", ""]

    tgt = [x for x in B[0]["targets"]] if B and B[0]["targets"] else []
    if tgt:
        L += ["## 제안이 겨냥한 분기", "", "회차마다 따로 셌습니다. 대조군은 일부러 적용하지 않은 제안의 분기입니다.", "",
              "| 하네스 | 겨냥한 분기(적용) 열린 수, 회차별 | 대조군 열린 수, 회차별 |", "|---|---|---|"]
        for name, runs in (("공식", A), ("+ gapfuzz 수정", B)):
            app = [sum(x["opened"] for x in r["targets"] if x["applied"]) for r in runs]
            ctl = [sum(x["opened"] for x in r["targets"] if not x["applied"]) for r in runs]
            n_app = sum(1 for x in runs[0]["targets"] if x["applied"])
            n_ctl = sum(1 for x in runs[0]["targets"] if not x["applied"])
            L.append(f"| {name} | {', '.join(f'{v}/{n_app}' for v in app)} | {', '.join(f'{v}/{n_ctl}' for v in ctl) if n_ctl else '–'} |")
        L.append("")
    L += ["## 크래시", "", "| 하네스 | 크래시가 난 회차 | 판정 |", "|---|---:|---|"]
    for name, runs in (("공식", A), ("+ gapfuzz 수정", B)):
        n = sum(1 for r in runs if r["crashes"])
        verdicts = sorted({f"{t['verdict']}({t['confidence']})" for r in runs for t in r["triage"]})
        L.append(f"| {name} | {n}/{len(runs)} | {', '.join(verdicts) or '–'} |")
    L += ["", "## 실행 환경", "",
          f"- clang: {'; '.join(clangs)}" + (" **(서로 다름: 비교에 주의)**" if len(clangs) > 1 else ""),
          f"- CPU: {'; '.join(cpus)}" + (" **(서로 다름)**" if len(cpus) > 1 else ""),
          f"- 실행한 사람: {', '.join(sorted({r['by'] for r in A + B}))}",
          f"- 실행 수 중앙값: 공식 {sorted(r['execs'] or 0 for r in A)[len(A) // 2]:,}, 수정 {sorted(r['execs'] or 0 for r in B)[len(B) // 2]:,}"]
    (RESULTS / lib / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return stats


def report(a) -> int:
    targets = LIBS if a.all else [a.lib]
    rows = []
    for lib in targets:
        if not load(lib, "official") and not load(lib, "official_v2"):
            continue
        st = report_lib(lib)
        print(f"[report] results/{lib}/REPORT.md")
        if st:
            b = st["branches"]
            rows.append(f"| {lib} | {len(b['official'])} | {_fmt(b['official'])} | {_fmt(b['official_v2'])} | {b['a12']:.2f} | {b['p']:.4g} |")
    if a.all:
        L = ["# 1시간 반복 실험 요약 (분기 커버리지)", "", "| 라이브러리 | 회차 | 공식 | + gapfuzz 수정 | A12 | p |",
             "|---|---:|---|---|---:|---:|", *rows]
        (RESULTS / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("[report] results/SUMMARY.md")
    return 0


# ------------------------------------------------------------------ 올리기
def submit(a) -> int:
    lib = a.lib
    report_lib(lib)
    path = f"results/{lib}"
    g = lambda *c: sh(["git", "-C", str(ROOT), *c])
    if g("rev-parse", "--is-inside-work-tree").returncode:
        raise SystemExit("git 저장소가 아닙니다")
    staged_other = [f for f in g("diff", "--cached", "--name-only").stdout.split() if not f.startswith(path + "/")]
    if staged_other:
        raise SystemExit("results/ 밖의 파일이 이미 staged 상태입니다. 실험 결과만 따로 올리도록 먼저 정리하세요:\n  " + "\n  ".join(staged_other))
    g("add", path)
    if not g("diff", "--cached", "--name-only", "--", path).stdout.strip():
        print("[submit] 올릴 새 결과가 없습니다")
        return 0
    n = {h: len(done_trials(lib, h)) for h in HARNESSES}
    who = who_am_i()
    msg = f"results({lib}): official {n['official']}회, official_v2 {n['official_v2']}회 ({who})"
    r = g("commit", "-m", msg)
    if r.returncode:
        raise SystemExit(r.stderr or r.stdout)
    print(f"[submit] 커밋: {msg}")
    if a.no_push:
        return 0
    r = g("pull", "--rebase", "--autostash")
    if r.returncode:
        raise SystemExit("[submit] pull --rebase 실패. 다른 사람이 같은 results/ 폴더를 고쳤는지 확인하세요\n" + r.stderr)
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
    c = sub.add_parser("claim", help="라이브러리를 맡기 (results/<lib>/OWNER.txt를 올려 다른 사람과 겹치지 않게)")
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
    p = sub.add_parser("report", help="results/<lib>/REPORT.md 만들기")
    p.add_argument("lib", nargs="?")
    p.add_argument("--all", action="store_true", help="모든 라이브러리 + results/SUMMARY.md")
    s = sub.add_parser("submit", help="results/<lib>/만 커밋하고 push")
    s.add_argument("lib")
    s.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if a.cmd == "report" and not a.all and not a.lib:
        ap.error("라이브러리 이름이나 --all을 주세요")
    return {"doctor": doctor, "libs": libs, "claim": claim, "fetch": fetch, "run": run, "report": report,
            "submit": submit}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
