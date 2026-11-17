// [gapfuzz-llm] 이 파일은 Claude(claude-sonnet-5-5)가 gapfuzz 제안 1,3를 OSS-Fuzz 하네스에 적용하고
// [gapfuzz-llm] gapfuzz가 검사해 통과한 하네스입니다 (scripts/make_llm_harness.py, 기록: evaluation/artifacts/llm/combined/jsoncpp/).
// OSS-Fuzz 하네스: jsoncpp 저장소 src/test_lib_json/fuzz.cpp (커밋 93acc7b) 그대로. fuzz.h 포함만 뺌.
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

  uint64_t wide_bits = 0; // [gapfuzz-llm] 직접 만들 Value(Int)/Value(Int64)용 값을 담는다(입력이 짧으면 0)
  if (size >= 2 * sizeof(uint64_t)) { // [gapfuzz-llm] 파서 입력이 최소 8바이트 남도록, 충분히 길 때만 뒤쪽 8바이트를 떼어 쓴다
    size -= sizeof(uint64_t); // [gapfuzz-llm] 뒤쪽 8바이트를 파서 입력에서 분리해 hash_settings·파서 입력과 겹치지 않게 한다
    for (size_t i = 0; i < sizeof(uint64_t); ++i) { // [gapfuzz-llm] 떼어낸 8바이트를 리틀엔디안으로 64비트 값으로 조립한다
      wide_bits |= static_cast<uint64_t>(data[size + i]) << (8 * i); // [gapfuzz-llm] 입력 바이트로 음수·양수·32비트 초과 값을 고르게 만든다
    }
  }

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

  Json::Value root(static_cast<Json::ValueType>((hash_settings >> 12) & 0x7)); // [gapfuzz-llm] Value 생성자의 type 인자를 입력의 미사용 비트(12~14)에서 골라 0~7(유효한 ValueType 전부)을 만들고, 0이면 기존 nullValue가 됨
  const auto data_str = reinterpret_cast<const char*>(data);
#if JSON_USE_EXCEPTION
  try {
#endif // JSON_USE_EXCEPTION
    reader->parse(data_str, data_str + size, &root, nullptr);
#if JSON_USE_EXCEPTION
  } catch (Json::Exception const&) {
  }
#endif // JSON_USE_EXCEPTION

  Json::Value int_value(static_cast<Json::Int>(wide_bits & 0xFFFFFFFFu)); // [gapfuzz-llm] Value(Int)를 직접 호출하고 떼어낸 바이트의 하위 32비트로 음수·양수 값을 고르게 넘겨 int_ >= 0 거짓 분기를 만든다
  (void)int_value.isUInt(); // [gapfuzz-llm] 직접 만든 intValue에 isUInt()를 호출해 1404행의 조건 분기를 실행한다

#if defined(JSON_HAS_INT64)
  Json::Value wide_value(static_cast<Json::Int64>(wide_bits)); // [gapfuzz-llm] Value(Int64)로 int_가 maxUInt를 넘는 값(2^32 이상)을 넘겨 LargestUInt(int_) <= maxUInt 거짓 경로를 만든다
  (void)wide_value.isUInt(); // [gapfuzz-llm] 64비트 값이 들어간 intValue에 isUInt()를 호출해 해당 분기를 실행한다
#endif // JSON_HAS_INT64

  // Whether it succeeded or not doesn't matter.
  return 0;
}
