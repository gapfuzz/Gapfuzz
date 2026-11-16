"""크래시 원인 귀속 (차별점 C): 크래시가 하네스 탓인지 라이브러리 탓인지 가린다.

크래시 입력을 퍼징 바이너리에 다시 넣어 sanitizer 리포트를 받고,
접근·해제·할당 스택에서 '처음으로 나오는 우리 코드 프레임'이 하네스인지 라이브러리인지 본다.

분류 (기획서의 크래시 4종)
  LIBRARY   ⓐ 라이브러리 결함 의심  : 접근·할당·해제가 모두 라이브러리 코드
  HARNESS   ⓑ 하네스 버그 의심      : 하네스가 메모리를 해제/할당했거나, 하네스 코드 자체에서 오류,
                                       또는 하네스(FuzzedDataProvider 포함)가 abort
  RESOURCE  ⓒ 리소스 상한           : timeout, out-of-memory, 스택 오버플로, 너무 큰 할당
  ASSERT    ⓓ 의도된 assert         : 라이브러리의 assert가 실패해 abort
  UNCLEAR   판단 보류                : 재현 안 됨, 스택 정보 부족, 근거가 엇갈림

프레임 소유 판정
  harness : 하네스 소스 파일, 또는 하네스 디렉터리 아래 파일(FuzzedDataProvider.h 등)
  library : 라이브러리 디렉터리 아래 파일
  runtime : 그 밖의 모든 것(compiler-rt, libFuzzer, C/C++ 표준 라이브러리, libc)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass, field, asdict

CLASS_KO = {
    "LIBRARY": "ⓐ 라이브러리 결함 의심",
    "HARNESS": "ⓑ 하네스 버그 의심",
    "RESOURCE": "ⓒ 리소스 상한",
    "ASSERT": "ⓓ 의도된 assert",
    "UNCLEAR": "판단 보류",
}
CLASS_ACTION = {
    "LIBRARY": "최소화·재현 후 라이브러리 개발자에게 보고 검토",
    "HARNESS": "하네스를 고친 뒤 같은 입력으로 다시 확인 (라이브러리에 보고하지 않음)",
    "RESOURCE": "상한 설정이 적절한지 확인. 입력 크기에 비해 과도하면 라이브러리 문제일 수 있음",
    "ASSERT": "assert 조건이 '입력으로 도달하면 안 되는 상태'인지 확인. 입력만으로 걸리면 결함일 수 있음",
    "UNCLEAR": "직접 리포트를 읽고 판단",
}
# 비교 실험용: 1이면 2026-10에 고친 파서·규칙(UBSan 메모 줄 건너뛰기, 새 ASan 할당 머리말, null·vptr·
# API 사용 규칙 위반 판정) 없이 예전 동작 그대로 쓴다
LEGACY = os.environ.get("GAPFUZZ_TRIAGE_LEGACY") == "1"
FRAME_HEAD_RE = re.compile(r"^\s*#(\d+)\s+0x[0-9a-f]+\s*(?:in\s+)?(.*)$")
FRAME_LOC_RE = re.compile(r"\s(\S+?):(\d+)(?::(\d+))?$")
FRAME_MOD_RE = re.compile(r"\s*\((?:BuildId:[^()]*|[^()]*\+0x[0-9a-f]+)\)\s*$")   # 끝의 "(모듈+0x..)", "(BuildId: ..)"


def parse_frame_line(line: str):
    """'#3 0x.. in func /path/file.cpp:12:5' 같은 스택 줄을 (함수, 파일, 줄)로 나눈다.
    함수 이름이 없거나(모듈만 찍힘) 경로가 상대 경로(glibc 소스)인 줄도 처리한다."""
    m = FRAME_HEAD_RE.match(line)
    if not m:
        return None
    rest = m.group(2).rstrip()
    while True:                                   # 끝에 붙은 모듈·BuildId 괄호를 떼어 낸다
        nm = FRAME_MOD_RE.search(rest)
        if not nm:
            break
        rest = rest[:nm.start()].rstrip()
    f = ln = None
    lm = FRAME_LOC_RE.search(" " + rest)
    if lm:
        f, ln = lm.group(1), int(lm.group(2))
        rest = (" " + rest)[:lm.start()].strip()
    return rest or "?", f, ln
MEM_TYPES = ("use-after-free", "double-free", "buffer-overflow", "use-after-return", "use-after-scope",
             "attempting free", "bad-free", "alloc-dealloc-mismatch", "SEGV", "invalid-pointer-pair",
             "memcpy-param-overlap", "negative-size-param", "container-overflow", "BUS", "FPE",
             "deadly signal", "leak")


@dataclass
class Frame:
    func: str
    file: str | None
    line: int | None
    owner: str              # harness | library | runtime


@dataclass
class Report:
    kind: str                       # 예: heap-use-after-free, timeout, ub:..., leak
    summary: str
    access: list[Frame] = field(default_factory=list)   # 오류가 난(접근한) 스택
    freed: list[Frame] = field(default_factory=list)
    alloc: list[Frame] = field(default_factory=list)
    scope: list[Frame] = field(default_factory=list)    # 스택 변수 오류: 그 변수가 있던 함수
    zero_page: bool = False                             # SEGV 주소가 0번지 근처 (null 포인터 접근)
    uncaught: str = ""                                  # 잡히지 않은 C++ 예외의 타입과 메시지 (std::terminate로 abort)
    request: int = 0                                    # out-of-memory: 한 번에 요청한 할당 크기(바이트). 누적으로 넘은 경우 0


@dataclass
class Verdict:
    cls: str
    confidence: str                 # 강 | 약
    reason: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class CrashResult:
    files: list[str]
    kind: str
    summary: str
    signature: str
    verdict: Verdict
    reproduced: str                 # 예: "3/3"
    top_frames: list[str] = field(default_factory=list)


class Owner:
    def __init__(self, harness_files: list[str], harness_dirs: list[str], lib_dirs: list[str]):
        self.hfiles = {os.path.realpath(p) for p in harness_files}
        self.hdirs = [os.path.realpath(d).rstrip("/") + "/" for d in harness_dirs]
        self.ldirs = [os.path.realpath(d).rstrip("/") + "/" for d in lib_dirs]

    def __call__(self, path: str | None) -> str:
        if not path or not os.path.isabs(path):     # 상대 경로는 glibc 등 시스템 소스
            return "runtime"
        p = os.path.realpath(path)
        # 순서: 하네스 파일 자체 → 라이브러리 디렉터리 → 하네스 디렉터리
        # (하네스와 라이브러리가 같은 디렉터리에 있어도 라이브러리 파일을 하네스로 보지 않도록)
        if p in self.hfiles:
            return "harness"
        if any(p.startswith(d) for d in self.ldirs):
            return "library"
        if any(p.startswith(d) for d in self.hdirs):
            return "harness"
        return "runtime"


def _parse_frames(lines: list[str], i: int, owner: Owner, skip: int = 0) -> tuple[list[Frame], int]:
    """i번째 줄부터 스택 프레임을 읽는다. skip: 첫 프레임 전에 건너뛸 수 있는 설명 줄 수 (UBSan의 메모·메모리 덤프)."""
    frames = []
    while i < len(lines):
        p = parse_frame_line(lines[i])
        if not p:
            if frames:
                break
            l = lines[i].strip()
            if l == "" or l.startswith(("READ", "WRITE", "==")):
                i += 1
                continue
            if skip > 0 and not l.startswith(("SUMMARY:", "ERROR:")) and "ERROR:" not in l:
                skip -= 1
                i += 1
                continue
            break
        func, f, ln = p
        frames.append(Frame(func, f, ln, owner(f)))
        i += 1
    return frames, i


def parse_report(text: str, owner: Owner) -> Report | None:
    """sanitizer / libFuzzer 출력에서 첫 번째 오류 리포트를 뽑는다."""
    lines = text.splitlines()
    kind = summary = None
    start = None
    for i, l in enumerate(lines):
        if "ERROR: libFuzzer: timeout" in l:
            kind, start = "timeout", i
        elif "ERROR: libFuzzer: out-of-memory" in l:
            kind, start = "out-of-memory", i
        elif "ERROR: libFuzzer: deadly signal" in l:
            kind, start = "deadly signal", i
        elif "ERROR: LeakSanitizer: detected memory leaks" in l:
            kind, start = "leak", i
        elif "ERROR: AddressSanitizer:" in l:
            m = re.search(r"ERROR: AddressSanitizer: ([\w-]+(?: on unknown address)?)", l)
            kind, start = (m.group(1) if m else "asan"), i
            if kind.startswith("SEGV"):
                kind = "SEGV"
        elif "runtime error:" in l and kind is None:
            kind, start = "ub: " + l.split("runtime error:", 1)[1].strip()[:80], i
        if kind:
            break
    if kind is None:
        return None
    for l in lines[start:]:
        if l.startswith("SUMMARY:"):
            summary = l[len("SUMMARY:"):].strip()
            break
    rep = Report(kind, summary or lines[start].strip())
    if not LEGACY:
        for i, l in enumerate(lines[:start]):
            m = re.search(r"terminate called after throwing an instance of '([^']+)'", l)
            if m:
                what = lines[i + 1].strip() if i + 1 < len(lines) and "what()" in lines[i + 1] else ""
                rep.uncaught = m.group(1) + (f" ({what.split(':', 1)[1].strip()})" if what else "")
    rep.zero_page = not LEGACY and (kind == "SEGV" and any("address points to the zero page" in l for l in lines[start:start + 6])) or (
        kind.startswith("ub:") and "null pointer" in kind)

    i = start + 1
    # 첫 스택 = 오류가 난 지점 (timeout/oom은 libFuzzer가 찍은 스택)
    # libFuzzer의 timeout/out-of-memory는 오류 줄과 스택 사이에 안내 줄("To change the out-of-memory limit use ...")이 끼어 있다.
    # 이 줄에서 읽기를 멈추면 스택을 통째로 놓쳐 "가장 가까운 코드: ?"가 된다(2026-11-16 jsoncpp 사례).
    skip = 0
    if not LEGACY:
        skip = 12 if kind.startswith("ub:") else (4 if kind in ("timeout", "out-of-memory") else 0)
        m = re.search(r"out-of-memory \(malloc\((\d+)\)\)", lines[start])
        if m:
            rep.request = int(m.group(1))
    rep.access, i = _parse_frames(lines, i, owner, skip=skip)
    while i < len(lines):
        l = lines[i]
        if "freed by thread" in l:
            rep.freed, i = _parse_frames(lines, i + 1, owner)
        elif "is located in stack of thread" in l:
            rep.scope, i = _parse_frames(lines, i + 1, owner)
        elif ("allocated by thread" in l if not LEGACY else "previously allocated by thread" in l) or "allocated from:" in l:
            fr, i = _parse_frames(lines, i + 1, owner)
            if kind == "leak" and not rep.access:
                rep.access = fr
            rep.alloc = rep.alloc or fr
        elif l.startswith("SUMMARY:"):
            break
        else:
            i += 1
    return rep


def _first(frames: list[Frame]) -> Frame | None:
    return next((f for f in frames if f.owner != "runtime"), None)


DESTROY_RE = re.compile(r"(~\w+|Delete\w*|Destroy\w*|Free\w*|Release\w*|Clear\w*|Close\w*|Reset\w*|Remove\w*|"
                        r"Unlink\w*|Dispose\w*|operator delete)\s*(\(|$)")


def _entry(frames: list[Frame]) -> tuple[Frame | None, Frame | None]:
    """하네스가 라이브러리를 부른 진입 지점: (하네스 프레임, 하네스가 직접 부른 라이브러리 API 프레임)."""
    for i, f in enumerate(frames):
        if f.owner == "harness":
            api = next((frames[j] for j in range(i - 1, -1, -1) if frames[j].owner == "library"), None)
            return f, api
    return None, None


def _short(func: str) -> str:
    if not LEGACY:
        func = func.replace("(anonymous namespace)::", "")      # 이름 없는 네임스페이스의 함수 이름이 통째로 지워지지 않게
    return func.split("(")[0].strip()


def _loc(f: Frame | None, root: str) -> str:
    if not f:
        return "(우리 코드 프레임 없음)"
    where = f"{os.path.relpath(f.file, root)}:{f.line}" if f.file else "?"
    return f"`{_short(f.func) if not LEGACY else f.func.split('(')[0]}` @ {where}"


def classify(rep: Report, root: str) -> Verdict:
    k = rep.kind
    acc, fre, alc, scp = _first(rep.access), _first(rep.freed), _first(rep.alloc), _first(rep.scope)
    ev = []
    if acc:
        ev.append(f"오류 지점: {_loc(acc, root)} ({acc.owner})")
    if fre:
        ev.append(f"해제 위치: {_loc(fre, root)} ({fre.owner})")
    if alc:
        ev.append(f"할당 위치: {_loc(alc, root)} ({alc.owner})")
    if scp:
        ev.append(f"변수가 있던 함수: {_loc(scp, root)} ({scp.owner})")

    # ⓒ 리소스
    if k in ("timeout", "out-of-memory", "stack-overflow", "allocation-size-too-big", "requested allocation size"):
        owner = acc.owner if acc else "?"
        if not LEGACY:
            if rep.request:
                ev.append(f"한 번에 요청한 할당: {rep.request:,}바이트 ({rep.request / (1 << 20):.0f}MB)")
            h, api = _entry(rep.access)
            if h and api:
                ev.append(f"하네스가 부른 API: {_loc(api, root)}, 하네스 위치: {_loc(h, root)}")
            elif h:
                ev.append(f"하네스 위치: {_loc(h, root)}")
        return Verdict("RESOURCE", "강", f"{k}: 시간·메모리·스택 상한에 걸림 (가장 가까운 코드: {owner})", ev)

    # ⓑ 잡히지 않은 C++ 예외: 라이브러리는 잘못된 사용을 예외로 알리도록 되어 있는데 하네스가 받지 않음
    if rep.uncaught:
        h, api = _entry(rep.access)
        thrower = next((f for f in rep.access if f.owner == "library"), None)
        if h and thrower:
            ev.append(f"예외: {rep.uncaught}")
            ev.append(f"하네스가 부른 API: {_loc(api, root)}, 하네스 위치: {_loc(h, root)}")
            return Verdict("HARNESS", "강", f"라이브러리 API `{_short(api.func) if api else '?'}`가 던진 예외 "
                                            f"`{rep.uncaught.split(' ')[0]}`를 하네스가 잡지 않아 프로그램이 종료됨 — "
                                            f"그 호출을 try/catch로 감싸거나 API 문서의 인자 범위를 지켜야 함", ev)
        if thrower:
            ev.append(f"예외: {rep.uncaught}")
            return Verdict("LIBRARY", "약", "라이브러리 내부에서 던진 예외가 라이브러리 안에서 처리되지 않음", ev)

    # ⓓ assert / abort
    funcs = [f.func for f in rep.access]
    if any("__assert_fail" in f or "__assert_rtn" in f for f in funcs) or (
            k == "deadly signal" and any(f.split("(")[0].strip() in ("abort", "__GI_abort") for f in funcs)):
        if acc and acc.owner == "library":
            # assert가 아닌 명시적 abort를, 하네스가 직접 부른 공개 API가 들어오자마자(그 함수나 바로 아래 오류 처리 함수에서) 부름:
            # 라이브러리가 인자 범위를 검사해 거부한 것이므로 하네스의 사용 규칙 위반
            lib_depth = 0
            for f in rep.access:
                if f.owner == "harness":
                    break
                if f.owner == "library":
                    lib_depth += 1
            h, api = _entry(rep.access)
            is_assert = any("__assert_fail" in f or "__assert_rtn" in f for f in funcs)
            if not LEGACY and not is_assert and h and api and lib_depth <= 2:   # assert(불변 조건)가 아니라 명시적 abort
                ev.append(f"하네스가 부른 API: {_loc(api, root)}, 하네스 위치: {_loc(h, root)}")
                return Verdict("HARNESS", "중", f"하네스가 직접 부른 API `{_short(api.func)}`가 입구의 인자 검사에서 abort함 — "
                                               f"API가 허용하지 않는 인자를 하네스가 넘김 (문서의 인자 범위를 지켜야 함)", ev)
            return Verdict("ASSERT", "강", "라이브러리의 assert/abort가 실패함", ev)
        if acc and acc.owner == "harness":
            return Verdict("HARNESS", "강", "하네스 쪽 코드(FuzzedDataProvider 포함)가 abort함 — 하네스의 사용 규칙 위반", ev)
        return Verdict("UNCLEAR", "약", "abort했지만 호출한 코드를 특정하지 못함", ev)

    # ⓑ / ⓐ 메모리 오류, UB, 누수
    if fre and fre.owner == "harness":
        return Verdict("HARNESS", "강", "메모리를 해제한 곳이 하네스 — 하네스가 넘긴 메모리의 수명이 라이브러리 사용보다 짧음", ev)
    if scp and scp.owner == "harness" and k in ("stack-use-after-scope", "stack-use-after-return"):
        return Verdict("HARNESS", "강", "수명이 끝난 하네스 지역 변수를 가리키는 포인터가 쓰임", ev)
    if not LEGACY and "does not point to an object of type" in k:
        # 라이브러리가 자체 메모리 풀을 쓰면 ASan은 해제를 못 보고, 소멸된 객체의 vptr이 깨진 것으로만 드러난다
        if acc and acc.owner == "harness":
            return Verdict("HARNESS", "강", "하네스가 이미 소멸된 객체(또는 다른 타입의 객체)의 멤버 함수를 호출 — "
                           "문서·부모가 정리한 노드를 계속 쓴 사용 규칙 위반일 가능성이 큼 "
                           "(라이브러리 메모리 풀 안의 객체라 ASan의 해제 추적 대신 UBSan의 vptr 검사로 드러남)", ev)
        if acc and acc.owner == "library":
            return Verdict("LIBRARY", "약", "라이브러리 안에서 소멸된 객체를 호출 — 하네스가 이미 지운 노드를 넘겼는지 먼저 확인", ev)
    if acc and acc.owner == "harness":
        return Verdict("HARNESS", "강", "오류가 하네스 코드 안에서 직접 발생", ev)
    if k == "leak":
        if alc and alc.owner == "harness":
            return Verdict("HARNESS", "강", "누수된 메모리를 하네스가 할당함", ev)
        if alc and alc.owner == "library":
            return Verdict("LIBRARY", "약", "라이브러리가 할당한 메모리가 누수됨 (하네스가 해제 API를 안 불렀을 수도 있음)", ev)
        return Verdict("UNCLEAR", "약", "누수의 할당 위치를 특정하지 못함", ev)
    # API 사용 규칙 위반: 하네스가 해제를 요청한 객체(소멸자·Delete류 API)를 하네스의 다른 줄에서 다시 씀
    fh, fapi = _entry(rep.freed)
    ah, aapi = _entry(rep.access)
    if fapi:
        ev.append(f"해제를 요청한 하네스 호출: {_loc(fapi, root)} ← {_loc(fh, root)}")
    if aapi:
        ev.append(f"오류가 난 하네스 호출: {_loc(aapi, root)} ← {_loc(ah, root)}")
    if (not LEGACY and k in ("heap-use-after-free", "double-free") and fh and ah and fapi
            and DESTROY_RE.search(_short(fapi.func).split("::")[-1])
            and (fh.file, fh.line) != (ah.file, ah.line)):
        what = "같은 객체를 두 번 해제하도록 요청" if k == "double-free" else "해제를 요청한 객체를 나중에 다시 사용"
        return Verdict("HARNESS", "강",
                       f"하네스가 `{_short(fapi.func)}`로 {what} — 라이브러리 내부가 아니라 API 사용 규칙 위반 "
                       f"(해제 요청 {os.path.basename(fh.file or '?')}:{fh.line}, 사용 {os.path.basename(ah.file or '?')}:{ah.line})", ev)
    if alc and alc.owner == "harness" and acc and acc.owner == "library":
        return Verdict("HARNESS", "약", "라이브러리가 하네스가 준 메모리를 잘못 읽음 — 하네스가 크기·수명 규칙을 어겼을 가능성", ev)
    if not LEGACY and acc and acc.owner == "library" and rep.zero_page:
        api = f"`{_short(aapi.func)}`" if aapi else "라이브러리 API"
        return Verdict("LIBRARY", "약", f"라이브러리가 null 포인터를 따라감 ({api}). 하네스가 null을 넘겼다면 그 API가 "
                       "null을 허용하는지 문서를 확인 — 허용하지 않으면 하네스 탓, 허용하거나 명시가 없으면 라이브러리의 방어 누락", ev)
    if acc and acc.owner == "library" and (not alc or alc.owner == "library") and (not fre or fre.owner == "library"):
        return Verdict("LIBRARY", "강", "오류 지점과 메모리 할당·해제가 모두 라이브러리 코드", ev)
    return Verdict("UNCLEAR", "약", "근거가 엇갈리거나 스택 정보가 부족함", ev)


def signature(rep: Report) -> str:
    """같은 버그인지 묶는 서명: 오류 종류 + 접근 스택 위쪽 3개(함수:줄) + 해제 스택의 첫 우리 코드 함수.
    함수 이름만 쓰면 같은 함수에서 터진 서로 다른 버그(예: 라이브러리 내부 해제 후 사용 vs 하네스의 해제 후 사용)가 묶인다."""
    def key(f: Frame) -> str:
        return f"{f.func.split('(')[0]}:{f.line}" if not LEGACY else f.func.split("(")[0]
    top = [key(f) for f in rep.access if f.owner != "runtime"][:3]
    if not LEGACY:
        fr = _first(rep.freed)
        if fr:
            top.append("free@" + key(fr))
    base = re.sub(r"0x[0-9a-f]+", "", rep.kind)
    return hashlib.sha1((base + "|" + "|".join(top)).encode()).hexdigest()[:12]


def run_one(binary: str, path: str, timeout: int, rss: int) -> str:
    env = dict(os.environ)
    env.setdefault("ASAN_OPTIONS", "symbolize=1:detect_leaks=1:allocator_may_return_null=0")
    env.setdefault("UBSAN_OPTIONS", "print_stacktrace=1:halt_on_error=1")
    cmd = [binary, f"-timeout={timeout}", f"-rss_limit_mb={rss}", path]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, errors="replace",
                           timeout=timeout * 3 + 30, env=env)
        return p.stderr + p.stdout
    except subprocess.TimeoutExpired as e:
        return (e.stderr or "") + "\nERROR: libFuzzer: timeout (외부 제한 시간 초과)"


def triage(binary: str, crashes: list[str], harness_files: list[str], lib_dirs: list[str],
           harness_dirs: list[str] | None = None, repeat: int = 3, timeout: int = 10,
           rss: int = 2048, root: str | None = None) -> list[CrashResult]:
    root = os.path.abspath(root or os.getcwd())
    hdirs = harness_dirs if harness_dirs is not None else sorted({os.path.dirname(os.path.abspath(h)) for h in harness_files})
    owner = Owner(harness_files, hdirs, lib_dirs)
    groups: dict[str, CrashResult] = {}
    for path in crashes:
        reps = [parse_report(run_one(binary, path, timeout, rss), owner) for _ in range(max(repeat, 1))]
        first = next((r for r in reps if r), None)
        if first is None:
            sig = "no-repro"
            v = Verdict("UNCLEAR", "약", f"{repeat}번 다시 실행했지만 크래시가 재현되지 않음 (비결정적이거나 이미 고쳐짐)")
            res = groups.setdefault(sig, CrashResult([], "재현 안 됨", "", sig, v, f"0/{repeat}"))
            res.files.append(path)
            continue
        sig = signature(first)
        ok = sum(1 for r in reps if r and signature(r) == sig)
        if sig in groups:
            groups[sig].files.append(path)
            continue
        v = classify(first, root)
        if ok < len(reps) and v.confidence == "강":
            v.confidence = "약"
            v.reason += f" (재현 {ok}/{len(reps)}: 비결정적)"
        top = [f"{f.func.split('(')[0]} [{f.owner}]" for f in first.access if f.owner != "runtime"][:4]
        groups[sig] = CrashResult([path], first.kind, first.summary, sig, v, f"{ok}/{len(reps)}", top)
    order = list(CLASS_KO)
    return sorted(groups.values(), key=lambda r: (order.index(r.verdict.cls), r.signature))


def write_reports(results: list[CrashResult], out_md: str, meta: dict) -> None:
    json.dump({"meta": meta, "crashes": [asdict(r) for r in results]},
              open(os.path.splitext(out_md)[0] + ".json", "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    cnt = Counter(r.verdict.cls for r in results)
    out = [f"# 크래시 원인 귀속 — {meta.get('name', '')}", "",
           f"- 바이너리: `{meta.get('binary', '')}`",
           f"- 크래시 입력 {sum(len(r.files) for r in results)}개 → 서로 다른 크래시 {len(results)}개 (스택 기준으로 묶음)",
           f"- 입력마다 {meta.get('repeat', 3)}번씩 다시 실행해 재현 여부 확인", "",
           "| 분류 | 개수 | 다음 조치 |", "|---|---:|---|"]
    for c in CLASS_KO:
        if cnt[c]:
            out.append(f"| {CLASS_KO[c]} | {cnt[c]} | {CLASS_ACTION[c]} |")
    out.append("")
    for i, r in enumerate(results, 1):
        v = r.verdict
        out.append(f"## {i}. {CLASS_KO[v.cls]} (확신 {v.confidence}) — {r.kind}")
        out.append(f"- 판단 근거: {v.reason}")
        for e in v.evidence:
            out.append(f"  - {e}")
        if r.top_frames:
            out.append("- 오류 스택(우리 코드만): " + " → ".join(f"`{f}`" for f in r.top_frames))
        out.append(f"- 재현: {r.reproduced}")
        if r.summary:
            out.append(f"- sanitizer 요약: `{r.summary}`")
        out.append(f"- 입력 파일 {len(r.files)}개: " + ", ".join(f"`{os.path.basename(f)}`" for f in r.files[:5])
                   + (" …" if len(r.files) > 5 else ""))
        out.append(f"- 다음 조치: {CLASS_ACTION[v.cls]}")
        out.append("")
    if not results:
        out.append("크래시 입력이 없습니다.")
    open(out_md, "w").write("\n".join(out) + "\n")
