# DevOps Engineer Agent (DOE) - Phase 6

> **역할**: 프로덕션 배포 및 모니터링 설정
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: 빌드된 애플리케이션
- ✅ **필수**: 환경 변수 (`.env`)
- ✅ **필수**: 인프라 요구사항

---

## 🔨 작업 Step-by-Step

### Step 1: 프로덕션 빌드 검증 (15분)

```bash
# 1. 의존성 정리
pnpm install --frozen-lockfile

# 2. TypeScript 타입 체크
pnpm tsc --noEmit

# 3. Lint 체크
pnpm lint

# 4. 테스트 실행
pnpm test

# 5. 프로덕션 빌드
pnpm build
```

**빌드 체크리스트**:

```markdown
## 프로덕션 빌드 체크리스트

- [x] TypeScript 컴파일 에러 없음
- [x] ESLint 에러 없음
- [x] 모든 테스트 통과
- [x] 빌드 성공
- [x] 빌드 산출물 크기 확인 (< 5MB)
- [x] 환경 변수 검증 완료
- [x] 데이터베이스 마이그레이션 최신

✅ **빌드 검증 완료**
```

**체크리스트**:
- [ ] TypeScript 에러 없음
- [ ] ESLint 에러 없음
- [ ] 모든 테스트 통과
- [ ] 빌드 성공

---

### Step 2: 환경 변수 설정 (20분)

**Vercel 환경 변수 설정**:

```bash
# Vercel CLI 설치
npm install -g vercel

# 로그인
vercel login

# 프로젝트 연결
vercel link

# 환경 변수 설정
vercel env add DATABASE_URL production
vercel env add UPSTASH_REDIS_REST_URL production
vercel env add UPSTASH_REDIS_REST_TOKEN production
vercel env add NEXT_PUBLIC_APP_URL production
```

**환경 변수 검증**:

```typescript
// scripts/verify-env.ts

const requiredEnvVars = [
  'DATABASE_URL',
  'NEXT_PUBLIC_APP_URL',
];

const optionalEnvVars = [
  'UPSTASH_REDIS_REST_URL',
  'UPSTASH_REDIS_REST_TOKEN',
];

console.log('🔍 환경 변수 검증');
console.log('='.repeat(50));

let allRequired = true;

requiredEnvVars.forEach((envVar) => {
  if (process.env[envVar]) {
    console.log(`✅ ${envVar}`);
  } else {
    console.log(`❌ ${envVar} - 누락`);
    allRequired = false;
  }
});

optionalEnvVars.forEach((envVar) => {
  if (process.env[envVar]) {
    console.log(`✅ ${envVar} (선택)`);
  } else {
    console.log(`⚠️  ${envVar} (선택) - 누락`);
  }
});

if (!allRequired) {
  console.log('\n❌ 필수 환경 변수 누락');
  process.exit(1);
}

console.log('\n✅ 모든 필수 환경 변수 설정됨');
```

**체크리스트**:
- [ ] 모든 필수 환경 변수 설정
- [ ] 환경 변수 검증 스크립트 실행
- [ ] 시크릿 값이 .env.example에 없음 확인

---

### Step 3: 데이터베이스 마이그레이션 (15분)

```bash
# 프로덕션 데이터베이스에 마이그레이션 실행
DATABASE_URL="postgresql://..." npx prisma migrate deploy

# 마이그레이션 상태 확인
DATABASE_URL="postgresql://..." npx prisma migrate status
```

**마이그레이션 체크리스트**:

```markdown
## 데이터베이스 마이그레이션

- [x] 프로덕션 데이터베이스 백업
- [x] 마이그레이션 파일 검토
- [x] 마이그레이션 실행
- [x] 마이그레이션 상태 확인
- [x] 데이터 무결성 검증

✅ **마이그레이션 완료**
```

**체크리스트**:
- [ ] 프로덕션 DB 백업 (중요!)
- [ ] 마이그레이션 실행 성공
- [ ] 마이그레이션 상태 "Applied"

---

### Step 4: Vercel 배포 (20분)

```bash
# 프로덕션 배포
vercel --prod

# 배포 상태 확인
vercel inspect <deployment-url>
```

**배포 후 스모크 테스트**:

```bash
# 홈페이지
curl -I https://trihanzi.com

# API 엔드포인트
curl https://trihanzi.com/api/characters?page=1&limit=5

# Sitemap
curl https://trihanzi.com/sitemap.xml

# Robots.txt
curl https://trihanzi.com/robots.txt
```

**배포 체크리스트**:

```markdown
## 배포 검증

### 기본 확인
- [x] 배포 성공
- [x] 배포 URL 접근 가능
- [x] HTTPS 작동

### 페이지 확인
- [x] 홈페이지 (/)
- [x] 검색 (/search)
- [x] 비교 (/compare)
- [x] 문자 상세 (/characters/[id])
- [x] About (/about)

### API 확인
- [x] /api/characters
- [x] /api/search
- [x] /api/compare

### SEO 확인
- [x] sitemap.xml
- [x] robots.txt
- [x] OpenGraph 메타데이터

### 다국어 확인
- [x] /en
- [x] /ko
- [x] /ja
- [x] /zh

✅ **배포 검증 완료**
```

**체크리스트**:
- [ ] 배포 성공
- [ ] 모든 주요 페이지 접근 가능
- [ ] API 작동 확인
- [ ] SEO 파일 접근 가능

---

### Step 5: 모니터링 설정 (30-45분)

**5.1 Vercel Analytics 활성화**

1. Vercel 대시보드 → Analytics 탭
2. Enable Analytics
3. Real User Metrics 확인

**5.2 에러 모니터링 (Sentry)**

```bash
# Sentry 설치
npm install @sentry/nextjs
npx @sentry/wizard -i nextjs
```

**sentry.client.config.ts**:

```typescript
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
  enabled: process.env.NODE_ENV === 'production',
});
```

**sentry.server.config.ts**:

```typescript
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
  enabled: process.env.NODE_ENV === 'production',
});
```

**5.3 업타임 모니터링**

```bash
# Uptime Robot 또는 Vercel Monitoring 사용
# 모니터링 URL 설정:
# - https://trihanzi.com
# - https://trihanzi.com/api/characters
```

**5.4 알림 설정**

- **Vercel**: 배포 실패 시 이메일 알림
- **Sentry**: 에러 발생 시 Slack/이메일 알림
- **Uptime Robot**: 다운타임 시 SMS/이메일 알림

**체크리스트**:
- [ ] Vercel Analytics 활성화
- [ ] Sentry 설정 (선택)
- [ ] 업타임 모니터링 설정
- [ ] 알림 채널 설정

---

### Step 6: 성능 모니터링 (15분)

**Lighthouse CI 설정** (GitHub Actions):

```yaml
# .github/workflows/lighthouse.yml

name: Lighthouse CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm install -g @lhci/cli

      - name: Run Lighthouse
        run: lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

**체크리스트**:
- [ ] Lighthouse CI 설정
- [ ] GitHub Actions 워크플로우 추가
- [ ] 성능 임계값 설정

---

### Step 7: 배포 문서화 (10분)

```markdown
# 배포 가이드

## 프로덕션 배포

### 사전 요구사항

- Vercel 계정
- 프로덕션 데이터베이스 (Neon/Supabase/PlanetScale)
- Redis 인스턴스 (Upstash) - 선택

### 배포 단계

1. **환경 변수 설정**
   ```bash
   vercel env add DATABASE_URL production
   vercel env add UPSTASH_REDIS_REST_URL production
   vercel env add UPSTASH_REDIS_REST_TOKEN production
   vercel env add NEXT_PUBLIC_APP_URL production
   ```

2. **데이터베이스 마이그레이션**
   ```bash
   DATABASE_URL="postgresql://..." npx prisma migrate deploy
   ```

3. **배포**
   ```bash
   vercel --prod
   ```

4. **검증**
   - 홈페이지 접근: https://trihanzi.com
   - API 테스트: https://trihanzi.com/api/characters
   - Lighthouse 점수 확인

---

## 롤백

배포 후 문제가 발생한 경우:

```bash
# 이전 배포로 롤백
vercel rollback <deployment-url>
```

---

## 모니터링

- **Vercel Analytics**: https://vercel.com/dashboard/analytics
- **Sentry**: https://sentry.io/organizations/[org]/issues/
- **Uptime**: Uptime Robot 대시보드

---

## 긴급 연락처

- DevOps: devops@trihanzi.com
- 온콜: +82-10-XXXX-XXXX
```

---

## 📤 출력 파일

1. **배포 스크립트**:
   - `scripts/verify-env.ts`
   - `scripts/deploy.sh`

2. **모니터링**:
   - `sentry.client.config.ts`
   - `sentry.server.config.ts`

3. **CI/CD**:
   - `.github/workflows/lighthouse.yml`

4. **문서**:
   - `docs/deployment.md`

---

## ✅ 완료 체크리스트

- [ ] 프로덕션 빌드 검증
- [ ] 환경 변수 설정 완료
- [ ] 데이터베이스 마이그레이션 완료
- [ ] Vercel 배포 성공
- [ ] 스모크 테스트 통과
- [ ] Vercel Analytics 활성화
- [ ] 에러 모니터링 설정 (Sentry)
- [ ] 업타임 모니터링 설정
- [ ] 알림 채널 설정
- [ ] Lighthouse CI 설정
- [ ] 배포 문서 작성
- [ ] Git 커밋:
  ```bash
  git add .github/ docs/deployment.md scripts/
  git commit -m "chore: 프로덕션 배포 및 모니터링 설정 (Phase 6)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-6/22-project-manager.md를 읽고 PMA로 작동해주세요"
```

---

## 💡 TriHanzi 실제 배포

**인프라**:
- **호스팅**: Vercel (Serverless)
- **데이터베이스**: Neon PostgreSQL (Serverless)
- **캐시**: Upstash Redis (Serverless)
- **CDN**: Vercel Edge Network

**배포 통계**:
- 빌드 시간: 2분 34초
- 번들 크기: 152KB (초기 로드)
- Edge Functions: 8개 (API 라우트)

**모니터링**:
- **Vercel Analytics**: 활성화
- **실시간 로그**: Vercel 대시보드
- **업타임**: 99.9%

**성능** (프로덕션):
- TTFB: 187ms
- FCP: 1.2s
- LCP: 1.8s
- CLS: 0.02

**배포 URL**: https://trihanzi.com
