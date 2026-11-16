// [gapfuzz-ops] 이 파일은 Claude(claude-sonnet-5-5)가 새로 쓴 하네스입니다. OSS-Fuzz 하네스 전체를 합쳐도 불리지 않던 API 10개를 부릅니다.
// [gapfuzz-ops] gapfuzz가 검사해 통과했습니다 (python3 -m gapfuzz llmops jsoncpp --union, 기록: samples/llm/ops/jsoncpp/_union/).
// jsoncpp 신규 하네스(수정판): gapfuzz가 찾은 미호출 API(Reader::parse, StyledWriter,
// StyledStreamWriter, operator<<, Value::resize/compare/!=/isConvertibleTo/as<Int>, Path)를 호출한다.
// 입력 구조: [0]=Reader 옵션 비트, [1]=연산 횟수, [2]=문서 분할 위치, [3..]=연산 선택 바이트, 그 뒤=데이터
// 수정: Path 생성자에 NUL 바이트가 든 경로 문자열을 넘기면 makePath가 끝나지 않고
//       args_를 무한히 push_back 하여 OOM이 나므로, 경로 문자열에서 NUL을 제거한다.
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <json/config.h>
#include <json/json.h>
#include <sstream>
#include <string>

namespace {

constexpr size_t kMaxInput = 64 * 1024;
constexpr unsigned kMaxOps = 16;
constexpr int kMaxWriteDepth = 64;  // 출력 크기를 제한하기 위한 중첩 깊이 상한
constexpr size_t kMaxOut = 1 << 20; // 출력 상한 1MB

// 값의 중첩 깊이를 limit까지만 계산한다(재귀 깊이도 limit으로 제한됨).
int Depth(const Json::Value& v, int limit) {
  if (limit <= 0) return 1;
  int best = 0;
  if (v.isArray() || v.isObject()) {
    for (const auto& child : v) {
      int d = Depth(child, limit - 1);
      if (d > best) best = d;
      if (best >= limit) break;
    }
    return best + 1;
  }
  return 1;
}

bool SafeToWrite(const Json::Value& v) { return Depth(v, kMaxWriteDepth + 1) <= kMaxWriteDepth; }

// Path 생성자용 문자열 정리: NUL 바이트는 makePath(strchr 사용)에서
// 진행이 멈춰 무한 루프/무한 할당을 일으키므로 다른 문자로 바꾼다.
std::string SanitizePath(const std::string& s, size_t max_len) {
  std::string out = s.substr(0, max_len);
  for (char& c : out) {
    if (c == '\0') c = 'x';
  }
  return out;
}

}  // namespace

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size < 4) return 0;
  if (size > kMaxInput) size = kMaxInput;

  const uint8_t flags = data[0];
  const unsigned num_ops = (data[1] % kMaxOps) + 1;
  const uint8_t split_sel = data[2];
  data += 3;
  size -= 3;

  // 연산 선택 바이트
  if (size < num_ops) return 0;
  const uint8_t* ops = data;
  data += num_ops;
  size -= num_ops;

  // 데이터를 두 문서로 나눈다
  const size_t split = size ? (static_cast<size_t>(split_sel) * size) / 256 : 0;
  const std::string doc_a(reinterpret_cast<const char*>(data), split);
  const std::string doc_b(reinterpret_cast<const char*>(data) + split, size - split);

  // Reader 옵션 (Features)
  Json::Features features = (flags & 1) ? Json::Features::strictMode() : Json::Features::all();
  if (!(flags & 1)) {
    features.allowComments_ = (flags & 2) != 0;
    features.allowDroppedNullPlaceholders_ = (flags & 4) != 0;
    features.allowNumericKeys_ = (flags & 8) != 0;
  }
  const bool collect_comments = (flags & 16) != 0;

  Json::Value a, b;
  bool a_ok = false;
  bool b_ok = false;

  // [gapfuzz-ops] Reader::parse(const std::string &, Value &, bool)
  try {
    Json::Reader reader_a(features);
    a_ok = reader_a.parse(doc_a, a, collect_comments);
    Json::Reader reader_b(features);
    b_ok = reader_b.parse(doc_b, b, !collect_comments);
  } catch (const std::exception&) {
  }
  if (!a_ok) a = Json::Value();  // 실패한 객체는 더 쓰지 않는다
  if (!b_ok) b = a;

  for (unsigned i = 0; i < num_ops; ++i) {
    const uint8_t op = ops[i];
    const unsigned sel = op % 9;
    try {
      switch (sel) {
        case 0: {
          // [gapfuzz-ops] StyledWriter::write(const Value &)
          if (!SafeToWrite(a)) break;
          Json::StyledWriter w;
          std::string out = w.write(a);
          if (out.size() > kMaxOut) break;
          break;
        }
        case 1: {
          // [gapfuzz-ops] StyledStreamWriter::write(OStream &, const Value &)
          if (!SafeToWrite(b)) break;
          Json::StyledStreamWriter w(std::string(op % 5, ' '));
          std::ostringstream os;
          w.write(os, b);
          break;
        }
        case 2: {
          // [gapfuzz-ops] operator<<(OStream &, const Value &)
          if (!SafeToWrite(a)) break;
          std::ostringstream os;
          os << a;
          break;
        }
        case 3: {
          // [gapfuzz-ops] Value::isConvertibleTo(ValueType) const
          for (int t = Json::nullValue; t <= Json::objectValue; ++t) {
            (void)a.isConvertibleTo(static_cast<Json::ValueType>(t));
            (void)b.isConvertibleTo(static_cast<Json::ValueType>(t));
          }
          break;
        }
        case 4: {
          // [gapfuzz-ops] Value::resize(ArrayIndex)
          // null 또는 array일 때만 호출 가능(사전 조건). 복사본에 적용한다.
          Json::Value c = (op & 0x80) ? a : b;
          if (c.isNull() || c.isArray()) {
            Json::ArrayIndex n = static_cast<Json::ArrayIndex>(
                (op >> 1) * 8 + (i < size ? static_cast<uint8_t>(data[i]) : 0));  // 최대 약 1300
            c.resize(n);
            if (c.size() != n) std::abort();
            c.resize(n / 2);
          }
          break;
        }
        case 5: {
          // [gapfuzz-ops] Value::compare(const Value &) const
          // [gapfuzz-ops] Value::operator!=(const Value &) const
          int c1 = a.compare(b);
          int c2 = b.compare(a);
          bool ne = (a != b);
          bool ne_self = (a != a);
          if (ne_self) std::abort();   // 자기 자신과는 항상 같아야 한다
          (void)c1; (void)c2; (void)ne;
          Json::Value copy = a;
          if (copy != a) std::abort();
          break;
        }
        case 6: {
          // [gapfuzz-ops] as() const  (Value::as<Int>)
          // 변환 불가/범위 초과 시 예외가 나므로 try/catch 안에서 호출
          if (a.isConvertibleTo(Json::intValue)) {
            Json::Int v = a.as<Json::Int>();
            (void)v;
          }
          break;
        }
        case 7: {
          // [gapfuzz-ops] Path::Path(const String &, const PathArgument &, ...)
          // 입력 데이터 일부를 경로 문자열로 사용(최대 32자, NUL 제거)
          std::string path_str = SanitizePath(doc_b, 32);
          Json::Path p(path_str, Json::PathArgument(static_cast<Json::ArrayIndex>(op)),
                       Json::PathArgument(SanitizePath(doc_a, 8)),
                       Json::PathArgument(static_cast<Json::ArrayIndex>(op >> 2)));
          Json::Value r = p.resolve(a);
          (void)r;
          Json::Value def(static_cast<int>(op));
          Json::Value r2 = p.resolve(b, def);
          (void)r2;
          break;
        }
        case 8: {
          // as<Int>를 실수 값에도 시도: 입력 기반 값 생성 후 변환
          Json::Value n(static_cast<double>(static_cast<int8_t>(op)) * 1000.5);
          if (n.isConvertibleTo(Json::intValue)) (void)n.as<Json::Int>();
          if (n != a) (void)n.compare(a);
          break;
        }
      }
    } catch (const std::exception&) {
      // Json::Exception 포함: 입력에 의한 정상적인 오류 경로
    }
  }
  return 0;
}
