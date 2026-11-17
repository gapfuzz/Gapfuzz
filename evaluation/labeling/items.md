# 라벨링 항목

69개. 기준은 GUIDE.md. 정답은 sheet.csv에 적습니다.

## 1. `element.Parent()` 가 한 번도 거짓이 되지 않음

- 함수: `XMLPrinter::VisitEnter(const XMLElement &, const XMLAttribute *)`
- 위치: tinyxml2.cpp:2983

```cpp
   2975      }
   2976      return true;
   2977  }
   2978  
   2979  
   2980  bool XMLPrinter::VisitEnter( const XMLElement& element, const XMLAttribute* attribute )
   2981  {
   2982      const XMLElement* parentElem = 0;
>  2983      if ( element.Parent() ) {
   2984          parentElem = element.Parent()->ToElement();
   2985      }
   2986      const bool compactMode = parentElem ? CompactMode( *parentElem ) : _compactMode;
   2987      OpenElement( element.Name(), compactMode );
   2988      while ( attribute ) {
   2989          PushAttribute( attribute->Name(), attribute->Value() );
   2990          attribute = attribute->Next();
   2991      }
```

## 2. `!doc` 가 한 번도 참이 되지 않음

- 함수: `XMLComment::ShallowClone(XMLDocument *) const`
- 위치: tinyxml2.cpp:1317

```cpp
   1309          _document->SetError( XML_ERROR_PARSING_COMMENT, _parseLineNum, 0 );
   1310      }
   1311      return p;
   1312  }
   1313  
   1314  
   1315  XMLNode* XMLComment::ShallowClone( XMLDocument* doc ) const
   1316  {
>  1317      if ( !doc ) {
   1318          doc = _document;
   1319      }
   1320      XMLComment* comment = doc->NewComment( Value() );	// fixme: this will always allocate memory. Intern?
   1321      return comment;
   1322  }
   1323  
   1324  
   1325  bool XMLComment::ShallowEqual( const XMLNode* compare ) const
```

## 3. `nBytes == 0` 가 한 번도 참이 되지 않음

- 함수: `XMLDocument::Parse(const char *, size_t)`
- 위치: tinyxml2.cpp:2459

```cpp
   2451      return _errorID;
   2452  }
   2453  
   2454  
   2455  XMLError XMLDocument::Parse( const char* xml, size_t nBytes )
   2456  {
   2457      Clear();
   2458  
>  2459      if ( nBytes == 0 || !xml || !*xml ) {
   2460          SetError( XML_ERROR_EMPTY_DOCUMENT, 0, 0 );
   2461          return _errorID;
   2462      }
   2463      if ( nBytes == static_cast<size_t>(-1) ) {
   2464          nBytes = strlen( xml );
   2465      }
   2466      TIXMLASSERT( _charBuffer == 0 );
   2467      _charBuffer = new char[ nBytes+1 ];
```

## 4. `(aposInAttributes == ESCAPE_APOS_CHARS_IN_ATTRIBUTES)` 가 한 번도 거짓이 되지 않음

- 함수: `XMLPrinter::XMLPrinter(FILE *, bool, int, EscapeAposCharsInAttributes)`
- 위치: tinyxml2.cpp:2605

```cpp
   2597      _buffer()
   2598  {
   2599      for( int i=0; i<ENTITY_RANGE; ++i ) {
   2600          _entityFlag[i] = false;
   2601          _restrictedEntityFlag[i] = false;
   2602      }
   2603      for( int i=0; i<NUM_ENTITIES; ++i ) {
   2604          const char entityValue = entities[i].value;
>  2605          if ((aposInAttributes == ESCAPE_APOS_CHARS_IN_ATTRIBUTES) || (entityValue != SINGLE_QUOTE)) {
   2606              const unsigned char flagIndex = static_cast<unsigned char>(entityValue);
   2607              TIXMLASSERT( flagIndex < ENTITY_RANGE );
   2608              _entityFlag[flagIndex] = true;
   2609          }
   2610      }
   2611      _restrictedEntityFlag[static_cast<unsigned char>('&')] = true;
   2612      _restrictedEntityFlag[static_cast<unsigned char>('<')] = true;
   2613      _restrictedEntityFlag[static_cast<unsigned char>('>')] = true;	// not required, but consistency is nice
```

## 5. `*length == 0` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::GetCharacterRef(const char *, char *, int *)`
- 위치: tinyxml2.cpp:544

```cpp
    536              --q;
    537          }
    538          // Out of range:
    539          if (ucs > MAX_CODE_POINT) {
    540              return 0;
    541          }
    542          // convert the UCS to UTF-8
    543          ConvertUTF32ToUTF8(ucs, value, length);
>   544          if (*length == 0) {
    545              // If *length is 0, ConvertUTF32ToUTF8 rejected the code point.
    546              // Fail safely.
    547              return 0;
    548          }
    549          return p + delta + 1;
    550      }
    551      return p + 1;
    552  }
```

## 6. `XMLUtil::StringEqual( unknown->Value(), Value() )` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUnknown::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1426

```cpp
   1418      return text;
   1419  }
   1420  
   1421  
   1422  bool XMLUnknown::ShallowEqual( const XMLNode* compare ) const
   1423  {
   1424      TIXMLASSERT( compare );
   1425      const XMLUnknown* unknown = compare->ToUnknown();
>  1426      return ( unknown && XMLUtil::StringEqual( unknown->Value(), Value() ));
   1427  }
   1428  
   1429  
   1430  bool XMLUnknown::Accept( XMLVisitor* visitor ) const
   1431  {
   1432      TIXMLASSERT( visitor );
   1433      return visitor->Visit( *this );
   1434  }
```

## 7. `visitor->VisitEnter( *this, _rootAttribute )` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::Accept(XMLVisitor *) const`
- 위치: tinyxml2.cpp:2152

```cpp
   2144      }
   2145      return false;
   2146  }
   2147  
   2148  
   2149  bool XMLElement::Accept( XMLVisitor* visitor ) const
   2150  {
   2151      TIXMLASSERT( visitor );
>  2152      if ( visitor->VisitEnter( *this, _rootAttribute ) ) {
   2153          for ( const XMLNode* node=FirstChild(); node; node=node->NextSibling() ) {
   2154              if ( !node->Accept( visitor ) ) {
   2155                  break;
   2156              }
   2157          }
   2158      }
   2159      return visitor->VisitExit( *this );
   2160  }
```

## 8. `mult > MAX_CODE_POINT` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::GetCharacterRef(const char *, char *, int *)`
- 위치: tinyxml2.cpp:533

```cpp
    525              // or if adding it to ucs would exceed it (checked without overflow by
    526              // testing ucs > MAX_CODE_POINT - digitScaled, safe since digitScaled
    527              // <= MAX_CODE_POINT at this point).
    528              if (digitScaled > MAX_CODE_POINT || ucs > MAX_CODE_POINT - digitScaled) {
    529                  return 0;
    530              }
    531              ucs += digitScaled;
    532              mult *= radix;
>   533              if (mult > MAX_CODE_POINT) {
    534                  mult = MAX_CODE_POINT;
    535              }
    536              --q;
    537          }
    538          // Out of range:
    539          if (ucs > MAX_CODE_POINT) {
    540              return 0;
    541          }
```

## 9. `ucs > MAX_CODE_POINT - digitScaled` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::GetCharacterRef(const char *, char *, int *)`
- 위치: tinyxml2.cpp:528

```cpp
    520              }
    521              TIXMLASSERT(digit < radix);
    522  
    523              const unsigned int digitScaled = mult * digit;
    524              // Reject before adding: if digitScaled alone exceeds MAX_CODE_POINT,
    525              // or if adding it to ucs would exceed it (checked without overflow by
    526              // testing ucs > MAX_CODE_POINT - digitScaled, safe since digitScaled
    527              // <= MAX_CODE_POINT at this point).
>   528              if (digitScaled > MAX_CODE_POINT || ucs > MAX_CODE_POINT - digitScaled) {
    529                  return 0;
    530              }
    531              ucs += digitScaled;
    532              mult *= radix;
    533              if (mult > MAX_CODE_POINT) {
    534                  mult = MAX_CODE_POINT;
    535              }
    536              --q;
```

## 10. `IsPrefixHex(str)` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ToUnsigned(const char *, unsigned int *)`
- 위치: tinyxml2.cpp:618

```cpp
    610              return true;
    611          }
    612      }
    613      return false;
    614  }
    615  
    616  bool XMLUtil::ToUnsigned(const char* str, unsigned* value)
    617  {
>   618      if (TIXML_SSCANF(str, IsPrefixHex(str) ? "%x" : "%u", value) == 1) {
    619          return true;
    620      }
    621      return false;
    622  }
    623  
    624  bool XMLUtil::ToBool( const char* str, bool* value )
    625  {
    626      int ival = 0;
```

## 11. `InsertEndChild(node)` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::InsertNewComment(const char *)`
- 위치: tinyxml2.cpp:2054

```cpp
   2046  {
   2047      XMLElement* node = _document->NewElement(name);
   2048      return InsertEndChild(node) ? node : 0;
   2049  }
   2050  
   2051  XMLComment* XMLElement::InsertNewComment(const char* comment)
   2052  {
   2053      XMLComment* node = _document->NewComment(comment);
>  2054      return InsertEndChild(node) ? node : 0;
   2055  }
   2056  
   2057  XMLText* XMLElement::InsertNewText(const char* text)
   2058  {
   2059      XMLText* node = _document->NewText(text);
   2060      return InsertEndChild(node) ? node : 0;
   2061  }
   2062  
```

## 12. `curLineNumPtr` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUtil::SkipWhiteSpace(const char *, int *)`
- 위치: tinyxml2.h:550

```cpp
    542  */
    543  class TINYXML2_LIB XMLUtil
    544  {
    545  public:
    546      static const char* SkipWhiteSpace( const char* p, int* curLineNumPtr )	{
    547          TIXMLASSERT( p );
    548  
    549          while( IsWhiteSpace(*p) ) {
>   550              if (curLineNumPtr && *p == '\n') {
    551                  ++(*curLineNumPtr);
    552              }
    553              ++p;
    554          }
    555          TIXMLASSERT( p );
    556          return p;
    557      }
    558      static char* SkipWhiteSpace( char* const p, int* curLineNumPtr ) {
```

## 13. `addThis->_document != _document` 가 한 번도 참이 되지 않음

- 함수: `XMLNode::InsertFirstChild(XMLNode *)`
- 위치: tinyxml2.cpp:964

```cpp
    956      addThis->_parent = this;
    957      return addThis;
    958  }
    959  
    960  
    961  XMLNode* XMLNode::InsertFirstChild( XMLNode* addThis )
    962  {
    963      TIXMLASSERT( addThis );
>   964      if ( addThis->_document != _document ) {
    965          TIXMLASSERT( false );
    966          return 0;
    967      }
    968      InsertChildPreamble( addThis );
    969  
    970      if ( _firstChild ) {
    971          TIXMLASSERT( _lastChild );
    972          TIXMLASSERT( _firstChild->_prev == 0 );
```

## 14. `XMLUtil::StringEqual( other->Name(), Name() )` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:2127

```cpp
   2119      return element;
   2120  }
   2121  
   2122  
   2123  bool XMLElement::ShallowEqual( const XMLNode* compare ) const
   2124  {
   2125      TIXMLASSERT( compare );
   2126      const XMLElement* other = compare->ToElement();
>  2127      if ( other && XMLUtil::StringEqual( other->Name(), Name() )) {
   2128  
   2129          const XMLAttribute* a=FirstAttribute();
   2130          const XMLAttribute* b=other->FirstAttribute();
   2131  
   2132          while ( a && b ) {
   2133              if ( !XMLUtil::StringEqual( a->Value(), b->Value() ) ) {
   2134                  return false;
   2135              }
```

## 15. `!node->Accept( visitor )` 가 한 번도 참이 되지 않음

- 함수: `XMLElement::Accept(XMLVisitor *) const`
- 위치: tinyxml2.cpp:2154

```cpp
   2146  }
   2147  
   2148  
   2149  bool XMLElement::Accept( XMLVisitor* visitor ) const
   2150  {
   2151      TIXMLASSERT( visitor );
   2152      if ( visitor->VisitEnter( *this, _rootAttribute ) ) {
   2153          for ( const XMLNode* node=FirstChild(); node; node=node->NextSibling() ) {
>  2154              if ( !node->Accept( visitor ) ) {
   2155                  break;
   2156              }
   2157          }
   2158      }
   2159      return visitor->VisitExit( *this );
   2160  }
   2161  
   2162  
```

## 16. `!xml` 가 한 번도 참이 되지 않음

- 함수: `XMLDocument::Parse(const char *, size_t)`
- 위치: tinyxml2.cpp:2459

```cpp
   2451      return _errorID;
   2452  }
   2453  
   2454  
   2455  XMLError XMLDocument::Parse( const char* xml, size_t nBytes )
   2456  {
   2457      Clear();
   2458  
>  2459      if ( nBytes == 0 || !xml || !*xml ) {
   2460          SetError( XML_ERROR_EMPTY_DOCUMENT, 0, 0 );
   2461          return _errorID;
   2462      }
   2463      if ( nBytes == static_cast<size_t>(-1) ) {
   2464          nBytes = strlen( xml );
   2465      }
   2466      TIXMLASSERT( _charBuffer == 0 );
   2467      _charBuffer = new char[ nBytes+1 ];
```

## 17. `InsertEndChild(node)` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::InsertNewText(const char *)`
- 위치: tinyxml2.cpp:2060

```cpp
   2052  {
   2053      XMLComment* node = _document->NewComment(comment);
   2054      return InsertEndChild(node) ? node : 0;
   2055  }
   2056  
   2057  XMLText* XMLElement::InsertNewText(const char* text)
   2058  {
   2059      XMLText* node = _document->NewText(text);
>  2060      return InsertEndChild(node) ? node : 0;
   2061  }
   2062  
   2063  XMLDeclaration* XMLElement::InsertNewDeclaration(const char* text)
   2064  {
   2065      XMLDeclaration* node = _document->NewDeclaration(text);
   2066      return InsertEndChild(node) ? node : 0;
   2067  }
   2068  
```

## 18. `XMLUtil::StringEqual( comment->Value(), Value() )` 가 한 번도 거짓이 되지 않음

- 함수: `XMLComment::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1329

```cpp
   1321      return comment;
   1322  }
   1323  
   1324  
   1325  bool XMLComment::ShallowEqual( const XMLNode* compare ) const
   1326  {
   1327      TIXMLASSERT( compare );
   1328      const XMLComment* comment = compare->ToComment();
>  1329      return ( comment && XMLUtil::StringEqual( comment->Value(), Value() ));
   1330  }
   1331  
   1332  
   1333  bool XMLComment::Accept( XMLVisitor* visitor ) const
   1334  {
   1335      TIXMLASSERT( visitor );
   1336      return visitor->Visit( *this );
   1337  }
```

## 19. `p == q` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::StringEqual(const char *, const char *, int)`
- 위치: tinyxml2.h:592

```cpp
    584      }
    585  
    586      inline static bool IsPrefixHex( const char* p) {
    587          p = SkipWhiteSpace(p, 0);
    588          return p && *p == '0' && ( *(p + 1) == 'x' || *(p + 1) == 'X');
    589      }
    590  
    591      inline static bool StringEqual( const char* p, const char* q, int nChar=INT_MAX )  {
>   592          if ( p == q ) {
    593              return true;
    594          }
    595          TIXMLASSERT( p );
    596          TIXMLASSERT( q );
    597          TIXMLASSERT( nChar >= 0 );
    598          return strncmp( p, q, static_cast<size_t>(nChar) ) == 0;
    599      }
    600  
```

## 20. `case 3` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`
- 위치: tinyxml2.cpp:443

```cpp
    435      // Scary scary fall throughs are annotated with carefully designed comments
    436      // to suppress compiler warnings such as -Wimplicit-fallthrough in gcc
    437      switch (*length) {
    438          case 4:
    439              --output;
    440              *output = static_cast<char>((input | BYTE_MARK) & BYTE_MASK);
    441              input >>= 6;
    442              TIXML_FALLTHROUGH;
>   443          case 3:
    444              --output;
    445              *output = static_cast<char>((input | BYTE_MARK) & BYTE_MASK);
    446              input >>= 6;
    447              TIXML_FALLTHROUGH;
    448          case 2:
    449              --output;
    450              *output = static_cast<char>((input | BYTE_MARK) & BYTE_MASK);
    451              input >>= 6;
```

## 21. `!doc` 가 한 번도 참이 되지 않음

- 함수: `XMLDeclaration::ShallowClone(XMLDocument *) const`
- 위치: tinyxml2.cpp:1366

```cpp
   1358          _document->SetError( XML_ERROR_PARSING_DECLARATION, _parseLineNum, 0 );
   1359      }
   1360      return p;
   1361  }
   1362  
   1363  
   1364  XMLNode* XMLDeclaration::ShallowClone( XMLDocument* doc ) const
   1365  {
>  1366      if ( !doc ) {
   1367          doc = _document;
   1368      }
   1369      XMLDeclaration* dec = doc->NewDeclaration( Value() );	// fixme: this will always allocate memory. Intern?
   1370      return dec;
   1371  }
   1372  
   1373  
   1374  bool XMLDeclaration::ShallowEqual( const XMLNode* compare ) const
```

## 22. `afterThis == addThis` 가 한 번도 참이 되지 않음

- 함수: `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`
- 위치: tinyxml2.cpp:1006

```cpp
    998      }
    999  
   1000      TIXMLASSERT( afterThis );
   1001  
   1002      if ( afterThis->_parent != this ) {
   1003          TIXMLASSERT( false );
   1004          return 0;
   1005      }
>  1006      if ( afterThis == addThis ) {
   1007          // Current state: BeforeThis -> AddThis -> OneAfterAddThis
   1008          // Now AddThis must disappear from it's location and then
   1009          // reappear between BeforeThis and OneAfterAddThis.
   1010          // So just leave it where it is.
   1011          return addThis;
   1012      }
   1013  
   1014      if ( afterThis->_next == 0 ) {
```

## 23. `visitor->VisitEnter( *this )` 가 한 번도 거짓이 되지 않음

- 함수: `XMLDocument::Accept(XMLVisitor *) const`
- 위치: tinyxml2.cpp:781

```cpp
    773      *node = returnNode;
    774      return p;
    775  }
    776  
    777  
    778  bool XMLDocument::Accept( XMLVisitor* visitor ) const
    779  {
    780      TIXMLASSERT( visitor );
>   781      if ( visitor->VisitEnter( *this ) ) {
    782          for ( const XMLNode* node=FirstChild(); node; node=node->NextSibling() ) {
    783              if ( !node->Accept( visitor ) ) {
    784                  break;
    785              }
    786          }
    787      }
    788      return visitor->VisitExit( *this );
    789  }
```

## 24. `IsPrefixHex(str)` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ToInt(const char *, int *)`
- 위치: tinyxml2.cpp:601

```cpp
    593  void XMLUtil::ToStr( uint64_t v, char* buffer, int bufferSize )
    594  {
    595      // horrible syntax trick to make the compiler happy about %llu
    596      TIXML_SNPRINTF(buffer, bufferSize, "%llu", static_cast<unsigned long long>(v));
    597  }
    598  
    599  bool XMLUtil::ToInt(const char* str, int* value)
    600  {
>   601      if (IsPrefixHex(str)) {
    602          unsigned v;
    603          if (TIXML_SSCANF(str, "%x", &v) == 1) {
    604              *value = static_cast<int>(v);
    605              return true;
    606          }
    607      }
    608      else {
    609          if (TIXML_SSCANF(str, "%d", value) == 1) {
```

## 25. `comment` 가 한 번도 거짓이 되지 않음

- 함수: `XMLComment::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1329

```cpp
   1321      return comment;
   1322  }
   1323  
   1324  
   1325  bool XMLComment::ShallowEqual( const XMLNode* compare ) const
   1326  {
   1327      TIXMLASSERT( compare );
   1328      const XMLComment* comment = compare->ToComment();
>  1329      return ( comment && XMLUtil::StringEqual( comment->Value(), Value() ));
   1330  }
   1331  
   1332  
   1333  bool XMLComment::Accept( XMLVisitor* visitor ) const
   1334  {
   1335      TIXMLASSERT( visitor );
   1336      return visitor->Visit( *this );
   1337  }
```

## 26. `!node->Accept( visitor )` 가 한 번도 참이 되지 않음

- 함수: `XMLDocument::Accept(XMLVisitor *) const`
- 위치: tinyxml2.cpp:783

```cpp
    775  }
    776  
    777  
    778  bool XMLDocument::Accept( XMLVisitor* visitor ) const
    779  {
    780      TIXMLASSERT( visitor );
    781      if ( visitor->VisitEnter( *this ) ) {
    782          for ( const XMLNode* node=FirstChild(); node; node=node->NextSibling() ) {
>   783              if ( !node->Accept( visitor ) ) {
    784                  break;
    785              }
    786          }
    787      }
    788      return visitor->VisitExit( *this );
    789  }
    790  
    791  
```

## 27. `input < 0x200000` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`
- 위치: tinyxml2.cpp:425

```cpp
    417          *length = 1;
    418      }
    419      else if ( input < 0x800 ) {
    420          *length = 2;
    421      }
    422      else if ( input < 0x10000 ) {
    423          *length = 3;
    424      }
>   425      else if ( input < 0x200000 ) {
    426          *length = 4;
    427      }
    428      else {
    429          *length = 0;    // This code won't convert this correctly anyway.
    430          return;
    431      }
    432  
    433      output += *length;
```

## 28. `*(p + 1) == 'x'` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::IsPrefixHex(const char *)`
- 위치: tinyxml2.h:588

```cpp
    580          return IsNameStartChar( ch )
    581                 || isdigit( ch )
    582                 || ch == '.'
    583                 || ch == '-';
    584      }
    585  
    586      inline static bool IsPrefixHex( const char* p) {
    587          p = SkipWhiteSpace(p, 0);
>   588          return p && *p == '0' && ( *(p + 1) == 'x' || *(p + 1) == 'X');
    589      }
    590  
    591      inline static bool StringEqual( const char* p, const char* q, int nChar=INT_MAX )  {
    592          if ( p == q ) {
    593              return true;
    594          }
    595          TIXMLASSERT( p );
    596          TIXMLASSERT( q );
```

## 29. `b` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:2132

```cpp
   2124  {
   2125      TIXMLASSERT( compare );
   2126      const XMLElement* other = compare->ToElement();
   2127      if ( other && XMLUtil::StringEqual( other->Name(), Name() )) {
   2128  
   2129          const XMLAttribute* a=FirstAttribute();
   2130          const XMLAttribute* b=other->FirstAttribute();
   2131  
>  2132          while ( a && b ) {
   2133              if ( !XMLUtil::StringEqual( a->Value(), b->Value() ) ) {
   2134                  return false;
   2135              }
   2136              a = a->Next();
   2137              b = b->Next();
   2138          }
   2139          if ( a || b ) {
   2140              // different count
```

## 30. `input < 0x10000` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`
- 위치: tinyxml2.cpp:422

```cpp
    414      const unsigned long FIRST_BYTE_MARK[7] = { 0x00, 0x00, 0xC0, 0xE0, 0xF0, 0xF8, 0xFC };
    415  
    416      if (input < 0x80) {
    417          *length = 1;
    418      }
    419      else if ( input < 0x800 ) {
    420          *length = 2;
    421      }
>   422      else if ( input < 0x10000 ) {
    423          *length = 3;
    424      }
    425      else if ( input < 0x200000 ) {
    426          *length = 4;
    427      }
    428      else {
    429          *length = 0;    // This code won't convert this correctly anyway.
    430          return;
```

## 31. `!doc` 가 한 번도 참이 되지 않음

- 함수: `XMLText::ShallowClone(XMLDocument *) const`
- 위치: tinyxml2.cpp:1268

```cpp
   1260          }
   1261      }
   1262      return 0;
   1263  }
   1264  
   1265  
   1266  XMLNode* XMLText::ShallowClone( XMLDocument* doc ) const
   1267  {
>  1268      if ( !doc ) {
   1269          doc = _document;
   1270      }
   1271      XMLText* text = doc->NewText( Value() );	// fixme: this will always allocate memory. Intern?
   1272      text->SetCData( this->CData() );
   1273      return text;
   1274  }
   1275  
   1276  
```

## 32. `text` 가 한 번도 거짓이 되지 않음

- 함수: `XMLText::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1281

```cpp
   1273      return text;
   1274  }
   1275  
   1276  
   1277  bool XMLText::ShallowEqual( const XMLNode* compare ) const
   1278  {
   1279      TIXMLASSERT( compare );
   1280      const XMLText* text = compare->ToText();
>  1281      return ( text && XMLUtil::StringEqual( text->Value(), Value() ) );
   1282  }
   1283  
   1284  
   1285  bool XMLText::Accept( XMLVisitor* visitor ) const
   1286  {
   1287      TIXMLASSERT( visitor );
   1288      return visitor->Visit( *this );
   1289  }
```

## 33. `case 4` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`
- 위치: tinyxml2.cpp:438

```cpp
    430          return;
    431      }
    432  
    433      output += *length;
    434  
    435      // Scary scary fall throughs are annotated with carefully designed comments
    436      // to suppress compiler warnings such as -Wimplicit-fallthrough in gcc
    437      switch (*length) {
>   438          case 4:
    439              --output;
    440              *output = static_cast<char>((input | BYTE_MARK) & BYTE_MASK);
    441              input >>= 6;
    442              TIXML_FALLTHROUGH;
    443          case 3:
    444              --output;
    445              *output = static_cast<char>((input | BYTE_MARK) & BYTE_MASK);
    446              input >>= 6;
```

## 34. `this->ToDocument()` 가 한 번도 참이 되지 않음

- 함수: `XMLNode::Value() const`
- 위치: tinyxml2.cpp:856

```cpp
    848  	}
    849  
    850  	return count;
    851  }
    852  
    853  const char* XMLNode::Value() const
    854  {
    855      // Edge case: XMLDocuments don't have a Value. Return null.
>   856      if ( this->ToDocument() )
    857          return 0;
    858      return _value.GetStr();
    859  }
    860  
    861  void XMLNode::SetValue( const char* str, bool staticMem )
    862  {
    863      if ( staticMem ) {
    864          _value.SetInternedStr( str );
```

## 35. `unknown` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUnknown::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1426

```cpp
   1418      return text;
   1419  }
   1420  
   1421  
   1422  bool XMLUnknown::ShallowEqual( const XMLNode* compare ) const
   1423  {
   1424      TIXMLASSERT( compare );
   1425      const XMLUnknown* unknown = compare->ToUnknown();
>  1426      return ( unknown && XMLUtil::StringEqual( unknown->Value(), Value() ));
   1427  }
   1428  
   1429  
   1430  bool XMLUnknown::Accept( XMLVisitor* visitor ) const
   1431  {
   1432      TIXMLASSERT( visitor );
   1433      return visitor->Visit( *this );
   1434  }
```

## 36. `element` 가 한 번도 참이 되지 않음

- 함수: `XMLNode::PreviousSiblingElement(const char *) const`
- 위치: tinyxml2.cpp:1070

```cpp
   1062      return 0;
   1063  }
   1064  
   1065  
   1066  const XMLElement* XMLNode::PreviousSiblingElement( const char* name ) const
   1067  {
   1068      for( const XMLNode* node = _prev; node; node = node->_prev ) {
   1069          const XMLElement* element = node->ToElementWithName( name );
>  1070          if ( element ) {
   1071              return element;
   1072          }
   1073      }
   1074      return 0;
   1075  }
   1076  
   1077  
   1078  char* XMLNode::ParseDeep( char* p, StrPair* parentEndTag, int* curLineNumPtr )
```

## 37. `b` 가 한 번도 참이 되지 않음

- 함수: `XMLElement::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:2139

```cpp
   2131  
   2132          while ( a && b ) {
   2133              if ( !XMLUtil::StringEqual( a->Value(), b->Value() ) ) {
   2134                  return false;
   2135              }
   2136              a = a->Next();
   2137              b = b->Next();
   2138          }
>  2139          if ( a || b ) {
   2140              // different count
   2141              return false;
   2142          }
   2143          return true;
   2144      }
   2145      return false;
   2146  }
   2147  
```

## 38. `declaration` 가 한 번도 거짓이 되지 않음

- 함수: `XMLDeclaration::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1378

```cpp
   1370      return dec;
   1371  }
   1372  
   1373  
   1374  bool XMLDeclaration::ShallowEqual( const XMLNode* compare ) const
   1375  {
   1376      TIXMLASSERT( compare );
   1377      const XMLDeclaration* declaration = compare->ToDeclaration();
>  1378      return ( declaration && XMLUtil::StringEqual( declaration->Value(), Value() ));
   1379  }
   1380  
   1381  
   1382  
   1383  bool XMLDeclaration::Accept( XMLVisitor* visitor ) const
   1384  {
   1385      TIXMLASSERT( visitor );
   1386      return visitor->Visit( *this );
```

## 39. `IsPrefixHex(str)` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ToInt64(const char *, int64_t *)`
- 위치: tinyxml2.cpp:670

```cpp
    662          return true;
    663      }
    664      return false;
    665  }
    666  
    667  
    668  bool XMLUtil::ToInt64(const char* str, int64_t* value)
    669  {
>   670      if (IsPrefixHex(str)) {
    671          unsigned long long v = 0;	// horrible syntax trick to make the compiler happy about %llx
    672          if (TIXML_SSCANF(str, "%llx", &v) == 1) {
    673              *value = static_cast<int64_t>(v);
    674              return true;
    675          }
    676      }
    677      else {
    678          long long v = 0;	// horrible syntax trick to make the compiler happy about %lld
```

## 40. `addThis->_document != _document` 가 한 번도 참이 되지 않음

- 함수: `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`
- 위치: tinyxml2.cpp:995

```cpp
    987      addThis->_parent = this;
    988      return addThis;
    989  }
    990  
    991  
    992  XMLNode* XMLNode::InsertAfterChild( XMLNode* afterThis, XMLNode* addThis )
    993  {
    994      TIXMLASSERT( addThis );
>   995      if ( addThis->_document != _document ) {
    996          TIXMLASSERT( false );
    997          return 0;
    998      }
    999  
   1000      TIXMLASSERT( afterThis );
   1001  
   1002      if ( afterThis->_parent != this ) {
   1003          TIXMLASSERT( false );
```

## 41. `afterThis->_parent != this` 가 한 번도 참이 되지 않음

- 함수: `XMLNode::InsertAfterChild(XMLNode *, XMLNode *)`
- 위치: tinyxml2.cpp:1002

```cpp
    994      TIXMLASSERT( addThis );
    995      if ( addThis->_document != _document ) {
    996          TIXMLASSERT( false );
    997          return 0;
    998      }
    999  
   1000      TIXMLASSERT( afterThis );
   1001  
>  1002      if ( afterThis->_parent != this ) {
   1003          TIXMLASSERT( false );
   1004          return 0;
   1005      }
   1006      if ( afterThis == addThis ) {
   1007          // Current state: BeforeThis -> AddThis -> OneAfterAddThis
   1008          // Now AddThis must disappear from it's location and then
   1009          // reappear between BeforeThis and OneAfterAddThis.
   1010          // So just leave it where it is.
```

## 42. `*(pu+2) == TIXML_UTF_LEAD_2` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ReadBOM(const char *, bool *)`
- 위치: tinyxml2.cpp:401

```cpp
    393  {
    394      TIXMLASSERT( p );
    395      TIXMLASSERT( bom );
    396      *bom = false;
    397      const unsigned char* pu = reinterpret_cast<const unsigned char*>(p);
    398      // Check for BOM:
    399      if (    *(pu+0) == TIXML_UTF_LEAD_0
    400              && *(pu+1) == TIXML_UTF_LEAD_1
>   401              && *(pu+2) == TIXML_UTF_LEAD_2 ) {
    402          *bom = true;
    403          p += 3;
    404      }
    405      TIXMLASSERT( p );
    406      return p;
    407  }
    408  
    409  
```

## 43. `_node` 가 한 번도 거짓이 되지 않음

- 함수: `XMLHandle::FirstChildElement(const char *)`
- 위치: tinyxml2.h:2075

```cpp
   2067      }
   2068  
   2069      /// Get the first child of this handle.
   2070      XMLHandle FirstChild() 													{
   2071          return XMLHandle( _node ? _node->FirstChild() : 0 );
   2072      }
   2073      /// Get the first child element of this handle.
   2074      XMLHandle FirstChildElement( const char* name = 0 )						{
>  2075          return XMLHandle( _node ? _node->FirstChildElement( name ) : 0 );
   2076      }
   2077      /// Get the last child of this handle.
   2078      XMLHandle LastChild()													{
   2079          return XMLHandle( _node ? _node->LastChild() : 0 );
   2080      }
   2081      /// Get the last child element of this handle.
   2082      XMLHandle LastChildElement( const char* name = 0 )						{
   2083          return XMLHandle( _node ? _node->LastChildElement( name ) : 0 );
```

## 44. `!XMLUtil::StringEqual( a->Value(), b->Value() )` 가 한 번도 참이 되지 않음

- 함수: `XMLElement::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:2133

```cpp
   2125      TIXMLASSERT( compare );
   2126      const XMLElement* other = compare->ToElement();
   2127      if ( other && XMLUtil::StringEqual( other->Name(), Name() )) {
   2128  
   2129          const XMLAttribute* a=FirstAttribute();
   2130          const XMLAttribute* b=other->FirstAttribute();
   2131  
   2132          while ( a && b ) {
>  2133              if ( !XMLUtil::StringEqual( a->Value(), b->Value() ) ) {
   2134                  return false;
   2135              }
   2136              a = a->Next();
   2137              b = b->Next();
   2138          }
   2139          if ( a || b ) {
   2140              // different count
   2141              return false;
```

## 45. `*(p + 2)` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUtil::GetCharacterRef(const char *, char *, int *)`
- 위치: tinyxml2.cpp:470

```cpp
    462  
    463  const char* XMLUtil::GetCharacterRef(const char* p, char* value, int* length)
    464  {
    465      // Assume an entity, and pull it out.
    466      *length = 0;
    467  
    468      static const uint32_t MAX_CODE_POINT = 0x10FFFF;
    469  
>   470      if (*(p + 1) == '#' && *(p + 2)) {
    471          uint32_t ucs = 0;
    472          ptrdiff_t delta = 0;
    473          uint32_t mult = 1;
    474          static const char SEMICOLON = ';';
    475  
    476          bool hex = false;
    477          uint32_t radix = 10;
    478          const char* q = 0;
```

## 46. `!value` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::Attribute(const char *, const char *) const`
- 위치: tinyxml2.cpp:1639

```cpp
   1631  
   1632  
   1633  const char* XMLElement::Attribute( const char* name, const char* value ) const
   1634  {
   1635      const XMLAttribute* a = FindAttribute( name );
   1636      if ( !a ) {
   1637          return 0;
   1638      }
>  1639      if ( !value || XMLUtil::StringEqual( a->Value(), value )) {
   1640          return a->Value();
   1641      }
   1642      return 0;
   1643  }
   1644  
   1645  int XMLElement::IntAttribute(const char* name, int defaultValue) const
   1646  {
   1647  	int i = defaultValue;
```

## 47. `!doc` 가 한 번도 참이 되지 않음

- 함수: `XMLElement::ShallowClone(XMLDocument *) const`
- 위치: tinyxml2.cpp:2112

```cpp
   2104      p = XMLNode::ParseDeep( p, parentEndTag, curLineNumPtr );
   2105      return p;
   2106  }
   2107  
   2108  
   2109  
   2110  XMLNode* XMLElement::ShallowClone( XMLDocument* doc ) const
   2111  {
>  2112      if ( !doc ) {
   2113          doc = _document;
   2114      }
   2115      XMLElement* element = doc->NewElement( Value() );					// fixme: this will always allocate memory. Intern?
   2116      for( const XMLAttribute* a=FirstAttribute(); a; a=a->Next() ) {
   2117          element->SetAttribute( a->Name(), a->Value() );					// fixme: this will always allocate memory. Intern?
   2118      }
   2119      return element;
   2120  }
```

## 48. `*(p + 1) == 'X'` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::IsPrefixHex(const char *)`
- 위치: tinyxml2.h:588

```cpp
    580          return IsNameStartChar( ch )
    581                 || isdigit( ch )
    582                 || ch == '.'
    583                 || ch == '-';
    584      }
    585  
    586      inline static bool IsPrefixHex( const char* p) {
    587          p = SkipWhiteSpace(p, 0);
>   588          return p && *p == '0' && ( *(p + 1) == 'x' || *(p + 1) == 'X');
    589      }
    590  
    591      inline static bool StringEqual( const char* p, const char* q, int nChar=INT_MAX )  {
    592          if ( p == q ) {
    593              return true;
    594          }
    595          TIXMLASSERT( p );
    596          TIXMLASSERT( q );
```

## 49. `XMLUtil::StringEqual( text->Value(), Value() )` 가 한 번도 거짓이 되지 않음

- 함수: `XMLText::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1281

```cpp
   1273      return text;
   1274  }
   1275  
   1276  
   1277  bool XMLText::ShallowEqual( const XMLNode* compare ) const
   1278  {
   1279      TIXMLASSERT( compare );
   1280      const XMLText* text = compare->ToText();
>  1281      return ( text && XMLUtil::StringEqual( text->Value(), Value() ) );
   1282  }
   1283  
   1284  
   1285  bool XMLText::Accept( XMLVisitor* visitor ) const
   1286  {
   1287      TIXMLASSERT( visitor );
   1288      return visitor->Visit( *this );
   1289  }
```

## 50. `InsertEndChild(node)` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::InsertNewUnknown(const char *)`
- 위치: tinyxml2.cpp:2072

```cpp
   2064  {
   2065      XMLDeclaration* node = _document->NewDeclaration(text);
   2066      return InsertEndChild(node) ? node : 0;
   2067  }
   2068  
   2069  XMLUnknown* XMLElement::InsertNewUnknown(const char* text)
   2070  {
   2071      XMLUnknown* node = _document->NewUnknown(text);
>  2072      return InsertEndChild(node) ? node : 0;
   2073  }
   2074  
   2075  
   2076  
   2077  //
   2078  //	<ele></ele>
   2079  //	<ele>foo<b>bar</b></ele>
   2080  //
```

## 51. `!doc` 가 한 번도 참이 되지 않음

- 함수: `XMLUnknown::ShallowClone(XMLDocument *) const`
- 위치: tinyxml2.cpp:1414

```cpp
   1406          _document->SetError( XML_ERROR_PARSING_UNKNOWN, _parseLineNum, 0 );
   1407      }
   1408      return p;
   1409  }
   1410  
   1411  
   1412  XMLNode* XMLUnknown::ShallowClone( XMLDocument* doc ) const
   1413  {
>  1414      if ( !doc ) {
   1415          doc = _document;
   1416      }
   1417      XMLUnknown* text = doc->NewUnknown( Value() );	// fixme: this will always allocate memory. Intern?
   1418      return text;
   1419  }
   1420  
   1421  
   1422  bool XMLUnknown::ShallowEqual( const XMLNode* compare ) const
```

## 52. `ucs > MAX_CODE_POINT` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::GetCharacterRef(const char *, char *, int *)`
- 위치: tinyxml2.cpp:539

```cpp
    531              ucs += digitScaled;
    532              mult *= radix;
    533              if (mult > MAX_CODE_POINT) {
    534                  mult = MAX_CODE_POINT;
    535              }
    536              --q;
    537          }
    538          // Out of range:
>   539          if (ucs > MAX_CODE_POINT) {
    540              return 0;
    541          }
    542          // convert the UCS to UTF-8
    543          ConvertUTF32ToUTF8(ucs, value, length);
    544          if (*length == 0) {
    545              // If *length is 0, ConvertUTF32ToUTF8 rejected the code point.
    546              // Fail safely.
    547              return 0;
```

## 53. `node->_parent` 가 한 번도 참이 되지 않음

- 함수: `XMLDocument::DeleteNode(XMLNode *)`
- 위치: tinyxml2.cpp:2337

```cpp
   2329      return fp;
   2330  }
   2331  
   2332  void XMLDocument::DeleteNode( XMLNode* node )	{   
   2333      if(node == 0) {
   2334          return; // check for null pointer
   2335      }
   2336      TIXMLASSERT(node->_document == this);
>  2337      if (node->_parent) {
   2338          node->_parent->DeleteChild( node );
   2339      }
   2340      else {
   2341          // Isn't in the tree.
   2342          // Use the parent delete.
   2343          // Also, we need to mark it tracked: we 'know'
   2344          // it was never used.
   2345          node->_memPool->SetTracked();
```

## 54. `XMLUtil::StringEqual( declaration->Value(), Value() )` 가 한 번도 거짓이 되지 않음

- 함수: `XMLDeclaration::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:1378

```cpp
   1370      return dec;
   1371  }
   1372  
   1373  
   1374  bool XMLDeclaration::ShallowEqual( const XMLNode* compare ) const
   1375  {
   1376      TIXMLASSERT( compare );
   1377      const XMLDeclaration* declaration = compare->ToDeclaration();
>  1378      return ( declaration && XMLUtil::StringEqual( declaration->Value(), Value() ));
   1379  }
   1380  
   1381  
   1382  
   1383  bool XMLDeclaration::Accept( XMLVisitor* visitor ) const
   1384  {
   1385      TIXMLASSERT( visitor );
   1386      return visitor->Visit( *this );
```

## 55. `streamer` 가 한 번도 거짓이 되지 않음

- 함수: `XMLDocument::Print(XMLPrinter *) const`
- 위치: tinyxml2.cpp:2488

```cpp
   2480          _commentPool.Clear();
   2481      }
   2482      return _errorID;
   2483  }
   2484  
   2485  
   2486  void XMLDocument::Print( XMLPrinter* streamer ) const
   2487  {
>  2488      if ( streamer ) {
   2489          Accept( streamer );
   2490      }
   2491      else {
   2492          XMLPrinter stdoutStreamer( stdout );
   2493          Accept( &stdoutStreamer );
   2494      }
   2495  }
   2496  
```

## 56. `_unlinked.Size()` 가 한 번도 참이 되지 않음

- 함수: `XMLDocument::Clear()`
- 위치: tinyxml2.cpp:2233

```cpp
   2225  			break;
   2226  		}
   2227  	}
   2228  }
   2229  
   2230  void XMLDocument::Clear()
   2231  {
   2232      DeleteChildren();
>  2233  	while( _unlinked.Size()) {
   2234  		DeleteNode(_unlinked[0]);	// Will remove from _unlinked as part of delete.
   2235  	}
   2236  
   2237  #ifdef TINYXML2_DEBUG
   2238      const bool hadError = Error();
   2239  #endif
   2240      ClearError();
   2241  
```

## 57. `nBytes == static_cast<size_t>(-1)` 가 한 번도 거짓이 되지 않음

- 함수: `XMLDocument::Parse(const char *, size_t)`
- 위치: tinyxml2.cpp:2463

```cpp
   2455  XMLError XMLDocument::Parse( const char* xml, size_t nBytes )
   2456  {
   2457      Clear();
   2458  
   2459      if ( nBytes == 0 || !xml || !*xml ) {
   2460          SetError( XML_ERROR_EMPTY_DOCUMENT, 0, 0 );
   2461          return _errorID;
   2462      }
>  2463      if ( nBytes == static_cast<size_t>(-1) ) {
   2464          nBytes = strlen( xml );
   2465      }
   2466      TIXMLASSERT( _charBuffer == 0 );
   2467      _charBuffer = new char[ nBytes+1 ];
   2468      memcpy( _charBuffer, xml, nBytes );
   2469      _charBuffer[nBytes] = 0;
   2470  
   2471      Parse();
```

## 58. `*(p + 1) == '#'` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUtil::GetCharacterRef(const char *, char *, int *)`
- 위치: tinyxml2.cpp:470

```cpp
    462  
    463  const char* XMLUtil::GetCharacterRef(const char* p, char* value, int* length)
    464  {
    465      // Assume an entity, and pull it out.
    466      *length = 0;
    467  
    468      static const uint32_t MAX_CODE_POINT = 0x10FFFF;
    469  
>   470      if (*(p + 1) == '#' && *(p + 2)) {
    471          uint32_t ucs = 0;
    472          ptrdiff_t delta = 0;
    473          uint32_t mult = 1;
    474          static const char SEMICOLON = ';';
    475  
    476          bool hex = false;
    477          uint32_t radix = 10;
    478          const char* q = 0;
```

## 59. `InsertEndChild(node)` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::InsertNewChildElement(const char *)`
- 위치: tinyxml2.cpp:2048

```cpp
   2040      attrib->_memPool->SetTracked();
   2041      return attrib;
   2042  }
   2043  
   2044  
   2045  XMLElement* XMLElement::InsertNewChildElement(const char* name)
   2046  {
   2047      XMLElement* node = _document->NewElement(name);
>  2048      return InsertEndChild(node) ? node : 0;
   2049  }
   2050  
   2051  XMLComment* XMLElement::InsertNewComment(const char* comment)
   2052  {
   2053      XMLComment* node = _document->NewComment(comment);
   2054      return InsertEndChild(node) ? node : 0;
   2055  }
   2056  
```

## 60. `p` 가 한 번도 거짓이 되지 않음

- 함수: `XMLUtil::IsPrefixHex(const char *)`
- 위치: tinyxml2.h:588

```cpp
    580          return IsNameStartChar( ch )
    581                 || isdigit( ch )
    582                 || ch == '.'
    583                 || ch == '-';
    584      }
    585  
    586      inline static bool IsPrefixHex( const char* p) {
    587          p = SkipWhiteSpace(p, 0);
>   588          return p && *p == '0' && ( *(p + 1) == 'x' || *(p + 1) == 'X');
    589      }
    590  
    591      inline static bool StringEqual( const char* p, const char* q, int nChar=INT_MAX )  {
    592          if ( p == q ) {
    593              return true;
    594          }
    595          TIXMLASSERT( p );
    596          TIXMLASSERT( q );
```

## 61. `node == 0` 가 한 번도 참이 되지 않음

- 함수: `XMLDocument::DeleteNode(XMLNode *)`
- 위치: tinyxml2.cpp:2333

```cpp
   2325      }
   2326  #else
   2327      FILE* fp = fopen( filepath, mode );
   2328  #endif
   2329      return fp;
   2330  }
   2331  
   2332  void XMLDocument::DeleteNode( XMLNode* node )	{   
>  2333      if(node == 0) {
   2334          return; // check for null pointer
   2335      }
   2336      TIXMLASSERT(node->_document == this);
   2337      if (node->_parent) {
   2338          node->_parent->DeleteChild( node );
   2339      }
   2340      else {
   2341          // Isn't in the tree.
```

## 62. `other` 가 한 번도 거짓이 되지 않음

- 함수: `XMLElement::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:2127

```cpp
   2119      return element;
   2120  }
   2121  
   2122  
   2123  bool XMLElement::ShallowEqual( const XMLNode* compare ) const
   2124  {
   2125      TIXMLASSERT( compare );
   2126      const XMLElement* other = compare->ToElement();
>  2127      if ( other && XMLUtil::StringEqual( other->Name(), Name() )) {
   2128  
   2129          const XMLAttribute* a=FirstAttribute();
   2130          const XMLAttribute* b=other->FirstAttribute();
   2131  
   2132          while ( a && b ) {
   2133              if ( !XMLUtil::StringEqual( a->Value(), b->Value() ) ) {
   2134                  return false;
   2135              }
```

## 63. `_node` 가 한 번도 거짓이 되지 않음

- 함수: `XMLConstHandle::LastChildElement(const char *) const`
- 위치: tinyxml2.h:2157

```cpp
   2149      }
   2150      const XMLConstHandle FirstChildElement( const char* name = 0 ) const				{
   2151          return XMLConstHandle( _node ? _node->FirstChildElement( name ) : 0 );
   2152      }
   2153      const XMLConstHandle LastChild()	const										{
   2154          return XMLConstHandle( _node ? _node->LastChild() : 0 );
   2155      }
   2156      const XMLConstHandle LastChildElement( const char* name = 0 ) const				{
>  2157          return XMLConstHandle( _node ? _node->LastChildElement( name ) : 0 );
   2158      }
   2159      const XMLConstHandle PreviousSibling() const									{
   2160          return XMLConstHandle( _node ? _node->PreviousSibling() : 0 );
   2161      }
   2162      const XMLConstHandle PreviousSiblingElement( const char* name = 0 ) const		{
   2163          return XMLConstHandle( _node ? _node->PreviousSiblingElement( name ) : 0 );
   2164      }
   2165      const XMLConstHandle NextSibling() const										{
```

## 64. `*(pu+1) == TIXML_UTF_LEAD_1` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ReadBOM(const char *, bool *)`
- 위치: tinyxml2.cpp:400

```cpp
    392  const char* XMLUtil::ReadBOM( const char* p, bool* bom )
    393  {
    394      TIXMLASSERT( p );
    395      TIXMLASSERT( bom );
    396      *bom = false;
    397      const unsigned char* pu = reinterpret_cast<const unsigned char*>(p);
    398      // Check for BOM:
    399      if (    *(pu+0) == TIXML_UTF_LEAD_0
>   400              && *(pu+1) == TIXML_UTF_LEAD_1
    401              && *(pu+2) == TIXML_UTF_LEAD_2 ) {
    402          *bom = true;
    403          p += 3;
    404      }
    405      TIXMLASSERT( p );
    406      return p;
    407  }
    408  
```

## 65. `addThis->_document != _document` 가 한 번도 참이 되지 않음

- 함수: `XMLNode::InsertEndChild(XMLNode *)`
- 위치: tinyxml2.cpp:934

```cpp
    926  	TIXMLASSERT(node->_parent == 0);
    927      DeleteNode( node );
    928  }
    929  
    930  
    931  XMLNode* XMLNode::InsertEndChild( XMLNode* addThis )
    932  {
    933      TIXMLASSERT( addThis );
>   934      if ( addThis->_document != _document ) {
    935          TIXMLASSERT( false );
    936          return 0;
    937      }
    938      InsertChildPreamble( addThis );
    939  
    940      if ( _lastChild ) {
    941          TIXMLASSERT( _firstChild );
    942          TIXMLASSERT( _lastChild->_next == 0 );
```

## 66. `WhitespaceMode() == PEDANTIC_WHITESPACE` 가 한 번도 참이 되지 않음

- 함수: `XMLDocument::Identify(char *, XMLNode **, bool)`
- 위치: tinyxml2.cpp:752

```cpp
    744      else if ( XMLUtil::StringEqual( p, dtdHeader, dtdHeaderLen ) ) {
    745          returnNode = CreateUnlinkedNode<XMLUnknown>( _commentPool );
    746          returnNode->_parseLineNum = _parseCurLineNum;
    747          p += dtdHeaderLen;
    748      }
    749      else if ( XMLUtil::StringEqual( p, elementHeader, elementHeaderLen ) ) {
    750  
    751          // Preserve whitespace pedantically before closing tag, when it's immediately after opening tag
>   752          if (WhitespaceMode() == PEDANTIC_WHITESPACE && first && p != start && *(p + elementHeaderLen) == '/') {
    753              returnNode = CreateUnlinkedNode<XMLText>(_textPool);
    754              returnNode->_parseLineNum = startLine;
    755              p = start;	// Back it up, all the text counts.
    756              _parseCurLineNum = startLine;
    757          }
    758          else {
    759              returnNode = CreateUnlinkedNode<XMLElement>(_elementPool);
    760              returnNode->_parseLineNum = _parseCurLineNum;
```

## 67. `doc.HasBOM()` 가 한 번도 참이 되지 않음

- 함수: `XMLPrinter::VisitEnter(const XMLDocument &)`
- 위치: tinyxml2.cpp:2973

```cpp
   2965      Write( value );
   2966      Putc( '>' );
   2967  }
   2968  
   2969  
   2970  bool XMLPrinter::VisitEnter( const XMLDocument& doc )
   2971  {
   2972      _processEntities = doc.ProcessEntities();
>  2973      if ( doc.HasBOM() ) {
   2974          PushHeader( true, false );
   2975      }
   2976      return true;
   2977  }
   2978  
   2979  
   2980  bool XMLPrinter::VisitEnter( const XMLElement& element, const XMLAttribute* attribute )
   2981  {
```

## 68. `default` 가 한 번도 참이 되지 않음

- 함수: `XMLUtil::ConvertUTF32ToUTF8(unsigned long, char *, int *)`
- 위치: tinyxml2.cpp:457

```cpp
    449              --output;
    450              *output = static_cast<char>((input | BYTE_MARK) & BYTE_MASK);
    451              input >>= 6;
    452              TIXML_FALLTHROUGH;
    453          case 1:
    454              --output;
    455              *output = static_cast<char>(input | FIRST_BYTE_MARK[*length]);
    456              break;
>   457          default:
    458              TIXMLASSERT( false );
    459      }
    460  }
    461  
    462  
    463  const char* XMLUtil::GetCharacterRef(const char* p, char* value, int* length)
    464  {
    465      // Assume an entity, and pull it out.
```

## 69. `a` 가 한 번도 참이 되지 않음

- 함수: `XMLElement::ShallowEqual(const XMLNode *) const`
- 위치: tinyxml2.cpp:2139

```cpp
   2131  
   2132          while ( a && b ) {
   2133              if ( !XMLUtil::StringEqual( a->Value(), b->Value() ) ) {
   2134                  return false;
   2135              }
   2136              a = a->Next();
   2137              b = b->Next();
   2138          }
>  2139          if ( a || b ) {
   2140              // different count
   2141              return false;
   2142          }
   2143          return true;
   2144      }
   2145      return false;
   2146  }
   2147  
```
