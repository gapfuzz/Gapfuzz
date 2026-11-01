"""clang JSON AST에서 함수 선언, 클래스 계층, 호출 지점, 조건문, 필드 쓰기를 뽑아내는 모듈.

clang의 `-ast-dump=json` 출력은 위치 정보가 '증분' 방식이다.
각 위치 객체는 이전에 출력된 위치와 file/line이 달라졌을 때만 그 값을 적는다.
그래서 JSON을 출력 순서대로 훑으며 현재 file/line 상태를 들고 다녀야 한다.

선언 id(예: "0x55e7...")는 번역 단위(TU) 안에서만 유효하므로,
TU 하나를 다 훑은 뒤 mangled 이름이나 "클래스::필드" 같은 전역 키로 바꿔 저장한다.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field

FUNC_KINDS = {
    "FunctionDecl", "CXXMethodDecl", "CXXConstructorDecl",
    "CXXDestructorDecl", "CXXConversionDecl",
}
CALL_KINDS = {"CallExpr", "CXXMemberCallExpr", "CXXOperatorCallExpr"}
CTOR_KINDS = {"CXXConstructExpr", "CXXTemporaryObjectExpr"}
WRAPPER_KINDS = {
    "ImplicitCastExpr", "ParenExpr", "MaterializeTemporaryExpr", "CXXBindTemporaryExpr",
    "ExprWithCleanups", "ConstantExpr", "CStyleCastExpr", "CXXStaticCastExpr",
    "CXXFunctionalCastExpr",
}
LITERAL_KINDS = {
    "IntegerLiteral", "FloatingLiteral", "StringLiteral", "CXXBoolLiteralExpr", "CharacterLiteral",
}
ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "|=", "&=", "^=", "<<=", ">>="}


@dataclass
class FuncDecl:
    mangled: str
    name: str
    qualname: str          # 예: tinyxml2::XMLNode::DeleteChildren
    record: str | None     # 소속 클래스(정규화된 이름), 자유 함수면 None
    kind: str
    sig: str               # 예: void (XMLNode *)
    access: str | None
    virtual: bool
    implicit: bool
    deleted: bool
    pure: bool             # 순수 가상 함수(= 0): 몸체가 없어 실행될 수 없음
    file: str | None
    line: int | None
    params: list[str] = field(default_factory=list)   # 매개변수 이름(순서대로, 이름이 없으면 "")
    param_types: list[str] = field(default_factory=list)


@dataclass
class Arg:
    """호출 지점에서 넘긴 인자 하나의 성격."""
    kind: str              # default | literal | same_object | fuzzer | variable
    value: str | None = None
    params: set = field(default_factory=set)   # 이 인자 식이 읽는, 호출한 함수의 매개변수 번호들
    member_only: set = field(default_factory=set)  # 그중 p->필드로만 읽는 것 (값이 객체 안 상태에서 옴)


@dataclass
class CallSite:
    caller: str            # 호출하는 함수의 mangled 이름
    callees: list[str]     # 호출되는 함수 후보(mangled). 생성자는 후보가 여러 개일 수 있다
    file: str
    line: int
    col: int
    via_ctor: bool = False
    args: list[Arg] = field(default_factory=list)


@dataclass
class Cond:
    """조건식 하나(if/while/for/?:의 조건, &&·||의 각 피연산자)."""
    file: str
    line: int
    col: int
    end_line: int
    end_col: int
    params: set[int]       # 이 함수의 몇 번째 매개변수를 읽는가
    fields: set[str]       # 어떤 필드("클래스::필드")를 읽는가
    calls: set[str]        # 조건 안에서 부르는 함수(mangled) — 게터 추적용
    member_only: set[int] = field(default_factory=set)  # 값 자체가 아니라 p->필드로만 읽는 매개변수


@dataclass
class FieldWrite:
    """필드에 값을 넣는 곳."""
    writer: str            # 쓰는 함수(mangled)
    params: set[int]       # 쓰는 값이 writer의 몇 번째 매개변수에서 오는가
    kind: str              # init(생성자 초기화) | assign(대입) | addr(주소를 넘겨 간접 설정)
    file: str | None = None
    line: int | None = None


@dataclass
class AstIndex:
    funcs: dict[str, FuncDecl] = field(default_factory=dict)
    records: dict[str, list[str]] = field(default_factory=dict)   # 클래스 -> 부모 클래스들
    record_access: dict[str, str | None] = field(default_factory=dict)  # 중첩 클래스의 접근 지정자
    ctors: dict[str, set[str]] = field(default_factory=dict)      # 클래스 -> 생성자 mangled들
    calls: list[CallSite] = field(default_factory=list)
    conds: dict[str, list[Cond]] = field(default_factory=dict)    # 함수 -> 조건식들
    field_writes: dict[str, list[FieldWrite]] = field(default_factory=dict)
    getters: dict[str, str] = field(default_factory=dict)         # 게터 함수 -> 돌려주는 필드


class _LocState:
    def __init__(self):
        self.file: str | None = None
        self.line: int | None = None

    def bare(self, b: dict | None, end: bool = False):
        """위치 객체 하나를 처리하고 (file, line, col)을 돌려준다. end=True면 토큰 끝 열."""
        if not b:
            return None
        if "spellingLoc" in b or "expansionLoc" in b:
            res = None
            if "spellingLoc" in b:
                self.bare(b["spellingLoc"])
            if "expansionLoc" in b:
                res = self.bare(b["expansionLoc"], end)
            return res
        if "file" in b:
            self.file = b["file"]
        if "line" in b:
            self.line = b["line"]
        if "offset" not in b and "col" not in b:
            return None
        col = b.get("col", 0)
        if end:
            col += max(b.get("tokLen", 1), 1)
        return (self.file, self.line, col)


def _norm_type(qual: str) -> str:
    t = qual.replace("const ", "").replace("struct ", "").replace("class ", "").strip()
    return t.rstrip("*& ").strip()


def _norm_sig(sig: str) -> str:
    return " ".join(sig.replace("tinyxml2::", "").split())


def _strip(n: dict) -> dict:
    while n.get("kind") in WRAPPER_KINDS and n.get("inner"):
        n = n["inner"][0]
    return n


def _find_callee(node: dict) -> str | None:
    """호출식의 callee 부분에서 참조하는 함수 선언 id를 찾는다."""
    stack = [node]
    while stack:
        n = stack.pop(0)
        if n.get("kind") in CALL_KINDS:
            continue
        if "referencedMemberDecl" in n:
            return n["referencedMemberDecl"]
        ref = n.get("referencedDecl")
        if isinstance(ref, dict) and ref.get("kind") in FUNC_KINDS:
            return ref.get("id")
        stack.extend(n.get("inner", []))
    return None


def _subtree(n: dict):
    stack = [n]
    while stack:
        x = stack.pop()
        yield x
        stack.extend(x.get("inner", []))


def _uses_fuzzer(n: dict) -> bool:
    """인자 식 안에 FuzzedDataProvider의 Consume* 호출이 있는가."""
    for x in _subtree(n):
        if x.get("kind") == "MemberExpr" and str(x.get("name", "")).startswith("Consume"):
            return True
    return False


def classify_arg(n: dict) -> Arg:
    """하네스가 넘긴 인자가 고정값인지, 입력에 따라 바뀌는지 판정한다."""
    if n.get("kind") == "CXXDefaultArgExpr":
        return Arg("default")
    s = _strip(n)
    k = s.get("kind")
    if k == "CXXDefaultArgExpr":
        return Arg("default")
    if k in LITERAL_KINDS:
        return Arg("literal", str(s.get("value")))
    if k == "CXXNullPtrLiteralExpr":
        return Arg("literal", "nullptr")
    if k == "GNUNullExpr":
        return Arg("literal", "NULL")
    if k == "UnaryOperator" and s.get("opcode") == "-" and s.get("inner"):
        inner = _strip(s["inner"][0])
        if inner.get("kind") in LITERAL_KINDS:
            return Arg("literal", "-" + str(inner.get("value")))
    if k == "DeclRefExpr":
        ref = s.get("referencedDecl") or {}
        if ref.get("kind") == "EnumConstantDecl":
            return Arg("literal", ref.get("name"))
        qt = (ref.get("type") or {}).get("qualType", "")
        if ref.get("kind") == "VarDecl" and qt.startswith("const ") and "*" not in qt and "&" not in qt:
            return Arg("literal", ref.get("name"))      # 이름 붙은 상수 (예: const unsigned int parse_minimal)
    if k == "UnaryOperator" and s.get("opcode") == "&" and s.get("inner"):
        tgt = _strip(s["inner"][0])
        ref = tgt.get("referencedDecl") or {}
        if tgt.get("kind") == "DeclRefExpr" and ref.get("kind") == "VarDecl":
            return Arg("same_object", "&" + str(ref.get("name")))
    if k == "CXXThisExpr":
        return Arg("same_object", "this")
    if k == "ConditionalOperator" and len(s.get("inner", [])) == 3:
        # cond ? A : B — 조건은 입력으로 바뀌어도 고를 수 있는 값이 A, B뿐이면 '선택지 제한'
        a, b = classify_arg(s["inner"][1]), classify_arg(s["inner"][2])
        if a.kind in ("literal", "same_object", "choice") and b.kind in ("literal", "same_object", "choice"):
            vals = []
            for x in (a, b):
                for v in (x.value or "").split("|"):
                    if v and v not in vals:
                        vals.append(v)
            return Arg("choice", "|".join(vals))
    if _uses_fuzzer(n):
        return Arg("fuzzer")
    return Arg("variable")


def dump_ast(source: str, include_dirs: list[str], extra_flags: list[str] | None = None) -> dict:
    if source.endswith(".c"):   # C 라이브러리·하네스는 C 모드로 분석 (함수 이름이 맹글링되지 않음)
        cmd = ["clang", "-std=gnu11", "-fsyntax-only", "-Xclang", "-ast-dump=json"]
    else:
        cmd = ["clang++", "-std=c++17", "-fsyntax-only", "-Xclang", "-ast-dump=json"]
    for d in include_dirs:
        cmd.append("-I" + os.path.abspath(d))
    cmd += extra_flags or []
    cmd.append(os.path.abspath(source))
    out = subprocess.run(cmd, check=True, capture_output=True).stdout
    return json.loads(out)


def _member_only_params(n: dict, pmap: dict[str, int]) -> set[int]:
    """조건식이 매개변수를 상태 객체로만 쓰는 매개변수: `p->필드`로 읽거나 다른 함수에 그대로 넘길 뿐,
    포인터 값 자체(null 검사·비교)는 보지 않는다. 이런 매개변수는 라이브러리가 상태를 쌓는 객체라서,
    하네스가 '같은 객체'를 넘긴다는 사실이 원인이 아닐 수 있다(다형 객체 여부는 causes.py에서 따로 본다)."""
    def strip(x):
        while x.get("kind") in ("ImplicitCastExpr", "ParenExpr") and x.get("inner"):
            x = x["inner"][0]
        return x
    state_ids, refs = set(), {}
    stack = [n]
    while stack:
        x = stack.pop()
        inner = x.get("inner", [])
        stack.extend(inner)
        k = x.get("kind")
        if (k == "MemberExpr" and inner
                and "bound member function" not in (x.get("type") or {}).get("qualType", "")):  # p->Method()는 제외
            b = strip(inner[0])
            if b.get("kind") == "DeclRefExpr":
                state_ids.add(b.get("id"))
        if k in ("CallExpr",) and len(inner) > 1:          # f(..., p, ...): 인자로 그대로 넘김
            for a in inner[1:]:
                b = strip(a)
                if b.get("kind") == "DeclRefExpr":
                    state_ids.add(b.get("id"))
        ref = x.get("referencedDecl")
        if k == "DeclRefExpr" and isinstance(ref, dict) and ref.get("kind") == "ParmVarDecl" and ref.get("id") in pmap:
            refs.setdefault(pmap[ref["id"]], []).append(x.get("id"))
    return {p for p, ids in refs.items() if ids and all(i in state_ids for i in ids)}


def _cond_children(n: dict) -> list[dict]:
    """조건 역할을 하는 자식 노드들을 돌려준다."""
    k, inner = n.get("kind"), n.get("inner", [])
    if k == "IfStmt":
        i = int(bool(n.get("hasInit"))) + int(bool(n.get("hasVar")))
        return [inner[i]] if len(inner) > i else []
    if k == "WhileStmt":
        i = int(bool(n.get("hasVar")))
        return [inner[i]] if len(inner) > i else []
    if k == "ForStmt":
        # init, condVar, cond, inc, body (없는 부분은 빈 객체)
        return [inner[2]] if len(inner) > 2 and inner[2] else []
    if k == "DoStmt":
        return [inner[1]] if len(inner) > 1 else []
    if k == "ConditionalOperator":
        return [inner[0]] if inner else []
    if k == "BinaryOperator" and n.get("opcode") in ("&&", "||"):
        return list(inner[:2])
    return []


def index_tu(ast: dict, idx: AstIndex) -> None:
    """번역 단위(TU) 하나의 AST를 훑어 idx에 누적한다."""
    loc = _LocState()
    id2mangled: dict[str, str] = {}
    field_ids: dict[str, str] = {}                    # FieldDecl id -> "클래스::필드"
    pending_calls: list[tuple] = []
    pending_conds: list[tuple] = []                  # (func, file, l, c, el, ec, params, member_ids, callee_ids)
    pending_writes: list[tuple] = []                 # (field_id, writer, params, kind, file, line)
    pending_getters: list[tuple] = []                # (func, member_id)
    cond_ids: set[str] = set()
    case_refs: dict[str, tuple] = {}                 # CaseStmt/DefaultStmt id -> switch 조건의 참조들
    var_refs: dict[str, tuple] = {}                  # 지역 변수 id -> 초기값이 읽는 (매개변수, 멤버, 호출)

    def node_pos(n: dict):
        p = loc.bare(n.get("loc"))
        r = n.get("range") or {}
        b = loc.bare(r.get("begin"))
        e = loc.bare(r.get("end"), end=True)
        return p, b, e

    def refs(n: dict, pmap: dict[str, int]):
        """식 안에서 읽는 매개변수 번호, 멤버 id, 부르는 함수 id.
        지역 변수는 그 초기값이 읽는 것으로 한 단계 펼친다 (예: comment = compare->ToComment())."""
        ps, ms, cs = set(), set(), set()
        for x in _subtree(n):
            ref = x.get("referencedDecl")
            if isinstance(ref, dict) and ref.get("kind") == "ParmVarDecl" and ref.get("id") in pmap:
                ps.add(pmap[ref["id"]])
            if isinstance(ref, dict) and ref.get("kind") == "VarDecl" and ref.get("id") in var_refs:
                vp, vm, vc = var_refs[ref["id"]]
                ps |= vp
                ms |= vm
                cs |= vc
            if x.get("kind") == "MemberExpr" and "referencedMemberDecl" in x:
                ms.add(x["referencedMemberDecl"])
            if x.get("kind") in CALL_KINDS and x.get("inner"):
                cid = _find_callee(x["inner"][0])
                if cid:
                    cs.add(cid)
        return ps, ms, cs

    def walk(n: dict, scope: list[str], records: list[str], fstack: list[tuple[str, dict]], access: str | None):
        kind = n.get("kind")
        pos, begin, end = node_pos(n)
        inner = n.get("inner", [])
        func, pmap = fstack[-1] if fstack else ("", {})

        if kind == "NamespaceDecl":
            for c in inner:
                walk(c, scope + [n.get("name", "")], records, fstack, None)
            return

        if kind == "ClassTemplateDecl":
            # 템플릿 껍데기: 안쪽 CXXRecordDecl이 실제 클래스이므로 이름을 한 번 더 붙이지 않는다
            for c in inner:
                walk(c, scope, records, fstack, access)
            return

        if kind in ("CXXRecordDecl", "ClassTemplateSpecializationDecl") and n.get("name"):
            qname = "::".join(scope + [n["name"]])
            if n.get("completeDefinition"):
                bases = [_norm_type(b["type"]["qualType"]) for b in n.get("bases", [])]
                idx.records.setdefault(qname, bases)
            if records:  # 다른 클래스 안에 선언된 중첩 클래스
                idx.record_access.setdefault(qname, n.get("access", access))
            cur = "private" if n.get("tagUsed") == "class" else "public"
            for c in inner:
                if c.get("kind") == "AccessSpecDecl":
                    node_pos(c)
                    cur = c.get("access", cur)
                    continue
                walk(c, scope + [n["name"]], records + [qname], fstack, cur)
            return

        if kind == "FieldDecl" and records:
            field_ids[n["id"]] = f"{records[-1]}::{n.get('name', '')}"

        if kind in FUNC_KINDS:
            mangled = n.get("mangledName") or ""
            id2mangled[n["id"]] = mangled
            record = records[-1] if records and kind != "FunctionDecl" else None
            if record is None and kind != "FunctionDecl" and scope:
                record = "::".join(scope)
            params = [c for c in inner if c.get("kind") == "ParmVarDecl"]
            fd = FuncDecl(
                mangled=mangled,
                name=n.get("name", ""),
                qualname="::".join(scope + [n.get("name", "")]),
                record=record,
                kind=kind,
                sig=(n.get("type") or {}).get("qualType", ""),
                access=n.get("access", access),
                virtual=bool(n.get("virtual")),
                implicit=bool(n.get("isImplicit")),
                deleted=bool(n.get("explicitlyDeleted")),
                pure=bool(n.get("pure")),
                file=pos[0] if pos else None,
                line=pos[1] if pos else None,
                params=[p.get("name", "") for p in params],
                param_types=[(p.get("type") or {}).get("qualType", "") for p in params],
            )
            # 같은 함수의 선언이 여러 번(헤더 선언 + .cpp 정의) 나오면 헤더 쪽 정보를 우선한다
            old = idx.funcs.get(mangled)
            if mangled and (old is None or (old.file and old.file.endswith(".cpp") and fd.file and fd.file.endswith(".h"))):
                if old is not None:
                    fd.access = fd.access or old.access
                    fd.virtual = fd.virtual or old.virtual
                    if not all(fd.params) and len(old.params) == len(fd.params):
                        fd.params = [a or b for a, b in zip(fd.params, old.params)]
                    fd.param_types = fd.param_types or old.param_types
                idx.funcs[mangled] = fd
            elif old is not None:
                old.virtual = old.virtual or fd.virtual
                if not all(old.params) and len(old.params) == len(fd.params):
                    old.params = [a or b for a, b in zip(old.params, fd.params)]
                old.param_types = old.param_types or fd.param_types
            if kind == "CXXConstructorDecl" and record and mangled:
                idx.ctors.setdefault(record, set()).add(mangled)

            new_pmap = {p["id"]: i for i, p in enumerate(params)}
            body = next((c for c in inner if c.get("kind") == "CompoundStmt"), None)
            # 게터: 몸체가 'return 필드;' 한 줄이고 매개변수를 읽지 않음
            if body and len(body.get("inner", [])) == 1 and body["inner"][0].get("kind") == "ReturnStmt":
                ps, ms, cs = refs(body["inner"][0], new_pmap)
                if len(ms) == 1 and not ps and not cs:
                    pending_getters.append((mangled, next(iter(ms))))
            for c in inner:
                walk(c, scope, records, fstack + [(mangled, new_pmap)], access)
            return

        # ---- 함수 몸체 안 ----
        if func:
            if n.get("id") in cond_ids and begin and end:
                ps, ms, cs = refs(n, pmap)
                pending_conds.append((func, begin[0], begin[1], begin[2], end[1], end[2], ps, ms, cs,
                                      _member_only_params(n, pmap)))

            if n.get("id") in case_refs and begin and end:
                ps, ms, cs, mo = case_refs[n["id"]]
                pending_conds.append((func, begin[0], begin[1], begin[2], end[1], end[2], ps, ms, cs, mo))

            for c in _cond_children(n):
                if c.get("id"):
                    cond_ids.add(c["id"])

            if kind == "SwitchStmt":
                # switch의 각 case/default 분기는 switch 조건과 같은 값에 달려 있다
                i = int(bool(n.get("hasInit"))) + int(bool(n.get("hasVar")))
                if len(inner) > i:
                    r = (*refs(inner[i], pmap), _member_only_params(inner[i], pmap))
                    stack = list(inner[i + 1:])
                    while stack:
                        x = stack.pop()
                        if x.get("kind") == "SwitchStmt":
                            continue                       # 안쪽 switch의 case는 제외
                        if x.get("kind") in ("CaseStmt", "DefaultStmt") and x.get("id"):
                            case_refs[x["id"]] = r
                        stack.extend(x.get("inner", []))

            if kind == "VarDecl" and inner and n.get("id"):
                init = _strip(inner[-1])
                if init.get("kind") == "CXXMemberCallExpr" and init.get("inner"):
                    # obj->Method(args)의 결과는 주로 obj의 상태에 달려 있다 → 호출 대상 객체만 따라간다
                    callee = init["inner"][0]
                    ps, ms, cs = refs({"inner": callee.get("inner", [])}, pmap)
                    cid = _find_callee(callee)
                    var_refs[n["id"]] = (ps, ms, cs | ({cid} if cid else set()))
                else:
                    var_refs[n["id"]] = refs({"inner": inner}, pmap)

            if kind == "CXXCtorInitializer":
                init = n.get("anyInit") or {}
                if init.get("kind") == "FieldDecl":
                    ps, _, _ = refs(n, pmap)
                    pending_writes.append((init.get("id"), func, ps, "init",
                                           begin[0] if begin else None, begin[1] if begin else None))

            if (kind == "BinaryOperator" and n.get("opcode") == "=") or kind == "CompoundAssignOperator":
                if len(inner) >= 2:
                    lhs = _strip(inner[0])
                    if lhs.get("kind") == "MemberExpr" and "referencedMemberDecl" in lhs:
                        ps, _, _ = refs(inner[1], pmap)
                        pending_writes.append((lhs["referencedMemberDecl"], func, ps, "assign",
                                               begin[0] if begin else None, begin[1] if begin else None))

            if kind in CALL_KINDS and begin:
                callee_id = _find_callee(inner[0]) if inner else None
                args = [] if kind == "CXXOperatorCallExpr" else [classify_arg(a) for a in inner[1:]]
                if kind != "CXXOperatorCallExpr":
                    for a, node in zip(args, inner[1:]):
                        a.params = set(refs(node, pmap)[0])
                        a.member_only = _member_only_params(node, pmap) & a.params
                pending_calls.append((func, callee_id, begin, False, None, None, args))
                # 필드 주소를 넘기는 호출: 그 함수가 필드를 간접적으로 설정할 수 있음
                for a in inner[1:]:
                    s = _strip(a)
                    if s.get("kind") == "UnaryOperator" and s.get("opcode") == "&" and s.get("inner"):
                        t = _strip(s["inner"][0])
                        if t.get("kind") == "MemberExpr" and "referencedMemberDecl" in t:
                            pending_writes.append((t["referencedMemberDecl"], func, set(), "addr",
                                                   begin[0], begin[1]))
            elif kind in CTOR_KINDS and begin:
                rec = _norm_type((n.get("type") or {}).get("desugaredQualType")
                                 or (n.get("type") or {}).get("qualType", ""))
                csig = (n.get("ctorType") or {}).get("qualType", "")
                args = [classify_arg(a) for a in inner]
                for a, node in zip(args, inner):
                    a.params = set(refs(node, pmap)[0])
                    a.member_only = _member_only_params(node, pmap) & a.params
                pending_calls.append((func, None, begin, True, rec, csig, args))

        for c in inner:
            walk(c, scope, records, fstack, access)

    walk(ast, [], [], [], None)

    # ---- TU 단위로 id 를 전역 키로 바꾼다 ----
    def fkey(mid):
        return field_ids.get(mid)

    for func, callee_id, (f, line, col), is_ctor, rec, csig, args in pending_calls:
        if not f or not line:
            continue
        if is_ctor:
            cands = sorted(idx.ctors.get(rec, set()))
            if not cands and rec and "::" not in rec:   # 짧게 적힌 클래스 이름
                cands = sorted(next((v for k, v in idx.ctors.items() if k.endswith("::" + rec)), set()))
            exact = [c for c in cands if _norm_sig(idx.funcs[c].sig) == _norm_sig(csig)] if csig else []
            callees = exact or cands
            if not callees:
                continue
        else:
            m = id2mangled.get(callee_id or "")
            if not m:
                continue
            callees = [m]
        idx.calls.append(CallSite(func, callees, os.path.abspath(f), line, col or 0, is_ctor, args))

    for func, f, l, c, el, ec, ps, ms, cs, mo in pending_conds:
        if not f:
            continue
        cond = Cond(os.path.abspath(f), l, c, el or l, ec or c, set(ps),
                    {fkey(m) for m in ms if fkey(m)},
                    {id2mangled[x] for x in cs if id2mangled.get(x)}, set(mo) & set(ps))
        lst = idx.conds.setdefault(func, [])
        if not any((x.file, x.line, x.col) == (cond.file, cond.line, cond.col) for x in lst):
            lst.append(cond)

    for mid, writer, ps, kind, f, line in pending_writes:
        k = fkey(mid)
        if not k or not writer:
            continue
        w = FieldWrite(writer, set(ps), kind, os.path.abspath(f) if f else None, line)
        lst = idx.field_writes.setdefault(k, [])
        if not any((x.writer, x.kind, x.line) == (w.writer, w.kind, w.line) for x in lst):
            lst.append(w)

    for func, mid in pending_getters:
        k = fkey(mid)
        if k and func:
            idx.getters[func] = k


def build_index(sources: list[str], include_dirs: list[str], defines: list[str] | None = None) -> AstIndex:
    """defines: 빌드와 같은 전처리 옵션(-DNAME=값). 설정 헤더가 필요한 라이브러리(expat 등)에 씀."""
    idx = AstIndex()
    for s in sources:
        index_tu(dump_ast(s, include_dirs, defines), idx)
    # 위치를 절대 경로로 통일
    for fd in idx.funcs.values():
        if fd.file:
            fd.file = os.path.abspath(fd.file)
    return idx
