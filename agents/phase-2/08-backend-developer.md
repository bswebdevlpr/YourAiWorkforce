# Backend Developer Agent (BDA) - Phase 2

> **역할**: P0 API 완성, 데이터 검증, 성능 최적화
> **소요**: 1.5-2시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: `prisma/schema.prisma`
- ✅ **필수**: 데이터베이스 (Data Engineer가 로드한 데이터)
- ✅ **필수**: `src/app/api/*` (Phase 1에서 생성한 기본 API)

---

## 🔨 작업 Step-by-Step

### Step 1: P0 API 완성도 검증 (15분)

PRD의 P0 기능과 현재 API를 매핑하여 누락된 엔드포인트를 식별하세요.

**필요 API 체크리스트**:

| P0 기능 | 필요 API | 상태 |
|---------|---------|------|
| 목록 조회 | GET `/api/resources?page=1&limit=20` | [ ] |
| 상세 조회 | GET `/api/resources/[id]` | [ ] |
| 검색 | GET `/api/search?q=query` | [ ] |
| 필터링 | GET `/api/resources?filter=[...]` | [ ] |
| 자동완성 | GET `/api/resources/autocomplete?q=...` | [ ] |

**체크리스트**:
- [ ] 모든 P0 기능에 대응하는 API 존재 확인
- [ ] 누락된 API 목록 작성

---

### Step 2: 검색 API 구현 (30분)

**Full-text 검색** 구현:

```typescript
// src/app/api/search/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const query = searchParams.get('q') || '';
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');

    if (!query) {
      return NextResponse.json({ error: 'Query required' }, { status: 400 });
    }

    // PostgreSQL full-text search
    const [results, total] = await Promise.all([
      prisma.$queryRaw`
        SELECT *
        FROM "Resource"
        WHERE
          to_tsvector('english', title || ' ' || description)
          @@ plainto_tsquery('english', ${query})
        ORDER BY
          ts_rank(
            to_tsvector('english', title || ' ' || description),
            plainto_tsquery('english', ${query})
          ) DESC
        LIMIT ${limit}
        OFFSET ${(page - 1) * limit}
      `,
      prisma.$queryRaw`
        SELECT COUNT(*)::int as count
        FROM "Resource"
        WHERE
          to_tsvector('english', title || ' ' || description)
          @@ plainto_tsquery('english', ${query})
      `,
    ]);

    return NextResponse.json({
      data: results,
      pagination: {
        page,
        limit,
        total: (total as any)[0].count,
        totalPages: Math.ceil((total as any)[0].count / limit),
      },
    });
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

**간단한 검색** (LIKE 사용):

```typescript
// 간단한 버전 (소규모 데이터셋)
const results = await prisma.resource.findMany({
  where: {
    OR: [
      { title: { contains: query, mode: 'insensitive' } },
      { description: { contains: query, mode: 'insensitive' } },
    ],
  },
  take: limit,
  skip: (page - 1) * limit,
});
```

**검색 방식 선택 기준**:
- 데이터 10,000건 이상 또는 한국어/일본어/중국어 검색: PostgreSQL Full-text Search (`to_tsvector`)
- 데이터 10,000건 미만이고 영문/숫자만: `LIKE` 또는 Prisma `contains`

**체크리스트**:
- [ ] 검색 API 구현
- [ ] 페이지네이션 지원
- [ ] 빈 쿼리 처리
- [ ] 검색 결과 정렬 (관련성 순)

---

### Step 3: 자동완성 API 구현 (20분)

```typescript
// src/app/api/resources/autocomplete/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const query = searchParams.get('q') || '';
    const limit = parseInt(searchParams.get('limit') || '10');

    if (query.length < 2) {
      return NextResponse.json({ suggestions: [] });
    }

    // 빠른 자동완성: 제목만 검색
    const suggestions = await prisma.resource.findMany({
      where: {
        title: {
          contains: query,
          mode: 'insensitive',
        },
      },
      select: {
        id: true,
        title: true,
      },
      take: limit,
      orderBy: {
        title: 'asc',
      },
    });

    return NextResponse.json({ suggestions });
  } catch (error) {
    console.error('Autocomplete error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

**체크리스트**:
- [ ] 자동완성 API 구현
- [ ] 최소 2자 이상 입력 시 작동
- [ ] 결과 제한 (5-10개)
- [ ] 빠른 응답 (<100ms)

---

### Step 4: 고급 필터링 API 구현 (30분)

```typescript
// src/app/api/resources/route.ts (확장)
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';
import { z } from 'zod';

// 입력 검증 스키마
const querySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
  category: z.string().optional(),
  sortBy: z.enum(['relevance', 'date', 'title']).default('relevance'),
  order: z.enum(['asc', 'desc']).default('desc'),
});

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Zod로 입력 검증
    const params = querySchema.parse({
      page: searchParams.get('page'),
      limit: searchParams.get('limit'),
      category: searchParams.get('category'),
      sortBy: searchParams.get('sortBy'),
      order: searchParams.get('order'),
    });

    // 필터 조건 구축
    const where: any = {};

    if (params.category) {
      where.category = params.category;
    }

    // 정렬 조건
    let orderBy: any = {};
    switch (params.sortBy) {
      case 'date':
        orderBy = { createdAt: params.order };
        break;
      case 'title':
        orderBy = { title: params.order };
        break;
      default:
        orderBy = { id: 'asc' };
    }

    const [data, total] = await Promise.all([
      prisma.resource.findMany({
        where,
        orderBy,
        take: params.limit,
        skip: (params.page - 1) * params.limit,
        include: {
          relatedData: true,
        },
      }),
      prisma.resource.count({ where }),
    ]);

    return NextResponse.json({
      data,
      pagination: {
        page: params.page,
        limit: params.limit,
        total,
        totalPages: Math.ceil(total / params.limit),
      },
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: error.errors },
        { status: 400 }
      );
    }

    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

**체크리스트**:
- [ ] Zod 입력 검증
- [ ] 다중 필터 지원 (카테고리, 날짜 범위 등)
- [ ] 정렬 옵션 (오름차순/내림차순)
- [ ] 에러 메시지 명확함

---

### Step 5: 캐시 레이어 추가 (20-30분)

**Redis/Upstash 캐싱**:

```typescript
// src/lib/cache/redis.ts
import { Redis } from '@upstash/redis';

export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

// 캐시 헬퍼 함수
export async function getCached<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number = 3600 // 1시간
): Promise<T> {
  // 캐시 확인
  const cached = await redis.get(key);
  if (cached) {
    return cached as T;
  }

  // 캐시 미스 → 데이터 페칭
  const data = await fetchFn();

  // 캐시 저장
  await redis.set(key, data, { ex: ttl });

  return data;
}
```

**API에 캐시 적용**:

```typescript
// src/app/api/resources/[id]/route.ts
import { getCached } from '@/lib/cache/redis';
import { prisma } from '@/lib/db/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const { id } = params;

  const resource = await getCached(
    `resource:${id}`,
    async () => {
      return await prisma.resource.findUnique({
        where: { id },
        include: {
          relatedData: true,
        },
      });
    },
    3600 // 1시간 캐시
  );

  if (!resource) {
    return NextResponse.json(
      { error: 'Resource not found' },
      { status: 404 }
    );
  }

  return NextResponse.json({ data: resource });
}
```

**체크리스트**:
- [ ] Redis 클라이언트 설정
- [ ] 캐시 헬퍼 함수 구현
- [ ] 자주 조회되는 API에 캐시 적용 (상세, 목록)
- [ ] TTL 설정 (1시간 ~ 24시간)

---

### Step 6: API 응답 표준화 (15분)

**일관된 응답 형식**:

```typescript
// src/lib/api-helpers.ts
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export function successResponse<T>(data: T, pagination?: any): ApiResponse<T> {
  return {
    data,
    ...(pagination && { pagination }),
  };
}

export function errorResponse(error: string, status: number = 500) {
  return NextResponse.json({ error }, { status });
}
```

**사용 예시**:

```typescript
// API route
import { successResponse, errorResponse } from '@/lib/api-helpers';

export async function GET(request: NextRequest) {
  try {
    const data = await fetchData();
    return NextResponse.json(successResponse(data));
  } catch (error) {
    return errorResponse('Failed to fetch data', 500);
  }
}
```

**체크리스트**:
- [ ] API 응답 인터페이스 정의
- [ ] 모든 API가 동일한 형식 사용
- [ ] 에러 응답 표준화
- [ ] HTTP 상태 코드 올바르게 사용 (200, 400, 404, 500)

---

## 📤 출력 파일

1. **새로운 API 엔드포인트**:
   - `src/app/api/search/route.ts`
   - `src/app/api/resources/autocomplete/route.ts`
   - `src/app/api/compare/route.ts` (필요시)

2. **캐시 레이어**:
   - `src/lib/cache/redis.ts`

3. **API 헬퍼**:
   - `src/lib/api-helpers.ts`

4. **업데이트된 기존 API**:
   - `src/app/api/resources/route.ts` (필터링, 정렬 추가)
   - `src/app/api/resources/[id]/route.ts` (캐시 추가)

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| 검색 결과 0건 | 쿼리 로깅 활성화, 인덱스 확인, `ILIKE` 또는 trigram 인덱스 추가 고려 |
| API 응답 시간 > 500ms | `EXPLAIN ANALYZE`로 쿼리 분석, 필요 시 인덱스 추가 |
| 캐시 무효화 실패 | TTL 기반 캐시만 사용 (수동 무효화 없이), TTL은 최대 5분 |

## ✅ 완료 체크리스트

- [ ] 모든 P0 기능에 대응하는 API 구현
- [ ] 검색 API 작동 확인 (쿼리 테스트)
- [ ] 자동완성 API 작동 확인 (<100ms 응답)
- [ ] 필터링 및 정렬 작동 확인
- [ ] 캐시 적용 및 작동 확인
- [ ] 모든 API 응답 형식 통일
- [ ] Zod 입력 검증 적용
- [ ] API 테스트:
  ```bash
  curl http://localhost:3000/api/search?q=test
  curl http://localhost:3000/api/resources/autocomplete?q=te
  ```
- [ ] Git 커밋:
  ```bash
  git add src/app/api/ src/lib/
  git commit -m "feat: P0 API 완성 - 검색, 자동완성, 캐싱 (Phase 2)"
  ```

---

## 🎬 다음 단계

Backend P0 API를 완료했다면:

```
"agent-system/agents/phase-2/09-data-engineer.md를 읽고 DEN으로 작동해주세요"
```

Data Engineer가 데이터를 보강하고 품질을 개선합니다.

