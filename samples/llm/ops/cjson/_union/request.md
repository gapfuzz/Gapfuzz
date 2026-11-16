라이브러리: cjson
OSS-Fuzz 하네스 1개(official)의 커버리지를 모두 합쳐도, 공개 API 78개 중 71개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `cJSON_Compare(const cJSON *const, const cJSON *const, const cJSON_bool)` — 새로 실행될 수 있는 코드 영역 149개
```
/* Duplicate will create a new, identical cJSON item to the one you pass, in new memory that will
 * need to be released. With recurse!=0, it will duplicate any children connected to the item.
 * The item->next and ->prev pointers are always zero on return from Duplicate. */
/* Recursively compare two cJSON items for equality. If either a or b is NULL or invalid, they will be considered unequal.
 * case_sensitive determines if object keys are treated case sensitive (1) or case insensitive (0) */
CJSON_PUBLIC(cJSON_bool) cJSON_Compare(const cJSON * const a, const cJSON * const b, const cJSON_bool case_sensitive);
/* Minify a strings, remove blank characters(such as ' ', '\t', '\r', '\n') from strings.
 * The input pointer json cannot point to a read-only address area, such as a string constant, 
 * but should point to a readable and writable address area. */
```

### 2. `cJSON_AddItemReferenceToObject(cJSON *, const char *, cJSON *)` — 새로 실행될 수 있는 코드 영역 67개
```
CJSON_PUBLIC(cJSON_bool) cJSON_AddItemReferenceToObject(cJSON *object, const char *string, cJSON *item);
/* Remove/Detach items from Arrays/Objects. */
```

### 3. `cJSON_ReplaceItemInObjectCaseSensitive(cJSON *, const char *, cJSON *)` — 새로 실행될 수 있는 코드 영역 47개
```
CJSON_PUBLIC(cJSON_bool) cJSON_ReplaceItemInObjectCaseSensitive(cJSON *object,const char *string,cJSON *newitem);
/* Duplicate a cJSON item */
```

### 4. `cJSON_Duplicate(const cJSON *, cJSON_bool)` — 새로 실행될 수 있는 코드 영역 47개
```
/* Duplicate a cJSON item */
CJSON_PUBLIC(cJSON *) cJSON_Duplicate(const cJSON *item, cJSON_bool recurse);
/* Duplicate will create a new, identical cJSON item to the one you pass, in new memory that will
 * need to be released. With recurse!=0, it will duplicate any children connected to the item.
 * The item->next and ->prev pointers are always zero on return from Duplicate. */
```

### 5. `cJSON_CreateIntArray(const int *, int)` — 새로 실행될 수 있는 코드 영역 36개
```
/* These utilities create an Array of count items.
 * The parameter count cannot be greater than the number of elements in the number array, otherwise array access will be out of bounds.*/
CJSON_PUBLIC(cJSON *) cJSON_CreateIntArray(const int *numbers, int count);
```

### 6. `cJSON_DeleteItemFromArray(cJSON *, int)` — 새로 실행될 수 있는 코드 영역 32개
```
CJSON_PUBLIC(void) cJSON_DeleteItemFromArray(cJSON *array, int which);
```

### 7. `cJSON_CreateStringArray(const char *const *, int)` — 새로 실행될 수 있는 코드 영역 29개
```
CJSON_PUBLIC(cJSON *) cJSON_CreateStringArray(const char *const *strings, int count);
/* Append item to the specified array/object. */
```

### 8. `cJSON_SetValuestring(cJSON *, const char *)` — 새로 실행될 수 있는 코드 영역 28개
```
/* Change the valuestring of a cJSON_String object, only takes effect when type of object is cJSON_String */
CJSON_PUBLIC(char*) cJSON_SetValuestring(cJSON *object, const char *valuestring);
/* If the object is not a boolean type this does nothing and returns cJSON_Invalid else it returns the new type*/
```

### 9. `cJSON_CreateFloatArray(const float *, int)` — 새로 실행될 수 있는 코드 영역 22개
```
CJSON_PUBLIC(cJSON *) cJSON_CreateFloatArray(const float *numbers, int count);
```

### 10. `cJSON_CreateDoubleArray(const double *, int)` — 새로 실행될 수 있는 코드 영역 22개
```
CJSON_PUBLIC(cJSON *) cJSON_CreateDoubleArray(const double *numbers, int count);
```

## 참고: 기존 하네스 official.c (고치지 마세요. include와 작성 방식만 참고)
```
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "cJSON.h"

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size); /* required by C89 */

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
{
    cJSON *json;
    size_t offset = 4;
    unsigned char *copied;
    char *printed_json = NULL;
    int minify, require_termination, formatted, buffered;


    if(size <= offset) return 0;
    if(data[size-1] != '\0') return 0;
    if(data[0] != '1' && data[0] != '0') return 0;
    if(data[1] != '1' && data[1] != '0') return 0;
    if(data[2] != '1' && data[2] != '0') return 0;
    if(data[3] != '1' && data[3] != '0') return 0;

    minify              = data[0] == '1' ? 1 : 0;
    require_termination = data[1] == '1' ? 1 : 0;
    formatted           = data[2] == '1' ? 1 : 0;
    buffered            = data[3] == '1' ? 1 : 0;

    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);

    if(json == NULL) return 0;

    if(buffered)
    {
        printed_json = cJSON_PrintBuffered(json, 1, formatted);
    }
    else
    {
        /* unbuffered printing */
        if(formatted)
        {
            printed_json = cJSON_Print(json);
        }
        else
        {
            printed_json = cJSON_PrintUnformatted(json);
        }
    }

    if(printed_json != NULL) free(printed_json);

    if(minify)
    {
        copied = (unsigned char*)malloc(size);
        if(copied == NULL) return 0;

        memcpy(copied, data, size);

        cJSON_Minify((char*)copied + offset);

        free(copied);
    }

    cJSON_Delete(json);

    return 0;
}

#ifdef __cplusplus
}
#endif


```