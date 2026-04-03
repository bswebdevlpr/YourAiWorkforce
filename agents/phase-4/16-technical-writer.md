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
│   │   ├── [resources].md  # /api/[resources]
│   │   ├── search.md       # /api/search
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
# GET /api/[resources]

[Resource] 목록을 조회합니다.

## 요청

### HTTP Method
\`GET\`

### URL
\`/api/[resources]\`

### 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `page` | number | ❌ | 1 | 페이지 번호 |
| `limit` | number | ❌ | 20 | 페이지당 항목 수 (최대 100) |
| `category` | string | ❌ | - | 카테고리 필터 |
| `search` | string | ❌ | - | 검색 키워드 |

### 예시 요청

\`\`\`bash
curl -X GET "https://example.com/api/[resources]?page=1&limit=10&category=[category]"
\`\`\`

## 응답

### 성공 응답 (200 OK)

\`\`\`json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "clx123456",
        "name": "[Resource Name]",
        "description": "[Resource description]",
        "category": "[category]",
        "metadata": { }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1000,
      "totalPages": 100
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
    "message": "Invalid category parameter."
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
| `id` | string | 리소스 고유 ID |
| `name` | string | 리소스 이름 |
| `description` | string | 리소스 설명 |
| `category` | string | 카테고리 |
| `metadata` | object | 도메인별 메타데이터 |

## 예시 코드

### JavaScript (fetch)

\`\`\`javascript
async function getResources(page = 1, category = null) {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: '20',
  });

  if (category) {
    params.append('category', category);
  }

  const response = await fetch(`https://example.com/api/[resources]?${params}`);
  const data = await response.json();

  if (data.success) {
    return data.data.items;
  } else {
    throw new Error(data.error.message);
  }
}

// 사용 예시
const items = await getResources(1, '[category]');
console.log(items);
\`\`\`

### Python (requests)

\`\`\`python
import requests

def get_resources(page=1, category=None):
    params = {
        'page': page,
        'limit': 20,
    }

    if category:
        params['category'] = category

    response = requests.get(
        'https://example.com/api/[resources]',
        params=params
    )

    data = response.json()

    if data['success']:
        return data['data']['items']
    else:
        raise Exception(data['error']['message'])

# 사용 예시
items = get_resources(page=1, category='[category]')
print(items)
\`\`\`

### cURL

\`\`\`bash
# 기본 요청
curl -X GET "https://example.com/api/[resources]"

# 필터링
curl -X GET "https://example.com/api/[resources]?category=[category]&page=2"

# 검색
curl -X GET "https://example.com/api/[resources]?search=keyword"
\`\`\`

## 참고 사항

- 검색은 주요 텍스트 필드에서 부분 일치 검색을 수행한다
- 페이지 번호는 1부터 시작한다
- `limit`은 최대 100까지 설정 가능하다
```

**각 엔드포인트에 대해 반복**:
- `/api/[resources]`
- `/api/[resources]/[id]`
- `/api/search`
- `src/app/api/` 디렉토리의 모든 public 라우트를 문서화한다. `_internal/` 접두사가 붙은 라우트는 제외한다.

모든 코드 예시에 에러 처리를 포함한다:
```javascript
// JavaScript 예시
const response = await fetch('/api/[resources]?q=keyword');
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const data = await response.json();
```

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

## 시나리오 1: 검색 및 상세 정보 조회

### 1단계: 검색

\`\`\`javascript
const response = await fetch('https://example.com/api/search?q=keyword');
const data = await response.json();

const firstItem = data.data.items[0];
console.log(firstItem); // { id: "...", name: "[Resource]", ... }
\`\`\`

### 2단계: 상세 정보 조회

\`\`\`javascript
const detailResponse = await fetch(`https://example.com/api/[resources]/${firstItem.id}`);
const detailData = await detailResponse.json();

console.log(detailData.data);
// {
//   item: { ... },
//   details: [ ... ],
//   related: [ ... ]
// }
\`\`\`

## 시나리오 2: 필터링된 목록 조회

\`\`\`javascript
const filteredResponse = await fetch(
  'https://example.com/api/[resources]?category=[category]&page=1'
);
const filteredData = await filteredResponse.json();

console.log(filteredData.data.items);
// [
//   { id: "...", name: "[Resource]", category: "[category]" },
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
   - `docs/api/endpoints/[resources].md`
   - `docs/api/endpoints/search.md`
   - 프로젝트 API 라우트별 추가 문서
   - `docs/api/examples.md`

2. **OpenAPI 스키마** (선택):
   - `docs/api/openapi.yaml`

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| API 응답 예시와 실제 응답 불일치 | 실제 API를 호출하여 응답을 캡처, 문서에 반영 |
| 링크 깨짐 | `npx markdown-link-check docs/` 실행하여 깨진 링크 수정 |
| 코드 예시 실행 실패 | 각 예시를 실제로 실행하여 검증. 실패 시 수정 |

## ✅ 완료 체크리스트

- [ ] API 개요 문서 작성
- [ ] 모든 엔드포인트 문서화
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

