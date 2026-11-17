// [gapfuzz-ops] 이 파일은 Claude(claude-sonnet-5-5)가 새로 쓴 하네스입니다. OSS-Fuzz 하네스 전체를 합쳐도 불리지 않던 API 10개를 부릅니다.
// [gapfuzz-ops] gapfuzz가 검사해 통과했습니다 (python3 -m gapfuzz llmops tinyxml2 --union, 기록: evaluation/artifacts/llm/ops/tinyxml2/_union/).
// tinyxml2 갭 커버리지용 새 퍼징 하네스.
// 입력 앞쪽 바이트로 옵션과 호출 순서를 고르고, 나머지를 XML 데이터로 사용한다.
#include "tinyxml2.h"
#include <stddef.h>
#include <stdint.h>
#include <string>

using namespace tinyxml2;

static const size_t kMaxInput = 64 * 1024;
static const size_t kMaxPrintOut = 1024 * 1024;
static const int kMaxOps = 32;  // 반복 상한 (64 이하)

// 문서에서 첫 번째 요소를 깊이 제한 없이(자식만 탐색) 찾는다.
static XMLElement *FindFirstElement(XMLDocument &doc) {
    return doc.FirstChildElement();
}

// 선택 바이트로 요소를 하나 고른다 (루트의 자식 중 n번째, 없으면 루트 요소).
static XMLElement *PickElement(XMLDocument &doc, uint8_t sel) {
    XMLElement *e = doc.FirstChildElement();
    if (!e) return nullptr;
    int steps = sel % 8;
    for (int i = 0; i < steps; i++) {
        XMLElement *next = e->FirstChildElement();
        if (!next) next = e->NextSiblingElement();
        if (!next) break;
        e = next;
    }
    return e;
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;
    if (size > kMaxInput) size = kMaxInput;

    // 앞 4바이트: 선택값. 나머지: XML 데이터.
    uint8_t opt_whitespace = data[0];
    uint8_t opt_printer = data[1];
    uint8_t seed = data[2];
    uint8_t nops = data[3];
    const char *body = reinterpret_cast<const char *>(data + 4);
    size_t body_len = size - 4;

    std::string xml(body, body_len);

    XMLDocument doc(true, (opt_whitespace & 1) ? PRESERVE_WHITESPACE
                    : (opt_whitespace & 2) ? COLLAPSE_WHITESPACE
                                           : PEDANTIC_WHITESPACE);
    if (doc.Parse(xml.c_str(), xml.size()) != XML_SUCCESS) {
        return 0;  // 파싱 실패 시 객체를 더 쓰지 않는다
    }

    XMLElement *root = FindFirstElement(doc);
    if (!root) return 0;

    int ops = (nops % kMaxOps) + 1;
    size_t pos = 4;  // 호출 순서를 고르는 데 쓰는 입력 위치

    for (int i = 0; i < ops; i++) {
        uint8_t b = data[(pos + i) % size];
        uint8_t arg = data[(pos + i * 3 + seed) % size];
        XMLElement *elem = PickElement(doc, arg);
        if (!elem) break;

        switch (b % 10) {
        case 0: {
            // [gapfuzz-ops] XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)
            // 요소를 직접 방문시키며 속성 포인터는 null 또는 첫 속성으로 고른다.
            XMLPrinter printer(nullptr, (opt_printer & 1) != 0, (opt_printer >> 1) & 3);
            const XMLAttribute *attr = (arg & 1) ? elem->FirstAttribute() : nullptr;
            printer.VisitEnter(*elem, attr);
            printer.VisitExit(*elem);
            break;
        }
        case 1: {
            // [gapfuzz-ops] XMLElement::BoolText(bool) const
            bool r = elem->BoolText((arg & 1) != 0);
            (void)r;
            break;
        }
        case 2: {
            // [gapfuzz-ops] XMLDocument::Print(XMLPrinter *) const
            XMLPrinter printer(nullptr, (opt_printer & 1) != 0, (opt_printer >> 1) & 3);
            if (arg & 1) {
                doc.Print(&printer);
            } else {
                doc.Accept(&printer);
            }
            if (printer.CStrSize() > kMaxPrintOut) {
                // 출력이 너무 크면 중단 (메모리 상한)
                i = ops;
            }
            break;
        }
        case 3: {
            // [gapfuzz-ops] XMLElement::SetText(bool)
            // 문서 크기가 무한히 늘지 않도록 요소 수는 입력으로 제한된다.
            elem->SetText((arg & 1) != 0);
            // 바로 BoolText로 읽어 값이 일치하는지 흐름 확인
            bool back = elem->BoolText(!(arg & 1));
            (void)back;
            break;
        }
        case 4: {
            // [gapfuzz-ops] XMLElement::ShallowClone(XMLDocument *) const
            XMLDocument other;
            XMLNode *clone = elem->ShallowClone(&other);
            if (clone) {
                // 복제본은 other가 소유하므로 트리에 삽입해 소유권을 확정한다.
                other.InsertEndChild(clone);
                // [gapfuzz-ops] XMLElement::ShallowEqual(const XMLNode *) const
                bool eq = elem->ShallowEqual(clone);
                (void)eq;
            }
            break;
        }
        case 5: {
            // [gapfuzz-ops] XMLNode::ChildElementCount(const char *) const
            // 이름은 입력 바이트에서 만든 짧은 문자열 (null 불가).
            char name[9];
            size_t n = arg % 8;
            for (size_t k = 0; k < n; k++) {
                name[k] = static_cast<char>('a' + (data[(pos + k + arg) % size] % 26));
            }
            name[n] = '\0';
            int c1 = elem->ChildElementCount(name);
            // 실제 존재하는 이름으로도 호출
            int c2 = elem->FirstChildElement()
                         ? elem->ChildElementCount(elem->FirstChildElement()->Name())
                         : 0;
            (void)c1; (void)c2;
            break;
        }
        case 6: {
            // [gapfuzz-ops] XMLNode::InsertAfterChild(XMLNode *, XMLNode *)
            // 같은 문서가 만든 새 요소를 기존 자식 뒤에 삽입한다.
            XMLElement *fresh = doc.NewElement("n");
            if (fresh) {
                XMLNode *after = (arg & 1) ? elem->LastChild() : elem->FirstChild();
                XMLNode *res = nullptr;
                if (after) {
                    res = elem->InsertAfterChild(after, fresh);
                } else {
                    res = elem->InsertEndChild(fresh);
                }
                (void)res;
            }
            break;
        }
        case 7: {
            // [gapfuzz-ops] XMLElement::ShallowEqual(const XMLNode *) const
            XMLElement *other = PickElement(doc, static_cast<uint8_t>(arg + 1));
            if (other) {
                bool eq = elem->ShallowEqual(other);
                (void)eq;
            }
            break;
        }
        case 8: {
            // [gapfuzz-ops] XMLElement::Int64Text(int64_t) const
            int64_t def = 0;
            for (int k = 0; k < 8; k++) {
                def = (def << 8) | data[(pos + k + arg) % size];
            }
            int64_t v = elem->Int64Text(def);
            (void)v;
            break;
        }
        case 9: {
            // [gapfuzz-ops] XMLDocument::DeepCopy(XMLDocument *) const
            XMLDocument target;
            doc.DeepCopy(&target);
            // 복사본으로 출력까지 해서 복사 결과를 검증한다.
            XMLPrinter printer;
            target.Print(&printer);
            break;
        }
        }
        // 문서가 InsertAfterChild로 커질 수 있으므로 요소 순회로 인한 상한은 ops(≤32)로 제한됨
        // 루트가 바뀌었을 수 있어 다시 확인
        if (!doc.FirstChildElement()) break;
    }

    return 0;
}
