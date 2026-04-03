# QA Lead Agent (QLA) - Phase 4

> **역할**: E2E 테스트, 통합 테스트, Lighthouse 감사
> **소요**: 2-3시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: 모든 페이지 및 컴포넌트
- ✅ **필수**: 모든 API 라우트
- ✅ **필수**: PRD (`docs/specs/prd.md`)

---

## 🔨 작업 Step-by-Step

### Step 1: E2E 테스트 프레임워크 설정 (20분)

```bash
# Playwright 설치
npm install -D @playwright/test
npx playwright install
```

**playwright.config.ts**:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './test/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: process.env.TEST_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // 모바일 테스트
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

**체크리스트**:
- [ ] Playwright 설치 및 설정
- [ ] 테스트 디렉토리 생성 (`test/e2e/`)
- [ ] 브라우저 설정 (Chrome, Firefox, Safari)
- [ ] 모바일 디바이스 설정

---

### Step 2: 핵심 사용자 플로우 E2E 테스트 (60-90분)

**2.1 홈페이지 테스트**

```typescript
// test/e2e/home.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/en');

    // 타이틀 확인
    await expect(page).toHaveTitle(/[project-name]/);

    // 주요 요소 확인
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
  });

  test('should switch language', async ({ page }) => {
    await page.goto('/en');

    // 언어 스위처 클릭
    await page.click('[data-testid="language-switcher"]');
    await page.click('[data-testid="lang-ko"]');

    // URL 변경 확인
    await expect(page).toHaveURL('/ko');

    // 콘텐츠 변경 확인 (한국어로)
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should have working search bar', async ({ page }) => {
    await page.goto('/en');

    // 검색창에 입력
    await page.fill('[data-testid="search-input"]', 'keyword');

    // 자동완성 나타남
    await expect(page.locator('[data-testid="autocomplete"]')).toBeVisible();

    // Enter 키 입력
    await page.press('[data-testid="search-input"]', 'Enter');

    // 검색 결과 페이지로 이동
    await expect(page).toHaveURL(/\/search/);
  });
});
```

**2.2 검색 플로우 테스트**

```typescript
// test/e2e/search.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Search Flow', () => {
  test('should search for items', async ({ page }) => {
    await page.goto('/en/search');

    // 검색어 입력
    await page.fill('[data-testid="search-input"]', 'keyword');
    await page.click('[data-testid="search-button"]');

    // 로딩 상태
    await expect(page.locator('[data-testid="loading"]')).toBeVisible();

    // 결과 표시
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();

    // 결과 개수 확인
    const results = page.locator('[data-testid="result-card"]');
    expect(await results.count()).toBeGreaterThan(0);
  });

  test('should filter search results', async ({ page }) => {
    await page.goto('/en/search?q=keyword');

    // 필터 열기
    await page.click('[data-testid="filter-button"]');

    // 카테고리 필터 선택
    await page.check('[data-testid="filter-[category]"]');
    await page.click('[data-testid="apply-filters"]');

    // URL 업데이트 확인
    await expect(page).toHaveURL(/category=/);

    // 결과 업데이트 확인
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
  });

  test('should handle empty search results', async ({ page }) => {
    await page.goto('/en/search?q=nonexistentquery123');

    // 빈 결과 메시지
    await expect(page.locator('[data-testid="no-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="no-results"]')).toContainText(
      /No results found/i
    );
  });

  test('should paginate search results', async ({ page }) => {
    await page.goto('/en/search?q=a');

    // 첫 페이지 확인
    await expect(page.locator('[data-testid="page-1"]')).toHaveClass(/active/);

    // 다음 페이지 클릭
    await page.click('[data-testid="next-page"]');

    // URL 업데이트
    await expect(page).toHaveURL(/page=2/);

    // 페이지 번호 업데이트
    await expect(page.locator('[data-testid="page-2"]')).toHaveClass(/active/);
  });
});
```

**2.3 비교 플로우 테스트**

```typescript
// test/e2e/compare.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Compare Flow', () => {
  test('should compare items', async ({ page }) => {
    await page.goto('/en/compare');

    // 첫 번째 항목 검색
    await page.fill('[data-testid="compare-search"]', 'item-a');
    await page.click('[data-testid="autocomplete-item-0"]');

    // 선택된 항목 확인
    await expect(page.locator('[data-testid="selected-item-0"]')).toBeVisible();

    // 두 번째 항목 검색
    await page.fill('[data-testid="compare-search"]', 'item-b');
    await page.click('[data-testid="autocomplete-item-0"]');

    // 비교 테이블 표시
    await expect(page.locator('[data-testid="comparison-table"]')).toBeVisible();

    // 비교 데이터 확인
    await expect(page.locator('[data-testid="similarity-score"]')).toContainText(
      /%/
    );
  });

  test('should remove selected item', async ({ page }) => {
    await page.goto('/en/compare');

    // 항목 선택
    await page.fill('[data-testid="compare-search"]', 'item-a');
    await page.click('[data-testid="autocomplete-item-0"]');

    // 제거 버튼 클릭
    await page.click('[data-testid="remove-item-0"]');

    // 항목 제거 확인
    await expect(page.locator('[data-testid="selected-item-0"]')).not.toBeVisible();
  });

  test('should export comparison to PDF', async ({ page }) => {
    await page.goto('/en/compare');

    // 2개 항목 선택
    await page.fill('[data-testid="compare-search"]', 'item-a');
    await page.click('[data-testid="autocomplete-item-0"]');
    await page.fill('[data-testid="compare-search"]', 'item-b');
    await page.click('[data-testid="autocomplete-item-0"]');

    // PDF 내보내기 다운로드 시작 대기
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-pdf"]');
    const download = await downloadPromise;

    // 파일명 확인
    expect(download.suggestedFilename()).toMatch(/comparison.*\.pdf/);
  });
});
```

**2.4 [Resource] 상세 페이지 테스트**

```typescript
// test/e2e/resource-detail.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Resource Detail', () => {
  test('should display resource details', async ({ page }) => {
    // 실제 리소스 ID로 이동
    await page.goto('/en/[resources]/clx123456');

    // 리소스 표시 확인
    await expect(page.locator('[data-testid="resource-display"]')).toBeVisible();

    // 상세 섹션
    await expect(page.locator('[data-testid="details"]')).toBeVisible();

    // 메타데이터 섹션
    await expect(page.locator('[data-testid="metadata"]')).toBeVisible();
  });

  test('should show related items', async ({ page }) => {
    await page.goto('/en/[resources]/clx123456');

    // 관련 항목 섹션
    await expect(page.locator('[data-testid="related-items"]')).toBeVisible();

    // 관련 항목 클릭
    await page.click('[data-testid="related-item-0"]');

    // 새 상세 페이지로 이동
    await expect(page).toHaveURL(/\/[resources]\//);
  });

  test('should handle 404 for non-existent resource', async ({ page }) => {
    await page.goto('/en/[resources]/nonexistent');

    // 404 페이지
    await expect(page.locator('h1')).toContainText(/404|Not Found/i);
  });
});
```

**체크리스트**:
- [ ] 홈페이지 테스트
- [ ] 검색 플로우 테스트
- [ ] 비교 플로우 테스트
- [ ] [Resource] 상세 페이지 테스트
- [ ] 404/에러 케이스 테스트
- [ ] 모바일 반응형 테스트
- [ ] 다국어 테스트

---

### Step 3: API 통합 테스트 (30-45분)

```typescript
// test/integration/api.test.ts

import { describe, it, expect } from 'vitest';

describe('API Integration Tests', () => {
  describe('GET /api/[resources]', () => {
    it('should return paginated items', async () => {
      const response = await fetch('http://localhost:3000/api/[resources]?page=1&limit=10');
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data.items).toHaveLength(10);
      expect(data.data.pagination).toMatchObject({
        page: 1,
        limit: 10,
        total: expect.any(Number),
        totalPages: expect.any(Number),
      });
    });

    it('should filter by category', async () => {
      const response = await fetch('http://localhost:3000/api/[resources]?category=[category]');
      const data = await response.json();

      expect(response.status).toBe(200);
      data.data.items.forEach((item: any) => {
        expect(item.category).toBe('[category]');
      });
    });

    it('should handle invalid category parameter', async () => {
      const response = await fetch('http://localhost:3000/api/[resources]?category=INVALID');
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('INVALID_INPUT');
    });

    it('should respect rate limit', async () => {
      // 10개 요청 (제한)
      for (let i = 0; i < 10; i++) {
        await fetch('http://localhost:3000/api/[resources]');
      }

      // 11번째 요청 (초과)
      const response = await fetch('http://localhost:3000/api/[resources]');

      expect(response.status).toBe(429);
      expect(response.headers.get('X-RateLimit-Limit')).toBe('10');
    });
  });

  describe('GET /api/search', () => {
    it('should search items by keyword', async () => {
      const response = await fetch('http://localhost:3000/api/search?q=keyword');
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.data.items.length).toBeGreaterThan(0);
    });

    it('should return empty results for nonexistent query', async () => {
      const response = await fetch('http://localhost:3000/api/search?q=nonexistentquery123');
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.data.items).toHaveLength(0);
    });
  });
});
```

**체크리스트**:
- [ ] 모든 API 엔드포인트 테스트
- [ ] 페이지네이션 테스트
- [ ] 필터링 테스트
- [ ] 에러 케이스 테스트
- [ ] Rate limiting 테스트

---

### Step 4: Lighthouse 감사 (20분)

```bash
# Lighthouse CI 실행
npm install -g @lhci/cli

# 서버 시작
npm run build
npm run start

# Lighthouse 실행
lhci autorun
```

**lighthouserc.js**:

```javascript
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/en',
        'http://localhost:3000/en/search',
        'http://localhost:3000/en/compare',
        'http://localhost:3000/en/[resources]/clx123456',
      ],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.85 }],
        'categories:accessibility': ['error', { minScore: 0.85 }],
        'categories:seo': ['error', { minScore: 0.90 }],
        'categories:best-practices': ['error', { minScore: 0.85 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

**체크리스트**:
- [ ] Lighthouse Performance >= 85
- [ ] Lighthouse Accessibility >= 85
- [ ] Lighthouse SEO >= 90
- [ ] Lighthouse Best Practices >= 85
- [ ] 주요 페이지 모두 감사 (최소 4개)

---

### Step 5: 품질 보고서 생성 (15분)

```markdown
# Phase 4 품질 보고서

**날짜**: 2026-02-16
**Phase**: 4 - Integration & Polish

## E2E 테스트

### 실행 결과

- **총 테스트**: 25개
- **통과**: 25개
- **실패**: 0개
- **성공률**: 100%

### 커버리지

- ✅ 홈페이지 (3 테스트)
- ✅ 검색 플로우 (4 테스트)
- ✅ 비교 플로우 (3 테스트)
- ✅ [Resource] 상세 (3 테스트)
- ✅ 다국어 (4 테스트)
- ✅ 모바일 (4 테스트)
- ✅ 에러 케이스 (4 테스트)

## API 통합 테스트

- **총 테스트**: 15개
- **통과**: 15개
- **실패**: 0개

## Lighthouse 감사

| 페이지 | Performance | Accessibility | SEO | Best Practices |
|--------|-------------|---------------|-----|----------------|
| 홈페이지 | 92 | 100 | 100 | 96 |
| 검색 | 89 | 100 | 100 | 96 |
| 비교 | 87 | 100 | 100 | 96 |
| [Resource] 상세 | 91 | 100 | 100 | 96 |

**평균**:
- Performance: **89.75** ✅ (>= 85)
- Accessibility: **100** ✅ (>= 85)
- SEO: **100** ✅ (>= 90)
- Best Practices: **96** ✅ (>= 85)

## 결론

✅ **Phase 4 품질 게이트 통과**

모든 테스트 통과, Lighthouse 점수 목표 달성.
```

---

## 📤 출력 파일

1. **E2E 테스트**:
   - `test/e2e/home.spec.ts`
   - `test/e2e/search.spec.ts`
   - `test/e2e/compare.spec.ts`
   - `test/e2e/resource-detail.spec.ts`

2. **통합 테스트**:
   - `test/integration/api.test.ts`

3. **설정**:
   - `playwright.config.ts`
   - `lighthouserc.js`

4. **보고서**:
   - `docs/reports/phase-4-quality-report.md`

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| E2E 테스트 Flaky (실행마다 결과 다름) | `test.retry(2)` 설정, 테스트 간 상태 격리 확인, 네트워크 의존성 제거 |
| Lighthouse 점수 편차 > 5점 | `numberOfRuns`를 5로 증가, median 값 사용 |
| 테스트 타임아웃 | `timeout: 30000` 설정, 느린 API에 대해 `waitForResponse` 사용 |
| 접근성 테스트 실패 | `@axe-core/playwright`로 구체적 위반 사항 확인, WCAG AA 기준으로 수정 |

## ✅ 완료 체크리스트

- [ ] Playwright 설정 완료
- [ ] E2E 테스트 25개 이상 작성
- [ ] 모든 E2E 테스트 통과
- [ ] API 통합 테스트 15개 이상 작성
- [ ] 모든 통합 테스트 통과
- [ ] Lighthouse 감사 완료
- [ ] Performance >= 85
- [ ] Accessibility >= 85
- [ ] SEO >= 90
- [ ] Best Practices >= 85
- [ ] 품질 보고서 생성
- [ ] Git 커밋:
  ```bash
  git add test/ playwright.config.ts lighthouserc.js docs/reports/
  git commit -m "test: E2E 테스트, 통합 테스트, Lighthouse 감사 (Phase 4)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-5/18-domain-expert-review.md를 읽고 DEA로 작동해주세요"
```

---

