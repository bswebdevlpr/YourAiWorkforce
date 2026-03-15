# QA Lead Agent (QLA) - Phase 2

> **역할**: 테스트 전략 수립, 기본 테스트 작성, P0 기능 검증
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐☆☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: `src/app/api/*` (모든 API 엔드포인트)
- ✅ **필수**: `src/components/*` (모든 컴포넌트)

---

## 🔨 작업 Step-by-Step

### Step 1: 테스트 전략 수립 (15분)

**테스트 피라미드**:

```
        /\
       /  \      E2E 테스트 (10%)
      /    \     - 핵심 사용자 플로우
     /------\
    /        \   통합 테스트 (30%)
   /          \  - API 엔드포인트
  /            \ - 컴포넌트 상호작용
 /--------------\
/                \ 단위 테스트 (60%)
                  - 유틸리티 함수
                  - 단일 컴포넌트
```

**Phase 2 목표**:
- ✅ 단위 테스트: P0 기능 핵심 로직
- ✅ API 테스트: 모든 P0 엔드포인트
- ⚠️ E2E 테스트: Phase 4로 연기

**체크리스트**:
- [ ] 테스트 대상 식별 (P0 기능 우선)
- [ ] 테스트 우선순위 결정
- [ ] 테스트 도구 선택 (Vitest, Testing Library)

---

### Step 2: API 테스트 작성 (30-45분)

**테스트 환경 설정**:

```typescript
// test/setup.ts
import { beforeAll, afterAll, afterEach } from 'vitest';
import { prisma } from '@/lib/db/prisma';

beforeAll(async () => {
  // 테스트 DB 준비
  await prisma.$connect();
});

afterEach(async () => {
  // 각 테스트 후 DB 초기화
  await prisma.resource.deleteMany();
});

afterAll(async () => {
  await prisma.$disconnect();
});
```

**API 테스트 예시**:

```typescript
// test/api/search.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { GET } from '@/app/api/search/route';
import { prisma } from '@/lib/db/prisma';

describe('/api/search', () => {
  beforeEach(async () => {
    // 테스트 데이터 삽입
    await prisma.resource.createMany({
      data: [
        { id: '1', title: 'Apple', description: 'A fruit' },
        { id: '2', title: 'Banana', description: 'A yellow fruit' },
        { id: '3', title: 'Cherry', description: 'A red fruit' },
      ],
    });
  });

  it('should return search results', async () => {
    const request = new Request('http://localhost:3000/api/search?q=fruit');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.data).toHaveLength(3);
  });

  it('should return empty for no matches', async () => {
    const request = new Request('http://localhost:3000/api/search?q=xyz');
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.data).toHaveLength(0);
  });

  it('should return 400 for missing query', async () => {
    const request = new Request('http://localhost:3000/api/search');
    const response = await GET(request);

    expect(response.status).toBe(400);
  });

  it('should support pagination', async () => {
    const request = new Request('http://localhost:3000/api/search?q=fruit&page=1&limit=2');
    const response = await GET(request);
    const data = await response.json();

    expect(data.data).toHaveLength(2);
    expect(data.pagination.totalPages).toBe(2);
  });
});
```

**체크리스트**:
- [ ] 모든 P0 API 엔드포인트 테스트
- [ ] 성공 케이스 테스트
- [ ] 에러 케이스 테스트 (400, 404, 500)
- [ ] 페이지네이션 테스트

---

### Step 3: 컴포넌트 테스트 작성 (30-45분)

```typescript
// test/components/SearchBar.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchBar } from '@/components/search/SearchBar';

// Next.js router 모킹
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe('SearchBar', () => {
  it('should render input field', () => {
    render(<SearchBar />);
    const input = screen.getByRole('textbox');
    expect(input).toBeInTheDocument();
  });

  it('should update input value on change', () => {
    render(<SearchBar />);
    const input = screen.getByRole('textbox') as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'test query' } });

    expect(input.value).toBe('test query');
  });

  it('should navigate on submit', () => {
    const { useRouter } = require('next/navigation');
    const mockPush = vi.fn();
    useRouter.mockReturnValue({ push: mockPush });

    render(<SearchBar />);
    const input = screen.getByRole('textbox');
    const form = input.closest('form')!;

    fireEvent.change(input, { target: { value: 'apple' } });
    fireEvent.submit(form);

    expect(mockPush).toHaveBeenCalledWith('/search?q=apple');
  });

  it('should not submit empty query', () => {
    const { useRouter } = require('next/navigation');
    const mockPush = vi.fn();
    useRouter.mockReturnValue({ push: mockPush });

    render(<SearchBar />);
    const form = screen.getByRole('textbox').closest('form')!;

    fireEvent.submit(form);

    expect(mockPush).not.toHaveBeenCalled();
  });
});
```

**체크리스트**:
- [ ] 주요 컴포넌트 테스트 (SearchBar, Pagination 등)
- [ ] 사용자 상호작용 테스트 (클릭, 입력 등)
- [ ] Props 전달 테스트
- [ ] 조건부 렌더링 테스트

---

### Step 4: 유틸리티 함수 테스트 (15-20분)

```typescript
// test/lib/utils.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate, truncate, calculateSimilarity } from '@/lib/utils';

describe('Utility Functions', () => {
  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date('2024-01-15');
      expect(formatDate(date)).toBe('Jan 15, 2024');
    });
  });

  describe('truncate', () => {
    it('should truncate long text', () => {
      const text = 'This is a very long text that needs truncation';
      expect(truncate(text, 20)).toBe('This is a very long...');
    });

    it('should not truncate short text', () => {
      const text = 'Short';
      expect(truncate(text, 20)).toBe('Short');
    });
  });

  describe('calculateSimilarity', () => {
    it('should return 1 for identical strings', () => {
      expect(calculateSimilarity('apple', 'apple')).toBe(1);
    });

    it('should return 0 for completely different strings', () => {
      expect(calculateSimilarity('apple', 'xyz')).toBe(0);
    });
  });
});
```

**체크리스트**:
- [ ] 모든 유틸리티 함수 테스트
- [ ] 엣지 케이스 테스트 (null, undefined, 빈 문자열)
- [ ] 경계값 테스트

---

### Step 5: 테스트 커버리지 확인 (10분)

```bash
# 커버리지 리포트 생성
pnpm test --coverage
```

**목표 커버리지**:
- **전체**: > 70%
- **핵심 로직**: > 90%
- **API 엔드포인트**: 100%

**package.json 스크립트**:

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

**체크리스트**:
- [ ] 커버리지 70% 이상 달성
- [ ] 커버리지 리포트 확인
- [ ] 미테스트 영역 식별

---

## 📤 출력 파일

1. **테스트 파일**:
   ```
   test/
   ├── setup.ts
   ├── api/
   │   ├── search.test.ts
   │   ├── resources.test.ts
   │   └── autocomplete.test.ts
   ├── components/
   │   ├── SearchBar.test.tsx
   │   ├── Pagination.test.tsx
   │   └── [Domain]Card.test.tsx
   └── lib/
       └── utils.test.ts
   ```

2. **테스트 설정**:
   - `vitest.config.ts`
   - `test/setup.ts`

3. **커버리지 리포트**:
   - `coverage/` 디렉토리

---

## ✅ 완료 체크리스트

- [ ] 테스트 전략 문서 작성
- [ ] 모든 P0 API 테스트 (최소 5개 엔드포인트)
- [ ] 주요 컴포넌트 테스트 (최소 3개)
- [ ] 유틸리티 함수 테스트
- [ ] 모든 테스트 통과: `pnpm test`
- [ ] 커버리지 > 70%
- [ ] Git 커밋:
  ```bash
  git add test/ vitest.config.ts
  git commit -m "feat: P0 기능 테스트 작성 (Phase 2 완료)"
  ```

---

## 🎬 다음 단계

**Phase 2 완료!** 🎉

이제 Phase 3 (Advanced Features)로 진행하세요:

```
"agent-system/agents/phase-3/11-algorithm-engineer.md를 읽고 AEA로 작동해주세요"
```

---

## 💡 TriHanzi 실제 테스트

**테스트 파일** (15개):
- API 테스트: 8개
- 컴포넌트 테스트: 5개
- 유틸리티 테스트: 2개

**커버리지**:
- 전체: 78.5%
- API: 100%
- 컴포넌트: 72.3%
- 유틸리티: 95.1%

**테스트 도구**:
- Vitest
- @testing-library/react
- @testing-library/jest-dom
