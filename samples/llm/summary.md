# LLM(Claude) 하네스 수정 평가

모델 `claude-sonnet-5-5`. 제안 하나마다 Claude가 하네스를 고치고, gapfuzz가 컴파일 → 60초 × 2회 퍼징 → 겨냥한 분기가 열렸는지 → 크래시 귀속으로 검사.
실패하면 이유를 같은 대화로 돌려주고 최대 3번까지 다시 받음. 사람 결과는 samples/verify/*.md(같은 제안을 사람이 적용, 120초 × 5회).

- 제안 45개 중 통과 44개 (첫 시도에 통과 42개)
- 겨냥한 분기 108개 중 열림 100개
- 사람도 적용한 제안 35개: 사람 85/97, LLM 89/97
- 하네스 탓 크래시(걸러 냄) 0번, 컴파일 실패 1번, 라이브러리 결함 의심 0번
- 토큰: 입력 209,109, 출력 177,798

| 라이브러리 | 제안 | 판정 | 겨냥 | LLM 열림 | 시도 | 걸러 낸 크래시 | 사람 열림 |
|---|---|---|---:|---:|---:|---:|---:|
| tinyxml2/official | 1. XMLDocument::Parse · nBytes | FIXED | 2 | 2 | 1 | 0 | 2/2 |
| tinyxml2/official | 2. XMLDocument::XMLDocument · whitespaceMode | FIXED | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/official | 3. XMLDocument::Parse · xml | NARROW | 1 | 1 | 1 | 0 | – |
| tinyxml2/official | 4. XMLDocument::DeleteNode · node | DIRECT_CALL | 2 | 2 | 1 | 0 | 2/2 |
| tinyxml2/official | 5. XMLElement::Attribute · value | DIRECT_CALL | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/official | 6. XMLNode::Value | DIRECT_CALL | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/official | 7. XMLNode::InsertEndChild · addThis | DIRECT_CALL | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/stateful | 1. XMLComment::ShallowClone · document | FIXED | 5 | 5 | 1 | 0 | 5/5 |
| tinyxml2/stateful | 2. XMLDocument::Accept · visitor | FIXED | 4 | 4 | 1 | 0 | 4/4 |
| tinyxml2/stateful | 3. XMLDocument::Parse · nBytes | FIXED | 2 | 2 | 1 | 0 | 2/2 |
| tinyxml2/stateful | 4. XMLDocument::Print · streamer | FIXED | 1 | 1 | 1 | 0 | – |
| tinyxml2/stateful | 5. XMLHandle::XMLHandle · node | FIXED | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/stateful | 6. XMLPrinter::XMLPrinter · aposInAttributes | FIXED | 1 | 1 | 2 | 0 | 1/1 |
| tinyxml2/stateful | 7. XMLDocument::SetBOM · useBOM | SETTER_NOT_CALLED | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/stateful | 8. XMLConstHandle::XMLConstHandle · node | NARROW | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/stateful | 9. XMLDocument::Parse · xml | NARROW | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/stateful | 10. XMLDocument::DeleteNode · node | NARROW | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/stateful | 11. XMLDocument::XMLDocument · whitespaceMode | NARROW | 1 | 1 | 1 | 0 | 1/1 |
| tinyxml2/stateful | 12. XMLPrinter::VisitEnter · doc | DIRECT_CALL | 1 | 1 | 1 | 0 | – |
| tinyxml2/stateful | 13. XMLPrinter::VisitEnter · element | DIRECT_CALL | 1 | 1 | 1 | 0 | – |
| pugixml/official | 1. xml_document::load_buffer · encoding | FIXED | 5 | 5 | 2 | 0 | 4/5 |
| pugixml/official | 2. xml_node::xml_node · p | SETTER_NOT_CALLED | 1 | 1 | 2 | 0 | – |
| pugixml/official | 3. xml_document::load_buffer · options | NARROW | 26 | 24 | 3 | 0 | 24/26 |
| pugixml/official | 4. xml_document::load_buffer · contents | NARROW | 2 | 1 | 2 | 0 | 1/2 |
| cjson/official | 1. cJSON_ParseWithOpts · return_parse_end | FIXED | 2 | 2 | 1 | 0 | 2/2 |
| cjson/official | 2. cJSON_PrintBuffered · prebuffer | FIXED | 1 | 1 | 1 | 0 | 1/1 |
| cjson/official | 3. cJSON_ParseWithOpts · value | NARROW | 3 | 3 | 2 | 0 | 1/3 |
| cjson/official | 4. cJSON_PrintBuffered · item | NARROW | 1 | 1 | 1 | 0 | 1/1 |
| cjson/official | 5. cJSON_Minify · json | NARROW | 1 | 1 | 1 | 0 | – |
| jsoncpp/official | 1. Value::Value · type | FIXED | 6 | 5 | 2 | 0 | 5/6 |
| jsoncpp/official | 2. CharReaderBuilder::validate · invalid | FIXED | 1 | 1 | 1 | 0 | – |
| jsoncpp/official | 3. Value::Value · value | DIRECT_CALL | 2 | 2 | 2 | 0 | 1/2 |
| zlib/official | 1. uncompress · destLen | FIXED | 3 | 1 | 2 | 0 | 1/3 |
| zlib/official | 2. uncompress · source | NARROW | 1 | 1 | 1 | 0 | – |
| zlib/official | 3. uncompress · dest | NARROW | 1 | 1 | 1 | 0 | 1/1 |
| zlib/official | 4. inflate · flush | DIRECT_CALL | 7 | 7 | 1 | 0 | 7/7 |
| expat/official | 1. XML_ParserReset · encoding | FIXED | 1 | 1 | 1 | 0 | 1/1 |
| expat/official | 2. XML_ExternalEntityParserCreate · context | NARROW | 5 | 4 | 2 | 0 | 4/5 |
| expat/official | 3. XML_Parse · s | NARROW | 1 | 1 | 1 | 0 | 1/1 |
| expat/official | 4. XML_SetHashSalt16Bytes · entropy | NARROW | 1 | 1 | 1 | 0 | – |
| json-c/official | 1. json_tokener_free · tok | NARROW | 2 | 2 | 2 | 0 | – |
| json-c/official | 2. json_object_object_add_ex · opts | DIRECT_CALL | 2 | 2 | 1 | 0 | 2/2 |
| json-c/official | 3. json_tokener_new_ex · depth | DIRECT_CALL | 1 | 1 | 1 | 0 | 1/1 |
| json-c/official | 4. json_object_to_json_string_length · length | DIRECT_CALL | 1 | 1 | 1 | 0 | 1/1 |
| json-c/official | 5. json_object_array_shrink · empty_slots | DIRECT_CALL | 1 | 0 (실패) | 3 | 0 | 0/1 |
