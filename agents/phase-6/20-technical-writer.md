# Technical Writer Agent (TWA) - Phase 6

> **역할**: README 완성, 문서 최종 검토 및 통합
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐☆☆

## 📥 입력 파일

- ✅ **필수**: 모든 코드베이스
- ✅ **필수**: 모든 기존 문서 (`docs/`, `README.md`, `scripts/README.md`)
- ✅ **필수**: Phase 5 최종 보고서

---

## 🔨 작업 Step-by-Step

### Step 1: README.md 최종 업데이트 (30-45분)

```markdown
# TriHanzi - CJK Character Comparison Platform

한중일 한자를 비교하고 학습하는 인터랙티브 웹 플랫폼

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black)](https://trihanzi.com)

---

## 🌟 주요 기능

- 🔍 **한자 검색** - 10,000+ 한자 데이터베이스에서 실시간 검색
- 🌐 **3개국 비교** - 한국, 일본, 중국의 한자 비교
- 🎓 **교육 레벨** - HSK (중국), JLPT (일본) 레벨 표시
- ⚠️ **False Friends** - 형태는 유사하나 의미가 다른 662개 한자 쌍
- 🎨 **다크 모드** - 눈의 피로를 줄이는 다크 모드 지원
- 🌏 **4개 언어** - 한국어, 영어, 일본어, 중국어 지원

---

## 📊 프로젝트 통계

| 메트릭 | 값 |
|--------|-----|
| 총 한자 | 10,000자 |
| 발음 데이터 | 40,868개 |
| 의미 데이터 | 26,832개 |
| False Friends | 662쌍 |
| 코드베이스 | 15,234 줄 |
| 컴포넌트 | 41개 |
| API 엔드포인트 | 8개 |
| 지원 언어 | 4개 |

---

## 🚀 빠른 시작

### 필수 요구사항

- Node.js >= 18
- pnpm >= 8
- PostgreSQL >= 14
- Redis (선택, 캐싱용)

### 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/trihanzi.git
cd trihanzi

# 2. 의존성 설치
pnpm install

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 URL 등 설정

# 4. 데이터베이스 마이그레이션
npx prisma migrate dev

# 5. 데이터 시드 (선택)
pnpm run seed

# 6. 개발 서버 시작
pnpm dev
```

브라우저에서 http://localhost:3000 접속

---

## 📦 기술 스택

### Frontend
- **Next.js 16** (App Router) - React 프레임워크
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 유틸리티 우선 CSS
- **next-intl** - 국제화 (i18n)

### Backend
- **Next.js API Routes** - 서버리스 API
- **Prisma** - ORM
- **PostgreSQL** - 관계형 데이터베이스
- **Upstash Redis** - 캐싱 (선택)

### DevOps
- **Vercel** - 호스팅 및 배포
- **GitHub Actions** - CI/CD
- **Playwright** - E2E 테스트
- **Vitest** - 단위 테스트

---

## 📁 프로젝트 구조

```
trihanzi/
├── src/
│   ├── app/
│   │   ├── [locale]/          # 로케일별 페이지
│   │   │   ├── page.tsx        # 홈페이지
│   │   │   ├── search/         # 검색 페이지
│   │   │   ├── compare/        # 비교 페이지
│   │   │   └── characters/[id]/ # 문자 상세
│   │   └── api/                # API 라우트
│   │       ├── characters/
│   │       ├── search/
│   │       └── compare/
│   ├── components/             # React 컴포넌트
│   │   ├── ui/                 # UI 프리미티브
│   │   ├── character/          # 문자 관련
│   │   ├── search/             # 검색 관련
│   │   └── compare/            # 비교 관련
│   ├── lib/
│   │   ├── algorithms/         # 도메인 알고리즘
│   │   ├── services/           # 비즈니스 로직
│   │   ├── db/                 # 데이터베이스 클라이언트
│   │   └── cache/              # 캐시 유틸리티
│   ├── i18n/
│   │   └── locales/            # 번역 파일
│   └── constants/              # 상수 및 설정
├── prisma/
│   ├── schema.prisma           # 데이터베이스 스키마
│   └── migrations/             # 마이그레이션
├── scripts/
│   ├── migration/              # 데이터 마이그레이션
│   ├── enrichment/             # 데이터 보강
│   ├── pronunciation/          # 발음 처리
│   └── reporting/              # 통계 및 보고
├── test/
│   ├── e2e/                    # E2E 테스트
│   └── integration/            # 통합 테스트
└── docs/
    ├── api/                    # API 문서
    ├── design/                 # 디자인 시스템
    ├── reports/                # 품질 보고서
    └── personas/               # 도메인 전문가

```

---

## 🗄️ 데이터 소스

| 소스 | 설명 | 항목 수 | 라이선스 |
|------|------|---------|---------|
| **Unihan Database** | Unicode 한자 데이터베이스 | 10,000자 | Public Domain |
| **CC-CEDICT** | 중국어-영어 사전 | 124,259 항목 | CC BY-SA 4.0 |
| **KANJIDIC2** | 일본 한자 사전 | 13,108자 | CC BY-SA 3.0 |
| **한국어문회** | 한국 한자 데이터 | 8,000자 | Open Data |

---

## 🧪 테스팅

```bash
# 단위 테스트
pnpm test

# E2E 테스트
pnpm test:e2e

# 테스트 커버리지
pnpm test:coverage

# Lighthouse 감사
pnpm lighthouse
```

---

## 🌐 배포

### Vercel (권장)

1. GitHub 저장소 연결
2. 환경 변수 설정
3. 자동 배포

### 수동 배포

```bash
# 프로덕션 빌드
pnpm build

# 프로덕션 서버 시작
pnpm start
```

---

## 📖 문서

- [API 문서](docs/api/README.md)
- [디자인 시스템](docs/design/README.md)
- [스크립트 가이드](scripts/README.md)
- [도메인 전문가 페르소나](docs/personas/hanzi-expert.md)

---

## 🛣️ 로드맵

### ✅ Phase 0-2 (완료)
- [x] 기본 아키텍처 수립
- [x] 데이터베이스 설계 및 구축
- [x] P0 기능 구현 (검색, 상세, 기본 UI)

### ✅ Phase 3 (완료)
- [x] 도메인 특화 알고리즘 (발음 유추, False Friends)
- [x] 디자인 시스템 구축
- [x] P1 기능 구현 (비교, 컬렉션)

### ✅ Phase 4 (완료)
- [x] SEO 최적화 (Lighthouse 100점)
- [x] 성능 최적화
- [x] 보안 강화 (rate limiting, 헤더)

### ✅ Phase 5 (완료)
- [x] 도메인 전문가 리뷰 (A 등급 달성)
- [x] 데이터 품질 개선
- [x] 최종 QA

### ✅ Phase 6 (현재)
- [x] 문서 완성
- [ ] 프로덕션 배포
- [ ] 모니터링 설정

### 🚧 향후 계획 (Phase 7+)
- [ ] 발음 오디오 추가
- [ ] 사용자 계정 및 학습 진도 추적
- [ ] 플래시카드 생성 기능
- [ ] 모바일 앱 (React Native)

---

## 🤝 기여

기여를 환영합니다! [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

---

## 📄 라이선스

- **코드**: MIT License
- **데이터**: 각 출처의 라이선스 참조 (위 "데이터 소스" 섹션)

---

## 📞 연락처

- **이메일**: contact@trihanzi.com
- **이슈**: [GitHub Issues](https://github.com/yourusername/trihanzi/issues)

---

**만든 이** ❤️ with [Claude Code](https://claude.com/claude-code)

Last updated: 2026-02-16
```

**체크리스트**:
- [ ] 프로젝트 개요 업데이트
- [ ] 통계 메트릭 최신화
- [ ] 빠른 시작 가이드 검증
- [ ] 프로젝트 구조 정확성 확인
- [ ] 데이터 소스 및 라이선스 명시
- [ ] 로드맵 업데이트 (완료/진행/계획)
- [ ] 모든 링크 작동 확인

---

### Step 2: 문서 일관성 검토 (30분)

**2.1 문서 목록 확인**

```bash
# 모든 문서 파일 나열
find docs -name "*.md" | sort
```

**2.2 링크 검증**

```bash
# Markdown 링크 체크
npm install -g markdown-link-check
find . -name "*.md" -exec markdown-link-check {} \;
```

**2.3 일관성 체크리스트**

```markdown
## 문서 일관성 체크리스트

### 용어 일관성
- [ ] "한자" vs "漢字" - 일관되게 사용
- [ ] "False Friends" vs "거짓 친구" - 영문 문서는 False Friends
- [ ] API 엔드포인트 표기 (/api/characters vs /api/character)

### 메트릭 일관성
- [ ] README.md 통계
- [ ] 각 문서의 통계
- [ ] 코드 주석의 통계

### 날짜 일관성
- [ ] 최종 업데이트 날짜 동일
- [ ] 리뷰 날짜 정확

### 링크 일관성
- [ ] 모든 내부 링크 작동
- [ ] 모든 외부 링크 작동
- [ ] 상대 경로 vs 절대 경로 일관성
```

**체크리스트**:
- [ ] 모든 문서 링크 작동 확인
- [ ] 용어 일관성 검토
- [ ] 메트릭 일관성 검토
- [ ] 날짜 업데이트

---

### Step 3: CONTRIBUTING.md 생성 (20분)

```markdown
# 기여 가이드

TriHanzi에 기여해주셔서 감사합니다! 🙏

---

## 기여 방법

### 1. 이슈 생성

버그 리포트나 기능 제안은 [GitHub Issues](https://github.com/yourusername/trihanzi/issues)에서 생성하세요.

**버그 리포트 템플릿**:
- 예상 동작
- 실제 동작
- 재현 단계
- 스크린샷 (선택)

**기능 제안 템플릿**:
- 문제 설명
- 제안하는 해결책
- 대안
- 추가 컨텍스트

### 2. Pull Request

1. 저장소 포크
2. 새 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

---

## 코드 스타일

- **TypeScript**: ESLint 규칙 준수
- **Formatting**: Prettier 사용
- **커밋 메시지**: [Conventional Commits](https://www.conventionalcommits.org/)

### 커밋 메시지 형식

```
<type>: <subject>

<body> (optional)
```

**타입**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅
- `refactor`: 리팩토링
- `test`: 테스트 추가
- `chore`: 빌드, 의존성 업데이트

**예시**:
```
feat: 발음 오디오 재생 기능 추가

사용자가 발음 버튼을 클릭하면 해당 한자의 발음을 오디오로 재생합니다.
```

---

## 테스트

Pull Request를 제출하기 전에 모든 테스트가 통과하는지 확인하세요:

```bash
# 단위 테스트
pnpm test

# E2E 테스트
pnpm test:e2e

# Lint
pnpm lint
```

---

## 데이터 기여

데이터 수정이나 추가는 다음 가이드라인을 따르세요:

1. **출처 명시**: 모든 데이터는 신뢰할 수 있는 출처에서
2. **라이선스 확인**: 데이터 라이선스가 프로젝트와 호환되는지 확인
3. **검증**: 도메인 전문가 리뷰 필요

---

## 질문?

궁금한 점이 있으면 [GitHub Discussions](https://github.com/yourusername/trihanzi/discussions)에 질문하세요.
```

**체크리스트**:
- [ ] CONTRIBUTING.md 생성
- [ ] 기여 방법 명확히 설명
- [ ] 코드 스타일 가이드 제공
- [ ] 테스트 가이드라인 포함

---

### Step 4: LICENSE 파일 생성 (5분)

```
MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### Step 5: 문서 최종 검토 (15분)

```markdown
# 문서 최종 검토 체크리스트

## 필수 문서
- [x] README.md (완성, 최신 정보)
- [x] CONTRIBUTING.md (생성)
- [x] LICENSE (생성)
- [x] .env.example (실제 값 제거)
- [x] docs/api/README.md (API 개요)
- [x] docs/design/README.md (디자인 시스템)
- [x] scripts/README.md (스크립트 가이드)

## 품질 체크
- [x] 모든 링크 작동
- [x] 메트릭 일관성
- [x] 용어 일관성
- [x] 날짜 최신화
- [x] 코드 예시 정확
- [x] 오타 및 문법 검토

## 접근성
- [x] 명확한 구조
- [x] 적절한 제목 계층
- [x] 코드 블록 언어 명시
- [x] 이미지 alt 텍스트 (해당 시)

✅ **문서 최종 검토 완료**
```

---

## 📤 출력 파일

1. **루트 문서**:
   - `README.md` (업데이트)
   - `CONTRIBUTING.md` (생성)
   - `LICENSE` (생성)

2. **문서 검증**:
   - `docs/reports/documentation-review.md`

---

## ✅ 완료 체크리스트

- [ ] README.md 최종 업데이트
- [ ] 모든 통계 메트릭 최신화
- [ ] CONTRIBUTING.md 생성
- [ ] LICENSE 파일 생성
- [ ] 문서 일관성 검토 완료
- [ ] 모든 링크 작동 확인
- [ ] 오타 및 문법 검토
- [ ] Git 커밋:
  ```bash
  git add README.md CONTRIBUTING.md LICENSE docs/
  git commit -m "docs: 문서 최종 완성 (Phase 6)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-6/21-devops-engineer.md를 읽고 DOE로 작동해주세요"
```

---

## 💡 TriHanzi 실제 문서

**문서 구조**:
```
trihanzi/
├── README.md (238줄)
├── CONTRIBUTING.md (생성)
├── LICENSE (MIT)
├── docs/
│   ├── api/
│   │   ├── README.md (API 개요)
│   │   └── endpoints/ (8개 파일)
│   ├── design/
│   │   ├── README.md
│   │   ├── styles.md
│   │   └── components.md
│   ├── reports/
│   │   ├── PROJECT-REPORT.md
│   │   ├── domain-expert-review.md
│   │   └── tech-lead-review.md
│   └── personas/
│       └── hanzi-expert.md (412줄)
└── scripts/
    └── README.md (333줄)
```

**메트릭 (README.md)**:
- 총 한자: 10,000자
- 발음: 40,868개
- 의미: 26,832개
- False Friends: 662쌍
- 코드: 15,234줄
- 컴포넌트: 41개
- API: 8개
- 언어: 4개
