"""입력 내용에 막힌 분기를 위한 딕셔너리 후보 생성.

원인 추적에서 하네스로 고칠 수 없다고 나온 분기(라이브러리 내부·입력 내용 때문, 또는 원인 불명)의
조건식에서 퍼저가 직접 만들기 어려운 값을 뽑아 libFuzzer 딕셔너리(-dict) 형식으로 쓴다.

뽑는 것
  1) 문자·문자열 상수:           *p == '#'              → "#"
  2) 포인터 위치별 문자 조합:     *p == '0' && *(p+1) == 'x' → "0x"
  3) 숫자 경계값 (10진·16진 문자열): input < 0x10000      → "65536", "10000", "65535", "ffff"
     이름 붙은 상수는 같은 소스에서 `NAME = 값` 정의를 찾아 값으로 바꾼다.

이미 기존 딕셔너리에 있는 토큰은 빼고, 토큰마다 근거(파일:줄과 조건식)를 주석으로 남긴다.
AFL++의 자동 딕셔너리와 같은 발상이지만, 원인 추적 결과를 이용해 "하네스로 못 여는 분기"에만 집중한다.
"""
from __future__ import annotations

import itertools
import json
import os
import re
from typing import Dict, Iterable, List, Optional, Tuple

FIX_VERDICTS = {"FIXED", "SETTER_NOT_CALLED", "NARROW", "DIRECT_CALL"}

_ESC = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "\\": "\\", "'": "'", '"': '"'}
CHAR_RE = re.compile(r"'(\\.|[^\\'])'")
STR_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
NUM_RE = re.compile(r"(?<![\w.])(0[xX][0-9a-fA-F]+|\d+)[uUlL]*(?![\w.])")
# 비교식: 왼쪽 피연산자 (연산자) 오른쪽 피연산자
_DEREF = r"\*\s*\(\s*\w+\s*\+\s*\d+\s*\)|\*\s*\w+|\w+\s*\[\s*\d+\s*\]"
_VAL = r"'(?:\\.|[^\\'])'|0[xX][0-9a-fA-F]+|\d+|[A-Za-z_]\w*"
CMP_RE = re.compile(r"(" + _DEREF + r"|[A-Za-z_][\w.]*(?:->\w+)*(?:\(\))?)\s*(==|!=|<=|>=|<|>)\s*(" + _VAL + r")")
DEREF_RE = re.compile(r"\*\s*\(\s*(\w+)\s*\+\s*(\d+)\s*\)|\*\s*(\w+)|(\w+)\s*\[\s*(\d+)\s*\]")


def _unesc(s: str) -> str:
    return _ESC.get(s[1], s[1]) if s.startswith("\\") and len(s) > 1 else s


def _quote(tok: str) -> str:
    out = []
    for ch in tok:
        o = ord(ch)
        if ch in '"\\':
            out.append("\\" + ch)
        elif 0x20 <= o < 0x7F:
            out.append(ch)
        else:
            out.append("\\x%02X" % (o & 0xFF))
    return '"' + "".join(out) + '"'


class ConstTable:
    """소스 파일에서 `NAME = 숫자` 형태의 상수 정의를 모은다 (static const, enum, #define)."""

    DEF_RE = re.compile(r"\b([A-Z_][A-Z0-9_]{2,})\s*=\s*(0[xX][0-9a-fA-F]+|\d+)")
    MACRO_RE = re.compile(r"#\s*define\s+([A-Z_][A-Z0-9_]{2,})\s+\(?\s*(0[xX][0-9a-fA-F]+|\d+)")

    def __init__(self, sources: Iterable[str]):
        self.values: Dict[str, int] = {}
        for path in sources:
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in itertools.chain(self.DEF_RE.finditer(text), self.MACRO_RE.finditer(text)):
                self.values.setdefault(m.group(1), int(m.group(2), 0))

    def get(self, name: str) -> Optional[int]:
        if re.fullmatch(r"0[xX][0-9a-fA-F]+|\d+", name):
            return int(name, 0)
        return self.values.get(name)


def _numeric_tokens(v: int) -> List[str]:
    # 경계 바로 위·아래 값을 10진·16진 문자열로 (텍스트 형식 입력을 파싱하는 라이브러리용)
    toks = []
    for x in (v - 1, v, v + 1):
        if x < 10:          # 한 자리 숫자는 퍼저가 쉽게 만든다
            continue
        toks.append(str(x))
        toks.append(format(x, "x"))
    return toks


def _value(tok: str, consts: "ConstTable") -> Optional[int]:
    if tok.startswith("'"):
        return ord(_unesc(tok[1:-1]))
    return consts.get(tok)


def _deref(lhs: str) -> Optional[Tuple[str, int]]:
    m = DEREF_RE.fullmatch(lhs.strip())
    if not m:
        return None
    return (m.group(1) or m.group(3) or m.group(4)), int(m.group(2) or m.group(5) or 0)


def tokens_for_line(source: str, expr: str, consts: ConstTable, stmt: str = "") -> List[Tuple[str, str]]:
    """(토큰, 종류) 목록. source는 조건이 있는 줄, expr는 막힌 피연산자, stmt는 그 줄 앞뒤를 포함한 문장."""
    found: List[Tuple[str, str]] = []
    # 1) 막힌 피연산자의 문자열 상수
    for m in STR_RE.finditer(expr):
        s = re.sub(r"\\(.)", lambda mm: _ESC.get(mm.group(1), mm.group(1)), m.group(1))
        if s:
            found.append((s, "문자열"))
    # 2) 막힌 피연산자의 비교: 바이트 비교면 원시 바이트, 값 비교면 경계값 문자열
    for m in CMP_RE.finditer(expr):
        v = _value(m.group(3), consts)
        if v is None:
            continue
        if _deref(m.group(1)) is not None or m.group(3).startswith("'"):
            if v < 256:
                found.append((chr(v), "문자" if 0x20 <= v < 0x7F else "바이트"))
        elif v >= 10:
            for t in _numeric_tokens(v):
                found.append((t, "숫자 경계"))
    # 3) 같은 문장에서 같은 포인터의 연속 위치를 비교하면 그 바이트들을 이어 붙인 조합
    pos: Dict[str, Dict[int, List[str]]] = {}
    for m in CMP_RE.finditer(stmt or source):
        d = _deref(m.group(1))
        v = _value(m.group(3), consts)
        if d is None or v is None or v >= 256 or m.group(2) != "==":
            continue
        pos.setdefault(d[0], {}).setdefault(d[1], [])
        if chr(v) not in pos[d[0]][d[1]]:
            pos[d[0]][d[1]].append(chr(v))
    for base, offs in pos.items():
        keys = sorted(offs)
        if len(keys) < 2 or keys != list(range(keys[0], keys[0] + len(keys))):
            continue
        for combo in itertools.islice(itertools.product(*(offs[k] for k in keys)), 8):
            found.append(("".join(combo), "바이트 조합"))
    return found


def _statement(path: str, line: int, cache: Dict[str, List[str]]) -> str:
    if path not in cache:
        try:
            cache[path] = open(path, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            cache[path] = []
    lines = cache[path]
    return " ".join(lines[max(0, line - 4):line + 3])


def generate(gaps: List[dict], sources: List[str], existing: Optional[str] = None,
             include_fixable: bool = False) -> List[dict]:
    consts = ConstTable(sources)
    have = set()
    if existing and os.path.exists(existing):
        for line in open(existing, encoding="utf-8", errors="replace"):
            m = re.search(r'"((?:\\.|[^"\\])*)"\s*$', line.strip())
            if m and not line.lstrip().startswith("#"):
                have.add(re.sub(r"\\(.)", r"\1", m.group(1)))
    out: Dict[str, dict] = {}
    files: Dict[str, List[str]] = {}
    for gap in gaps:
        for r in gap["results"]:
            for b in r.get("stuck_branches", []):
                verdicts = {c["verdict"] for c in b.get("causes", [])}
                if not include_fixable and verdicts & FIX_VERDICTS:
                    continue  # 하네스를 고쳐서 열 분기는 제외
                stmt = _statement(b["file"], b["line"], files)
                for tok, kind in tokens_for_line(b.get("source", ""), b.get("expr", ""), consts, stmt):
                    if not tok or tok.strip("\0") == "" or tok in have:
                        continue
                    e = out.setdefault(tok, {"token": tok, "kind": kind, "evidence": []})
                    ev = f"{os.path.basename(b['file'])}:{b['line']} {b.get('expr', '').strip()}"
                    if ev not in e["evidence"]:
                        e["evidence"].append(ev)
    return sorted(out.values(), key=lambda e: (-len(e["evidence"]), e["token"]))


def write_dict(entries: List[dict], path: str, base: Optional[str] = None) -> None:
    lines = ["# gapfuzz dict: 하네스로 열 수 없는(입력 내용에 막힌) 분기의 조건식에서 뽑은 토큰", ""]
    if base and os.path.exists(base):
        lines.append(f"# --- 기존 딕셔너리: {base}")
        lines += [l.rstrip("\n") for l in open(base, encoding="utf-8", errors="replace")]
        lines.append("")
        lines.append("# --- gapfuzz가 추가한 토큰")
    for i, e in enumerate(entries, 1):
        lines.append(f"# {e['kind']}: " + "; ".join(e["evidence"][:3]))
        lines.append(f"gapfuzz_{i}={_quote(e['token'])}")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
