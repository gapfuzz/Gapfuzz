라이브러리: jsoncpp
OSS-Fuzz 하네스 1개(official)의 커버리지를 모두 합쳐도, 공개 API 271개 중 213개는 한 번도 불리지 않습니다.

## 새 하네스가 불러야 할 API 10개 (새로 실행될 수 있는 코드가 많은 순서)

### 1. `Reader::parse(const std::string &, Value &, bool)` — 새로 실행될 수 있는 코드 영역 406개
```
  /** \brief Read a Value from a <a HREF="http://www.json.org">JSON</a>
   * document.
   *
   * \param      document        UTF-8 encoded string containing the document
   *                             to read.
   * \param[out] root            Contains the root value of the document if it
   *                             was successfully parsed.
   * \param      collectComments \c true to collect comment and allow writing
   *                             them back during serialization, \c false to
   *                             discard comments.  This parameter is ignored
   *                             if Features::allowComments_ is \c false.
   * \return \c true if the document was successfully parsed, \c false if an
   * error occurred.
   */
  bool parse(const std::string& document, Value& root,
             bool collectComments = true);
  /** \brief Read a Value from a <a HREF="http://www.json.org">JSON</a>
   * document.
   *
   * \param      beginDoc        Pointer on the beginning of the UTF-8 encoded
   *                             string of the document to read. The pointed-to
   *                             buffer must outlive this Reader if error
   *                             methods (e.g. getFormattedErrorMessages()) are
   *                             called after parse() returns.
   * \param      endDoc          Pointer on the end of the UTF-8 encoded string
   *                             of the document to read.  Must be >= beginDoc.
   * \param[out] root            Contains the root value of the document if it
   *                             was successfully parsed.
   * \param      collectComments \c true to collect comment and allow writing
   *                             them back during serialization, \c false to
   *                             discard comments.  This parameter is ignored
   *                             if Features::allowComments_ is \c false.
   * \return \c true if the document was successfully parsed, \c false if an
   * error occurred.
   */
```

### 2. `StyledWriter::write(const Value &)` — 새로 실행될 수 있는 코드 영역 385개
```
  /** \brief Serialize a Value in <a HREF="http://www.json.org">JSON</a> format.
   * \param root Value to serialize.
   * \return String containing the JSON document that represents the root value.
   */
  String write(const Value& root) override;
```

### 3. `Value::isConvertibleTo(ValueType) const` — 새로 실행될 수 있는 코드 영역 99개
```
  bool isConvertibleTo(ValueType other) const;
```

### 4. `StyledStreamWriter::write(OStream &, const Value &)` — 새로 실행될 수 있는 코드 영역 98개
```
  /** \brief Serialize a Value in <a HREF="http://www.json.org">JSON</a> format.
   * \param out Stream to write to. (Can be ostringstream, e.g.)
   * \param root Value to serialize.
   * \note There is no point in deriving from Writer, since write() should not
   * return a value.
   */
  void write(OStream& out, const Value& root);
```

### 5. `Value::resize(ArrayIndex)` — 새로 실행될 수 있는 코드 영역 58개
```
  /// Resize the array to newSize elements.
  /// New elements are initialized to null.
  /// May only be called on nullValue or arrayValue.
  /// \pre type() is arrayValue or nullValue
  /// \post type() is arrayValue
  void resize(ArrayIndex newSize);
```

### 6. `operator<<(OStream &, const Value &)` — 새로 실행될 수 있는 코드 영역 52개
```
/// \brief Output using the StyledStreamWriter.
/// \see Json::operator>>()
JSON_API OStream& operator<<(OStream&, const Value& root);
```

### 7. `Path::Path(const String &, const PathArgument &, const PathArgument &, const PathArgument &, const PathArgument &, const PathArgument &)` — 새로 실행될 수 있는 코드 영역 51개
```
  Path(const String& path, const PathArgument& a1 = PathArgument(),
       const PathArgument& a2 = PathArgument(),
       const PathArgument& a3 = PathArgument(),
       const PathArgument& a4 = PathArgument(),
       const PathArgument& a5 = PathArgument());
```

### 8. `Value::compare(const Value &) const` — 새로 실행될 수 있는 코드 영역 45개
```
  int compare(const Value& other) const;
```

### 9. `as() const` — 새로 실행될 수 있는 코드 영역 42개
```
template <> inline Int Value::as<Int>() const { return asInt(); }
```

### 10. `Value::operator!=(const Value &) const` — 새로 실행될 수 있는 코드 영역 34개
```
  bool operator!=(const Value& other) const;
```

## 참고: 기존 하네스 official.cpp (고치지 마세요. include와 작성 방식만 참고)
```
// OSS-Fuzz 공식 하네스: jsoncpp 저장소 src/test_lib_json/fuzz.cpp (커밋 93acc7b) 그대로. fuzz.h 포함만 뺌.
// Copyright 2007-2019 The JsonCpp Authors
// Distributed under MIT license, or public domain if desired and
// recognized in your jurisdiction.
// See file LICENSE for detail or copy at http://jsoncpp.sourceforge.net/LICENSE


#include <cstdint>
#include <cstdlib>
#include <json/config.h>
#include <json/json.h>
#include <memory>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  Json::CharReaderBuilder builder;

  if (size < sizeof(uint32_t)) {
    return 0;
  }

  const uint32_t hash_settings = static_cast<uint32_t>(data[0]) |
                                 (static_cast<uint32_t>(data[1]) << 8) |
                                 (static_cast<uint32_t>(data[2]) << 16) |
                                 (static_cast<uint32_t>(data[3]) << 24);
  data += sizeof(uint32_t);
  size -= sizeof(uint32_t);

  builder.settings_["failIfExtra"] = (hash_settings & (1 << 0)) != 0;
  builder.settings_["allowComments"] = (hash_settings & (1 << 1)) != 0;
  builder.settings_["strictRoot"] = (hash_settings & (1 << 2)) != 0;
  builder.settings_["allowDroppedNullPlaceholders"] =
      (hash_settings & (1 << 3)) != 0;
  builder.settings_["allowNumericKeys"] = (hash_settings & (1 << 4)) != 0;
  builder.settings_["allowSingleQuotes"] = (hash_settings & (1 << 5)) != 0;
  builder.settings_["skipBom"] = (hash_settings & (1 << 6)) != 0;
  builder.settings_["rejectDupKeys"] = (hash_settings & (1 << 7)) != 0;
  builder.settings_["allowSpecialFloats"] = (hash_settings & (1 << 8)) != 0;
  builder.settings_["collectComments"] = (hash_settings & (1 << 9)) != 0;
  builder.settings_["allowTrailingCommas"] = (hash_settings & (1 << 10)) != 0;
  // Bit 11 selects a small stack limit taken from the upper 16 bits, so that
  // the depth-limit error paths are reachable without huge inputs.
  if (hash_settings & (1 << 11)) {
    builder.settings_["stackLimit"] = (hash_settings >> 16) & 0x3FF;
  }

  // An unknown key is silently ignored by newCharReader(), so a typo here
  // would quietly stop the fuzzer from exercising that setting.
  if (!builder.validate(nullptr)) {
    std::abort();
  }

  std::unique_ptr<Json::CharReader> reader(builder.newCharReader());

  Json::Value root;
  const auto data_str = reinterpret_cast<const char*>(data);
#if JSON_USE_EXCEPTION
  try {
#endif // JSON_USE_EXCEPTION
    reader->parse(data_str, data_str + size, &root, nullptr);
#if JSON_USE_EXCEPTION
  } catch (Json::Exception const&) {
  }
#endif // JSON_USE_EXCEPTION
  // Whether it succeeded or not doesn't matter.
  return 0;
}

```