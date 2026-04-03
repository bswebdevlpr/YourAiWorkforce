# DevOps Engineer Agent (DOE) - Phase 1

> **역할**: 빌드 시스템 구성, 환경 변수 설정, 개발 도구 설정
> **소요**: 45-60분
> **난이도**: ⭐⭐⭐☆☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/architecture.md`
- ✅ **필수**: `package.json` (System Architect가 생성)

---

## 🔨 작업 Step-by-Step

### Step 1: 프레임워크별 빌드 설정 (15-20분)

Architecture 문서의 기술 스택에 맞는 빌드 설정 파일을 작성하세요.

#### Next.js 빌드 설정

**파일 위치**: `next.config.ts`

```typescript
import type { NextConfig } from 'next';
import createNextIntlPlugin from 'next-intl/plugin';

// i18n 플러그인 설정 (다국어 지원 시)
const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

const nextConfig: NextConfig = {
  // TypeScript strict 모드
  typescript: {
    ignoreBuildErrors: false,
  },

  // ESLint strict 모드
  eslint: {
    ignoreDuringBuilds: false,
  },

  // 이미지 최적화 (필요시)
  images: {
    domains: ['example.com'],  // 외부 이미지 도메인
  },

  // 환경 변수 (공개)
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  },

  // 프로덕션 최적화
  poweredByHeader: false,  // X-Powered-By 헤더 제거 (보안)
  compress: true,          // Gzip 압축
};

export default withNextIntl(nextConfig);
```

#### Tailwind CSS 설정

**파일 위치**: `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 프로젝트 특화 색상 (도메인 기반)
        // Phase 3에서 Frontend Developer가 추가
      },
    },
  },
  darkMode: 'class',  // 다크 모드 지원
  plugins: [],
};

export default config;
```

**체크리스트**:
- [ ] 프레임워크 설정 파일 생성 (`next.config.ts` 또는 `vite.config.ts`)
- [ ] Tailwind 설정 파일 생성 (UI 프레임워크 사용 시)
- [ ] 설정 파일에 주석으로 설명 추가
- [ ] `pnpm dev` 명령어로 개발 서버 실행 확인

---

### Step 2: TypeScript 설정 (10분)

**파일 위치**: `tsconfig.json`

```json
{
  "compilerOptions": {
    // Strict 모드 (타입 안전성 최대화)
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,

    // 모듈 해석
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,

    // Path alias (편의성)
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"]
    },

    // Next.js 특화 설정
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],

    // 출력 설정
    "skipLibCheck": true,
    "allowJs": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

**핵심 설정**:
- `"strict": true` - 타입 안전성 최대화 (⚠️ 필수)
- Path alias (`@/*`) - import 경로 단축
- `"skipLibCheck": true` - 외부 라이브러리 타입 체크 생략 (빌드 속도 향상)

**체크리스트**:
- [ ] `tsconfig.json` 생성
- [ ] `"strict": true` 설정 확인
- [ ] `pnpm build` 실행하여 TypeScript 에러 확인

---

### Step 3: Linting & Formatting 설정 (15-20분)

#### ESLint 설정

**파일 위치**: `eslint.config.mjs`

```javascript
import { FlatCompat } from '@eslint/eslintrc';
import js from '@eslint/js';
import typescriptEslint from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';

const compat = new FlatCompat();

export default [
  js.configs.recommended,
  ...compat.extends('next/core-web-vitals'),
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },
    rules: {
      // 경고를 에러로 승격 (엄격한 코드 품질)
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
];
```

#### Prettier 설정

**파일 위치**: `.prettierrc`

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "always"
}
```

**파일 위치**: `.prettierignore`

```
node_modules/
.next/
out/
build/
dist/
coverage/
.env*
*.log
```

**체크리스트**:
- [ ] `eslint.config.mjs` 생성
- [ ] `.prettierrc` 생성
- [ ] `pnpm lint` 실행하여 에러 확인
- [ ] `pnpm format` 스크립트 추가 (`package.json`):
  ```json
  "scripts": {
    "format": "prettier --write \"src/**/*.{ts,tsx}\""
  }
  ```

---

### Step 4: Pre-commit Hooks 설정 (10분)

코드가 커밋되기 전에 자동으로 lint + format을 실행하도록 설정하세요.

#### Husky + lint-staged 설치

```bash
pnpm add -D husky lint-staged
npx husky init
```

#### Pre-commit Hook 설정

**파일 위치**: `.husky/pre-commit`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npx lint-staged
```

**파일 위치**: `package.json` (lint-staged 설정 추가)

```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md}": [
      "prettier --write"
    ]
  }
}
```

**체크리스트**:
- [ ] Husky 설치 및 초기화 완료
- [ ] `.husky/pre-commit` 파일 생성 및 실행 권한 부여
- [ ] `package.json`에 `lint-staged` 설정 추가
- [ ] 테스트 커밋으로 pre-commit hook 작동 확인

---

### Step 5: 환경 변수 설정 (10분)

#### `.env.example` 완성

Backend Developer가 생성한 `.env.example`을 확장하세요:

```bash
# ==========================================
# 데이터베이스
# ==========================================
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# ==========================================
# 캐시 (선택적, Phase 2+)
# ==========================================
# Redis (로컬 개발)
# REDIS_URL="redis://localhost:6379"

# Upstash Redis (프로덕션)
# UPSTASH_REDIS_REST_URL=""
# UPSTASH_REDIS_REST_TOKEN=""

# ==========================================
# 앱 설정
# ==========================================
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NODE_ENV="development"

# ==========================================
# 모니터링 (Phase 6)
# ==========================================
# SENTRY_DSN=""
# VERCEL_ANALYTICS_ID=""
```

#### 환경 변수 검증 스크립트

**파일 위치**: `src/lib/env.ts`

```typescript
import { z } from 'zod';

const envSchema = z.object({
  // SQLite 사용 시 file: 프로토콜을 허용해야 함
  DATABASE_URL: z.string().min(1), // .url() 대신 .min(1) 사용 — SQLite file: 경로 호환
  NODE_ENV: z.enum(['development', 'production', 'test']),
  NEXT_PUBLIC_APP_URL: z.string().url(),

  // 선택적 변수 (Phase 2+)
  UPSTASH_REDIS_REST_URL: z.string().url().optional(),
  UPSTASH_REDIS_REST_TOKEN: z.string().optional(),
});

// 환경 변수 검증
export const env = envSchema.parse(process.env);
```

**사용 예시**:

```typescript
import { env } from '@/lib/env';

console.log(env.DATABASE_URL);  // 타입 안전하게 접근
```

**체크리스트**:
- [ ] `.env.example` 모든 필요한 변수 문서화
- [ ] 각 변수에 주석으로 설명 추가
- [ ] `src/lib/env.ts` 생성 (Zod 검증)
- [ ] `.env`를 `.gitignore`에 추가 (⚠️ 시크릿 노출 방지)

---

### Step 6: Vitest 설정 (선택적, Phase 2+) (10분)

**파일 위치**: `vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./test/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

**파일 위치**: `test/setup.ts`

```typescript
import '@testing-library/jest-dom';
```

**체크리스트**:
- [ ] `vitest.config.ts` 생성
- [ ] `test/setup.ts` 생성
- [ ] `package.json`에 테스트 스크립트 추가:
  ```json
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui"
  }
  ```

---

## 📤 출력 파일

1. **`next.config.ts`** (또는 `vite.config.ts`): 프레임워크 빌드 설정
2. **`tailwind.config.ts`**: Tailwind CSS 설정
3. **`tsconfig.json`**: TypeScript 설정
4. **`eslint.config.mjs`**: ESLint 설정
5. **`.prettierrc`**: Prettier 설정
6. **`.husky/pre-commit`**: Pre-commit hook
7. **`.env.example`**: 환경 변수 템플릿 (완성)
8. **`src/lib/env.ts`**: 환경 변수 검증
9. **`vitest.config.ts`**: Vitest 설정 (선택적)

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| `pnpm install` 의존성 충돌 | `pnpm install --force` 시도. 지속 시 충돌 패키지를 architecture.md 기준으로 버전 고정 |
| ESLint/Prettier 설정 충돌 | Prettier를 우선하고 ESLint 규칙을 `off`로 조정 |
| 환경변수 검증 실패 | `.env.example`과 대조하여 누락 변수 추가. 선택 변수는 `z.string().optional()` 처리 |

## ✅ 완료 체크리스트

- [ ] 모든 설정 파일 생성 완료
- [ ] `pnpm dev` 실행 성공
- [ ] `pnpm build` 실행 성공 (TypeScript 에러 0개). 단, Phase 1 시점에서는 API 라우트가 최소한이므로 빌드 경고(warning)는 허용한다.
- [ ] `pnpm lint` 실행 성공 (ESLint 에러 0개)
- [ ] Pre-commit hook 작동 확인 (테스트 커밋)
- [ ] `.env` 파일이 `.gitignore`에 있는지 확인
- [ ] Git 커밋:
  ```bash
  git add next.config.ts tailwind.config.ts tsconfig.json eslint.config.mjs .prettierrc .husky/ src/lib/env.ts .env.example
  git commit -m "feat: 빌드 시스템 및 개발 도구 설정 (Phase 1 완료)"
  ```

---

## 🎬 다음 단계

**Phase 1 완료!** 🎉

다음 항목들이 완성되었습니다:
- ✅ 데이터베이스 스키마
- ✅ 기본 API 엔드포인트
- ✅ 초기 데이터 로딩
- ✅ 빌드 시스템 구성
- ✅ 개발 도구 설정

이제 Phase 2 (Core Features)로 진행하세요:

```
"agent-system/agents/phase-2/07-frontend-developer.md를 읽고 FDA로 작동해주세요"
```

---

## 💡 핵심 설계 결정

**ADR-004: TypeScript Strict 모드**
- 이유: 타입 에러 조기 발견, 런타임 버그 방지
- 트레이드오프: 초기 개발 속도 약간 감소, 장기적으로는 유지보수 비용 절감
- 결과: 전체 프로젝트에서 TypeScript 에러 0개 유지

**ADR-005: Pre-commit Hook**
- 이유: 코드 품질 자동 검증, 리뷰 시간 절감
- 대안: CI/CD에서만 검증 (피드백 지연)
- 결과: 모든 커밋이 lint 통과 보장

**ADR-006: Zod 환경 변수 검증**
- 이유: 런타임 환경 변수 오류 조기 발견 (앱 시작 시 실패)
- 대안: 사용 시점에 검증 (에러 발견 지연)
- 결과: 배포 후 환경 변수 오류 0건
