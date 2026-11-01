// [gapfuzz ops] stateful_v3.cpp에 '호출 안 함' API 15개의 연산을 자동으로 추가한 버전.
// 우선순위: 그 API로 새로 실행될 수 있는 코드 영역 수. 생성 규칙은 gapfuzz/opgen.py 참고.
// TinyXML2 스테이트풀 하네스 v3
//
// stateful_v2.cpp에 gapfuzz의 '값의 범위를 좁힘' 제안 4개를 추가로 적용한 버전.
//   [좁힘 1] XMLDocument 공백 처리 모드를 2가지 중에서만 고름 → 3가지(PEDANTIC 포함) 중에서 고름
//   [좁힘 2] Parse의 xml에 null을 넘긴 적 없음                → nullptr도 넘김
//   [좁힘 3] DeleteNode에 null을 넘긴 적 없음                  → nullptr도 넘김
//   [좁힘 4] XMLConstHandle에 null을 넘긴 적 없음              → nullptr도 넘김
//
// 아래는 v2의 설명이다.
//
// stateful.cpp에 gapfuzz의 '하네스에서 고칠 곳' 제안을 적용한 버전. [제안 N] 주석이 바뀐 곳이다.
//   [제안 1] ShallowClone에 항상 &doc만 넘김       → nullptr도 넘김
//   [제안 2] Accept에 항상 같은 출력기만 넘김       → 방문을 중단하는(false를 돌려주는) 방문자도 넘김
//   [제안 3] Parse의 nBytes가 항상 기본값           → 입력 길이 이하의 값을 넘김(0 포함)
//   [제안 5] XMLHandle에 항상 &doc만 넘김          → nullptr도 넘김
//   [제안 6] XMLPrinter의 4번째 인자가 항상 기본값  → 퍼저 입력으로 고름
//   [제안 7] SetBOM을 부르지 않음                  → 출력 전에 호출
//   [제안 4] Print(nullptr)는 표준 출력으로 찍어 퍼징 로그를 어지럽히므로 적용하지 않았다.
//
// 입력 구조
//   [앞부분]  XML 문자열 → doc.Parse()
//   [나머지]  연산 번호 + 인자들 → 트리 조작 연산을 최대 kMaxOps번 실행
//
// 하네스가 스스로 오사용을 만들지 않도록 지키는 규칙(가드레일)
//   - 커서(cur)는 항상 doc 트리 안의 살아 있는 노드를 가리킨다
//   - 삭제는 cur의 '자식'만 대상으로 한다(cur 자신·조상은 삭제하지 않음)
//   - 기존 노드를 옮길 때는 cur의 자식만 옮긴다(조상을 자손 아래로 넣어 순환이 생기는 것 방지)
//   - 연산 횟수와 문자열 길이에 상한을 둔다
#include "tinyxml2.h"
#include <fuzzer/FuzzedDataProvider.h>

#include <cstdint>
#include <string>

using namespace tinyxml2;

namespace {

constexpr int kMaxOps = 64;
constexpr size_t kMaxStr = 64;

XMLNode *NthChild(XMLNode *parent, unsigned n) {
    XMLNode *c = parent->FirstChild();
    for (unsigned i = 0; c && i < n; ++i) c = c->NextSibling();
    return c;
}

unsigned ChildCount(const XMLNode *parent) {
    unsigned n = 0;
    for (const XMLNode *c = parent->FirstChild(); c; c = c->NextSibling()) ++n;
    return n;
}

// [제안 2] 방문 결과를 입력으로 정하는 방문자: false를 돌려주면 TinyXML2가 순회를 중단한다
class StopVisitor : public XMLVisitor {
public:
    explicit StopVisitor(uint8_t mask) : mask_(mask) {}
    bool VisitEnter(const XMLDocument &) override { return mask_ & 1; }
    bool VisitExit(const XMLDocument &) override { return mask_ & 2; }
    bool VisitEnter(const XMLElement &, const XMLAttribute *) override { return mask_ & 4; }
    bool VisitExit(const XMLElement &) override { return mask_ & 8; }
    bool Visit(const XMLDeclaration &) override { return mask_ & 16; }
    bool Visit(const XMLText &) override { return mask_ & 32; }
    bool Visit(const XMLComment &) override { return mask_ & 64; }
    bool Visit(const XMLUnknown &) override { return mask_ & 128; }
private:
    uint8_t mask_;
};

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    FuzzedDataProvider fdp(data, size);

    static const Whitespace kModes[] = {PRESERVE_WHITESPACE, COLLAPSE_WHITESPACE, PEDANTIC_WHITESPACE};
    XMLDocument doc(fdp.ConsumeBool(), kModes[fdp.ConsumeIntegralInRange<int>(0, 2)]);   // [좁힘 1]
    std::string xml = fdp.ConsumeRandomLengthString(4096);
    // [제안 3] nBytes: 기본값(-1, 문자열 끝까지) 또는 입력 길이 이하의 값(0 포함)
    if (fdp.ConsumeBool()) doc.Parse(fdp.ConsumeIntegralInRange<int>(0, 15) ? xml.c_str() : nullptr);   // [좁힘 2]
    else doc.Parse(xml.c_str(), fdp.ConsumeIntegralInRange<size_t>(0, xml.size()));

    XMLDocument other;          // DeepClone / 다른 문서 간 동작 확인용
    XMLNode *cur = &doc;

    for (int i = 0; i < kMaxOps && fdp.remaining_bytes() > 0; ++i) {
        std::string s = fdp.ConsumeRandomLengthString(kMaxStr);
        const char *str = s.c_str();
        XMLElement *ele = cur->ToElement();
        const unsigned nchild = ChildCount(cur);

        switch (fdp.ConsumeIntegralInRange<int>(0, 36)) {
        case 0:  // 새 요소를 끝에 추가
            cur->InsertEndChild(doc.NewElement(str));
            break;
        case 1:  // 다른 종류의 노드를 앞에 추가
            switch (fdp.ConsumeIntegralInRange<int>(0, 3)) {
            case 0: cur->InsertFirstChild(doc.NewText(str)); break;
            case 1: cur->InsertFirstChild(doc.NewComment(str)); break;
            case 2: cur->InsertFirstChild(doc.NewUnknown(str)); break;
            default: cur->InsertFirstChild(doc.NewDeclaration(s.empty() ? nullptr : str)); break;
            }
            break;
        case 2:  // 자식 뒤에 끼워 넣기
            if (XMLNode *after = NthChild(cur, fdp.ConsumeIntegralInRange<unsigned>(0, nchild)))
                cur->InsertAfterChild(after, doc.NewElement(str));
            break;
        case 3:  // 기존 자식을 다른 위치로 옮기기 (Unlink 경로)
            if (XMLNode *c = NthChild(cur, fdp.ConsumeIntegralInRange<unsigned>(0, nchild))) {
                if (fdp.ConsumeBool()) cur->InsertEndChild(c);
                else cur->InsertFirstChild(c);
            }
            break;
        case 4: {  // 커서 이동
            XMLNode *next = nullptr;
            switch (fdp.ConsumeIntegralInRange<int>(0, 5)) {
            case 0: next = cur->FirstChild(); break;
            case 1: next = cur->LastChild(); break;
            case 2: next = cur->NextSibling(); break;
            case 3: next = cur->PreviousSibling(); break;
            case 4: next = cur->Parent(); break;
            default: next = cur->FirstChildElement(fdp.ConsumeBool() ? str : nullptr); break;
            }
            cur = next ? next : &doc;
            break;
        }
        case 5:  // 속성 설정
            if (ele) {
                switch (fdp.ConsumeIntegralInRange<int>(0, 5)) {
                case 0: ele->SetAttribute(str, fdp.ConsumeRandomLengthString(kMaxStr).c_str()); break;
                case 1: ele->SetAttribute(str, fdp.ConsumeIntegral<int>()); break;
                case 2: ele->SetAttribute(str, fdp.ConsumeIntegral<int64_t>()); break;
                case 3: ele->SetAttribute(str, fdp.ConsumeBool()); break;
                case 4: ele->SetAttribute(str, fdp.ConsumeFloatingPoint<double>()); break;
                default: ele->SetAttribute(str, fdp.ConsumeIntegral<unsigned>()); break;
                }
            }
            break;
        case 6:  // 속성 조회
            if (ele) {
                int iv; unsigned uv; int64_t lv; bool bv; double dv; float fv;
                ele->QueryIntAttribute(str, &iv);
                ele->QueryUnsignedAttribute(str, &uv);
                ele->QueryInt64Attribute(str, &lv);
                ele->QueryBoolAttribute(str, &bv);
                ele->QueryDoubleAttribute(str, &dv);
                ele->QueryFloatAttribute(str, &fv);
                ele->Attribute(str, fdp.ConsumeBool() ? fdp.ConsumeRandomLengthString(kMaxStr).c_str() : nullptr);
                ele->IntAttribute(str, 7);
                ele->BoolAttribute(str, true);
                for (const XMLAttribute *a = ele->FirstAttribute(); a; a = a->Next()) {
                    a->IntValue(); a->BoolValue(); a->DoubleValue(); a->Int64Value(); a->UnsignedValue();
                }
            }
            break;
        case 7:  // 속성 삭제
            if (ele) {
                if (fdp.ConsumeBool()) ele->DeleteAttribute(str);
                else if (const XMLAttribute *a = ele->FirstAttribute()) ele->DeleteAttribute(a->Name());
            }
            break;
        case 8:  // 텍스트 설정
            if (ele) {
                switch (fdp.ConsumeIntegralInRange<int>(0, 4)) {
                case 0: ele->SetText(str); break;
                case 1: ele->SetText(fdp.ConsumeIntegral<int>()); break;
                case 2: ele->SetText(fdp.ConsumeBool()); break;
                case 3: ele->SetText(fdp.ConsumeFloatingPoint<double>()); break;
                default: ele->SetText(fdp.ConsumeIntegral<uint64_t>()); break;
                }
            }
            break;
        case 9:  // 텍스트 조회
            if (ele) {
                int iv; bool bv; double dv; int64_t lv;
                ele->GetText();
                ele->QueryIntText(&iv);
                ele->QueryBoolText(&bv);
                ele->QueryDoubleText(&dv);
                ele->QueryInt64Text(&lv);
                ele->IntText(1);
            }
            break;
        case 10:  // 자식 하나 삭제 (cur 자신·조상은 건드리지 않음)
            if (XMLNode *c = NthChild(cur, fdp.ConsumeIntegralInRange<unsigned>(0, nchild))) {
                if (fdp.ConsumeBool()) cur->DeleteChild(c);
                else doc.DeleteNode(fdp.ConsumeIntegralInRange<int>(0, 7) ? c : nullptr);   // [좁힘 3]
            }
            break;
        case 11:  // 자식 전부 삭제
            cur->DeleteChildren();
            break;
        case 12: {  // 복제
            if (fdp.ConsumeBool()) {
                XMLNode *clone = cur->DeepClone(&other);
                if (clone) other.InsertEndChild(clone);
            } else if (cur != &doc) {
                // [제안 1] nullptr를 넘기면 원래 노드의 문서를 쓴다
                XMLNode *clone = cur->ShallowClone(fdp.ConsumeBool() ? &doc : nullptr);
                if (clone) {
                    clone->ShallowEqual(cur);
                    if (XMLNode *p = cur->Parent()) p->InsertEndChild(clone);
                }
            }
            break;
        }
        case 13: {  // 출력
            // [제안 6] 4번째 인자(아포스트로피 이스케이프)를 입력으로 고름
            const bool compact = fdp.ConsumeBool();
            const int depth = fdp.ConsumeIntegralInRange<int>(0, 4);
            XMLPrinter printer(nullptr, compact, depth,
                               fdp.ConsumeBool() ? XMLPrinter::ESCAPE_APOS_CHARS_IN_ATTRIBUTES
                                                 : XMLPrinter::DONT_ESCAPE_APOS_CHARS_IN_ATTRIBUTES);
            doc.SetBOM(fdp.ConsumeBool());     // [제안 7]
            switch (fdp.ConsumeIntegralInRange<int>(0, 2)) {
            case 0: doc.Print(&printer); break;
            case 1: cur->Accept(&printer); break;
            default: {                        // [제안 2] 중간에 방문을 멈추는 방문자
                StopVisitor stop(fdp.ConsumeIntegral<uint8_t>());
                cur->Accept(&stop);
                break;
            }
            }
            printer.CStr();
            printer.CStrSize();
            break;
        }
        case 14: {  // XMLPrinter 직접 사용
            XMLPrinter printer(nullptr, fdp.ConsumeBool());
            printer.PushHeader(fdp.ConsumeBool(), fdp.ConsumeBool());
            printer.OpenElement(str, fdp.ConsumeBool());
            printer.PushAttribute("a", fdp.ConsumeIntegral<int>());
            printer.PushText(fdp.ConsumeRandomLengthString(kMaxStr).c_str(), fdp.ConsumeBool());
            printer.PushComment(str);
            printer.CloseElement(fdp.ConsumeBool());
            break;
        }
        case 15: {  // 핸들 탐색
            XMLHandle h(fdp.ConsumeBool() ? static_cast<XMLNode *>(&doc) : nullptr);   // [제안 5]
            h.FirstChildElement(fdp.ConsumeBool() ? str : nullptr).FirstChild().NextSiblingElement().ToElement();
            XMLConstHandle ch(fdp.ConsumeBool() ? static_cast<const XMLNode *>(cur) : nullptr);   // [좁힘 4]
            ch.LastChildElement().PreviousSibling().ToNode();
            break;
        }
        case 16:  // 이름으로 형제·자식 요소 찾기
            if (XMLElement *e = cur->FirstChildElement()) {
                e->NextSiblingElement(fdp.ConsumeBool() ? str : nullptr);
                e->PreviousSiblingElement(str);
                cur->LastChildElement(str);
            }
            break;
        case 17:  // 에러 상태 조회
            doc.Error();
            doc.ErrorID();
            doc.ErrorStr();
            doc.ErrorName();
            doc.ErrorLineNum();
            XMLDocument::ErrorIDToName(static_cast<XMLError>(fdp.ConsumeIntegralInRange<int>(0, XML_ERROR_COUNT - 1)));
            if (fdp.ConsumeBool()) doc.ClearError();
            break;
        case 18:  // 값 바꾸기
            // staticMem=true면 TinyXML2는 문자열을 복사하지 않고 포인터만 저장한다(SetInternedStr).
            // 반복마다 사라지는 s를 넘기면 해제된 메모리를 가리키게 되므로(하네스 버그),
            // 이 경우에는 프로그램 끝까지 살아 있는 정적 문자열만 넘긴다.
            if (cur != &doc) {
                static const char *const kStatic[] = {"a", "item", "ns:tag", "", "x y"};
                const bool staticMem = fdp.ConsumeBool();
                cur->SetValue(staticMem ? kStatic[s.size() % 5] : str, staticMem);
            }
            break;
        case 19:  // 편의 함수로 자식 만들기
            if (ele) {
                switch (fdp.ConsumeIntegralInRange<int>(0, 3)) {
                case 0: ele->InsertNewChildElement(str); break;
                case 1: ele->InsertNewText(str); break;
                case 2: ele->InsertNewComment(str); break;
                default: ele->InsertNewUnknown(str); break;
                }
            }
            break;
        case 20:  // 문서 비우고 다시 파싱
            doc.Clear();
            cur = &doc;
            if (fdp.ConsumeBool()) doc.Parse(str);
            break;
        case 22: {  // [자동 생성] XMLElement::Unsigned64Text(uint64_t) const — 새로 실행될 수 있는 코드 영역 18개
            if (XMLElement *r = cur->ToElement()) r->Unsigned64Text(fdp.ConsumeIntegral<uint64_t>());
            break;
        }
        case 23: {  // [자동 생성] XMLElement::QueryAttribute(const char *, uint64_t *) const — 새로 실행될 수 있는 코드 영역 17개
            uint64_t out1{};
            if (XMLElement *r = cur->ToElement()) r->QueryAttribute(str, &out1);
            break;
        }
        case 24: {  // [자동 생성] XMLElement::QueryUnsigned64Text(uint64_t *) const — 새로 실행될 수 있는 코드 영역 17개
            uint64_t out0{};
            if (XMLElement *r = cur->ToElement()) r->QueryUnsigned64Text(&out0);
            break;
        }
        case 25: {  // [자동 생성] XMLElement::Unsigned64Attribute(const char *, uint64_t) const — 새로 실행될 수 있는 코드 영역 17개
            if (XMLElement *r = cur->ToElement()) r->Unsigned64Attribute(str, fdp.ConsumeIntegral<uint64_t>());
            break;
        }
        case 26: {  // [자동 생성] XMLElement::QueryUnsigned64Attribute(const char *, uint64_t *) const — 새로 실행될 수 있는 코드 영역 16개
            uint64_t out1{};
            if (XMLElement *r = cur->ToElement()) r->QueryUnsigned64Attribute(str, &out1);
            break;
        }
        case 27: {  // [자동 생성] XMLAttribute::Unsigned64Value() const — 새로 실행될 수 있는 코드 영역 13개
            if (XMLAttribute *r = ele ? const_cast<XMLAttribute *>(ele->FirstAttribute()) : nullptr) r->Unsigned64Value();
            break;
        }
        case 28: {  // [자동 생성] XMLAttribute::QueryUnsigned64Value(uint64_t *) const — 새로 실행될 수 있는 코드 영역 12개
            uint64_t out0{};
            if (XMLAttribute *r = ele ? const_cast<XMLAttribute *>(ele->FirstAttribute()) : nullptr) r->QueryUnsigned64Value(&out0);
            break;
        }
        case 29: {  // [자동 생성] XMLDocument::DeepCopy(XMLDocument *) const — 새로 실행될 수 있는 코드 영역 10개
            doc.DeepCopy(&other);
            break;
        }
        case 30: {  // [자동 생성] XMLElement::FloatText(float) const — 새로 실행될 수 있는 코드 영역 10개
            if (XMLElement *r = cur->ToElement()) r->FloatText(fdp.ConsumeFloatingPoint<float>());
            break;
        }
        case 31: {  // [자동 생성] XMLElement::UnsignedText(unsigned int) const — 새로 실행될 수 있는 코드 영역 10개
            if (XMLElement *r = cur->ToElement()) r->UnsignedText(fdp.ConsumeIntegral<unsigned int>());
            break;
        }
        case 32: {  // [자동 생성] XMLElement::QueryFloatText(float *) const — 새로 실행될 수 있는 코드 영역 9개
            float out0{};
            if (XMLElement *r = cur->ToElement()) r->QueryFloatText(&out0);
            break;
        }
        case 33: {  // [자동 생성] XMLElement::QueryUnsignedText(unsigned int *) const — 새로 실행될 수 있는 코드 영역 9개
            unsigned int out0{};
            if (XMLElement *r = cur->ToElement()) r->QueryUnsignedText(&out0);
            break;
        }
        case 34: {  // [자동 생성] XMLUtil::ToUnsigned64(const char *, uint64_t *) — 새로 실행될 수 있는 코드 영역 8개
            uint64_t out1{};
            XMLUtil::ToUnsigned64(str, &out1);
            break;
        }
        case 35: {  // [자동 생성] XMLUtil::SetBoolSerialization(const char *, const char *) — 새로 실행될 수 있는 코드 영역 7개
            static const char *const keep0[] = {"true", "false", "1", "0", "yes", ""};
            static const char *const keep1[] = {"true", "false", "1", "0", "yes", ""};
            XMLUtil::SetBoolSerialization(keep0[s.size() % 6], keep1[s.size() % 6]);
            break;
        }
        case 36: {  // [자동 생성] XMLElement::InsertNewDeclaration(const char *) — 새로 실행될 수 있는 코드 영역 4개
            if (XMLElement *r = cur->ToElement()) r->InsertNewDeclaration(str);
            break;
        }
        default:  // 루트 요소·형 변환 조회
            doc.RootElement();
            cur->ToText(); cur->ToComment(); cur->ToUnknown(); cur->ToDeclaration(); cur->ToDocument();
            cur->GetLineNum();
            cur->Value();
            cur->NoChildren();
            break;
        }
    }
    return 0;
}
