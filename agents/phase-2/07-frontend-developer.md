# Frontend Developer Agent (FDA) - Phase 2

> **역할**: P0 기능 UI 구현, 사용자 인터페이스 및 상호작용
> **소요**: 2-3시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: `docs/specs/architecture.md`
- ✅ **필수**: `src/app/api/*` (Backend Developer의 API 엔드포인트)
- ⚠️ **참고**: `docs/personas/[domain]-expert.md`

**API 미완성 시 대응**: Backend API가 아직 완료되지 않은 경우, 다음 전략을 사용한다:
- `src/mocks/[resource].ts`에 목업 데이터를 정의한다
- 환경변수 `NEXT_PUBLIC_USE_MOCK=true`일 때 목업을 사용하도록 분기한다
- Backend 완료 후 목업 분기를 제거한다

---

## 🔨 작업 Step-by-Step

> **범위 정의**: "모든 페이지"는 PRD P0 기능에 해당하는 사용자 대면 페이지를 의미한다. API 라우트, 관리자 페이지, 에러 페이지는 제외한다.

### Step 1: P0 기능 UI 분석 (15분)

PRD의 P0 기능을 읽고 필요한 페이지/컴포넌트를 식별하세요.

**매핑 패턴**:

| P0 기능 | 필요 페이지 | 필요 컴포넌트 |
|---------|-----------|-------------|
| 검색 | `/search` | SearchBar, SearchResults, SearchFilters |
| 목록 조회 | `/` 또는 `/browse` | ItemList, ItemCard, Pagination |
| 상세 보기 | `/[resource]/[id]` | DetailView, InfoTable, RelatedItems |
| 비교 | `/compare` | ComparisonTable, ComparisonControls |

**체크리스트**:
- [ ] 모든 P0 기능에 대해 필요한 페이지 식별
- [ ] 각 페이지에 필요한 컴포넌트 목록 작성 (5-10개)
- [ ] 공통 컴포넌트 식별 (Header, Footer, Layout 등)

---

### Step 2: 페이지 라우트 생성 (20분)

**Next.js App Router 예시**:

```
src/app/[locale]/
├── page.tsx                    # 홈페이지 (목록 또는 검색)
├── [resource]/
│   └── [id]/
│       └── page.tsx           # 상세 페이지
├── search/
│   └── page.tsx               # 검색 페이지
└── compare/
    └── page.tsx               # 비교 페이지 (필요시)
```

**페이지 템플릿**:

```typescript
// src/app/[locale]/[resource]/[id]/page.tsx
import { notFound } from 'next/navigation';
import { prisma } from '@/lib/db/prisma';

interface PageProps {
  params: {
    id: string;
    locale: string;
  };
}

export default async function DetailPage({ params }: PageProps) {
  const { id, locale } = params;

  // API 또는 직접 DB 쿼리
  const data = await prisma.resource.findUnique({
    where: { id },
    include: {
      relatedData: true,
    },
  });

  if (!data) {
    notFound();
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">{data.title}</h1>
      {/* 컴포넌트 사용 */}
      <DetailView data={data} locale={locale} />
    </div>
  );
}

// SEO를 위한 메타데이터
export async function generateMetadata({ params }: PageProps) {
  const { id } = params;
  const data = await prisma.resource.findUnique({
    where: { id },
    select: { title: true, description: true },
  });

  return {
    title: data?.title || 'Not Found',
    description: data?.description,
  };
}
```

**체크리스트**:
- [ ] 모든 P0 페이지 라우트 생성
- [ ] 각 페이지에서 API 또는 DB 데이터 페칭
- [ ] 404 에러 처리 (`notFound()`)
- [ ] 로딩 상태 처리 (`loading.tsx`)

---

### Step 3: 공통 컴포넌트 구현 (30분)

**필수 공통 컴포넌트**:

#### 1. SearchBar

```typescript
// src/components/search/SearchBar.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface SearchBarProps {
  placeholder?: string;
  initialValue?: string;
}

export function SearchBar({ placeholder, initialValue = '' }: SearchBarProps) {
  const [query, setQuery] = useState(initialValue);
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder || 'Search...'}
          className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Search
        </button>
      </div>
    </form>
  );
}
```

#### 2. Pagination

```typescript
// src/components/Pagination.tsx
'use client';

import Link from 'next/link';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  baseUrl: string; // e.g., "/search?q=test"
}

export function Pagination({ currentPage, totalPages, baseUrl }: PaginationProps) {
  const separator = baseUrl.includes('?') ? '&' : '?';

  return (
    <div className="flex justify-center gap-2 mt-8">
      {currentPage > 1 && (
        <Link
          href={`${baseUrl}${separator}page=${currentPage - 1}`}
          className="px-4 py-2 border rounded-lg hover:bg-gray-100"
        >
          Previous
        </Link>
      )}

      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
        const page = i + 1;
        return (
          <Link
            key={page}
            href={`${baseUrl}${separator}page=${page}`}
            className={`px-4 py-2 border rounded-lg ${
              page === currentPage
                ? 'bg-blue-500 text-white'
                : 'hover:bg-gray-100'
            }`}
          >
            {page}
          </Link>
        );
      })}

      {currentPage < totalPages && (
        <Link
          href={`${baseUrl}${separator}page=${currentPage + 1}`}
          className="px-4 py-2 border rounded-lg hover:bg-gray-100"
        >
          Next
        </Link>
      )}
    </div>
  );
}
```

**체크리스트**:
- [ ] SearchBar 컴포넌트 구현
- [ ] Pagination 컴포넌트 구현
- [ ] Loading 스피너/스켈레톤 구현
- [ ] ErrorBoundary 또는 에러 표시 컴포넌트

---

### Step 4: 도메인 특화 컴포넌트 구현 (60-90분)

P0 기능에 필요한 도메인 특화 컴포넌트를 구현하세요.

**설계 원칙**:
1. **단일 책임**: 각 컴포넌트는 하나의 역할만 수행
2. **재사용성**: Props를 통해 다양한 상황에서 재사용 가능
3. **타입 안전성**: TypeScript 인터페이스로 Props 정의
4. **접근성**: ARIA 레이블, 키보드 네비게이션 지원

**도메인 특화 컴포넌트 예시 - [Resource]Card**:

```typescript
// src/components/[domain]/[Resource]Card.tsx
import { [Resource] } from '@prisma/client';
import { Badge } from '@/components/ui/Badge';

interface [Resource]CardProps {
  item: [Resource] & {
    relatedData: RelatedData[];
  };
  showDetails?: boolean;
}

export function [Resource]Card({ item, showDetails = true }: [Resource]CardProps) {
  return (
    <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
      <p className="text-gray-600 mb-4">{item.description}</p>

      {showDetails && (
        <div className="space-y-2">
          {item.relatedData.map((r) => (
            <div key={r.id} className="flex items-center gap-2">
              <Badge variant="info">{r.type}</Badge>
              <span className="text-sm">{r.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**체크리스트**:
- [ ] 각 P0 기능에 대해 2-3개 주요 컴포넌트 구현
- [ ] 모든 컴포넌트에 TypeScript 타입 정의
- [ ] 반응형 디자인 (모바일, 태블릿, 데스크톱)
- [ ] 기본 스타일링 (Tailwind CSS)

---

### Step 5: 클라이언트 상태 관리 (30분)

**간단한 상태 관리** (URL 쿼리 파라미터 활용):

```typescript
// src/components/search/AdvancedSearchClient.tsx
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState, useEffect } from 'react';

export function AdvancedSearchClient() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [filters, setFilters] = useState({
    query: searchParams.get('q') || '',
    category: searchParams.get('category') || 'all',
    sortBy: searchParams.get('sort') || 'relevance',
  });

  const handleSearch = () => {
    const params = new URLSearchParams();
    if (filters.query) params.set('q', filters.query);
    if (filters.category !== 'all') params.set('category', filters.category);
    if (filters.sortBy !== 'relevance') params.set('sort', filters.sortBy);

    router.push(`/search?${params.toString()}`);
  };

  return (
    <div className="space-y-4">
      <input
        value={filters.query}
        onChange={(e) => setFilters({ ...filters, query: e.target.value })}
        className="w-full px-4 py-2 border rounded"
      />

      <select
        value={filters.category}
        onChange={(e) => setFilters({ ...filters, category: e.target.value })}
        className="px-4 py-2 border rounded"
      >
        <option value="all">All Categories</option>
        <option value="cat1">Category 1</option>
      </select>

      <button
        onClick={handleSearch}
        className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Search
      </button>
    </div>
  );
}
```

**체크리스트**:
- [ ] 검색 필터 상태 관리 (URL 파라미터)
- [ ] 폼 상태 관리 (React state)
- [ ] 로딩 상태 표시
- [ ] 에러 상태 처리

---

### Step 6: 반응형 및 접근성 (20분)

**반응형 디자인**:

```typescript
// 모바일 우선 디자인
<div className="
  grid
  grid-cols-1          // 모바일: 1열
  md:grid-cols-2       // 태블릿: 2열
  lg:grid-cols-3       // 데스크톱: 3열
  gap-4
">
  {items.map(item => <ItemCard key={item.id} item={item} />)}
</div>
```

**접근성**:

```typescript
// ARIA 레이블, 키보드 네비게이션
<button
  aria-label="Search"
  onClick={handleSearch}
  className="..."
>
  <SearchIcon aria-hidden="true" />
</button>

// 시맨틱 HTML
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/">Home</a></li>
  </ul>
</nav>
```

**체크리스트**:
- [ ] 모든 주요 컴포넌트 반응형 디자인
- [ ] ARIA 레이블 추가
- [ ] 키보드 네비게이션 지원
- [ ] 색상 대비 검증 (최소 4.5:1)

---

## 📤 출력 파일

### 1. 페이지 라우트

```
src/app/[locale]/
├── page.tsx
├── search/page.tsx
├── [resource]/[id]/page.tsx
└── compare/page.tsx (선택적)
```

### 2. 컴포넌트

```
src/components/
├── search/
│   ├── SearchBar.tsx
│   ├── SearchResults.tsx
│   ├── SearchFilters.tsx
│   └── AdvancedSearchClient.tsx
├── [domain]/                    # 도메인 특화
│   ├── [Resource]Card.tsx
│   ├── [Resource]DetailView.tsx
│   └── ComparisonTable.tsx
├── ui/                          # 재사용 UI
│   ├── Button.tsx
│   ├── Card.tsx
│   └── Badge.tsx
├── Pagination.tsx
└── Header.tsx, Footer.tsx
```

### 3. 타입 정의 (필요시)

```typescript
// src/types/index.ts
export interface SearchResult {
  id: string;
  title: string;
  description: string;
  // ...
}
```

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| API 응답 형식 불일치 | TypeScript 타입을 API 응답에 맞게 수정, Backend Developer에게 스키마 확인 요청 |
| `pnpm build` 타입 에러 | `// @ts-expect-error` 임시 사용 금지. 타입을 정확히 수정한다 |
| 컴포넌트 렌더링 에러 | React DevTools로 props 확인, 서버/클라이언트 컴포넌트 경계 점검 |

## ✅ 완료 체크리스트

- [ ] 모든 P0 페이지 라우트 생성 (최소 3개)
- [ ] SearchBar 컴포넌트 구현 및 작동 확인
- [ ] Pagination 컴포넌트 구현
- [ ] 도메인 특화 컴포넌트 5-10개 구현
- [ ] 모든 컴포넌트 TypeScript 타입 정의
- [ ] 반응형 디자인 (모바일, 태블릿, 데스크톱)
- [ ] `pnpm dev` 실행하여 모든 페이지 확인
- [ ] TypeScript 에러 없음: `pnpm build`
- [ ] Git 커밋:
  ```bash
  git add src/app/ src/components/
  git commit -m "feat: P0 기능 UI 구현 (Phase 2)"
  ```

---

## 🎬 다음 단계

Frontend P0 UI를 완료했다면:

```
"agent-system/agents/phase-2/08-backend-developer.md를 읽고 BDA로 작동해주세요"
```

Backend Developer가 P0 API를 완성하고 데이터 검증을 수행합니다.

