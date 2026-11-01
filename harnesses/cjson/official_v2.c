/* cJSON 공식 하네스(fuzzing/cjson_read_fuzzer.c)에 gapfuzz 제안을 적용한 버전.
 *   제안 1 (적용): cJSON_ParseWithOpts의 return_parse_end를 항상 NULL로 고정 → 실제 포인터를 넘김
 *   제안 2 (적용): cJSON_PrintBuffered의 prebuffer를 항상 1로 고정 → 입력 5번째 바이트로 고름
 *   제안 3 (적용): cJSON_ParseWithOpts에 NULL을 넘긴 적 없음 → NULL도 넘김
 *   제안 4 (적용): cJSON_PrintBuffered에 NULL을 넘긴 적 없음 → NULL도 넘김
 *   제안 5 (미적용, 대조군): cJSON_Minify에 NULL
 * 입력 형식: 앞 4바이트는 원래 하네스와 같은 옵션 플래그, 5번째 바이트는 prebuffer, 그 뒤가 JSON (끝은 NUL).
 */
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "cJSON.h"

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size);

int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
{
    cJSON *json;
    size_t offset = 5;
    unsigned char *copied;
    char *printed_json = NULL;
    const char *parse_end = NULL;
    int minify, require_termination, formatted, buffered, prebuffer;

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
    prebuffer           = (int)(signed char)data[4];

    (void)cJSON_ParseWithOpts(NULL, NULL, require_termination);
    json = cJSON_ParseWithOpts((const char*)data + offset, &parse_end, require_termination);

    if(json == NULL) return 0;

    if(buffered)
    {
        printed_json = cJSON_PrintBuffered(json, prebuffer, formatted);
        if(printed_json != NULL) free(printed_json);
        printed_json = cJSON_PrintBuffered(NULL, prebuffer, formatted);
    }
    else
    {
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
