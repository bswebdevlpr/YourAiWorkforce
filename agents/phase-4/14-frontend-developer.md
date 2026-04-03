# Frontend Developer Agent (FDA) - Phase 4

> **역할**: SEO 최적화, 성능 개선, i18n 완성
> **소요**: 2-3시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: 모든 페이지 (`src/app/[locale]/`)
- ✅ **필수**: 컴포넌트 (`src/components/`)
- ✅ **필수**: i18n 번역 파일 (`src/i18n/locales/`)

> **범위 정의**: "모든 페이지"는 `src/app/[locale]/` 하위의 사용자 대면 페이지를 의미한다. API 라우트(`/api/`), 에러 페이지(`error.tsx`, `not-found.tsx`)는 제외한다.

---

## 🔨 작업 Step-by-Step

### Step 1: SEO 메타데이터 추가 (45-60분)

**1.1 페이지별 메타데이터**

```typescript
// src/app/[locale]/page.tsx

import type { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';

export async function generateMetadata({
  params: { locale },
}: {
  params: { locale: string };
}): Promise<Metadata> {
  const t = await getTranslations({ locale, namespace: 'home' });

  return {
    title: t('meta.title'),
    description: t('meta.description'),
    keywords: t('meta.keywords'),
    openGraph: {
      title: t('meta.title'),
      description: t('meta.description'),
      url: `https://example.com/${locale}`,
      siteName: '[project-name]',
      images: [
        {
          url: '/og-image.png',
          width: 1200,
          height: 630,
          alt: t('meta.title'),
        },
      ],
      locale: locale,
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: t('meta.title'),
      description: t('meta.description'),
      images: ['/og-image.png'],
    },
    alternates: {
      canonical: `https://example.com/${locale}`,
      languages: {
        en: '/en',
        ko: '/ko',
        // 필요한 로케일 추가
      },
    },
  };
}
```

**1.2 동적 페이지 메타데이터**

```typescript
// src/app/[locale]/[resources]/[id]/page.tsx

export async function generateMetadata({
  params: { id, locale },
}: {
  params: { id: string; locale: string };
}): Promise<Metadata> {
  const resource = await getResource(id);
  const t = await getTranslations({ locale, namespace: 'resource' });

  if (!resource) {
    return {
      title: 'Not Found',
    };
  }

  const title = `${resource.name} - ${t('meta.title')}`;
  const description = t('meta.description', {
    name: resource.name,
    summary: resource.summary,
  });

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `https://example.com/${locale}/[resources]/${id}`,
      images: [
        {
          url: `/api/og?id=${encodeURIComponent(id)}`,
          width: 1200,
          height: 630,
          alt: resource.name,
        },
      ],
    },
  };
}
```

**체크리스트**:
- [ ] 모든 페이지에 메타데이터 추가
- [ ] OpenGraph 이미지 설정
- [ ] Twitter Card 설정
- [ ] canonical URL 설정
- [ ] hreflang 대체 언어 설정

---

### Step 2: Sitemap 및 Robots.txt 생성 (30분)

**2.1 Sitemap**

```typescript
// src/app/sitemap.ts

import { MetadataRoute } from 'next';
import { prisma } from '@/lib/db/prisma';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://example.com';
  const locales = ['en', 'ko']; // 프로젝트 지원 로케일

  // 정적 페이지
  const staticPages = [
    '',
    '/search',
    '/about',
    // 프로젝트별 정적 페이지 추가
  ];

  const staticUrls = locales.flatMap((locale) =>
    staticPages.map((page) => ({
      url: `${baseUrl}/${locale}${page}`,
      lastModified: new Date(),
      changeFrequency: 'weekly' as const,
      priority: page === '' ? 1.0 : 0.8,
      alternates: {
        languages: Object.fromEntries(
          locales.map((l) => [l, `${baseUrl}/${l}${page}`])
        ),
      },
    }))
  );

  // 동적 페이지 ([Resource] 상세)
  const resources = await prisma.[resource].findMany({
    select: { id: true, updatedAt: true },
  });

  const resourceUrls = locales.flatMap((locale) =>
    resources.map((item) => ({
      url: `${baseUrl}/${locale}/[resources]/${item.id}`,
      lastModified: item.updatedAt,
      changeFrequency: 'monthly' as const,
      priority: 0.6,
      alternates: {
        languages: Object.fromEntries(
          locales.map((l) => [l, `${baseUrl}/${l}/[resources]/${item.id}`])
        ),
      },
    }))
  );

  return [...staticUrls, ...resourceUrls];
}
```

**2.2 Robots.txt**

```typescript
// src/app/robots.ts

import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/admin/'],
      },
    ],
    sitemap: 'https://example.com/sitemap.xml',
  };
}
```

**체크리스트**:
- [ ] sitemap.ts 구현
- [ ] robots.ts 구현
- [ ] 모든 공개 페이지 sitemap에 포함
- [ ] hreflang 대체 링크 포함

---

### Step 3: 구조화된 데이터 (JSON-LD) (30분)

```typescript
// src/components/StructuredData.tsx

export function StructuredData({ resource }: { resource: Resource }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: `${resource.name} - [MainEntity]`,
    description: resource.summary,
    author: {
      '@type': 'Organization',
      name: '[project-name]',
    },
    publisher: {
      '@type': 'Organization',
      name: '[project-name]',
      logo: {
        '@type': 'ImageObject',
        url: 'https://example.com/logo.png',
      },
    },
    datePublished: resource.createdAt,
    dateModified: resource.updatedAt,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}
```

**사용법**:

```typescript
// src/app/[locale]/[resources]/[id]/page.tsx

export default function ResourceDetailPage({ resource }) {
  return (
    <>
      <StructuredData resource={resource} />
      {/* 페이지 내용 */}
    </>
  );
}
```

**체크리스트**:
- [ ] Article 스키마 구현
- [ ] Organization 스키마 구현
- [ ] BreadcrumbList 스키마 구현 (선택)
- [ ] 주요 페이지에 JSON-LD 추가

---

### Step 4: 성능 최적화 (45-60분)

**4.1 이미지 최적화**

```typescript
// next/image 사용
import Image from 'next/image';

<Image
  src="/images/[resource].png"
  alt="[Resource]"
  width={200}
  height={200}
  loading="lazy"
  placeholder="blur"
/>
```

**4.2 번들 크기 최적화**

```typescript
// next.config.ts

const config = {
  // 번들 분석
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          // UI 컴포넌트 분리
          ui: {
            name: 'ui',
            test: /[\\/]src[\\/]components[\\/]ui[\\/]/,
            priority: 10,
          },
          // 라이브러리 분리
          lib: {
            test: /[\\/]node_modules[\\/]/,
            name(module) {
              const packageName = module.context.match(
                /[\\/]node_modules[\\/](.*?)([\\/]|$)/
              )[1];
              return `npm.${packageName.replace('@', '')}`;
            },
          },
        },
      };
    }
    return config;
  },

  // 압축
  compress: true,

  // 이미지 최적화
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
  },
};
```

**4.3 Lazy Loading**

**동적 import 대상 기준**:
- 초기 뷰포트에 보이지 않는 컴포넌트 (below-the-fold)
- 사용자 인터랙션 후에만 표시되는 모달, 드롭다운, 차트
- 조건부 렌더링 컴포넌트 (로그인 후에만 표시 등)

```typescript
// 동적 import
import dynamic from 'next/dynamic';

const CompareClient = dynamic(() => import('@/components/compare/CompareClient'), {
  loading: () => <ComparePageSkeleton />,
  ssr: false,
});
```

**4.4 Prefetching**

```typescript
// 중요한 리소스 prefetch
<link rel="prefetch" href="/api/[resources]/popular" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
```

**체크리스트**:
- [ ] 모든 이미지 next/Image로 변환
- [ ] 번들 크기 최적화 (< 200KB initial bundle) (gzipped 기준, CSS/폰트 제외. `next build` 출력의 "First Load JS" 항목으로 측정)
- [ ] Lazy loading 적용 (비필수 컴포넌트)
- [ ] Prefetching 설정
- [ ] 압축 활성화

---

### Step 5: i18n 완성 및 검증 (30분)

**5.1 번역 키 검증**

```typescript
// scripts/reporting/validate-i18n.ts

import * as fs from 'fs';
import * as path from 'path';

const locales = ['en', 'ko']; // 프로젝트 지원 로케일
const localesDir = path.join(process.cwd(), 'src/i18n/locales');

function validateI18n() {
  console.log('🌐 i18n 검증');
  console.log('='.repeat(50));

  // 모든 로케일 파일 로드
  const translations = locales.map((locale) => {
    const filePath = path.join(localesDir, `${locale}.json`);
    return {
      locale,
      data: JSON.parse(fs.readFileSync(filePath, 'utf-8')),
    };
  });

  // 기준 로케일 (영어)
  const baseLocale = translations.find((t) => t.locale === 'en')!;
  const baseKeys = getAllKeys(baseLocale.data);

  console.log(`\n기준 키 수 (en): ${baseKeys.length}개`);

  // 다른 로케일 검증
  const issues: string[] = [];

  translations.forEach((translation) => {
    if (translation.locale === 'en') return;

    const keys = getAllKeys(translation.data);
    const missing = baseKeys.filter((key) => !keys.includes(key));
    const extra = keys.filter((key) => !baseKeys.includes(key));

    console.log(`\n${translation.locale}:`);
    console.log(`  키 수: ${keys.length}개`);

    if (missing.length > 0) {
      console.log(`  ⚠️  누락: ${missing.length}개`);
      missing.slice(0, 5).forEach((key) => console.log(`    - ${key}`));
      issues.push(`${translation.locale}: ${missing.length}개 누락`);
    }

    if (extra.length > 0) {
      console.log(`  ⚠️  추가: ${extra.length}개`);
      issues.push(`${translation.locale}: ${extra.length}개 추가`);
    }

    if (missing.length === 0 && extra.length === 0) {
      console.log(`  ✅ 완벽`);
    }
  });

  if (issues.length === 0) {
    console.log('\n✅ 모든 로케일 검증 통과');
  } else {
    console.log('\n❌ i18n 이슈:');
    issues.forEach((issue) => console.log(`  - ${issue}`));
    process.exit(1);
  }
}

function getAllKeys(obj: any, prefix = ''): string[] {
  return Object.keys(obj).flatMap((key) => {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    return typeof obj[key] === 'object'
      ? getAllKeys(obj[key], fullKey)
      : [fullKey];
  });
}

validateI18n();
```

**5.2 번역 누락 자동 채우기** (선택)

```bash
# 번역 API 사용 (Google Translate API 등)
npm install @google-cloud/translate
```

**체크리스트**:
- [ ] 모든 로케일 키 일치 확인
- [ ] 누락된 번역 채우기
- [ ] 번역 품질 검토 (네이티브 스피커)
- [ ] 문화권별 날짜/숫자 포맷 적용

---

### Step 6: Lighthouse 감사 (20분)

```bash
# Lighthouse CI 실행
npm install -g @lhci/cli

lhci autorun --config=lighthouserc.js
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
  },
};
```

**체크리스트**:
- [ ] Lighthouse Performance >= 85
- [ ] Lighthouse Accessibility >= 85
- [ ] Lighthouse SEO >= 90
- [ ] Lighthouse Best Practices >= 85

---

## 📤 출력 파일

1. **SEO**:
   - 모든 페이지에 메타데이터 추가
   - `src/app/sitemap.ts`
   - `src/app/robots.ts`
   - `src/components/StructuredData.tsx`

2. **성능**:
   - `next.config.ts` (업데이트)
   - 이미지 최적화 (next/Image)
   - Lazy loading 적용

3. **i18n**:
   - `scripts/reporting/validate-i18n.ts`
   - 모든 로케일 파일 완성

4. **보고서**:
   - Lighthouse 보고서

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| Lighthouse Performance < 85 | 번들 분석(`@next/bundle-analyzer`), 미사용 의존성 제거, 이미지 최적화 확인 |
| CLS(Cumulative Layout Shift) > 0.1 | 이미지/폰트에 `width`/`height` 명시, 스켈레톤 UI 적용 |
| i18n 번역 키 누락 | `next-intl`의 `onError` 핸들러로 누락 키 로깅, 기본 언어(en) 폴백 |

## ✅ 완료 체크리스트

- [ ] 모든 페이지 SEO 메타데이터 추가
- [ ] OpenGraph 이미지 설정
- [ ] Sitemap 생성
- [ ] Robots.txt 생성
- [ ] JSON-LD 구조화된 데이터 추가
- [ ] 이미지 최적화 (next/Image)
- [ ] 번들 크기 최적화 (< 200KB)
- [ ] Lazy loading 적용
- [ ] i18n 검증 통과
- [ ] Lighthouse Performance >= 85
- [ ] Lighthouse Accessibility >= 85
- [ ] Lighthouse SEO >= 90
- [ ] Git 커밋:
  ```bash
  git add src/app/ src/components/ scripts/
  git commit -m "feat: SEO 최적화, 성능 개선, i18n 완성 (Phase 4)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-4/15-security-compliance.md를 읽고 SCA로 작동해주세요"
```

