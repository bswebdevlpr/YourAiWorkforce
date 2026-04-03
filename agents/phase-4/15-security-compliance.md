# Security & Compliance Agent (SCA) - Phase 4

> **역할**: 보안 검토, 개인정보 처리방침, 약관, 쿠키 동의 구현
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐☆☆

## 📥 입력 파일

- ✅ **필수**: 모든 API 라우트 (`src/app/api/`)
- ✅ **필수**: 데이터베이스 스키마 (`prisma/schema.prisma`)
- ✅ **필수**: 환경 변수 (`.env`)

---

## 🔨 작업 Step-by-Step

### Step 1: 보안 헤더 설정 (20분)

```typescript
// next.config.ts

const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
];

const config = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};

export default config;
```

**체크리스트**:
- [ ] HSTS 헤더 설정
- [ ] X-Frame-Options 설정
- [ ] X-Content-Type-Options 설정
- [ ] Referrer-Policy 설정
- [ ] Permissions-Policy 설정

---

### Step 2: Rate Limiting 검증 (15분)

```typescript
// src/lib/ratelimit.ts (검증)

import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

export const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
  prefix: '@upstash/ratelimit',
});

// API 라우트에서 사용
export async function withRateLimit(
  request: Request,
  handler: () => Promise<Response>
): Promise<Response> {
  const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1';

  const { success, limit, reset, remaining } = await ratelimit.limit(ip);

  if (!success) {
    return new Response('Too Many Requests', {
      status: 429,
      headers: {
        'X-RateLimit-Limit': limit.toString(),
        'X-RateLimit-Remaining': remaining.toString(),
        'X-RateLimit-Reset': reset.toString(),
      },
    });
  }

  return handler();
}
```

**체크리스트**:
- [ ] 모든 API 라우트에 rate limiting 적용
- [ ] Rate limit 헤더 반환
- [ ] Redis 연결 에러 처리 (graceful degradation)

---

### Step 3: 환경 변수 보안 검증 (15분)

```typescript
// src/lib/env.ts

import { z } from 'zod';

const envSchema = z.object({
  // 데이터베이스
  DATABASE_URL: z.string().url(),

  // Redis
  UPSTASH_REDIS_REST_URL: z.string().url().optional(),
  UPSTASH_REDIS_REST_TOKEN: z.string().optional(),

  // 외부 API
  OPENAI_API_KEY: z.string().optional(),

  // 애플리케이션
  NEXT_PUBLIC_APP_URL: z.string().url(),

  // Node 환경
  NODE_ENV: z.enum(['development', 'production', 'test']),
});

export const env = envSchema.parse(process.env);

**환경변수 누락 시 동작**:
- 필수 변수 (`DATABASE_URL`, `NODE_ENV`) 누락: 앱 시작 실패 + 명확한 에러 메시지
- 선택 변수 (`REDIS_URL`) 누락: 해당 기능 비활성화 + 경고 로그. 프로덕션에서는 rate limiting을 in-memory 폴백으로 대체

// 시크릿 검증 (프로덕션)
if (process.env.NODE_ENV === 'production') {
  const requiredSecrets = [
    'DATABASE_URL',
    'UPSTASH_REDIS_REST_URL',
    'UPSTASH_REDIS_REST_TOKEN',
  ];

  requiredSecrets.forEach((secret) => {
    if (!process.env[secret]) {
      throw new Error(`Missing required environment variable: ${secret}`);
    }
  });
}
```

**보안 체크리스트**:
```bash
# .env.example 생성 (실제 값 제거)
DATABASE_URL="postgresql://user:password@localhost:5432/db"
UPSTASH_REDIS_REST_URL="https://your-redis.upstash.io"
UPSTASH_REDIS_REST_TOKEN="your-token-here"
NEXT_PUBLIC_APP_URL="https://example.com"
```

**체크리스트**:
- [ ] `.env.example` 생성 (실제 값 제거)
- [ ] `.gitignore`에 `.env` 포함 확인
- [ ] 환경 변수 스키마 검증
- [ ] 프로덕션 필수 변수 체크

---

### Step 4: 개인정보 처리방침 페이지 (30-45분)

```markdown
# 개인정보 처리방침

**최종 업데이트**: 2026-02-16

## 1. 수집하는 정보

[프로젝트명]은 다음 정보를 수집합니다:

### 1.1 자동 수집 정보
- IP 주소 (rate limiting 목적)
- 브라우저 타입 및 버전
- 접속 시간 및 페이지 방문 기록

### 1.2 사용자 제공 정보
- 검색 쿼리 (로컬 스토리지에만 저장, 서버 전송 안 함)
- 사용자 선호 설정 (언어, 테마)

## 2. 정보 사용 목적

수집된 정보는 다음 목적으로 사용됩니다:

- 서비스 제공 및 개선
- 남용 방지 (rate limiting)
- 통계 분석

## 3. 정보 공유

[프로젝트명]은 사용자 정보를 제3자와 공유하지 않습니다.

## 4. 쿠키

당사는 다음 쿠키를 사용합니다:

| 쿠키명 | 목적 | 유효기간 |
|--------|------|---------|
| `theme` | 테마 설정 저장 | 1년 |
| `locale` | 언어 설정 저장 | 1년 |
| `cookie-consent` | 쿠키 동의 여부 | 1년 |

## 5. 사용자 권리

사용자는 다음 권리를 가집니다:

- 정보 접근 권리
- 정보 수정 권리
- 정보 삭제 권리
- 처리 제한 권리

## 6. 연락처

개인정보 관련 문의:
- 이메일: privacy@example.com

---

*이 개인정보 처리방침은 [날짜]부터 시행됩니다.*
```

**다국어 버전 생성**:
- `/[locale]/privacy/page.tsx`
- `src/i18n/locales/*/privacy.json`

**체크리스트**:
- [ ] 개인정보 처리방침 페이지 생성
- [ ] 4개 언어 번역 완료
- [ ] 수집 정보 명확히 기재
- [ ] 사용자 권리 명시
- [ ] 연락처 정보 포함

---

### Step 5: 서비스 약관 페이지 (30분)

```markdown
# 서비스 이용약관

**최종 업데이트**: 2026-02-16

## 1. 약관의 적용

이 약관은 [프로젝트명] 서비스 이용에 적용됩니다.

## 2. 서비스 제공

### 2.1 서비스 내용
[프로젝트명]은 다음 서비스를 제공합니다:
- [기능 1]
- [기능 2]
- [기능 3]

### 2.2 서비스 이용
- 서비스는 무료로 제공됩니다
- 서비스는 예고 없이 변경될 수 있습니다

## 3. 사용자 의무

사용자는 다음 행위를 해서는 안 됩니다:

- 불법적인 목적으로 서비스 사용
- 서비스에 과도한 부하를 주는 행위
- 다른 사용자의 서비스 이용 방해

## 4. 면책 조항

### 4.1 데이터 정확성
[프로젝트명]은 데이터의 정확성을 보장하지 않습니다.

### 4.2 서비스 가용성
서비스는 중단 없이 제공됨을 보장하지 않습니다.

## 5. 지적 재산권

### 5.1 데이터 출처
모든 데이터는 공개 소스에서 수집되었으며, 출처가 명시됩니다.

### 5.2 라이선스
- 코드: MIT License
- 데이터: [라이선스 명시]

## 6. 약관 변경

약관은 예고 없이 변경될 수 있으며, 변경 사항은 웹사이트에 게시됩니다.

## 7. 준거법

이 약관은 대한민국 법률의 적용을 받습니다.

---

*이 서비스 약관은 [날짜]부터 시행됩니다.*
```

**체크리스트**:
- [ ] 서비스 약관 페이지 생성
- [ ] 4개 언어 번역 완료
- [ ] 면책 조항 명확히 기재
- [ ] 데이터 출처 및 라이선스 명시

---

### Step 6: 쿠키 동의 배너 (30분)

```typescript
// src/components/CookieConsent.tsx

'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';

export function CookieConsent() {
  const t = useTranslations('cookie');
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookie-consent');
    if (!consent) {
      setShowBanner(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie-consent', 'accepted');
    setShowBanner(false);
  };

  const handleDecline = () => {
    localStorage.setItem('cookie-consent', 'declined');
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white p-4 shadow-lg dark:bg-gray-900">
      <div className="container mx-auto flex flex-col items-center justify-between gap-4 md:flex-row">
        <div className="flex-1">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            {t('message')}{' '}
            <a href="/privacy" className="underline">
              {t('learnMore')}
            </a>
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleDecline}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            {t('decline')}
          </button>
          <button
            onClick={handleAccept}
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            {t('accept')}
          </button>
        </div>
      </div>
    </div>
  );
}
```

**번역 파일**:

```json
// src/i18n/locales/en.json

{
  "cookie": {
    "message": "We use cookies to improve your experience on our site.",
    "learnMore": "Learn more",
    "accept": "Accept",
    "decline": "Decline"
  }
}
```

**쿠키 동의 정책**:
- 동의 쿠키 유효기간: 12개월. 만료 시 재동의 요청
- `localStorage`의 `cookie-consent` 값이 없으면 배너를 다시 표시한다

**체크리스트**:
- [ ] 쿠키 동의 배너 구현
- [ ] 4개 언어 지원
- [ ] 수락/거부 기능
- [ ] LocalStorage에 선택 저장
- [ ] 페이지 차단하지 않음 (하단 배너)

---

## 📤 출력 파일

1. **보안 헤더**:
   - `next.config.ts` (업데이트)

2. **Rate Limiting**:
   - `src/lib/ratelimit.ts` (검증)

3. **환경 변수**:
   - `.env.example`
   - `src/lib/env.ts` (업데이트)

4. **법적 페이지**:
   - `src/app/[locale]/privacy/page.tsx`
   - `src/app/[locale]/terms/page.tsx`
   - `src/i18n/locales/*/privacy.json`
   - `src/i18n/locales/*/terms.json`

5. **쿠키 동의**:
   - `src/components/CookieConsent.tsx`
   - `src/i18n/locales/*/cookie.json`

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| CSP 헤더로 인한 리소스 차단 | 브라우저 콘솔에서 차단된 도메인 확인, `Content-Security-Policy`에 추가 |
| Rate limiting 과도 적용 | 개발 환경에서는 rate limiting 비활성화 (`NODE_ENV === 'development'`) |
| HTTPS 리다이렉트 루프 | Vercel 등 PaaS의 자동 HTTPS 설정과 수동 설정 중복 확인 |

## ✅ 완료 체크리스트

- [ ] 보안 헤더 설정 완료
- [ ] Rate limiting 모든 API에 적용
- [ ] 환경 변수 검증 완료
- [ ] `.env.example` 생성 (실제 값 제거)
- [ ] `.gitignore`에 `.env` 포함 확인
- [ ] 개인정보 처리방침 페이지 생성 (4개 언어)
- [ ] 서비스 약관 페이지 생성 (4개 언어)
- [ ] 쿠키 동의 배너 구현
- [ ] 모든 법적 페이지 링크 추가 (Footer)
- [ ] Git 커밋:
  ```bash
  git add src/app/[locale]/privacy/ src/app/[locale]/terms/ src/components/CookieConsent.tsx
  git commit -m "feat: 보안 강화, 개인정보 처리방침, 약관, 쿠키 동의 (Phase 4)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-4/16-technical-writer.md를 읽고 TWA로 작동해주세요"
```

---

