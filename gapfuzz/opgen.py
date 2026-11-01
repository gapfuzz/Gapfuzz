"""'호출 안 함' 공개 API의 우선순위와 스테이트풀 하네스용 연산 코드 초안 생성 (TinyXML2용).

1) 우선순위: API에서 호출 그래프를 따라 닿는 '아직 한 번도 실행되지 않은 함수'들의 코드 영역 수.
   하네스가 이 API를 부르면 새로 실행될 수 있는 코드의 양에 대한 어림값이다.
2) 연산 초안: 시그니처의 타입 정보만으로 FuzzedDataProvider 인자를 채운 `case` 블록.
   하네스가 스스로 API를 잘못 써서 가짜 크래시를 내지 않도록 가드레일을 생성 단계에 넣는다.
     - 노드를 받는 인자: 기존 노드를 넣으면 순환 구조가 생길 수 있으므로 새로 만든 노드만 넘긴다
       (const 노드 인자, 즉 조회용은 현재 커서를 넘긴다)
     - 문자열 인자: null을 넘기지 않는다 (null 처리는 원인 추적의 '범위를 좁힘' 제안이 따로 다룬다).
       전역 상태를 바꾸는 Set 계열은 포인터를 저장할 수 있으므로 끝까지 살아 있는 문자열 상수만 넘긴다
     - 크기 인자: 0~64로 제한해 거대한 할당으로 인한 리소스 크래시를 막는다
     - 파일 입출력(FILE*, 파일 이름), 방문자 콜백, 연산자 오버로드, 템플릿은 생성하지 않고 이유를 남긴다
생성한 코드는 초안이다. 하네스에 넣기 전에 사람이 읽고, 크래시가 나면 크래시 귀속으로 하네스 탓인지 확인한다.
"""
from __future__ import annotations

import re
from collections import deque

from .analyze import Analyzer, _code_regions

INT_TYPES = {"int", "unsigned int", "unsigned", "int64_t", "uint64_t", "long", "long long",
             "unsigned long", "unsigned long long", "short", "unsigned short"}
FLOAT_TYPES = {"float", "double"}
OUT_PTR = {"int *": "int", "unsigned int *": "unsigned int", "int64_t *": "int64_t", "uint64_t *": "uint64_t",
           "bool *": "bool", "float *": "float", "double *": "double", "const char **": "const char *"}
# 받는 쪽(receiver) 클래스 → 그 객체를 얻는 코드와 이름
RECEIVERS = {
    "XMLDocument": (None, "doc."),
    "XMLNode": (None, "cur->"),
    "XMLElement": ("XMLElement *r = cur->ToElement()", "r->"),
    "XMLText": ("XMLText *r = cur->ToText()", "r->"),
    "XMLComment": ("XMLComment *r = cur->ToComment()", "r->"),
    "XMLDeclaration": ("XMLDeclaration *r = cur->ToDeclaration()", "r->"),
    "XMLUnknown": ("XMLUnknown *r = cur->ToUnknown()", "r->"),
    "XMLAttribute": ("XMLAttribute *r = ele ? const_cast<XMLAttribute *>(ele->FirstAttribute()) : nullptr", "r->"),
    "XMLHandle": ("XMLHandle r(cur); (void)0", "r."),
    "XMLConstHandle": ("XMLConstHandle r(cur); (void)0", "r."),
    "XMLPrinter": ("XMLPrinter r(nullptr, fdp.ConsumeBool()); (void)0", "r."),
    "XMLUtil": (None, "XMLUtil::"),
}
NEW_NODE = {"XMLNode": "doc.NewElement(str)", "XMLElement": "doc.NewElement(str)", "XMLText": "doc.NewText(str)",
            "XMLComment": "doc.NewComment(str)", "XMLUnknown": "doc.NewUnknown(str)",
            "XMLDeclaration": "doc.NewDeclaration(str)"}
CUR_NODE = {"XMLNode": "cur", "XMLElement": "ele", "XMLText": "cur->ToText()", "XMLComment": "cur->ToComment()",
            "XMLUnknown": "cur->ToUnknown()", "XMLDeclaration": "cur->ToDeclaration()", "XMLDocument": "&doc"}
FILE_NAMES = re.compile(r"File|filename|filepath", re.I)


def _norm(t: str, ns: str) -> str:
    t = t.replace(ns + "::", "").replace("struct ", "").replace("class ", "")
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"\s*\*", " *", t).replace("* *", "**").replace(" **", " **")


class OpGen:
    def __init__(self, an: Analyzer, ns: str = "tinyxml2"):
        self.an = an
        self.ns = ns
        self.fwd: dict[str, set[str]] = {}
        for cs in an.idx.calls:
            for c in cs.callees:
                self.fwd.setdefault(cs.caller, set()).add(c)
                for base in an._virtual_alias.get(c, []):
                    self.fwd[cs.caller].add(base)

    def potential(self, m: str) -> tuple[int, int]:
        """(새로 실행될 수 있는 함수 수, 그 함수들의 코드 영역 수)."""
        seen, q = {m}, deque([m])
        while q:
            cur = q.popleft()
            for c in self.fwd.get(cur, ()):
                if c not in seen and c in self.an.idx.funcs and not self.an._executed(c):
                    seen.add(c)
                    q.append(c)
        regions = sum(len(_code_regions(self.an.cov[f])) for f in seen if f in self.an.cov)
        return len(seen), regions

    # ------------------------------------------------------------------ 인자
    def _arg(self, t: str, name: str, i: int, pre: list[str], stable: bool = False) -> str | None:
        n = _norm(t, self.ns)
        base = n.replace("const ", "").replace(" *", "").replace(" &", "").strip()
        if n in INT_TYPES:
            return f"fdp.ConsumeIntegral<{n}>()"
        if n == "size_t":
            return "fdp.ConsumeIntegralInRange<size_t>(0, 64)"
        if n == "bool":
            return "fdp.ConsumeBool()"
        if n in FLOAT_TYPES:
            return f"fdp.ConsumeFloatingPoint<{n}>()"
        if n == "const char *":
            if stable:
                # 포인터를 저장할 수 있는 API(전역 설정 등): 반복마다 사라지는 str 대신 끝까지 살아 있는 상수
                pre.append(f'static const char *const keep{i}[] = {{"true", "false", "1", "0", "yes", ""}};')
                return f"keep{i}[s.size() % 6]"
            return "str"
        if n == "char *":
            pre.append(f"char buf{i}[64] = {{0}};")
            return f"buf{i}"
        if n in OUT_PTR:
            pre.append(f"{OUT_PTR[n]} out{i}{{}};")
            return f"&out{i}"
        if n in ("XMLDocument *", "XMLDocument &"):
            return "&other" if n.endswith("*") else "other"
        if n in ("XMLVisitor *", "XMLPrinter *"):
            pre.append(f"XMLPrinter vis{i}(nullptr, fdp.ConsumeBool());")
            return f"&vis{i}"
        if n.endswith(" *") and base in NEW_NODE:
            if n.startswith("const "):
                return CUR_NODE.get(base)            # 조회용: 현재 커서
            return NEW_NODE[base]                    # 변경용: 항상 새로 만든 노드 (기존 노드를 넣어 순환이 생기는 것 방지)
        if n.endswith(" &") and base in CUR_NODE and n.startswith("const "):
            return None                              # 방문자 콜백용 참조 인자: 생성하지 않음
        if " " not in n and n[:1].isupper() and f"{self.ns}::{n}" not in self.an.idx.records:
            return f"static_cast<{n}>(fdp.ConsumeIntegralInRange<int>(0, 3))"   # 열거형으로 보고 작은 범위
        return None

    def make(self, m: str) -> tuple[str | None, str]:
        fd = self.an.idx.funcs[m]
        cls = (fd.record or "").replace(self.ns + "::", "")
        name = fd.name
        if name.startswith("operator") or "<" in fd.sig:
            return None, "연산자·템플릿"
        if any("FILE" in t for t in fd.param_types) or FILE_NAMES.search(name):
            return None, "파일 입출력"
        if cls.startswith("XMLVisitor"):
            return None, "방문자 콜백 (방문자 클래스를 직접 만들어야 함)"
        pre: list[str] = []
        args = []
        for i, (t, pn) in enumerate(zip(fd.param_types, fd.params)):
            # 전역·정적 상태를 바꾸는 Set 계열(예: XMLUtil::SetBoolSerialization)은 넘긴 포인터를 저장할 수 있다
            stable = cls == "XMLUtil" and name.startswith("Set")
            a = self._arg(t, pn, i, pre, stable)
            if a is None:
                return None, f"인자 타입 `{_norm(t, self.ns)}`를 자동으로 채울 수 없음"
            args.append(a)
        if fd.kind == "CXXConstructorDecl":
            if cls not in ("XMLPrinter", "XMLHandle", "XMLConstHandle", "XMLDocument"):
                return None, "생성자 (직접 만들 수 없는 클래스)"
            call = f"{{ {cls} obj({', '.join(args)}); }}"
            guard = None
        else:
            if cls not in RECEIVERS:
                return None, f"`{cls}` 객체를 얻는 방법을 모름"
            guard, recv = RECEIVERS[cls]
            call = f"{recv}{name}({', '.join(args)});"
        body = pre + ([f"if ({guard}) {call}" if guard and not guard.endswith("(void)0") else
                       (f"{guard.replace('; (void)0', ';')} {call}" if guard else call)])
        return "\n".join(body), ""

    def generate(self, results: list[dict], start: int, top: int) -> tuple[str, list[dict]]:
        rows = []
        for r in results:
            if r["category"] != "NOT_CALLED":
                continue
            fns, regs = self.potential(r["mangled"])
            code, why = self.make(r["mangled"])
            rows.append({"api": r["api"], "mangled": r["mangled"], "functions": fns, "regions": regs,
                         "code": code, "skip": why})
        rows.sort(key=lambda x: (-x["regions"], x["api"]))
        chosen = [x for x in rows if x["code"]][:top]
        out = []
        for k, x in enumerate(chosen):
            body = "\n".join("            " + l for l in x["code"].splitlines())
            out.append(f"        case {start + k}: {{  // [자동 생성] {x['api']} — 새로 실행될 수 있는 코드 영역 {x['regions']}개\n"
                       f"{body}\n            break;\n        }}")
        return "\n".join(out), rows
