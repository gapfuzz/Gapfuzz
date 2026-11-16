# 호출 안 함 API 우선순위 — cjson/_union

'호출 안 함' API 71개. 추가 가능 71개, 제외 0개.

'추가 이득'은 위 순위의 API로 이미 닿는 코드를 뺀, 이 API를 더 불렀을 때 새로 실행될 수 있는 코드 영역 수입니다.

| 순위 | API | 새로 닿는 함수 | 코드 영역 | 추가 이득 | 비고 |
|---:|---|---:|---:|---:|---|
| 1 | `cJSON_Compare(const cJSON *const, const cJSON *const, const cJSON_bool)` | 5 | 149 | 149 | 이번에 추가 |
| 2 | `cJSON_AddItemReferenceToObject(cJSON *, const char *, cJSON *)` | 9 | 67 | 67 | 이번에 추가 |
| 3 | `cJSON_ReplaceItemInObjectCaseSensitive(cJSON *, const char *, cJSON *)` | 11 | 93 | 47 | 이번에 추가 |
| 4 | `cJSON_Duplicate(const cJSON *, cJSON_bool)` | 5 | 54 | 47 | 이번에 추가 |
| 5 | `cJSON_CreateIntArray(const int *, int)` | 4 | 37 | 36 | 이번에 추가 |
| 6 | `cJSON_DeleteItemFromArray(cJSON *, int)` | 4 | 32 | 32 | 이번에 추가 |
| 7 | `cJSON_CreateStringArray(const char *const *, int)` | 7 | 41 | 29 | 이번에 추가 |
| 8 | `cJSON_SetValuestring(cJSON *, const char *)` | 6 | 36 | 28 | 이번에 추가 |
| 9 | `cJSON_CreateFloatArray(const float *, int)` | 4 | 37 | 22 | 이번에 추가 |
| 10 | `cJSON_CreateDoubleArray(const double *, int)` | 4 | 37 | 22 | 이번에 추가 |
| 11 | `cJSON_InsertItemInArray(cJSON *, int, cJSON *)` | 4 | 44 | 20 |  |
| 12 | `cJSON_AddRawToObject(cJSON *const, const char *const, const char *const)` | 9 | 63 | 12 |  |
| 13 | `cJSON_AddBoolToObject(cJSON *const, const char *const, const cJSON_bool)` | 9 | 63 | 12 |  |
| 14 | `cJSON_InitHooks(cJSON_Hooks *)` | 1 | 12 | 12 |  |
| 15 | `cJSON_SetNumberHelper(cJSON *, double)` | 2 | 10 | 10 |  |
| 16 | `cJSON_GetStringValue(const cJSON *const)` | 2 | 10 | 10 |  |
| 17 | `cJSON_GetNumberValue(const cJSON *const)` | 3 | 10 | 10 |  |
| 18 | `cJSON_AddTrueToObject(cJSON *const, const char *const)` | 9 | 60 | 9 |  |
| 19 | `cJSON_AddObjectToObject(cJSON *const, const char *const)` | 9 | 60 | 9 |  |
| 20 | `cJSON_AddNullToObject(cJSON *const, const char *const)` | 9 | 60 | 9 |  |
| 21 | `cJSON_AddFalseToObject(cJSON *const, const char *const)` | 9 | 60 | 9 |  |
| 22 | `cJSON_PrintPreallocated(cJSON *, char *, const int, const cJSON_bool)` | 1 | 8 | 8 |  |
| 23 | `cJSON_IsBool(const cJSON *const)` | 1 | 7 | 7 |  |
| 24 | `cJSON_HasObjectItem(const cJSON *, const char *)` | 6 | 45 | 6 |  |
| 25 | `cJSON_IsTrue(const cJSON *const)` | 1 | 6 | 6 |  |
| 26 | `cJSON_IsRaw(const cJSON *const)` | 1 | 6 | 6 |  |
| 27 | `cJSON_IsObject(const cJSON *const)` | 1 | 6 | 6 |  |
| 28 | `cJSON_IsNull(const cJSON *const)` | 1 | 6 | 6 |  |
| 29 | `cJSON_IsInvalid(const cJSON *const)` | 1 | 6 | 6 |  |
| 30 | `cJSON_IsFalse(const cJSON *const)` | 1 | 6 | 6 |  |
| 31 | `cJSON_IsArray(const cJSON *const)` | 1 | 6 | 6 |  |
| 32 | `cJSON_GetArraySize(const cJSON *)` | 1 | 6 | 6 |  |
| 33 | `cJSON_AddNumberToObject(cJSON *const, const char *const, const double)` | 9 | 66 | 5 |  |
| 34 | `cJSON_AddStringToObject(cJSON *const, const char *const, const char *const)` | 9 | 63 | 5 |  |
| 35 | `cJSON_AddArrayToObject(cJSON *const, const char *const)` | 9 | 60 | 5 |  |
| 36 | `cJSON_ReplaceItemInArray(cJSON *, int, cJSON *)` | 3 | 40 | 5 |  |
| 37 | `cJSON_AddItemReferenceToArray(cJSON *, cJSON *)` | 5 | 29 | 5 |  |
| 38 | `cJSON_CreateStringReference(const char *)` | 2 | 6 | 5 |  |
| 39 | `cJSON_CreateObjectReference(const cJSON *)` | 2 | 6 | 5 |  |
| 40 | `cJSON_CreateArrayReference(const cJSON *)` | 2 | 6 | 5 |  |
| 41 | `cJSON_DeleteItemFromObjectCaseSensitive(cJSON *, const char *)` | 8 | 62 | 4 |  |
| 42 | `cJSON_GetArrayItem(const cJSON *, int)` | 2 | 12 | 4 |  |
| 43 | `cJSON_Version(void)` | 2 | 4 | 4 |  |
| 44 | `cJSON_ReplaceItemInObject(cJSON *, const char *, cJSON *)` | 11 | 93 | 2 |  |
| 45 | `cJSON_DeleteItemFromObject(cJSON *, const char *)` | 8 | 62 | 2 |  |
| 46 | `cJSON_AddItemToObjectCS(cJSON *, const char *, cJSON *)` | 8 | 53 | 2 |  |
| 47 | `cJSON_AddItemToObject(cJSON *, const char *, cJSON *)` | 8 | 53 | 2 |  |
| 48 | `cJSON_AddItemToArray(cJSON *, cJSON *)` | 3 | 17 | 1 |  |
| 49 | `cJSON_malloc(size_t)` | 1 | 1 | 1 |  |
| 50 | `cJSON_ParseWithLength(const char *, size_t)` | 1 | 1 | 1 |  |
| 51 | `cJSON_Parse(const char *)` | 1 | 1 | 1 |  |
| 52 | `cJSON_GetErrorPtr(void)` | 1 | 1 | 1 |  |
| 53 | `cJSON_DetachItemFromObjectCaseSensitive(cJSON *, const char *)` | 7 | 61 | 0 |  |
| 54 | `cJSON_DetachItemFromObject(cJSON *, const char *)` | 7 | 61 | 0 |  |
| 55 | `cJSON_GetObjectItemCaseSensitive(const cJSON *const, const char *const)` | 5 | 41 | 0 |  |
| 56 | `cJSON_GetObjectItem(const cJSON *const, const char *const)` | 5 | 41 | 0 |  |
| 57 | `cJSON_DetachItemFromArray(cJSON *, int)` | 3 | 31 | 0 |  |
| 58 | `cJSON_ReplaceItemViaPointer(cJSON *const, cJSON *const, cJSON *)` | 1 | 27 | 0 |  |
| 59 | `cJSON_DetachItemViaPointer(cJSON *, cJSON *const)` | 1 | 19 | 0 |  |
| 60 | `cJSON_CreateString(const char *)` | 4 | 14 | 0 |  |
| 61 | `cJSON_CreateRaw(const char *)` | 4 | 14 | 0 |  |
| 62 | `cJSON_CreateNumber(double)` | 1 | 10 | 0 |  |
| 63 | `cJSON_CreateBool(cJSON_bool)` | 1 | 7 | 0 |  |
| 64 | `cJSON_IsString(const cJSON *const)` | 1 | 6 | 0 |  |
| 65 | `cJSON_IsNumber(const cJSON *const)` | 1 | 6 | 0 |  |
| 66 | `cJSON_CreateTrue(void)` | 1 | 4 | 0 |  |
| 67 | `cJSON_CreateObject(void)` | 1 | 4 | 0 |  |
| 68 | `cJSON_CreateNull(void)` | 1 | 4 | 0 |  |
| 69 | `cJSON_CreateFalse(void)` | 1 | 4 | 0 |  |
| 70 | `cJSON_CreateArray(void)` | 1 | 4 | 0 |  |
| 71 | `cJSON_free(void *)` | 1 | 1 | 0 |  |
