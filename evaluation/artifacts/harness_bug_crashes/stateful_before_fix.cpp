// TinyXML2 스테이트풀 하네스 (초안)
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

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    FuzzedDataProvider fdp(data, size);

    XMLDocument doc(fdp.ConsumeBool(), fdp.ConsumeBool() ? COLLAPSE_WHITESPACE : PRESERVE_WHITESPACE);
    std::string xml = fdp.ConsumeRandomLengthString(4096);
    doc.Parse(xml.c_str());

    XMLDocument other;          // DeepClone / 다른 문서 간 동작 확인용
    XMLNode *cur = &doc;

    for (int i = 0; i < kMaxOps && fdp.remaining_bytes() > 0; ++i) {
        std::string s = fdp.ConsumeRandomLengthString(kMaxStr);
        const char *str = s.c_str();
        XMLElement *ele = cur->ToElement();
        const unsigned nchild = ChildCount(cur);

        switch (fdp.ConsumeIntegralInRange<int>(0, 21)) {
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
                else doc.DeleteNode(c);
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
                XMLNode *clone = cur->ShallowClone(&doc);
                if (clone) {
                    clone->ShallowEqual(cur);
                    if (XMLNode *p = cur->Parent()) p->InsertEndChild(clone);
                }
            }
            break;
        }
        case 13: {  // 출력
            XMLPrinter printer(nullptr, fdp.ConsumeBool(), fdp.ConsumeIntegralInRange<int>(0, 4));
            if (fdp.ConsumeBool()) doc.Print(&printer);
            else cur->Accept(&printer);
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
            XMLHandle h(&doc);
            h.FirstChildElement(fdp.ConsumeBool() ? str : nullptr).FirstChild().NextSiblingElement().ToElement();
            XMLConstHandle ch(cur);
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
            if (cur != &doc) cur->SetValue(str, fdp.ConsumeBool());
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
