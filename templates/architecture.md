# System Architecture Document

**프로젝트명**: [이름]
**작성일**: [YYYY-MM-DD]
**작성자**: System Architect Agent (SAA)

---

## 1. 아키텍처 요구사항

PRD 기능 분석 결과, 다음 기술 컴포넌트가 필요합니다:

| PRD 기능 | 필요 기술 컴포넌트 | 이유 |
|---------|------------------|------|
| [P0 기능 1] | [DB, API, 검색 등] | [설명] |
| [P0 기능 2] | [기술 컴포넌트] | [설명] |
| [P0 기능 3] | [기술 컴포넌트] | [설명] |
| [P1 기능 1] | [기술 컴포넌트] | [설명] |
| [P1 기능 2] | [기술 컴포넌트] | [설명] |

**공통 컴포넌트**:
- [공통으로 필요한 기술 1]
- [공통으로 필요한 기술 2]
- [공통으로 필요한 기술 3]

---

## 2. 기술 스택

### 2.1 프레임워크

**선택**: [Next.js / React + Vite / Vue / React Native / Flutter / ...]

**버전**: [구체적 버전]

**선택 이유**:
1. [이유 1]
2. [이유 2]
3. [이유 3]

**대안 및 선택하지 않은 이유**:
- [대안 1]: [왜 선택하지 않았는가]
- [대안 2]: [왜 선택하지 않았는가]

---

### 2.2 데이터베이스

**주 데이터베이스**: [PostgreSQL / MongoDB / MySQL / ...]

**버전**: [구체적 버전]

**선택 이유**:
1. [데이터 특성에 맞는 이유]
2. [성능 이유]
3. [생태계 이유]

**ORM**: [Prisma / Drizzle / TypeORM / Mongoose / ...]

**ORM 선택 이유**:
- [타입 안전성, 개발자 경험, 마이그레이션 등]

**캐시 레이어**: [Redis / Upstash / Memcached / 없음]
- **사용 목적**: [검색 결과 캐싱, 세션 저장 등]
- **예상 효과**: [응답 속도 X배 향상]

---

### 2.3 호스팅 & 인프라

**플랫폼**: [Vercel / Netlify / Railway / AWS / ...]

**선택 이유**:
1. [이유 1]
2. [이유 2]

**데이터베이스 호스팅**: [Vercel Postgres / Supabase / Neon / Railway / ...]

**스토리지** (필요시): [S3 / Cloudinary / ...]

**CDN**: [Vercel CDN / Cloudflare / ...]

---

### 2.4 UI & 스타일링

**CSS 프레임워크**: [Tailwind CSS / CSS Modules / Styled Components / ...]

**컴포넌트 라이브러리**: [shadcn/ui / Radix UI / MUI / 없음]

**선택 이유**:
- [개발 속도, 일관성, 커스터마이징 가능성]

---

### 2.5 개발 도구

**언어**: TypeScript [버전]

**패키지 매니저**: [pnpm / npm / yarn]

**린팅**: ESLint

**포매팅**: Prettier

**테스팅**: [Vitest / Jest / Playwright]

**Git Hooks**: Husky + lint-staged

---

## 3. 프로젝트 구조

```
project-root/
├── src/
│   ├── app/                    # [프레임워크별 라우팅]
│   │   ├── [locale]/          # (i18n 사용 시)
│   │   │   ├── page.tsx       # 홈페이지
│   │   │   ├── [feature]/     # 기능별 페이지
│   │   │   └── layout.tsx
│   │   ├── api/               # API routes
│   │   │   ├── [resource]/    # 리소스별 엔드포인트
│   │   │   └── ...
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css
│   ├── components/            # React 컴포넌트
│   │   ├── ui/               # 재사용 UI 프리미티브
│   │   ├── [domain]/         # 도메인 특화 컴포넌트
│   │   └── [feature]/        # 기능별 컴포넌트
│   ├── lib/                   # 유틸리티, 헬퍼
│   │   ├── db/               # DB 클라이언트
│   │   │   └── prisma.ts
│   │   ├── cache/            # 캐시 레이어
│   │   ├── services/         # 비즈니스 로직
│   │   ├── utils/            # 유틸리티 함수
│   │   └── env.ts            # 환경 변수 검증
│   ├── types/                 # TypeScript 타입 정의
│   │   └── index.ts
│   └── i18n/                  # (다국어 지원 시)
│       ├── request.ts
│       └── locales/
│           ├── en.json
│           └── ...
├── prisma/                    # (Prisma 사용 시)
│   └── schema.prisma
├── scripts/                   # 데이터 파이프라인
│   ├── download-data.sh      # 데이터 다운로드
│   ├── migration/            # 초기 데이터 로드
│   ├── enrichment/           # 데이터 보강
│   ├── validation/           # 품질 검증
│   └── README.md
├── docs/                      # 문서
│   ├── specs/                # PRD, Architecture
│   ├── design/               # 디자인 시스템
│   ├── personas/             # Domain Expert
│   └── reports/              # 품질 보고서
├── public/                    # 정적 파일
├── test/                      # 테스트 파일
├── .env.example              # 환경 변수 템플릿
├── .gitignore
├── package.json
├── tsconfig.json
├── next.config.ts            # (또는 프레임워크 설정)
└── tailwind.config.ts        # (Tailwind 사용 시)
```

**핵심 원칙**:
1. **프레임워크 관례 준수**: 선택한 프레임워크의 디렉토리 구조를 따름
2. **도메인별 그룹화**: 컴포넌트와 서비스를 도메인/기능별로 구조화
3. **Layer 분리**: Presentation (components) / Business Logic (services) / Data Access (db)
4. **명시적 문서화**: `docs/` 디렉토리에 모든 문서 집중

---

## 4. 데이터 흐름 아키텍처

```
[User]
  ↓
[Next.js Page (SSR/CSR)]
  ↓
[API Route Handler]
  ↓
[Service Layer] ← [Cache Layer (Redis)]
  ↓
[Prisma ORM]
  ↓
[PostgreSQL Database]
```

**설명**:
1. 사용자 요청이 Next.js 페이지로 들어옴
2. 클라이언트 사이드 또는 서버 사이드에서 API 호출
3. API Route Handler가 요청 검증
4. Service Layer에서 비즈니스 로직 실행 (캐시 확인)
5. ORM을 통해 데이터베이스 쿼리
6. 결과를 캐시에 저장 후 클라이언트에 반환

---

## 5. 인프라 컴포넌트

### 5.1 데이터베이스
- **호스팅**: [Vercel Postgres / Supabase / ...]
- **지역**: [us-east-1 / asia-northeast-1 / ...]
- **플랜**: [Free / Pro / ...]
- **예상 크기**: [100MB / 1GB / ...]

### 5.2 캐시
- **서비스**: [Upstash Redis / Vercel KV / ...]
- **플랜**: [Free / Pay-as-you-go]
- **예상 사용량**: [X MB RAM, Y requests/day]

### 5.3 CDN
- **서비스**: [자동 포함 (Vercel CDN) / Cloudflare]
- **목적**: 정적 파일 캐싱, 이미지 최적화

### 5.4 모니터링
- **에러 트래킹**: [Sentry / ...]
- **분석**: [Vercel Analytics / Google Analytics / ...]
- **성능 모니터링**: [Vercel Speed Insights / ...]

---

## 6. 개발 환경

### 6.1 필수 요구사항
- **Node.js**: 20.x 이상
- **패키지 매니저**: pnpm 9.x (권장)
- **PostgreSQL**: 16.x (로컬 개발용, Docker 사용 권장)

### 6.2 IDE 추천 확장
- ESLint
- Prettier
- Prisma (Prisma 사용 시)
- Tailwind CSS IntelliSense (Tailwind 사용 시)

### 6.3 로컬 개발 설정

```bash
# 1. 저장소 클론
git clone [repository-url]
cd [project-name]

# 2. 의존성 설치
pnpm install

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 DATABASE_URL 등 설정

# 4. 데이터베이스 스키마 적용
npx prisma db push

# 5. 초기 데이터 로딩 (선택적)
./scripts/download-data.sh
tsx scripts/migration/process-*.ts

# 6. 개발 서버 실행
pnpm dev
```

---

## 7. Architecture Decision Records (ADRs)

### ADR-001: [주요 기술 선택 1]

**날짜**: [YYYY-MM-DD]

**상태**: 승인됨

**컨텍스트**: [어떤 문제를 해결하려 했는가?]

**결정**: [무엇을 선택했는가]

**이유**:
1. [이유 1]
2. [이유 2]
3. [이유 3]

**고려한 대안**:
- **[대안 1]**: [왜 선택하지 않았는가]
- **[대안 2]**: [왜 선택하지 않았는가]

**결과**: [예상되는 영향, 트레이드오프]

---

### ADR-002: [주요 기술 선택 2]

**날짜**: [YYYY-MM-DD]

**상태**: 승인됨

**컨텍스트**: [...]

**결정**: [...]

**이유**: [...]

**고려한 대안**: [...]

**결과**: [...]

---

### ADR-003: [주요 기술 선택 3]

[동일 형식으로 작성]

---

## 8. 보안 고려사항

- **환경 변수**: `.env` 파일은 절대 Git에 커밋하지 않음 (`.gitignore` 필수)
- **API 인증**: [JWT / API Key / NextAuth / ...] (Phase 3+)
- **입력 검증**: Zod를 사용한 API 입력 검증
- **SQL Injection 방지**: Prisma ORM 사용 (파라미터화된 쿼리)
- **CORS**: API 라우트에 적절한 CORS 헤더 설정
- **Rate Limiting**: [Upstash Rate Limit / ...] (Phase 4+)

---

## 9. 확장성 고려사항

**현재 아키텍처의 확장 한계**:
- [예: Vercel Serverless Functions 10초 타임아웃]
- [예: Free tier database 1GB 제한]

**확장 전략** (필요시):
- [수평 확장: 캐시 레이어 강화]
- [수직 확장: 데이터베이스 플랜 업그레이드]
- [마이그레이션: AWS로 이동 (컨테이너화)]

---

## 승인 및 리뷰

- **작성자**: System Architect Agent
- **리뷰어**: [사용자 이름]
- **승인 날짜**: [YYYY-MM-DD]
- **다음 단계**: Domain Expert Generator에게 전달 → 도메인 전문가 페르소나 생성

---

## 변경 이력

| 날짜 | 변경 사항 | 작성자 |
|------|----------|--------|
| [YYYY-MM-DD] | 초안 작성 | SAA |
| [YYYY-MM-DD] | [변경 내용] | [이름] |
