"""실행 중 실제 인자 값 기록 (argtrace).

정적 분석은 "하네스가 이 인자에 변수를 넘긴다"까지만 안다. 그 변수가 실제로는 늘 같은 값인지는 돌려 봐야 안다.
argtrace는 하네스가 라이브러리를 부르는 지점마다 인자 식을 기록용 래퍼로 감싼 사본을 만들고,
이미 모아 둔 코퍼스를 한 번 다시 실행해 "지점별로 실제 넘어간 값의 종류"를 센다.

  python3 -m gapfuzz argtrace zlib official                # out/targets/zlib/official/r1/corpus 재실행 → r1/args.json
  python3 scripts/tgt.py analyze zlib official out/targets/zlib/official/r1   # args.json이 있으면 자동으로 반영

분석기는 이 기록을 이렇게 쓴다 (causes.py `_apply_runtime`):
  코드로는 '변수'인데 관찰한 값이 한 가지뿐(호출 50번 이상) → "고정"으로 판정하고 근거에 관찰 횟수를 적는다.
  값이 여러 가지면 판정은 그대로 두고 "실행 중 관찰: N번 호출에서 값 K가지"만 근거로 붙인다.

한계
  - 원본 하네스는 건드리지 않는다. 사본(out/…/argtrace/)만 계측한다.
  - 매크로에서 나온 인자, 기본값·상수 인자, C 하네스의 구조체 값 인자는 감싸지 않는다.
  - 포인터는 null 여부만, 객체는 "넘겼다"만 기록한다(가리키는 내용은 보지 않음).
  - 코퍼스에 있는 입력만 본다. 값이 한 가지였다는 것은 "이 코퍼스에서는"이라는 뜻이다.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from .ast_index import AstIndex, build_index
from .llmfix import ROOT, _tgt

SKIP_KINDS = {"default", "literal"}
INT_T = re.compile(r"^(unsigned |signed )?(char|short|int|long|long long|__int128|_Bool|bool|wchar_t|size_t)( unsigned| int| long)*$|^enum ")
FLOAT_T = re.compile(r"^(float|double|long double)$")


def _macro(ctype: str, cxx: bool) -> str | None:
    t = re.sub(r"\b(const|volatile|restrict)\b", "", ctype).strip()
    t = re.sub(r"\s+", " ", t)
    if t.endswith("*") or "(*)" in t:
        return "GAPFUZZ_ARG_P"
    if INT_T.match(t):
        return "GAPFUZZ_ARG_I"
    if FLOAT_T.match(t):
        return "GAPFUZZ_ARG_F"
    return "GAPFUZZ_ARG_O" if cxx else None       # C에서는 구조체 값을 감쌀 수 없다


def _balanced(s: bytes) -> bool:
    d = 0
    for ch in s.decode("utf-8", "replace"):
        d += ch in "([{"
        d -= ch in ")]}"
        if d < 0:
            return False
    return d == 0


def plan(idx: AstIndex, harness: str) -> list[dict]:
    """하네스 안의 호출 지점에서 감쌀 인자 목록. 라이브러리 함수(하네스 밖에 정의된 함수)를 부르는 지점만."""
    harness = os.path.abspath(harness)
    src = open(harness, "rb").read()
    cxx = not harness.endswith(".c")
    out, seen = [], set()
    for cs in idx.calls:
        if cs.file != harness:
            continue
        fds = [idx.funcs.get(m) for m in cs.callees]
        if not any(fd and os.path.abspath(fd.file or "") != harness for fd in fds):
            continue
        for p, a in enumerate(cs.args):
            if a.kind in SKIP_KINDS or not a.span or a.span in seen:
                continue
            b, e = a.span
            text = src[b:e]
            mac = _macro(a.ctype, cxx)
            if not mac or not text.strip() or text.lstrip()[:1] == b"{" or not _balanced(text):
                continue
            seen.add(a.span)
            out.append({"id": len(out), "line": cs.line, "col": cs.col, "arg": p, "macro": mac,
                        "span": [b, e], "expr": text.decode("utf-8", "replace"), "type": a.ctype})
    return out


def instrument(harness: str, sites: list[dict]) -> bytes:
    """인자 식을 감싼 하네스 사본의 내용. 줄 번호는 #line으로 원본에 맞춘다."""
    src = open(harness, "rb").read()
    ins = []                                  # (위치, 정렬키, 넣을 글자)
    for s in sites:
        b, e = s["span"]
        ins.append((b, 0, -(e - b), f"{s['macro']}({s['id']}, ".encode()))     # 같은 시작이면 바깥(긴) 식부터
        ins.append((e, 1, e - b, b")"))                                         # 같은 끝이면 안쪽(짧은) 식부터
    out, pos = [], 0
    for at, _, _, text in sorted(ins, key=lambda x: (x[0], x[1], x[2])):
        out.append(src[pos:at]); out.append(text); pos = at
    out.append(src[pos:])
    head = f'#define GAPFUZZ_ARGTRACE_N {max(len(sites), 1)}\n#include "gapfuzz_argtrace.h"\n#line 1 "{harness}"\n'.encode()
    return head + b"".join(out)


def read_raw(path: Path, sites: list[dict]) -> list[dict]:
    by = {s["id"]: s for s in sites}
    out = []
    if path.exists():
        for ln in path.read_text().splitlines():
            parts = ln.split()
            s = by.get(int(parts[0]))
            if s:
                out.append({"line": s["line"], "col": s["col"], "arg": s["arg"], "expr": s["expr"], "type": s["type"],
                            "count": int(parts[1]), "overflow": bool(int(parts[2])), "values": parts[3:]})
    return out


def load_runtime(path: str | None) -> dict:
    """args.json → {(줄, 열, 인자 번호): {"count", "values", "overflow"}} (Analyzer의 runtime 인자)."""
    if not path or not os.path.exists(path):
        return {}
    d = json.load(open(path))
    return {(s["line"], s["col"], s["arg"]): {"count": s["count"], "values": s["values"], "overflow": s["overflow"]}
            for s in d.get("sites", [])}


def run(target: str, harness: str, corpus: list[str] | None = None, out: str | None = None) -> dict:
    tg = _tgt()
    t = tg.load(target)
    hp = tg.harness_path(t, harness)
    base = ROOT / "out" / "targets" / t["name"] / harness
    corpus = [Path(c) for c in corpus] if corpus else [base / "r1" / "corpus"]
    for c in corpus:
        if not c.is_dir():
            raise SystemExit(f"코퍼스 없음: {c}  (먼저 `python3 scripts/tgt.py repeat {target} {harness} --trials 1` 로 퍼징)")
    outp = Path(out) if out else corpus[0].parent / "args.json"

    inc = [str(d) for d in t["incs"]] + [str(ROOT / "harnesses" / "include")]
    idx = build_index([str(s) for s in t["srcs"]] + [str(hp)], inc, [f for f in t.get("cflags", []) if f.startswith("-D")])
    sites = plan(idx, str(hp))
    work = base / "argtrace"
    work.mkdir(parents=True, exist_ok=True)
    inst = work / f"argtrace_{hp.name}"
    inst.write_bytes(instrument(str(hp), sites))

    t2 = dict(t, incs=[*t["incs"], hp.parent])
    for c in tg.compile_cmds(t2, inst, work, "cov"):
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"[argtrace] 계측한 하네스가 컴파일되지 않습니다 ({inst})\n{r.stderr[-3000:]}")
    raw = work / "args.raw"
    raw.unlink(missing_ok=True)
    env = dict(os.environ, GAPFUZZ_ARGTRACE_OUT=str(raw), LLVM_PROFILE_FILE="/dev/null")
    subprocess.run([str(work / "cov"), "-runs=0", "-rss_limit_mb=2048", "-timeout=10", *map(str, corpus)], env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not raw.exists():
        raise SystemExit("[argtrace] 기록 파일이 만들어지지 않았습니다 (코퍼스 재실행 중 비정상 종료)")
    rows = read_raw(raw, sites)
    data = {"target": target, "harness": harness, "corpus": [str(c) for c in corpus],
            "inputs": sum(1 for c in corpus for _ in c.iterdir()), "instrumented": len(sites), "sites": rows}
    json.dump(data, open(outp, "w"), ensure_ascii=False, indent=1)
    single = [r for r in rows if len(r["values"]) == 1 and not r["overflow"] and r["values"][0] not in ("o", "p:nonnull")]
    print(f"[argtrace] {target}/{harness}: 인자 {len(sites)}곳 계측, {len(rows)}곳 실행됨, 입력 {data['inputs']}개 재실행")
    print(f"[argtrace] 값이 한 가지뿐이던 인자 {len(single)}곳")
    for r in single[:20]:
        print(f"  {hp.name}:{r['line']}  `{r['expr'][:40]}`  항상 {r['values'][0]}  ({r['count']}번 호출)")
    print(f"[argtrace] -> {outp}")
    return data
