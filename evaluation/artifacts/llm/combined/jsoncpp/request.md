라이브러리: jsoncpp
하네스 파일: official.cpp

아래 제안 2개를 **모두 한 하네스에** 적용하세요.

## 제안 1
`Value::Value(ValueType)`의 1번째 인자 `type`를 하네스가 고정합니다(55행에서 기본값) → 퍼저 입력으로 바꾸세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (6개)
- `Value::Value(ValueType)` 407행, 조건 `case intValue`가 퍼징 중 한 번도 '참'이 되지 않음
```
  403    initBasic(type);
  404    switch (type) {
  405    case nullValue:
  406      break;
  407>   case intValue:
  408    case uintValue:
  409      value_.int_ = 0;
  410      break;
  411    case realValue:
```
- `Value::Value(ValueType)` 408행, 조건 `case uintValue`가 퍼징 중 한 번도 '참'이 되지 않음
```
  404    switch (type) {
  405    case nullValue:
  406      break;
  407    case intValue:
  408>   case uintValue:
  409      value_.int_ = 0;
  410      break;
  411    case realValue:
  412      value_.real_ = 0.0;
```
- `Value::Value(ValueType)` 411행, 조건 `case realValue`가 퍼징 중 한 번도 '참'이 되지 않음
```
  407    case intValue:
  408    case uintValue:
  409      value_.int_ = 0;
  410      break;
  411>   case realValue:
  412      value_.real_ = 0.0;
  413      break;
  414    case stringValue:
  415      // allocated_ == false, so this is safe.
```
- `Value::Value(ValueType)` 414행, 조건 `case stringValue`가 퍼징 중 한 번도 '참'이 되지 않음
```
  410      break;
  411    case realValue:
  412      value_.real_ = 0.0;
  413      break;
  414>   case stringValue:
  415      // allocated_ == false, so this is safe.
  416      value_.string_ = const_cast<char*>(static_cast<char const*>(emptyString));
  417      break;
  418    case arrayValue:
```
- `Value::Value(ValueType)` 422행, 조건 `case booleanValue`가 퍼징 중 한 번도 '참'이 되지 않음
```
  418    case arrayValue:
  419    case objectValue:
  420      value_.map_ = new ObjectValues();
  421      break;
  422>   case booleanValue:
  423      value_.bool_ = false;
  424      break;
  425    default:
  426      JSON_ASSERT_UNREACHABLE;
```
- `Value::Value(ValueType)` 425행, 조건 `default`가 퍼징 중 한 번도 '참'이 되지 않음
```
  421      break;
  422    case booleanValue:
  423      value_.bool_ = false;
  424      break;
  425>   default:
  426      JSON_ASSERT_UNREACHABLE;
  427    }
  428  }
  429  
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 1
@@ -52,7 +52,7 @@
 
   std::unique_ptr<Json::CharReader> reader(builder.newCharReader());
 
-  Json::Value root;
+  Json::Value root(static_cast<Json::ValueType>((hash_settings >> 12) & 0x7)); // [gapfuzz-llm] Value 생성자의 type 인자를 입력의 미사용 비트(12~14)에서 골라 0~7(유효한 ValueType 전부)을 만들고, 0이면 기존 nullValue가 됨
   const auto data_str = reinterpret_cast<const char*>(data);
 #if JSON_USE_EXCEPTION
   try {
```

## 제안 3
`Value::Value(Int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`CharReaderBuilder::setDefaults`)에서만 불립니다. 내부 호출은 1번째 인자 `value`를 한 가지 방식으로만 넘기므로 (필드 `int_`를 거쳐 조건에 쓰임) → 하네스가 직접 불러 다른 값을 넘겨 보세요

### 이 제안 때문에 막혀 있던 라이브러리 분기 (2개)
- `Value::isUInt() const` 1404행, 조건 `value_.int_ >= 0`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1400  bool Value::isUInt() const {
 1401    switch (type()) {
 1402    case intValue:
 1403  #if defined(JSON_HAS_INT64)
 1404>     return value_.int_ >= 0 && LargestUInt(value_.int_) <= LargestUInt(maxUInt);
 1405  #else
 1406      return value_.int_ >= 0;
 1407  #endif
 1408    case uintValue:
```
- `Value::isUInt() const` 1404행, 조건 `LargestUInt(value_.int_) <= LargestUInt(maxUInt)`가 퍼징 중 한 번도 '거짓'이 되지 않음
```
 1400  bool Value::isUInt() const {
 1401    switch (type()) {
 1402    case intValue:
 1403  #if defined(JSON_HAS_INT64)
 1404>     return value_.int_ >= 0 && LargestUInt(value_.int_) <= LargestUInt(maxUInt);
 1405  #else
 1406      return value_.int_ >= 0;
 1407  #endif
 1408    case uintValue:
```

### 참고: 이 제안 하나만 따로 적용해 검증을 통과했던 수정 (그대로 합치면 입력 바이트가 겹칠 수 있음)
```diff
--- 수정 전
+++ 시도 2
@@ -62,6 +62,20 @@
   } catch (Json::Exception const&) {
   }
 #endif // JSON_USE_EXCEPTION
+
+  Json::Value int_value(static_cast<Json::Int>(hash_settings)); // [gapfuzz-llm] Value(Int)를 직접 호출하고 입력 앞 4바이트로 음수·양수 값을 고르게 넘겨 int_ >= 0 거짓 분기를 만든다
+  (void)int_value.isUInt(); // [gapfuzz-llm] 직접 만든 intValue에 isUInt()를 호출해 1404행의 조건 분기를 실행한다
+
+#if defined(JSON_HAS_INT64)
+  uint64_t wide_high = 0; // [gapfuzz-llm] Json::Int(32비트)로는 int_가 maxUInt를 넘을 수 없으므로 상위 32비트를 입력에서 따로 모은다
+  for (size_t i = 0; i < size && i < sizeof(uint32_t); ++i) { // [gapfuzz-llm] 파서 입력은 건드리지 않고 남은 바이트를 최대 4개 읽어 상위 32비트를 만든다(없으면 0이라 원래 범위 값도 계속 나온다)
+    wide_high |= static_cast<uint64_t>(data[i]) << (8 * i); // [gapfuzz-llm] 입력 바이트로 상위 32비트를 채운다
+  }
+  const uint64_t wide_bits = (wide_high << 32) | hash_settings; // [gapfuzz-llm] 상위는 입력 바이트, 하위는 hash_settings로 64비트 값을 구성한다
+  Json::Value wide_value(static_cast<Json::Int64>(wide_bits)); // [gapfuzz-llm] 같은 intValue 타입을 만드는 Value(Int64) 생성자로 int_가 maxUInt를 넘는 값(예: 2^32 이상)을 넘긴다
+  (void)wide_value.isUInt(); // [gapfuzz-llm] LargestUInt(int_) <= maxUInt 조건이 거짓이 되는 경로를 실행한다
+#endif // JSON_HAS_INT64
+
   // Whether it succeeded or not doesn't matter.
   return 0;
 }
```

## 지금 하네스 (줄 번호는 참고용, 답에는 넣지 마세요)
```
   1  // OSS-Fuzz 공식 하네스: jsoncpp 저장소 src/test_lib_json/fuzz.cpp (커밋 93acc7b) 그대로. fuzz.h 포함만 뺌.
   2  // Copyright 2007-2019 The JsonCpp Authors
   3  // Distributed under MIT license, or public domain if desired and
   4  // recognized in your jurisdiction.
   5  // See file LICENSE for detail or copy at http://jsoncpp.sourceforge.net/LICENSE
   6  
   7  
   8  #include <cstdint>
   9  #include <cstdlib>
  10  #include <json/config.h>
  11  #include <json/json.h>
  12  #include <memory>
  13  #include <string>
  14  
  15  extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  16    Json::CharReaderBuilder builder;
  17  
  18    if (size < sizeof(uint32_t)) {
  19      return 0;
  20    }
  21  
  22    const uint32_t hash_settings = static_cast<uint32_t>(data[0]) |
  23                                   (static_cast<uint32_t>(data[1]) << 8) |
  24                                   (static_cast<uint32_t>(data[2]) << 16) |
  25                                   (static_cast<uint32_t>(data[3]) << 24);
  26    data += sizeof(uint32_t);
  27    size -= sizeof(uint32_t);
  28  
  29    builder.settings_["failIfExtra"] = (hash_settings & (1 << 0)) != 0;
  30    builder.settings_["allowComments"] = (hash_settings & (1 << 1)) != 0;
  31    builder.settings_["strictRoot"] = (hash_settings & (1 << 2)) != 0;
  32    builder.settings_["allowDroppedNullPlaceholders"] =
  33        (hash_settings & (1 << 3)) != 0;
  34    builder.settings_["allowNumericKeys"] = (hash_settings & (1 << 4)) != 0;
  35    builder.settings_["allowSingleQuotes"] = (hash_settings & (1 << 5)) != 0;
  36    builder.settings_["skipBom"] = (hash_settings & (1 << 6)) != 0;
  37    builder.settings_["rejectDupKeys"] = (hash_settings & (1 << 7)) != 0;
  38    builder.settings_["allowSpecialFloats"] = (hash_settings & (1 << 8)) != 0;
  39    builder.settings_["collectComments"] = (hash_settings & (1 << 9)) != 0;
  40    builder.settings_["allowTrailingCommas"] = (hash_settings & (1 << 10)) != 0;
  41    // Bit 11 selects a small stack limit taken from the upper 16 bits, so that
  42    // the depth-limit error paths are reachable without huge inputs.
  43    if (hash_settings & (1 << 11)) {
  44      builder.settings_["stackLimit"] = (hash_settings >> 16) & 0x3FF;
  45    }
  46  
  47    // An unknown key is silently ignored by newCharReader(), so a typo here
  48    // would quietly stop the fuzzer from exercising that setting.
  49    if (!builder.validate(nullptr)) {
  50      std::abort();
  51    }
  52  
  53    std::unique_ptr<Json::CharReader> reader(builder.newCharReader());
  54  
  55    Json::Value root;
  56    const auto data_str = reinterpret_cast<const char*>(data);
  57  #if JSON_USE_EXCEPTION
  58    try {
  59  #endif // JSON_USE_EXCEPTION
  60      reader->parse(data_str, data_str + size, &root, nullptr);
  61  #if JSON_USE_EXCEPTION
  62    } catch (Json::Exception const&) {
  63    }
  64  #endif // JSON_USE_EXCEPTION
  65    // Whether it succeeded or not doesn't matter.
  66    return 0;
  67  }
```