// [gapfuzz-ops] 이 파일은 Claude(claude-sonnet-5-5)가 official_llm.cpp에 '호출 안 함' API 10개의 호출을 추가하고
// [gapfuzz-ops] gapfuzz가 검사해 통과한 하네스입니다 (python3 -m gapfuzz llmops, 기록: samples/llm/ops/tinyxml2/official_llm/).
// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,2,4,5,6,7를 OSS-Fuzz 하네스에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness.py, 기록: samples/llm/combined/tinyxml2/).
// TinyXML2 공식 OSS-Fuzz 하네스 (projects/tinyxml2/xmltest.cpp)와 동일한 동작.
// 입력을 문자열로 바꿔 Parse 한 번만 호출한다.
#include "tinyxml2.h"
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <string>
#include <new>

using namespace tinyxml2;

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    uint8_t h[6] = {0, 0, 0, 0, 0, 0};  // [gapfuzz-llm] 입력 앞 6바이트를 제안별로 겹치지 않게 배분(0:공백모드, 1~2:nBytes, 3:DeleteNode, 4:Attribute, 5:InsertEndChild)
    size_t hdr = size < sizeof(h) ? size : sizeof(h);  // [gapfuzz-llm] 헤더로 쓸 바이트 수
    if (hdr > 0) memcpy(h, data, hdr);  // [gapfuzz-llm] 짧은 입력은 나머지를 0(원래 동작)으로 둠
    const uint8_t *payload = data + hdr;  // [gapfuzz-llm] 헤더 이후 바이트를 원래처럼 XML 본문으로 사용
    size_t payload_size = size - hdr;  // [gapfuzz-llm] 본문 길이

    std::string data_string(reinterpret_cast<const char *>(payload), payload_size);  // [gapfuzz-llm] 헤더를 뺀 본문으로 문자열 생성
    XMLDocument doc(true, static_cast<Whitespace>(h[0] % 3));  // [gapfuzz-llm] whitespaceMode를 입력으로 선택(0=PRESERVE 기본값 유지, 2=PEDANTIC)

    size_t nBytes = static_cast<size_t>(-1);  // [gapfuzz-llm] 기본값(-1, strlen 사용)이 계속 나오도록 유지
    if ((h[1] & 3) != 0) {  // [gapfuzz-llm] 약 1/4은 원래 값 유지, 나머지는 입력으로 nBytes 선택
        nBytes = ((static_cast<size_t>(h[1]) << 8) | h[2]) % (payload_size + 1);  // [gapfuzz-llm] 0~본문 길이로 제한해 nBytes==0 분기를 열고 버퍼 초과 읽기를 막음
    }
    doc.Parse(data_string.c_str(), nBytes);  // [gapfuzz-llm] 고정된 기본 nBytes 대신 퍼저가 고른 값 전달

    const char *doc_value = doc.Value(); (void)doc_value;  // [gapfuzz-llm] XMLDocument에서 Value()를 호출해 ToDocument() 참 분기(null 반환) 실행, 역참조하지 않음

    try {  // [gapfuzz-llm] 라이브러리/std 예외가 하네스 크래시가 되지 않도록 보호
        int dmode = h[3] % 4;  // [gapfuzz-llm] DeleteNode에 넘길 노드 상태 선택(0이면 호출 안 함)
        if (dmode == 1) {
            doc.DeleteNode(nullptr);  // [gapfuzz-llm] node == 0 분기 (null 허용)
        } else if (dmode == 2) {
            doc.DeleteNode(doc.FirstChild());  // [gapfuzz-llm] 트리에 연결된 노드로 node->_parent 참 분기 (없으면 null)
        } else if (dmode == 3) {
            doc.DeleteNode(doc.NewElement("gapfuzz"));  // [gapfuzz-llm] 연결되지 않은 같은 문서 노드로 _parent 거짓 분기
        }

        const XMLElement *root = doc.RootElement();  // [gapfuzz-llm] DeleteNode 이후 새로 얻어 dangling 포인터 방지
        const XMLAttribute *attr = root ? root->FirstAttribute() : 0;  // [gapfuzz-llm] 실제 존재하는 속성 이름을 쓰기 위해 첫 속성 획득
        if (root && attr) {  // [gapfuzz-llm] name은 null 금지이므로 속성이 있을 때만 호출
            unsigned amode = h[4] % 3;  // [gapfuzz-llm] value 전달 방식 선택
            const char *value = 0;  // [gapfuzz-llm] 0: null(기존 경로)
            if (amode == 1) {
                value = attr->Value();  // [gapfuzz-llm] 속성값과 같은 값으로 StringEqual 참 경로
            } else if (amode == 2) {
                value = data_string.c_str();  // [gapfuzz-llm] 입력 문자열로 !value 거짓 및 불일치 경로
            }
            (void)root->Attribute(attr->Name(), value);  // [gapfuzz-llm] Attribute(name, value) 직접 호출
        }

        XMLDocument other;  // [gapfuzz-llm] 다른 문서의 노드를 만들기 위한 문서(스코프 종료 시 자동 해제)
        int imode = h[5] % 4;  // [gapfuzz-llm] InsertEndChild 호출 방식 선택(0이면 호출 안 함)
        if (imode == 1) {
            doc.InsertEndChild(doc.NewElement("e"));  // [gapfuzz-llm] 같은 문서의 새 노드를 직접 삽입
        } else if (imode == 2) {
            doc.InsertEndChild(other.NewElement("f"));  // [gapfuzz-llm] 다른 문서 노드로 addThis->_document != _document 분기 (null 아님)
        } else if (imode == 3) {
            XMLNode *attached = doc.FirstChild();  // [gapfuzz-llm] 이미 연결된 노드를 다시 끝에 삽입
            if (attached) {
                doc.InsertEndChild(attached);  // [gapfuzz-llm] null이면 호출 생략
            }
        }
    } catch (...) {  // [gapfuzz-llm] 예외는 무시하고 계속 진행
    }

    // 아래부터 gapfuzz-ops 추가분. 위 원래 코드는 한 글자도 바꾸지 않았고, 추가분은 doc을 읽기/복사만 한다.
    // 추가분이 실행 속도를 떨어뜨려 원래 경로 탐색을 방해하지 않도록, 입력이 작을 때만(4KB 이하)
    // 그리고 끝 바이트 비트로 블록을 골라 일부 입력에서만 실행한다.
    auto tail = [&](size_t i) -> uint8_t {  // 끝에서 i번째 바이트(입력이 짧으면 0)
        return size > i ? data[size - 1 - i] : 0;
    };

    if (size <= 4096) {
        try {  // 라이브러리/std 예외가 하네스 크래시가 되지 않도록 보호
            XMLElement *root = doc.RootElement();  // 원래 코드의 변경이 끝난 뒤 새로 얻어 dangling 방지
            if (root) {  // 루트가 없으면 추가 호출을 모두 건너뜀
                const uint8_t sel = tail(5);  // 블록 선택 비트
                uint64_t udef = 0;  // 기본값을 입력 끝 8바이트로 구성
                for (size_t i = 0; i < 8; i++) udef = (udef << 8) | tail(6 + i);
                const int64_t idef = static_cast<int64_t>(udef);
                const bool bdef = (tail(0) & 1) != 0;
                const XMLElement *child = root->FirstChildElement();  // 없으면 null

                // [gapfuzz-ops] XMLElement::BoolText
                // [gapfuzz-ops] XMLElement::Int64Text
                if (sel & 1) {
                    (void)root->BoolText(bdef);  // 텍스트가 없거나 불리언이 아니면 기본값 반환
                    (void)root->Int64Text(idef);
                    if (child) {
                        (void)child->BoolText(!bdef);
                        (void)child->Int64Text(-idef);
                    }
                }

                const bool compact = ((tail(0) & 2) != 0) || size > 256;  // 들여쓰기 출력은 작은 입력에서만
                const int depth = tail(1) % 4;  // 시작 들여쓰기 깊이(0~3)

                // [gapfuzz-ops] XMLPrinter::VisitEnter
                // [gapfuzz-ops] XMLPrinter::VisitExit
                if (sel & 2) {
                    XMLPrinter printer(0, compact, depth);  // FILE*가 null이면 메모리 버퍼에만 기록(파일·stdout 미사용)
                    const XMLAttribute *firstAttr = (tail(1) & 4) ? 0 : root->FirstAttribute();  // 속성 null 허용
                    printer.VisitEnter(*root, firstAttr);  // 열기와 닫기를 항상 짝지어 호출
                    printer.VisitExit(*root);
                    (void)printer.CStr();
                }

                // [gapfuzz-ops] XMLDocument::Print
                if (sel & 4) {
                    XMLPrinter printer2(0, compact, 0);
                    doc.Print(&printer2);  // null이면 stdout으로 출력하므로 반드시 비null 프린터 전달
                    (void)printer2.CStrSize();
                }

                // [gapfuzz-ops] XMLElement::ShallowClone
                // [gapfuzz-ops] XMLElement::ShallowEqual
                if (sel & 8) {
                    XMLDocument scratch;  // 복제본을 소유할 별도 문서(스코프 종료 시 자동 해제)
                    XMLNode *clone = root->ShallowClone(&scratch);  // document는 비null
                    if (clone) {  // 실패하면 사용하지 않음
                        (void)root->ShallowEqual(clone);  // 같은 요소라 참 경로
                        if (child) (void)root->ShallowEqual(child);  // 이름이 다르면 거짓 경로
                        (void)root->ShallowEqual(&doc);  // 요소가 아닌 노드 경로
                        scratch.DeleteNode(clone);  // 연결되지 않은 노드는 소유 문서에서 삭제
                    }
                }

                // [gapfuzz-ops] XMLDocument::DeepCopy
                // [gapfuzz-ops] XMLNode::InsertAfterChild
                // [gapfuzz-ops] XMLElement::SetText(bool)
                if (sel & 16) {
                    XMLDocument copy;  // doc과 다른 대상 문서(자기 자신을 대상으로 쓰지 않음)
                    doc.DeepCopy(&copy);

                    const int mode = tail(3) % 4;
                    XMLNode *after = (mode == 1) ? copy.LastChild() : copy.FirstChild();  // copy의 자식만 afterThis로 사용
                    XMLNode *add = (mode == 2) ? copy.LastChild() : copy.NewElement("g");  // 2: 기존 노드 이동, 그 외: 새 노드
                    if (after && add) {  // afterThis는 null 금지
                        (void)copy.InsertAfterChild(after, add);
                    }

                    XMLElement *croot = copy.RootElement();  // 삽입 후 새로 얻음
                    if (croot) {
                        croot->SetText((tail(4) & 1) != 0);  // 복사본에만 쓰기 (원본 doc은 유지)
                        (void)croot->BoolText(false);
                    }
                }
            }
        } catch (...) {  // 예외는 무시하고 계속 진행
        }
    }
    return 0;
}
