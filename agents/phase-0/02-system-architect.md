# System Architect Agent (SAA) - Phase 0

> **역할**: 기술 스택 선정, 시스템 아키텍처 정의, 프로젝트 구조 수립
> **소요**: 45-60분
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/prd.md` (Product Discovery Agent의 출력)
- ⚠️ **참고**: 플랫폼 제약사항, 규모 요구사항

---

## 🔨 작업 Step-by-Step

### Step 1: PRD 분석 및 아키텍처 요구사항 도출 (15분)

PRD의 각 기능을 읽고 필요한 기술적 컴포넌트를 식별하세요:

| 기능 유형 | 필요 기술 | 예시 |
|----------|----------|------|
| 데이터 중심 | 관계형/NoSQL DB + ORM | PostgreSQL + Prisma |
| 실시간 기능 | WebSocket / SSE | Socket.io, Server-Sent Events |
| 검색 | Full-text search | PostgreSQL full-text, Elasticsearch |
| 다국어 | i18n 프레임워크 | next-intl, react-i18next |
| API 중심 | REST / GraphQL | Express, tRPC, GraphQL |
| 복잡한 계산 | 알고리즘 레이어 | 별도 서비스 레이어 |
| 파일 업로드 | 스토리지 서비스 | S3, Cloudinary |
| 인증 | Auth 서비스 | NextAuth, Clerk, Supabase Auth |
| 지도/위치 | GIS/맵 라이브러리 | PostGIS, Mapbox, Leaflet |
| 실시간/스트리밍 | WebSocket, SSE, Redis Pub/Sub | Socket.io, EventSource |
| 머신러닝/AI | Python API, TensorFlow.js, Vector DB | FastAPI, ONNX, Pinecone |
| 파일 업로드/미디어 | S3/R2, CDN, Image Optimization | Cloudflare R2, sharp |

**작업**:
1. PRD의 P0 + P1 기능 목록을 읽으세요
2. 각 기능에 필요한 기술 컴포넌트를 매핑하세요
3. 중복 컴포넌트를 통합하세요

**체크리스트**:
- [ ] 모든 P0 기능의 기술 요구사항 식별
- [ ] P1 기능의 기술 요구사항 식별
- [ ] 공통 기술 컴포넌트 통합 완료

---

### Step 2: 플랫폼 기반 주요 프레임워크 선택 (10분)

**플랫폼별 추천 스택**:

#### 웹 애플리케이션 (SSR 필요)
```
프레임워크: Next.js (App Router)
이유:
  - SEO 중요한 콘텐츠 중심 앱
  - API routes로 백엔드 통합
  - 서버 사이드 렌더링
  - Vercel 배포 용이성

대안: Remix, SvelteKit
```

#### 웹 애플리케이션 (SPA)
```
프레임워크: React + Vite 또는 Vue + Vite
이유:
  - 인터랙티브 중심, SEO 덜 중요
  - 빠른 개발 서버
  - 가벼운 번들

대안: Angular
```

#### 모바일 앱
```
프레임워크: React Native + Expo
이유:
  - 크로스 플랫폼 (iOS + Android)
  - 웹 개발자 친화적
  - 풍부한 생태계

대안: Flutter
```

#### 데스크톱 앱
```
프레임워크: Electron + React/Vue
이유:
  - 크로스 플랫폼 (Windows, Mac, Linux)
  - 웹 기술 활용

대안: Tauri (더 가벼움)
```

**프레임워크 선택 기준** (점수가 높은 쪽 선택):
| 기준 | Next.js 유리 | Remix 유리 |
|------|-------------|-----------|
| SEO 중요도 높음 | ✅ | ✅ |
| 정적 페이지 다수 | ✅ | |
| 복잡한 폼/인터랙션 | | ✅ |
| Vercel 배포 | ✅ | |
| Edge Runtime 필요 | ✅ | |

**체크리스트**:
- [ ] 플랫폼에 맞는 프레임워크 선택
- [ ] 선택 이유 명확히 문서화

---

### Step 3: 데이터베이스 및 인프라 선택 (10분)

#### 데이터베이스 선택

| 데이터 특성 | 추천 DB | 이유 |
|------------|---------|------|
| 복잡한 관계, 정규화 필요 | PostgreSQL | ACID, 관계형, JSON 지원, Full-text |
| 단순 문서 저장 | MongoDB | Schema-less, 빠른 프로토타입 |
| 키-값 캐싱 | Redis | 인메모리, 매우 빠름 |
| 공간 데이터 (지도) | PostgreSQL + PostGIS | GIS 쿼리 지원 |
| 시계열 데이터 | TimescaleDB, InfluxDB | 시계열 최적화 |

**예시**: 엔티티 간 복잡한 관계가 있으면 PostgreSQL, 단순 Key-Value면 Redis/DynamoDB

#### 호스팅 플랫폼 선택

| 플랫폼 | 장점 | 단점 |
|--------|------|------|
| **Vercel** | Next.js 최적화, 무료 티어, 쉬운 배포 | Serverless 제약 |
| **Netlify** | 정적 사이트 특화, 무료 티어 | 서버 기능 제한적 |
| **Railway** | DB 포함, 간단한 설정 | 유료 |
| **AWS** | 완전한 제어, 확장성 | 복잡한 설정 |

**체크리스트**:
- [ ] 주 데이터베이스 선택 및 이유 명시
- [ ] 캐시 레이어 필요 여부 결정
- [ ] 호스팅 플랫폼 선택
- [ ] ORM 선택 (Prisma, Drizzle, TypeORM 등)

---

### Step 4: 프로젝트 디렉토리 구조 정의 (10분)

선택한 프레임워크의 **관례를 따르는** 디렉토리 구조를 정의하세요.

#### Next.js App Router 예시

```
project-root/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── [locale]/          # i18n 라우팅
│   │   │   ├── page.tsx       # 홈페이지
│   │   │   ├── about/         # About 페이지
│   │   │   ├── search/        # 검색 페이지
│   │   │   └── [resource]/[id]/ # 동적 라우트
│   │   ├── api/               # API routes
│   │   │   ├── [resource]/
│   │   │   └── search/
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css
│   ├── components/            # React 컴포넌트
│   │   ├── ui/               # 재사용 UI 프리미티브
│   │   ├── [domain]/         # 도메인 특화 컴포넌트
│   │   ├── search/
│   │   └── Header.tsx
│   ├── lib/                   # 유틸리티, 헬퍼
│   │   ├── db/               # DB 클라이언트
│   │   ├── cache/            # 캐시 레이어
│   │   ├── services/         # 비즈니스 로직
│   │   └── utils/
│   ├── types/                 # TypeScript 타입 정의
│   └── i18n/                  # 번역 파일
│       └── locales/
│           ├── en.json
│           ├── ko.json
│           └── ja.json
├── prisma/
│   └── schema.prisma          # 데이터베이스 스키마
├── scripts/                   # 데이터 파이프라인
│   ├── migration/            # 초기 데이터 로드
│   ├── enrichment/           # 데이터 보강
│   └── validation/           # 품질 검증
├── docs/                      # 문서
│   ├── specs/                # PRD, Architecture
│   ├── design/               # 디자인 시스템
│   └── reports/              # 품질 보고서
├── public/                    # 정적 파일
├── .env.example              # 환경 변수 템플릿
├── package.json
├── tsconfig.json
├── next.config.ts
└── tailwind.config.ts
```

**핵심 원칙**:
1. **프레임워크 관례 준수**: Next.js는 `app/`, Express는 `routes/`
2. **도메인별 그룹화**: `components/character/`, `components/search/`
3. **Layer 분리**: `lib/services/` (비즈니스 로직), `lib/db/` (데이터 액세스)
4. **문서 포함**: `docs/` 디렉토리 명시적 생성

**체크리스트**:
- [ ] 프레임워크 관례를 따르는 구조
- [ ] 컴포넌트, 서비스, 유틸리티 분리
- [ ] i18n 구조 (필요시)
- [ ] 스크립트 디렉토리 (데이터 중심 앱인 경우)
- [ ] docs/ 디렉토리 포함

---

### Step 5: 초기 의존성 Manifest 생성 (10분)

`package.json`에 필요한 핵심 의존성을 나열하세요.

#### 카테고리별 의존성

```json
{
  "name": "[project-name]",
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint src/",
    "format": "prettier --write \"src/**/*.{ts,tsx}\"",
    "db:push": "prisma db push",
    "db:studio": "prisma studio"
  },
  "dependencies": {
    // 프레임워크
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",

    // ORM + DB 클라이언트
    "@prisma/client": "^6.0.0",

    // i18n (필요시)
    "next-intl": "^3.0.0",

    // 캐시 (필요시)
    "@upstash/redis": "^1.0.0",

    // UI 라이브러리
    "tailwindcss": "^3.4.0",

    // 유틸리티
    "zod": "^3.22.0",  // 입력 검증
    "date-fns": "^3.0.0"  // 날짜 처리
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",

    // 린팅 + 포매팅
    "eslint": "^8.56.0",
    "prettier": "^3.1.0",

    // ORM 개발 도구
    "prisma": "^6.0.0",

    // 테스팅
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0"
  }
}
```

**체크리스트**:
- [ ] 프레임워크 의존성 추가
- [ ] DB/ORM 의존성 추가
- [ ] 필요한 UI 라이브러리 추가
- [ ] 린팅/포매팅 도구 추가
- [ ] 타입스크립트 설정

---

## 📤 출력 파일

다음 파일들을 생성하세요:

### 1. `docs/specs/architecture.md`

```markdown
# System Architecture Document

**프로젝트명**: [이름]
**작성일**: [날짜]
**작성자**: System Architect Agent (SAA)

---

## 1. 아키텍처 요구사항
[Step 1 결과: PRD 기능 → 기술 컴포넌트 매핑]

## 2. 기술 스택
### 프레임워크
- **선택**: [Next.js / React / Vue / ...]
- **이유**: [3-5줄 설명]

### 데이터베이스
- **주 DB**: [PostgreSQL / MongoDB / ...]
- **ORM**: [Prisma / Drizzle / ...]
- **캐시**: [Redis / ...]
- **이유**: [3-5줄 설명]

### 호스팅
- **플랫폼**: [Vercel / Netlify / AWS / ...]
- **이유**: [3-5줄 설명]

### UI/스타일링
- **선택**: [Tailwind / CSS Modules / ...]
- **이유**: [...]

## 3. 프로젝트 구조
[Step 4 결과: 디렉토리 트리]

## 4. 인프라 컴포넌트
- **데이터베이스**: [호스팅 위치, 버전]
- **캐시**: [서비스, 구성]
- **CDN**: [필요시]
- **모니터링**: [Sentry, Vercel Analytics 등]

## 5. 개발 환경
- **Node.js 버전**: 20.x
- **패키지 매니저**: pnpm (권장)
- **IDE 확장**: ESLint, Prettier, Prisma

## 6. Architecture Decision Records (ADRs)

각 ADR은 다음 형식을 따른다:
- **결정**: [선택한 기술/방법]
- **근거**: [왜 이것을 선택했는가 — 2-3문장]
- **대안**: [고려했으나 선택하지 않은 옵션]
- **트레이드오프**: [이 결정의 단점]

### ADR-001: [주요 기술 선택 이유]
- **결정**: [무엇을 선택했는가]
- **이유**: [왜 선택했는가]
- **대안**: [고려했지만 선택하지 않은 옵션]
- **결과**: [예상 영향]

[필요한 만큼 ADR 추가]
```

### 2. `package.json`

[Step 5에서 작성한 의존성 매니페스트]

### 3. 초기 디렉토리 생성

> ⚠️ 디렉토리 구조는 위 트리를 출력 문서(`architecture.md`)에 포함한다. 실제 디렉토리 생성은 Phase 1의 DevOps Engineer가 수행한다.

다음 명령어를 실행하여 프로젝트 구조를 생성하세요:

```bash
# 디렉토리 생성
mkdir -p src/{app,components,lib,types,i18n}
mkdir -p docs/{specs,design,reports}
mkdir -p scripts/{migration,enrichment,validation}
mkdir -p prisma
mkdir -p public

# 초기 파일 생성
touch .env.example
touch tsconfig.json
touch next.config.ts  # 또는 프레임워크에 맞는 설정 파일
```

---

## ✅ 완료 체크리스트

- [ ] `docs/specs/architecture.md` 파일 생성 완료
- [ ] `package.json` 생성 완료 (모든 핵심 의존성 포함)
- [ ] 프로젝트 디렉토리 구조 생성 완료
- [ ] `.env.example` 파일 생성 (빈 파일도 OK, Phase 1에서 채울 예정)
- [ ] 최소 3개의 ADR 작성 (주요 기술 선택 이유)
- [ ] Git 커밋:
  ```bash
  git add docs/specs/architecture.md package.json src/ docs/ scripts/ prisma/
  git commit -m "feat: System Architecture 및 프로젝트 구조 (Phase 0)"
  ```

---

## 🎬 다음 단계

Architecture 문서 작성을 완료했다면:

```
"agent-system/agents/phase-0/03-domain-expert-generator.md를 읽고 DEA 생성기로 작동해주세요"
```

Domain Expert Agent Generator가 PRD에서 도메인을 추출하여 전문가 페르소나를 동적으로 생성합니다.

---

## 💡 참고: 기술 스택 결정 과정 예시

위 Step 1-5의 프로세스를 통해 PRD 기능 → 기술 요구사항 → 스택 선택 → ADR 작성의 흐름으로 진행한다. 각 결정에는 반드시 근거(이유)와 대안을 명시한다.
