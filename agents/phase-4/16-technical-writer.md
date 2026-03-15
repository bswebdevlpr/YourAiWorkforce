# Technical Writer Agent (TWA) - Phase 4

> **역할**: API 문서화 및 개발자 가이드 작성
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐☆☆

## 📥 입력 파일

- ✅ **필수**: 모든 API 라우트 (`src/app/api/`)
- ✅ **필수**: 데이터베이스 스키마 (`prisma/schema.prisma`)
- ✅ **필수**: 기존 README.md

---

## 🔨 작업 Step-by-Step

### Step 1: API 문서 구조 설계 (15분)

```markdown
# API 문서 구조

docs/
├── api/
│   ├── README.md           # API 개요
│   ├── authentication.md   # 인증 (필요 시)
│   ├── rate-limiting.md    # Rate limiting
│   ├── endpoints/
│   │   ├── characters.md   # /api/characters
│   │   ├── search.md       # /api/search
│   │   ├── compare.md      # /api/compare
│   │   └── ...
│   └── examples.md         # 사용 예시
```

**체크리스트**:
- [ ] API 문서 디렉토리 생성
- [ ] 엔드포인트별 문서 파일 생성

---

### Step 2: API 개요 문서 (20min)

```markdown
# API 개요

## 기본 정보

- **Base URL**: `https://example.com/api`
- **응답 형식**: JSON
- **인코딩**: UTF-8
- **Rate Limit**: 10 요청 / 10초

## 공통 응답 형식

### 성공 응답

\`\`\`json
{
  "success": true,
  "data": { /* 데이터 */ }
}
\`\`\`

### 에러 응답

\`\`\`json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
\`\`\`

## 에러 코드

| 코드 | HTTP 상태 | 설명 |
|------|-----------|------|
| `INVALID_INPUT` | 400 | 잘못된 요청 파라미터 |
| `NOT_FOUND` | 404 | 리소스를 찾을 수 없음 |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit 초과 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |

## Rate Limiting

모든 API 요청은 rate limiting이 적용됩니다:

- **제한**: 10 요청 / 10초
- **식별**: IP 주소 기반
- **헤더**:
  - `X-RateLimit-Limit`: 최대 요청 수
  - `X-RateLimit-Remaining`: 남은 요청 수
  - `X-RateLimit-Reset`: 리셋 시간 (Unix timestamp)

### 예시

\`\`\`http
HTTP/1.1 200 OK
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1640000000
\`\`\`

## 페이지네이션

목록 API는 페이지네이션을 지원합니다:

### 쿼리 파라미터

- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 항목 수 (기본값: 20, 최대: 100)

### 응답

\`\`\`json
{
  "success": true,
  "data": {
    "items": [ /* 항목 배열 */ ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 10000,
      "totalPages": 500
    }
  }
}
\`\`\`
```

**체크리스트**:
- [ ] API 개요 작성
- [ ] 공통 응답 형식 정의
- [ ] 에러 코드 문서화
- [ ] Rate limiting 설명
- [ ] 페이지네이션 설명

---

### Step 3: 엔드포인트별 문서 (60-90분)

각 API 엔드포인트에 대해 다음 형식으로 문서를 작성하세요:

```markdown
# GET /api/characters

한자 목록을 조회합니다.

## 요청

### HTTP Method
\`GET\`

### URL
\`/api/characters\`

### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `page` | number | ❌ | 1 | 페이지 번호 |
| `limit` | number | ❌ | 20 | 페이지당 항목 수 (최대 100) |
| `country` | string | ❌ | - | 국가 필터 (`KOREA`, `JAPAN`, `CHINA`) |
| `search` | string | ❌ | - | 검색 키워드 |

### 예시 요청

\`\`\`bash
curl -X GET "https://example.com/api/characters?page=1&limit=10&country=KOREA"
\`\`\`

## 응답

### 성공 응답 (200 OK)

\`\`\`json
{
  "success": true,
  "data": {
    "characters": [
      {
        "id": "clx123456",
        "char": "愛",
        "unicode": "U+611B",
        "meanings": ["love", "affection"],
        "pronunciations": {
          "korea": ["애", "ai"],
          "japan": ["あい", "ai"],
          "china": ["ài"]
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 10000,
      "totalPages": 1000
    }
  }
}
\`\`\`

### 에러 응답

#### 400 Bad Request

\`\`\`json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Invalid country parameter. Must be one of: KOREA, JAPAN, CHINA"
  }
}
\`\`\`

#### 429 Too Many Requests

\`\`\`json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later."
  }
}
\`\`\`

## 응답 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | 문자 고유 ID |
| `char` | string | 한자 문자 |
| `unicode` | string | Unicode 코드포인트 |
| `meanings` | string[] | 의미 배열 |
| `pronunciations.korea` | string[] | 한국어 발음 |
| `pronunciations.japan` | string[] | 일본어 발음 |
| `pronunciations.china` | string[] | 중국어 발음 |

## 예시 코드

### JavaScript (fetch)

\`\`\`javascript
async function getCharacters(page = 1, country = null) {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: '20',
  });

  if (country) {
    params.append('country', country);
  }

  const response = await fetch(`https://example.com/api/characters?${params}`);
  const data = await response.json();

  if (data.success) {
    return data.data.characters;
  } else {
    throw new Error(data.error.message);
  }
}

// 사용 예시
const characters = await getCharacters(1, 'KOREA');
console.log(characters);
\`\`\`

### Python (requests)

\`\`\`python
import requests

def get_characters(page=1, country=None):
    params = {
        'page': page,
        'limit': 20,
    }

    if country:
        params['country'] = country

    response = requests.get(
        'https://example.com/api/characters',
        params=params
    )

    data = response.json()

    if data['success']:
        return data['data']['characters']
    else:
        raise Exception(data['error']['message'])

# 사용 예시
characters = get_characters(page=1, country='KOREA')
print(characters)
\`\`\`

### cURL

\`\`\`bash
# 기본 요청
curl -X GET "https://example.com/api/characters"

# 필터링
curl -X GET "https://example.com/api/characters?country=KOREA&page=2"

# 검색
curl -X GET "https://example.com/api/characters?search=love"
\`\`\`

## 참고 사항

- 검색은 의미(meanings) 필드에서 부분 일치 검색을 수행합니다
- 페이지 번호는 1부터 시작합니다
- `limit`은 최대 100까지 설정 가능합니다
```

**각 엔드포인트에 대해 반복**:
- `/api/characters`
- `/api/characters/[id]`
- `/api/search`
- `/api/compare`
- `/api/false-friends`
- 기타 모든 API

**체크리스트**:
- [ ] 모든 엔드포인트 문서화
- [ ] 요청 파라미터 명시
- [ ] 응답 형식 예시
- [ ] 에러 케이스 문서화
- [ ] 예시 코드 (JavaScript, Python, cURL)

---

### Step 4: 사용 예시 및 튜토리얼 (20분)

```markdown
# API 사용 예시

## 시나리오 1: 한자 검색 및 상세 정보 조회

### 1단계: 검색

\`\`\`javascript
const response = await fetch('https://example.com/api/search?q=love');
const data = await response.json();

const firstCharacter = data.data.characters[0];
console.log(firstCharacter); // { id: "...", char: "愛", ... }
\`\`\`

### 2단계: 상세 정보 조회

\`\`\`javascript
const detailResponse = await fetch(`https://example.com/api/characters/${firstCharacter.id}`);
const detailData = await detailResponse.json();

console.log(detailData.data);
// {
//   character: { ... },
//   pronunciations: [ ... ],
//   meanings: [ ... ],
//   variants: [ ... ]
// }
\`\`\`

## 시나리오 2: 한자 비교

\`\`\`javascript
const compareResponse = await fetch(
  'https://example.com/api/compare?chars=愛,恋'
);
const compareData = await compareResponse.json();

console.log(compareData.data.comparison);
// {
//   characters: [ ... ],
//   similarities: {
//     visual: 75.2,
//     meaning: 82.5,
//   },
//   isFalseFriend: false
// }
\`\`\`

## 시나리오 3: False Friends 조회

\`\`\`javascript
const falseFriendsResponse = await fetch(
  'https://example.com/api/false-friends?page=1'
);
const falseFriendsData = await falseFriendsResponse.json();

console.log(falseFriendsData.data.falseFriends);
// [
//   {
//     char1: "手",
//     char2: "毛",
//     visualSimilarity: 85.2,
//     meaningSimilarity: 12.3
//   },
//   ...
// ]
\`\`\`
```

**체크리스트**:
- [ ] 일반적인 사용 시나리오 3-5개 작성
- [ ] 단계별 예시 코드
- [ ] 실제 응답 데이터 예시

---

### Step 5: API 문서 검증 (15분)

```bash
# OpenAPI 스키마 생성 (선택)
npx swagger-jsdoc -d swaggerDef.js src/app/api/**/*.ts -o docs/api/openapi.yaml
```

**체크리스트**:
- [ ] 모든 엔드포인트 문서 완성
- [ ] 예시 코드 테스트 (실제 실행 가능)
- [ ] 링크 깨짐 확인
- [ ] 오타 및 문법 검토

---

## 📤 출력 파일

1. **API 문서**:
   - `docs/api/README.md`
   - `docs/api/rate-limiting.md`
   - `docs/api/endpoints/characters.md`
   - `docs/api/endpoints/search.md`
   - `docs/api/endpoints/compare.md`
   - `docs/api/endpoints/false-friends.md`
   - `docs/api/examples.md`

2. **OpenAPI 스키마** (선택):
   - `docs/api/openapi.yaml`

---

## ✅ 완료 체크리스트

- [ ] API 개요 문서 작성
- [ ] 모든 엔드포인트 문서화 (8개 이상)
- [ ] 요청/응답 예시 포함
- [ ] 예시 코드 작성 (JavaScript, Python, cURL)
- [ ] 사용 시나리오 3-5개 작성
- [ ] 모든 링크 검증
- [ ] 오타 및 문법 검토
- [ ] Git 커밋:
  ```bash
  git add docs/api/
  git commit -m "docs: API 문서 작성 (Phase 4)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-4/17-qa-lead.md를 읽고 QLA로 작동해주세요"
```

---

## 💡 TriHanzi 실제 API 문서

**API 엔드포인트** (8개):

### 1. `/api/characters`
- **Method**: GET
- **설명**: 한자 목록 조회
- **쿼리**: `page`, `limit`, `country`, `search`
- **응답**: 페이지네이션된 문자 목록

### 2. `/api/characters/[id]`
- **Method**: GET
- **설명**: 한자 상세 정보
- **응답**: 문자, 발음, 의미, 변형

### 3. `/api/characters/[id]/analysis`
- **Method**: GET
- **설명**: 한자 분석 (유사 문자, 통계)
- **응답**: 분석 데이터

### 4. `/api/characters/[id]/similar`
- **Method**: GET
- **설명**: 유사 문자 조회
- **응답**: 유사도 기반 정렬

### 5. `/api/characters/autocomplete`
- **Method**: GET
- **설명**: 자동완성
- **쿼리**: `q`
- **응답**: 최대 10개 제안

### 6. `/api/search`
- **Method**: GET
- **설명**: 통합 검색
- **쿼리**: `q`, `filters`, `page`
- **응답**: 검색 결과

### 7. `/api/compare`
- **Method**: GET
- **설명**: 한자 비교
- **쿼리**: `chars` (쉼표 구분)
- **응답**: 비교 메타데이터

### 8. `/api/false-friends`
- **Method**: GET
- **설명**: False Friends 목록
- **쿼리**: `page`, `limit`
- **응답**: False Friends 쌍

**문서 구조**:
```
docs/api/
├── README.md (API 개요)
├── endpoints/
│   ├── characters.md
│   ├── search.md
│   ├── compare.md
│   └── false-friends.md
└── examples.md (사용 예시)
```

**예시 코드**:
- JavaScript (fetch)
- Python (requests)
- cURL
- Next.js (server component)
