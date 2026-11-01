// jsoncpp OSS-Fuzz 하네스(src/test_lib_json/fuzz.cpp)에 gapfuzz 제안을 적용한 버전.
//   제안 1 (적용, FIXED):       Json::Value root의 타입이 항상 기본값(nullValue) → 입력 비트로 8가지 타입 중 고름
//   제안 2 (적용, DIRECT_CALL): Value(Int)를 라이브러리만 부름(설정 기본값) → stackLimit을 부호 있는 정수(음수 포함)로도 넘김
//   제안 3 (미적용, 대조군):    CharReaderBuilder::validate의 invalid 인자가 항상 nullptr
//   (적용 중 하네스가 예외를 잡지 않아 생긴 가짜 크래시를 gapfuzz triage가 '하네스 버그'로 판정 → 아래 try/catch로 고침)
// 입력 형식은 원래 하네스와 같다 (앞 4바이트 옵션 플래그). 비트 12~14를 새로 씀.
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
    if (hash_settings & (1 << 12))                                           // [제안 2] 음수 포함 정수
      builder.settings_["stackLimit"] = Json::Value(static_cast<Json::Int>(static_cast<int16_t>(hash_settings >> 16)));
    else
      builder.settings_["stackLimit"] = (hash_settings >> 16) & 0x3FF;
  }

  // An unknown key is silently ignored by newCharReader(), so a typo here
  // would quietly stop the fuzzer from exercising that setting.
  if (!builder.validate(nullptr)) {
    std::abort();
  }

  // 제안 2를 처음 적용했을 때 음수 stackLimit에서 newCharReader가 Json::LogicError를 던졌고, 하네스가 잡지 않아
  // 가짜 크래시가 났다 (gapfuzz triage: 하네스 버그 의심, 확신 강). 라이브러리는 잘못된 설정을 예외로 알리도록 되어 있으므로 여기서 받는다.
  std::unique_ptr<Json::CharReader> reader;
#if JSON_USE_EXCEPTION
  try {
#endif
    reader.reset(builder.newCharReader());
#if JSON_USE_EXCEPTION
  } catch (Json::Exception const&) {
    return 0;
  }
#endif

  static const Json::ValueType kTypes[] = {Json::nullValue, Json::intValue, Json::uintValue, Json::realValue,
                                           Json::stringValue, Json::booleanValue, Json::arrayValue, Json::objectValue};
  Json::Value root(kTypes[(hash_settings >> 13) & 7]);                       // [제안 1]
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
