# Frontend Developer Agent (FDA) - Phase 3

> **역할**: 디자인 시스템 구축 및 P1 기능 UI 구현
> **소요**: 2-3시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: `src/app/api/` (Phase 2 API 엔드포인트)
- ✅ **필수**: 기존 컴포넌트 (Phase 2에서 구축)
- ✅ **선택**: `docs/personas/[domain]-expert.md` (도메인 색상 가이드)

---

## 🔨 작업 Step-by-Step

### Step 1: 디자인 시스템 정의 (30-45분)

**1.1 컬러 팔레트 정의**

도메인에 적합한 색상 체계를 구축하세요.

```typescript
// src/constants/colors.ts

export const colors = {
  // 브랜드 색상
  primary: '#3B82F6',      // Blue
  secondary: '#8B5CF6',    // Purple
  accent: '#F59E0B',       // Amber

  // 도메인 특화 색상 (예: TriHanzi 국가별 색상)
  domain: {
    korea: '#DC2626',      // Red
    japan: '#1E3A8A',      // Navy
    china: '#CA8A04',      // Gold
  },

  // 시맨틱 색상
  success: '#10B981',      // Green
  warning: '#F59E0B',      // Amber
  error: '#EF4444',        // Red
  info: '#3B82F6',         // Blue

  // 중립 색상
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },

  // 다크 모드
  dark: {
    bg: '#0F172A',
    surface: '#1E293B',
    border: '#334155',
    text: '#E2E8F0',
  },
};
```

**1.2 타이포그래피 스케일**

```typescript
// tailwind.config.ts

export default {
  theme: {
    extend: {
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
};
```

**1.3 간격 시스템**

```typescript
// spacing: 4px 기본 단위
spacing: {
  '0': '0px',
  '1': '0.25rem',  // 4px
  '2': '0.5rem',   // 8px
  '3': '0.75rem',  // 12px
  '4': '1rem',     // 16px
  '6': '1.5rem',   // 24px
  '8': '2rem',     // 32px
  '12': '3rem',    // 48px
  '16': '4rem',    // 64px
}
```

**체크리스트**:
- [ ] 컬러 팔레트 정의 (브랜드 + 도메인 + 시맨틱)
- [ ] 다크 모드 색상 정의
- [ ] 타이포그래피 스케일 설정
- [ ] 간격 시스템 설정
- [ ] WCAG AA 색상 대비 검증 (최소 4.5:1)

---

### Step 2: UI 컴포넌트 라이브러리 구축 (45-60분)

**2.1 Badge 컴포넌트**

```typescript
// src/components/ui/Badge.tsx

import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const variantStyles = {
  default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
  error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
};

const sizeStyles = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

export function Badge({ children, variant = 'default', size = 'md', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
}
```

**2.2 Tabs 컴포넌트**

```typescript
// src/components/ui/Tabs.tsx

'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface TabsProps {
  tabs: { id: string; label: string; content: React.ReactNode }[];
  defaultTab?: string;
  className?: string;
}

export function Tabs({ tabs, defaultTab, className }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  return (
    <div className={cn('w-full', className)}>
      {/* Tab Header */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'whitespace-nowrap border-b-2 px-1 py-4 text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              )}
              aria-current={activeTab === tab.id ? 'page' : undefined}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="py-6">
        {tabs.find((tab) => tab.id === activeTab)?.content}
      </div>
    </div>
  );
}
```

**2.3 기타 컴포넌트**

다음 컴포넌트를 추가로 구축하세요:
- `Button`: 다양한 variant (primary, secondary, outline, ghost)
- `Card`: 재사용 가능한 카드 컨테이너
- `Modal`: 모달 다이얼로그
- `Alert`: 알림 메시지
- `Meter`: 진행률/점수 표시

**체크리스트**:
- [ ] Badge 컴포넌트 구현
- [ ] Tabs 컴포넌트 구현
- [ ] Button 컴포넌트 구현
- [ ] Card 컴포넌트 구현
- [ ] Modal 컴포넌트 구현
- [ ] Alert 컴포넌트 구현
- [ ] Meter 컴포넌트 구현
- [ ] 모든 컴포넌트 다크 모드 지원
- [ ] 모든 컴포넌트 접근성 지원 (ARIA)

---

### Step 3: P1 기능 페이지 구현 (60-90분)

PRD의 P1 기능을 구현하세요.

**예시: 비교 페이지 (TriHanzi)**

```typescript
// src/app/[locale]/compare/page.tsx

import { Suspense } from 'react';
import { CompareClient } from '@/components/compare/CompareClient';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Compare Characters - TriHanzi',
  description: 'Compare CJK characters across Korea, Japan, and China',
};

export default function ComparePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 text-4xl font-bold">Compare Characters</h1>

      <Suspense fallback={<ComparePageSkeleton />}>
        <CompareClient />
      </Suspense>
    </div>
  );
}

function ComparePageSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-12 w-full animate-pulse rounded-lg bg-gray-200 dark:bg-gray-800" />
      <div className="h-64 w-full animate-pulse rounded-lg bg-gray-200 dark:bg-gray-800" />
    </div>
  );
}
```

**클라이언트 컴포넌트**:

```typescript
// src/components/compare/CompareClient.tsx

'use client';

import { useState } from 'react';
import { CompareSearch } from './CompareSearch';
import { ComparisonTable } from './ComparisonTable';
import { CompareExport } from './CompareExport';

export function CompareClient() {
  const [selectedCharacters, setSelectedCharacters] = useState<string[]>([]);

  const handleAddCharacter = (char: string) => {
    if (!selectedCharacters.includes(char) && selectedCharacters.length < 5) {
      setSelectedCharacters([...selectedCharacters, char]);
    }
  };

  const handleRemoveCharacter = (char: string) => {
    setSelectedCharacters(selectedCharacters.filter((c) => c !== char));
  };

  return (
    <div className="space-y-8">
      {/* Search */}
      <CompareSearch
        onSelect={handleAddCharacter}
        disabled={selectedCharacters.length >= 5}
      />

      {/* Selected Characters */}
      {selectedCharacters.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedCharacters.map((char) => (
            <SelectedCharacterTag
              key={char}
              character={char}
              onRemove={() => handleRemoveCharacter(char)}
            />
          ))}
        </div>
      )}

      {/* Comparison Table */}
      {selectedCharacters.length >= 2 && (
        <>
          <ComparisonTable characters={selectedCharacters} />
          <CompareExport characters={selectedCharacters} />
        </>
      )}
    </div>
  );
}
```

**체크리스트**:
- [ ] P1 기능 페이지 모두 구현
- [ ] 클라이언트/서버 컴포넌트 적절히 분리
- [ ] 로딩 상태 (Suspense, Skeleton)
- [ ] 에러 바운더리 (error.tsx)
- [ ] 모바일 반응형 (sm, md, lg 브레이크포인트)
- [ ] 다크 모드 지원

---

### Step 4: 디자인 시스템 문서화 (20분)

```markdown
# 디자인 시스템

## 컬러 팔레트

### 브랜드 색상
- **Primary**: `#3B82F6` (Blue) - 주요 액션, 링크
- **Secondary**: `#8B5CF6` (Purple) - 보조 액션
- **Accent**: `#F59E0B` (Amber) - 강조, 하이라이트

### 도메인 색상
- **Korea**: `#DC2626` (Red) - 한국 관련 요소
- **Japan**: `#1E3A8A` (Navy) - 일본 관련 요소
- **China**: `#CA8A04` (Gold) - 중국 관련 요소

### 시맨틱 색상
- **Success**: `#10B981` (Green) - 성공 메시지
- **Warning**: `#F59E0B` (Amber) - 경고
- **Error**: `#EF4444` (Red) - 에러
- **Info**: `#3B82F6` (Blue) - 정보

### 접근성
모든 색상 조합은 WCAG AA 기준을 충족합니다 (최소 4.5:1 대비).

## 타이포그래피

### 폰트 패밀리
- **Sans**: Inter (본문)
- **Display**: Poppins (제목)
- **Mono**: Fira Code (코드)

### 타입 스케일
- **xs**: 0.75rem (12px)
- **sm**: 0.875rem (14px)
- **base**: 1rem (16px)
- **lg**: 1.125rem (18px)
- **xl**: 1.25rem (20px)
- **2xl**: 1.5rem (24px)
- **3xl**: 1.875rem (30px)
- **4xl**: 2.25rem (36px)

## 컴포넌트

### Badge
**사용법**:
```tsx
<Badge variant="success">Active</Badge>
<Badge variant="error" size="sm">Error</Badge>
```

**Variants**: default, success, warning, error, info
**Sizes**: sm, md, lg

### Tabs
**사용법**:
```tsx
<Tabs
  tabs={[
    { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
    { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
  ]}
  defaultTab="tab1"
/>
```

## 다크 모드

다크 모드는 `dark:` 클래스를 사용하여 구현됩니다.

**예시**:
```tsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  Content
</div>
```
```

**체크리스트**:
- [ ] 컬러 팔레트 문서화
- [ ] 타이포그래피 문서화
- [ ] 컴포넌트 사용법 문서화
- [ ] 다크 모드 가이드 문서화
- [ ] 접근성 가이드 문서화

---

## 📤 출력 파일

1. **디자인 시스템**:
   - `src/constants/colors.ts`
   - `tailwind.config.ts` (업데이트)
   - `docs/design/styles.md`

2. **UI 컴포넌트**:
   - `src/components/ui/Badge.tsx`
   - `src/components/ui/Tabs.tsx`
   - `src/components/ui/Button.tsx`
   - `src/components/ui/Card.tsx`
   - `src/components/ui/Modal.tsx`
   - `src/components/ui/Alert.tsx`
   - `src/components/ui/Meter.tsx`

3. **P1 기능 페이지**:
   - `src/app/[locale]/[feature]/page.tsx`
   - `src/components/[feature]/[Feature]Client.tsx`
   - (예: `src/app/[locale]/compare/page.tsx`)

4. **문서**:
   - `docs/design/README.md`
   - `docs/design/components.md`

---

## ✅ 완료 체크리스트

- [ ] 컬러 팔레트 정의 완료
- [ ] 타이포그래피 스케일 설정 완료
- [ ] UI 컴포넌트 7개 이상 구현
- [ ] 모든 컴포넌트 다크 모드 지원
- [ ] 모든 컴포넌트 접근성 지원 (ARIA)
- [ ] WCAG AA 색상 대비 검증 완료
- [ ] P1 기능 페이지 모두 구현
- [ ] 모바일 반응형 구현
- [ ] 로딩/에러 상태 처리
- [ ] 디자인 시스템 문서화 완료
- [ ] TypeScript 에러 없음
- [ ] ESLint 에러 없음
- [ ] Git 커밋:
  ```bash
  git add src/components/ui/ src/constants/ docs/design/
  git commit -m "feat: 디자인 시스템 및 P1 UI 구현 (Phase 3)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-3/13-data-engineer.md를 읽고 DEN으로 작동해주세요"
```

---

## 💡 TriHanzi 실제 디자인 시스템

**구현된 디자인 시스템**:

### 1. 국가별 색상 체계
```typescript
// src/constants/colors.ts
export const countryColors = {
  korea: {
    primary: '#DC2626',    // Red
    light: '#FEE2E2',
    dark: '#991B1B',
  },
  japan: {
    primary: '#1E3A8A',    // Navy
    light: '#DBEAFE',
    dark: '#1E3A8A',
  },
  china: {
    primary: '#CA8A04',    // Gold
    light: '#FEF3C7',
    dark: '#92400E',
  },
};
```

### 2. 구현된 컴포넌트 (41개)

**UI 프리미티브** (`/ui/`):
- `CountryBadge` - 국가 표시 배지 (국가별 색상)
- `FalseFriendsAlert` - False Friends 경고
- `SimilarityMeter` - 유사도 점수 표시 (0-100)
- `Tabs` - 탭 네비게이션

**비교 컴포넌트** (`/character/`):
- `SideBySideComparison` - 나란히 비교
- `OverlayComparison` - 오버레이 비교
- `DifferenceVisualization` - 차이점 시각화
- `MobileComparisonCarousel` - 모바일 캐러셀

**기능 컴포넌트** (`/compare/`, `/search/`, `/collections/`):
- `CompareClient` - 비교 페이지 메인
- `CompareSearch` - 비교할 문자 검색
- `CompareExport` - PDF 내보내기
- `AdvancedSearchClient` - 고급 검색
- `SearchFilters` - 검색 필터
- `FalseFriendsCollectionClient` - False Friends 컬렉션

### 3. 타이포그래피

```typescript
fontFamily: {
  sans: ['Inter', 'Noto Sans KR', 'Noto Sans JP', 'Noto Sans SC', 'sans-serif'],
  display: ['Poppins', 'sans-serif'],
  mono: ['Fira Code', 'monospace'],
}
```

### 4. 다크 모드
모든 컴포넌트가 `dark:` 클래스로 다크 모드 지원.

### 5. 접근성
- WCAG AA 준수 (색상 대비 4.5:1 이상)
- ARIA 레이블 모든 인터랙티브 요소
- 키보드 네비게이션 지원

**문서**:
- `docs/design/README.md` - 디자인 시스템 개요
- `docs/design/styles.md` - 색상, 타이포그래피
- `docs/design/components.md` - 컴포넌트 가이드
