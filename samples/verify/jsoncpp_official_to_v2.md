# 제안 검증 — jsoncpp-official-r1 → jsoncpp-official_v2-r1

수정 전 분석이 제안한 '하네스에서 고칠 곳'마다, 그 때문에 막혀 있던 분기가 수정 후(5회 실행)에 열렸는지 봅니다.
한 회차라도 양쪽 방향이 모두 실행되면 '열림'으로 셉니다.

| # | 제안 | 적용 | 막혀 있던 분기 | 열림 |
|---:|---|---|---:|---:|
| 1 | Value::Value · type | 적용 | 6 | 5 |
| 2 | CharReaderBuilder::validate · invalid | 미적용 | 1 | 0 |
| 3 | Value::Value · value | 적용 | 2 | 1 |

**적용한 제안 기준: 막혀 있던 분기 8개 중 6개가 열림**

## 1. `Value::Value(ValueType)`의 1번째 인자 `type`를 하네스가 고정합니다(55행에서 기본값) → 퍼저 입력으로 바꾸세요
- 열림 (5/5) — `Value::Value(ValueType)` 407행 조건 `case intValue` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `Value::Value(ValueType)` 408행 조건 `case uintValue` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `Value::Value(ValueType)` 411행 조건 `case realValue` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `Value::Value(ValueType)` 414행 조건 `case stringValue` (수정 전: 한 번도 참 아님)
- 열림 (5/5) — `Value::Value(ValueType)` 422행 조건 `case booleanValue` (수정 전: 한 번도 참 아님)
- 여전히 막힘 (0/5) — `Value::Value(ValueType)` 425행 조건 `default` (수정 전: 한 번도 참 아님)

## 2. `CharReaderBuilder::validate(Value *) const`의 1번째 인자 `invalid`를 하네스가 고정합니다(49행에서 항상 `nullptr`) → 퍼저 입력으로 바꾸세요
- 여전히 막힘 (0/5) — `CharReaderBuilder::validate(Value *) const` 1981행 조건 `invalid` (수정 전: 한 번도 참 아님)

## 3. `Value::Value(Int)`는 공개 API인데 하네스가 직접 부르지 않고 라이브러리 내부(`CharReaderBuilder::setDefaults`)에서만 불립니다. 내부 호출은 1번째 인자 `value`를 한 가지 방식으로만 넘기므로 (필드 `int_`를 거쳐 조건에 쓰임) → 하네스가 직접 불러 다른 값을 넘겨 보세요
- 열림 (5/5) — `Value::isUInt() const` 1404행 조건 `value_.int_ >= 0` (수정 전: 한 번도 거짓 아님)
- 여전히 막힘 (0/5) — `Value::isUInt() const` 1404행 조건 `LargestUInt(value_.int_) <= LargestUInt(maxUInt)` (수정 전: 한 번도 거짓 아님)

