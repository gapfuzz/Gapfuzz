라이브러리: cjson
하네스 파일: official.c

아래 제안 4개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 2번째 인자 `return_parse_end`를 하네스가 고정합니다(34행에서 항상 `0`) (라이브러리 내부 `cJSON_ParseWithLengthOpts`를 거쳐 조건에 쓰임) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1187행, 조건 `return_parse_end`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1183          {
 1184              goto fail;
 1185          }
 1186      }
 1187>     if (return_parse_end)
 1188      {
 1189          *return_parse_end = (const char*)buffer_at_offset(&buffer);
 1190      }
 1191  
```
- `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1215행, 조건 `return_parse_end != NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1211          {
 1212              local_error.position = buffer.length - 1;
 1213          }
 1214  
 1215>         if (return_parse_end != NULL)
 1216          {
 1217              *return_parse_end = (const char*)local_error.json + local_error.position;
 1218          }
 1219  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -17,6 +17,8 @@
     unsigned char *copied;
     char *printed_json = NULL;
     int minify, require_termination, formatted, buffered;
+    const char *parse_end = NULL; // [gapfuzz-llm] return_parse_end 출력용 포인터 변수 (NULL 아님 경로를 위해 필요)
+    const char **return_parse_end; // [gapfuzz-llm] 입력에 따라 NULL 또는 &parse_end를 선택해 넘길 인자
 
 
     if(size <= offset) return 0;
@@ -31,7 +33,8 @@
     formatted           = data[2] == '1' ? 1 : 0;
     buffered            = data[3] == '1' ? 1 : 0;
 
-    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);
+    return_parse_end = (size & 1) ? &parse_end : NULL; // [gapfuzz-llm] 입력 크기의 홀짝으로 NULL(원래 값)과 유효한 포인터를 번갈아 선택
+    json = cJSON_ParseWithOpts((const char*)data + offset, return_parse_end, require_termination); // [gapfuzz-llm] return_parse_end를 항상 NULL로 고정하던 것을 퍼저 입력으로 선택하게 변경
 
     if(json == NULL) return 0;
 
@@ -74,4 +77,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```

## 제안 2
`cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 2번째 인자 `prebuffer`를 하네스가 고정합니다(40행에서 항상 `1`) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)` 1321행, 조건 `prebuffer < 0`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1317  CJSON_PUBLIC(char *) cJSON_PrintBuffered(const cJSON *item, int prebuffer, cJSON_bool fmt)
 1318  {
 1319      printbuffer p = { 0, 0, 0, 0, 0, 0, { 0, 0, 0 } };
 1320  
 1321>     if (prebuffer < 0)
 1322      {
 1323          return NULL;
 1324      }
 1325  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -37,7 +37,7 @@
 
     if(buffered)
     {
-        printed_json = cJSON_PrintBuffered(json, 1, formatted);
+        printed_json = cJSON_PrintBuffered(json, (int)(int8_t)data[size - 2], formatted); // [gapfuzz-llm] prebuffer를 입력 바이트(-128~127)에서 골라 음수 분기와 기존 값 1이 모두 나오게 함
     }
     else
     {
@@ -74,4 +74,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```

## 제안 3
`cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)`의 1번째 인자 `value`에 하네스가 null을 넘긴 적이 없습니다(34행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (3개)
- `cJSON_ParseWithOpts(const char *, const char **, cJSON_bool)` 1135행, 조건 `NULL == value`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1131  CJSON_PUBLIC(cJSON *) cJSON_ParseWithOpts(const char *value, const char **return_parse_end, cJSON_bool require_null_terminated)
 1132  {
 1133      size_t buffer_length;
 1134  
 1135>     if (NULL == value)
 1136      {
 1137          return NULL;
 1138      }
 1139  
```
- `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1156행, 조건 `value == NULL`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1152      /* reset error position */
 1153      global_error.json = NULL;
 1154      global_error.position = 0;
 1155  
 1156>     if (value == NULL || 0 == buffer_length)
 1157      {
 1158          goto fail;
 1159      }
 1160  
```
- `cJSON_ParseWithLengthOpts(const char *, size_t, const char **, cJSON_bool)` 1200행, 조건 `value != NULL`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1196      {
 1197          cJSON_Delete(item);
 1198      }
 1199  
 1200>     if (value != NULL)
 1201      {
 1202          error local_error;
 1203          local_error.json = (const unsigned char*)value;
 1204          local_error.position = 0;
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 2
@@ -17,6 +17,8 @@
     unsigned char *copied;
     char *printed_json = NULL;
     int minify, require_termination, formatted, buffered;
+    int use_null;
+    cJSON *null_json;
 
 
     if(size <= offset) return 0;
@@ -31,7 +33,15 @@
     formatted           = data[2] == '1' ? 1 : 0;
     buffered            = data[3] == '1' ? 1 : 0;
 
-    json = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);
+    use_null = ((data[size - 2] & 0x0F) == 0x0F); // [gapfuzz-llm] 입력의 끝에서 두 번째 바이트로 value에 NULL을 넘길지 고름 (약 1/16, 나머지는 원래 값 유지)
+
+    if(use_null)
+    {
+        null_json = cJSON_ParseWithLengthOpts(NULL, size - offset, NULL, require_termination); // [gapfuzz-llm] ParseWithOpts는 NULL이면 1135행에서 먼저 반환하므로 ParseWithLengthOpts에 직접 NULL을 넘겨 1156행/1200행 분기를 실행 (cJSON은 NULL을 허용하고 NULL을 반환함)
+        if(null_json != NULL) cJSON_Delete(null_json); // [gapfuzz-llm] 이론상 NULL만 반환되지만 만일에 대비해 해제
+    }
+
+    json = cJSON_ParseWithOpts(use_null ? NULL : (const char*)data + offset, NULL, require_termination); // [gapfuzz-llm] value에 NULL도 가끔 넘겨 NULL 검사 분기를 실행 (cJSON은 NULL을 허용하고 NULL을 반환함)
 
     if(json == NULL) return 0;
 
@@ -74,4 +84,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```

## 제안 4
`cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)`의 1번째 인자 `item`에 하네스가 null을 넘긴 적이 없습니다(40행) → nullptr도 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (1개)
- `cJSON_PrintBuffered(const cJSON *, int, cJSON_bool)` 1427행, 조건 `(item == NULL)`가 퍼징 중 한 번도 '참'이 되지 않음
```
 1423  static cJSON_bool print_value(const cJSON * const item, printbuffer * const output_buffer)
 1424  {
 1425      unsigned char *output = NULL;
 1426  
 1427>     if ((item == NULL) || (output_buffer == NULL))
 1428      {
 1429          return false;
 1430      }
 1431  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -37,7 +37,7 @@
 
     if(buffered)
     {
-        printed_json = cJSON_PrintBuffered(json, 1, formatted);
+        printed_json = cJSON_PrintBuffered(((data[size-2] & 0x07) == 0) ? NULL : json, 1, formatted); // [gapfuzz-llm] item이 NULL일 때의 분기(print_value의 item == NULL)를 닿게 하려고 입력 바이트로 가끔 NULL을 넘김 (그 외에는 기존 json 유지)
     }
     else
     {
@@ -74,4 +74,3 @@
 #ifdef __cplusplus
 }
 #endif
-
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  #include <stdlib.h>
   2  #include <stdint.h>
   3  #include <string.h>
   4  
   5  #ifdef __cplusplus
   6  extern "C" {
   7  #endif
   8  
   9  #include "cJSON.h"
  10  
  11  int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size); /* required by C89 */
  12  
  13  int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)
  14  {
  15      cJSON *json;
  16      size_t offset = 4;
  17      unsigned char *copied;
  18      char *printed_json = NULL;
  19      int minify, require_termination, formatted, buffered;
  20  
  21  
  22      if(size <= offset) return 0;
  23      if(data[size-1] != '\0') return 0;
  24      if(data[0] != '1' && data[0] != '0') return 0;
  25      if(data[1] != '1' && data[1] != '0') return 0;
  26      if(data[2] != '1' && data[2] != '0') return 0;
  27      if(data[3] != '1' && data[3] != '0') return 0;
  28  
  29      minify              = data[0] == '1' ? 1 : 0;
  30      require_termination = data[1] == '1' ? 1 : 0;
  31      formatted           = data[2] == '1' ? 1 : 0;
  32      buffered            = data[3] == '1' ? 1 : 0;
  33  
  34      json = cJSON_ParseWithOpts((const char*)data + offset, NULL, require_termination);
  35  
  36      if(json == NULL) return 0;
  37  
  38      if(buffered)
  39      {
  40          printed_json = cJSON_PrintBuffered(json, 1, formatted);
  41      }
  42      else
  43      {
  44          /* unbuffered printing */
  45          if(formatted)
  46          {
  47              printed_json = cJSON_Print(json);
  48          }
  49          else
  50          {
  51              printed_json = cJSON_PrintUnformatted(json);
  52          }
  53      }
  54  
  55      if(printed_json != NULL) free(printed_json);
  56  
  57      if(minify)
  58      {
  59          copied = (unsigned char*)malloc(size);
  60          if(copied == NULL) return 0;
  61  
  62          memcpy(copied, data, size);
  63  
  64          cJSON_Minify((char*)copied + offset);
  65  
  66          free(copied);
  67      }
  68  
  69      cJSON_Delete(json);
  70  
  71      return 0;
  72  }
  73  
  74  #ifdef __cplusplus
  75  }
  76  #endif
  77  
```