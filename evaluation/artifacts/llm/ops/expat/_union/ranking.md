# 호출 안 함 API 우선순위 — expat/_union

'호출 안 함' API 66개. 추가 가능 66개, 제외 0개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `XML_SetPropertyDouble(XML_Parser, enum XML_Parser_Property, double)` | 5 | 33 | 33 | 이번에 추가 |
| 2 | `XML_ResumeParser(XML_Parser)` | 1 | 26 | 26 | 이번에 추가 |
| 3 | `XML_SetPropertyUInt64(XML_Parser, enum XML_Parser_Property, uint64_t)` | 4 | 25 | 25 | 이번에 추가 |
| 4 | `XML_GetInputContext(XML_Parser, int *, int *)` | 2 | 25 | 25 | 이번에 추가 |
| 5 | `XML_SetPropertyBool(XML_Parser, enum XML_Parser_Property, XML_Bool)` | 3 | 23 | 23 | 이번에 추가 |
| 6 | `XML_DefaultCurrent(XML_Parser)` | 2 | 23 | 23 | 이번에 추가 |
| 7 | `XML_SetEncoding(XML_Parser, const XML_Char *)` | 1 | 18 | 18 | 이번에 추가 |
| 8 | `XML_GetFeatureList(void)` | 1 | 16 | 16 | 이번에 추가 |
| 9 | `XML_SetHashSalt(XML_Parser, unsigned long)` | 3 | 15 | 15 | 이번에 추가 |
| 10 | `XML_SetBase(XML_Parser, const XML_Char *)` | 1 | 14 | 14 | 이번에 추가 |
| 11 | `XML_GetPropertyUInt64(XML_Parser, enum XML_Parser_Property, uint64_t *)` | 1 | 14 | 14 |  |
| 12 | `XML_GetPropertyDouble(XML_Parser, enum XML_Parser_Property, double *)` | 1 | 14 | 14 |  |
| 13 | `XML_GetPropertyBool(XML_Parser, enum XML_Parser_Property, XML_Bool *)` | 1 | 14 | 14 |  |
| 14 | `XML_SetReturnNSTriplet(XML_Parser, int)` | 1 | 11 | 11 |  |
| 15 | `XML_GetCurrentColumnNumber(XML_Parser)` | 2 | 10 | 10 |  |
| 16 | `XML_GetCurrentByteCount(XML_Parser)` | 2 | 10 | 10 |  |
| 17 | `XML_GetCurrentByteIndex(XML_Parser)` | 2 | 8 | 8 |  |
| 18 | `XML_UseForeignDTD(XML_Parser, XML_Bool)` | 1 | 7 | 7 |  |
| 19 | `XML_SetParamEntityParsing(XML_Parser, enum XML_ParamEntityParsing)` | 1 | 7 | 7 |  |
| 20 | `XML_SetExternalEntityRefHandlerArg(XML_Parser, void *)` | 1 | 7 | 7 |  |
| 21 | `XML_SetReparseDeferralEnabled(XML_Parser, XML_Bool)` | 2 | 17 | 5 |  |
| 22 | `XML_SetBillionLaughsAttackProtectionMaximumAmplification(XML_Parser, float)` | 3 | 16 | 5 |  |
| 23 | `XML_SetAllocTrackerMaximumAmplification(XML_Parser, float)` | 3 | 16 | 5 |  |
| 24 | `XML_SetBillionLaughsAttackProtectionActivationThreshold(XML_Parser, unsigned long long)` | 2 | 12 | 5 |  |
| 25 | `XML_SetAllocTrackerActivationThreshold(XML_Parser, unsigned long long)` | 2 | 12 | 5 |  |
| 26 | `XML_SetDefaultHandlerExpand(XML_Parser, XML_DefaultHandler)` | 1 | 5 | 5 |  |
| 27 | `XML_SetDefaultHandler(XML_Parser, XML_DefaultHandler)` | 1 | 5 | 5 |  |
| 28 | `XML_GetParsingStatus(XML_Parser, XML_ParsingStatus *)` | 2 | 5 | 5 |  |
| 29 | `XML_ExpatVersion(void)` | 1 | 5 | 5 |  |
| 30 | `XML_SetUnknownEncodingHandler(XML_Parser, XML_UnknownEncodingHandler, void *)` | 1 | 4 | 4 |  |
| 31 | `XML_SetNamespaceDeclHandler(XML_Parser, XML_StartNamespaceDeclHandler, XML_EndNamespaceDeclHandler)` | 1 | 4 | 4 |  |
| 32 | `XML_SetDoctypeDeclHandler(XML_Parser, XML_StartDoctypeDeclHandler, XML_EndDoctypeDeclHandler)` | 1 | 4 | 4 |  |
| 33 | `XML_SetCdataSectionHandler(XML_Parser, XML_StartCdataSectionHandler, XML_EndCdataSectionHandler)` | 1 | 4 | 4 |  |
| 34 | `XML_MemRealloc(XML_Parser, void *, size_t)` | 1 | 4 | 4 |  |
| 35 | `XML_MemMalloc(XML_Parser, size_t)` | 1 | 4 | 4 |  |
| 36 | `XML_MemFree(XML_Parser, void *)` | 1 | 4 | 4 |  |
| 37 | `XML_GetSpecifiedAttributeCount(XML_Parser)` | 1 | 4 | 4 |  |
| 38 | `XML_GetIdAttributeIndex(XML_Parser)` | 1 | 4 | 4 |  |
| 39 | `XML_GetBase(XML_Parser)` | 1 | 4 | 4 |  |
| 40 | `XML_FreeContentModel(XML_Parser, XML_Content *)` | 1 | 4 | 4 |  |
| 41 | `XML_ExpatVersionInfo(void)` | 1 | 4 | 4 |  |
| 42 | `XML_UseParserAsHandlerArg(XML_Parser)` | 1 | 3 | 3 |  |
| 43 | `XML_SetXmlDeclHandler(XML_Parser, XML_XmlDeclHandler)` | 1 | 3 | 3 |  |
| 44 | `XML_SetUnparsedEntityDeclHandler(XML_Parser, XML_UnparsedEntityDeclHandler)` | 1 | 3 | 3 |  |
| 45 | `XML_SetStartNamespaceDeclHandler(XML_Parser, XML_StartNamespaceDeclHandler)` | 1 | 3 | 3 |  |
| 46 | `XML_SetStartElementHandler(XML_Parser, XML_StartElementHandler)` | 1 | 3 | 3 |  |
| 47 | `XML_SetStartDoctypeDeclHandler(XML_Parser, XML_StartDoctypeDeclHandler)` | 1 | 3 | 3 |  |
| 48 | `XML_SetStartCdataSectionHandler(XML_Parser, XML_StartCdataSectionHandler)` | 1 | 3 | 3 |  |
| 49 | `XML_SetSkippedEntityHandler(XML_Parser, XML_SkippedEntityHandler)` | 1 | 3 | 3 |  |
| 50 | `XML_SetProcessingInstructionHandler(XML_Parser, XML_ProcessingInstructionHandler)` | 1 | 3 | 3 |  |
| 51 | `XML_SetNotationDeclHandler(XML_Parser, XML_NotationDeclHandler)` | 1 | 3 | 3 |  |
| 52 | `XML_SetNotStandaloneHandler(XML_Parser, XML_NotStandaloneHandler)` | 1 | 3 | 3 |  |
| 53 | `XML_SetExternalEntityRefHandler(XML_Parser, XML_ExternalEntityRefHandler)` | 1 | 3 | 3 |  |
| 54 | `XML_SetEntityDeclHandler(XML_Parser, XML_EntityDeclHandler)` | 1 | 3 | 3 |  |
| 55 | `XML_SetEndNamespaceDeclHandler(XML_Parser, XML_EndNamespaceDeclHandler)` | 1 | 3 | 3 |  |
| 56 | `XML_SetEndElementHandler(XML_Parser, XML_EndElementHandler)` | 1 | 3 | 3 |  |
| 57 | `XML_SetEndDoctypeDeclHandler(XML_Parser, XML_EndDoctypeDeclHandler)` | 1 | 3 | 3 |  |
| 58 | `XML_SetEndCdataSectionHandler(XML_Parser, XML_EndCdataSectionHandler)` | 1 | 3 | 3 |  |
| 59 | `XML_SetElementDeclHandler(XML_Parser, XML_ElementDeclHandler)` | 1 | 3 | 3 |  |
| 60 | `XML_SetCommentHandler(XML_Parser, XML_CommentHandler)` | 1 | 3 | 3 |  |
| 61 | `XML_SetAttlistDeclHandler(XML_Parser, XML_AttlistDeclHandler)` | 1 | 3 | 3 |  |
| 62 | `XML_GetCurrentLineNumber(XML_Parser)` | 1 | 1 | 1 |  |
| 63 | `XML_GetInputContext64(XML_Parser, int64_t *, uint64_t *)` | 1 | 13 | 0 |  |
| 64 | `XML_GetCurrentColumnNumber64(XML_Parser)` | 1 | 9 | 0 |  |
| 65 | `XML_GetCurrentByteCount64(XML_Parser)` | 1 | 9 | 0 |  |
| 66 | `XML_GetCurrentByteIndex64(XML_Parser)` | 1 | 7 | 0 |  |
