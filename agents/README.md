# Universal AI Agent Orchestration System

> **아이디어 → 프로덕션급 프로젝트**를 위한 실행 가능한 에이전트 페르소나 시스템

---

## 🎯 개요

이 시스템은 **어떤 도메인의 아이디어든** 입력으로 받아 **프로덕션 배포 가능한 프로젝트**를 생성하는 보편적인 AI 에이전트 오케스트레이션 프레임워크입니다.

**핵심 개념**:
- ✅ **12개의 도메인 독립적 에이전트 페르소나** (Markdown 문서)
- ✅ **6단계 Phase-Gated 워크플로우** (Discovery → Launch)
- ✅ **실행 가능한 페르소나 문서** - API 없이 Claude Code와 대화로 실행
- ✅ **동적 도메인 적응** - Domain Expert를 자동 생성하여 모든 분야 지원
- ✅ **품질 게이트** - 각 Phase마다 검증 및 승인

---

## 🏗️ 시스템 아키텍처

### 12개 에이전트 페르소나

| Phase | 에이전트 | 역할 | 소요 |
|-------|---------|------|------|
| **Phase 0** | Product Discovery Agent (PDA) | 아이디어 → PRD 변환 | 30-45분 |
| | System Architect Agent (SAA) | 기술 스택 선정, 아키텍처 설계 | 45-60분 |
| | Domain Expert Generator (DEA) | 도메인 전문가 페르소나 동적 생성 | 30-45분 |
| **Phase 1** | Data Engineer (DEN) | 데이터 소스 식별, 초기 로딩 | 1-2시간 |
| | Backend Developer (BDA) | DB 스키마, 기본 API 구현 | 1.5-2시간 |
| | DevOps Engineer (DOE) | 빌드 시스템, 환경 구성 | 45-60분 |
| **Phase 2** | Frontend Developer (FDA) | P0 UI 구현 | 2-3시간 |
| | QA Lead (QLA) | 테스트 전략, 기본 테스트 작성 | 1-2시간 |
| **Phase 3** | Algorithm Engineer (AEA) | 도메인 특화 알고리즘 구현 | 2-4시간 |
| **Phase 4** | Frontend Developer (FDA) | SEO, 성능 최적화, i18n | 1.5-2시간 |
| | Security & Compliance (SCA) | 보안 검토, 규정 준수 | 1-2시간 |
| **Phase 5** | Domain Expert (DEA) | 도메인 정확성 검증 | 1-2시간 |
| | QA Lead (QLA) | 최종 품질 검증 | 1-2시간 |
| **Phase 6** | Technical Writer (TWA) | 문서 작성 | 1-2시간 |
| | DevOps Engineer (DOE) | 프로덕션 배포 | 1시간 |
| | Project Manager (PMA) | 최종 검토 및 승인 | 30분 |

**총 예상 기간**: 7-14일 (프로젝트 규모에 따라)

---

### 6단계 Phase 워크플로우

```
Phase 0: Discovery & Planning (10%)
├─ PDA → PRD 작성
├─ SAA → Architecture 설계
└─ DEA Generator → Domain Expert 생성
         ↓
Phase 1: Foundation (15%)
├─ BDA → DB 스키마 + 기본 API
├─ DEN → 데이터 파이프라인
└─ DOE → 빌드 시스템 구성
         ↓
Phase 2: Core Features (25%)
├─ FDA → P0 UI 구현
├─ BDA → P0 API 완성
├─ DEN → 데이터 보강
└─ QLA → 기본 테스트
         ↓
Phase 3: Advanced Features (20%)
├─ AEA → 알고리즘 구현
├─ FDA → P1 UI 구현
└─ DEN → 알고리즘 데이터 준비
         ↓
Phase 4: Integration & Polish (15%)
├─ FDA → SEO, 성능, i18n
├─ SCA → 보안 검토
├─ TWA → API 문서
└─ QLA → E2E 테스트
         ↓
Phase 5: Quality Improvement (10%)
├─ DEA → 도메인 검증
├─ QLA → 최종 테스트
└─ [반복] → 품질 게이트 통과 시 Phase 6
         ↓
Phase 6: Launch Preparation (5%)
├─ TWA → 사용자 문서
├─ DOE → 프로덕션 배포
└─ PMA → 최종 승인
```

---

## 🚀 빠른 시작

### 1. 아이디어 준비

원시 아이디어를 한 문장으로 작성하세요:

```
"한중일 한자를 비교하는 웹사이트를 만들고 싶어"
"AI 기반 음식 추천 앱"
"부동산 검색 플랫폼"
```

### 2. Phase 0 시작

Claude Code에게 다음과 같이 요청하세요:

```
"agent-system/agents/phase-0/01-product-discovery.md를 읽고
Product Discovery Agent로 작동해주세요.

아이디어: [여기에 아이디어 입력]"
```

### 3. 단계별 진행

각 에이전트 페르소나를 순서대로 실행하세요:

```
Phase 0:
1. PDA → docs/specs/prd.md 생성
2. SAA → docs/specs/architecture.md 생성
3. DEA Generator → docs/personas/[domain]-expert.md 생성

Phase 1:
4. BDA → DB 스키마 및 API 구현
5. DEN → 데이터 다운로드 및 로딩
6. DOE → 빌드 시스템 설정

[Phase 2-6 계속...]
```

### 4. 품질 게이트 확인

각 Phase 완료 후 체크리스트를 확인하고 다음 Phase로 진행하세요.

---

## 📁 디렉토리 구조

```
agent-system/
├── README.md                    # 이 파일
├── QUICKSTART.md                # 5분 퀵스타트 가이드
│
├── agents/                      # 에이전트 페르소나 문서
│   ├── phase-0/                # Discovery & Planning
│   │   ├── 01-product-discovery.md
│   │   ├── 02-system-architect.md
│   │   └── 03-domain-expert-generator.md
│   ├── phase-1/                # Foundation
│   │   ├── 04-backend-developer.md
│   │   ├── 05-data-engineer.md
│   │   └── 06-devops-engineer.md
│   ├── phase-2/                # Core Features (TODO)
│   ├── phase-3/                # Advanced Features (TODO)
│   ├── phase-4/                # Integration & Polish (TODO)
│   ├── phase-5/                # Quality Improvement (TODO)
│   └── phase-6/                # Launch Preparation (TODO)
│
├── templates/                   # 출력 파일 템플릿
│   ├── prd.md                  # PRD 템플릿
│   ├── architecture.md         # 아키텍처 문서 템플릿
│   ├── domain-knowledge.md     # 도메인 지식 템플릿
│   └── review-report.md        # 품질 검토 보고서 템플릿
│
└── examples/                    # 실행 예시
    └── trihanzi/               # TriHanzi 프로젝트 케이스 스터디
        ├── input.txt           # 초기 아이디어
        └── execution-log.md    # 실행 과정 기록
```

---

## 🎓 핵심 개념

### 1. 도메인 독립성

이 시스템의 11개 에이전트는 **도메인에 무관**하게 작동합니다. 오직 **Domain Expert만 동적으로 생성**되어 특정 도메인에 적응합니다.

**예시**:
- 한자 비교 프로젝트 → "Dr. Lee Hanja (Comparative Philologist)" 생성
- 음식 추천 프로젝트 → "Chef Kim Nutrition (Nutritionist)" 생성
- 부동산 검색 프로젝트 → "Agent Park Property (Real Estate Expert)" 생성

### 2. 실행 가능한 페르소나 문서

각 페르소나는 **Markdown 파일**로 작성되며, 다음 구조를 따릅니다:

```markdown
# [Agent Name] - Phase [N]

> **역할**: [역할 요약]
> **소요**: [예상 시간]
> **난이도**: ⭐⭐⭐☆☆

## 📥 입력 파일
[이전 단계의 출력 파일]

## 🔨 작업 Step-by-Step
[구체적인 작업 지시사항, 5-10개 Step]

## 📤 출력 파일
[생성할 파일 목록]

## ✅ 완료 체크리스트
[검증 항목]

## 🎬 다음 단계
[다음 실행할 에이전트]
```

**사용 방법**:
1. Claude Code에게 페르소나 파일을 읽도록 요청
2. Claude가 페르소나 지시사항을 따라 작업 수행
3. 출력 파일 생성 및 Git 커밋
4. 다음 에이전트로 진행

### 3. Phase-Gated 진행

각 Phase는 **품질 게이트**를 통과해야 다음으로 진행할 수 있습니다:

| Phase | 품질 게이트 |
|-------|-----------|
| Phase 0 | PRD, 아키텍처, 도메인 지식 문서 완성 |
| Phase 1 | 데이터베이스에 초기 데이터 로드, API 작동 확인 |
| Phase 2 | 모든 P0 기능 UI에서 작동 확인 |
| Phase 3 | P1 기능 작동, 알고리즘 정확도 80% 이상 |
| Phase 4 | Lighthouse 점수 90+ (Performance, SEO, Accessibility) |
| Phase 5 | Domain Expert 검증 85점 이상 (A- 등급) |
| Phase 6 | 프로덕션 배포 성공 |

---

## 💡 실제 사례: TriHanzi

### 프로젝트 개요

**아이디어**: "한중일 한자를 비교하는 웹사이트"

**결과**:
- **기간**: 7일
- **커밋**: 21개
- **데이터**: 10,000자, 40,868개 발음
- **스크립트**: 30개 (데이터 파이프라인)
- **컴포넌트**: 41개 React 컴포넌트
- **API**: 8개 라우트 그룹
- **품질**: A+ (Lighthouse 100점, Domain Expert 95점)

### Phase별 산출물

**Phase 0** (1일):
- PRD: 타겟 페르소나 3개, P0-P3 기능 분류
- Architecture: Next.js 16 + PostgreSQL + Prisma + Vercel
- Domain Expert: "Dr. Lee Hanja - Comparative Philologist"

**Phase 1** (1일):
- DB 스키마: 6개 모델, 15개 인덱스
- 데이터 파이프라인: Unihan, CC-CEDICT, KANJIDIC2
- 초기 데이터: 10,000자 로드

**Phase 2** (2일):
- P0 UI: 검색, 문자 상세, 비교 테이블
- API: `/api/characters`, `/api/search`, `/api/compare`

**Phase 3** (1.5일):
- 알고리즘: 발음 유사도, False Friends 감지
- 발음 유추: 일본어 음독 → 한국어 한자음 (73% 정확도)

**Phase 4** (1일):
- SEO: JSON-LD, OG 이미지, Sitemap
- i18n: 4개 언어 (en, ko, ja, zh)
- Lighthouse: 100/100/100/100

**Phase 5** (0.5일):
- Domain Expert 검증: 95/100점 (A+)
- 데이터 정확도: 97.3%
- 커버리지: 82.1%

**Phase 6** (0.5일):
- 배포: Vercel (프로덕션)
- 문서: README, API 문서, 사용 가이드

---

## 🔧 사용 방법

### 기본 워크플로우

```bash
# 1. Phase 0: Discovery & Planning

"agent-system/agents/phase-0/01-product-discovery.md를 읽고 PDA로 작동해주세요.
아이디어: [여기에 아이디어]"
→ docs/specs/prd.md 생성

"agent-system/agents/phase-0/02-system-architect.md를 읽고 SAA로 작동해주세요."
→ docs/specs/architecture.md, package.json, 프로젝트 구조 생성

"agent-system/agents/phase-0/03-domain-expert-generator.md를 읽고 DEA 생성기로 작동해주세요."
→ docs/personas/[domain]-expert.md 생성

# 2. Phase 1: Foundation

"agent-system/agents/phase-1/04-backend-developer.md를 읽고 BDA로 작동해주세요."
→ prisma/schema.prisma, src/app/api/* 생성

"agent-system/agents/phase-1/05-data-engineer.md를 읽고 DEN으로 작동해주세요."
→ scripts/download-data.sh, scripts/migration/*.ts 생성

"agent-system/agents/phase-1/06-devops-engineer.md를 읽고 DOE로 작동해주세요."
→ next.config.ts, tsconfig.json, eslint, prettier 설정

# 3. Phase 2-6 계속...
```

### 중간 점검 및 리뷰

각 Phase 완료 후:

1. **출력 파일 확인**: 페르소나의 "출력 파일" 섹션에 명시된 파일들이 모두 생성되었는가?
2. **체크리스트 검증**: "완료 체크리스트"의 모든 항목을 확인하세요.
3. **Git 커밋**: 페르소나가 제안하는 커밋 메시지로 커밋하세요.
4. **다음 단계**: 페르소나의 "다음 단계" 섹션을 따라 다음 에이전트를 실행하세요.

---

## 🎯 적용 가능한 프로젝트 유형

이 시스템은 다음과 같은 프로젝트에 적합합니다:

### ✅ 잘 작동하는 경우

- **데이터 중심 앱**: 한자 비교, 음식 추천, 부동산 검색, 도서 카탈로그
- **컨텐츠 플랫폼**: 블로그, 위키, 문서 사이트
- **비교/분석 도구**: 제품 비교, 가격 비교, 성능 벤치마크
- **검색/탐색 앱**: 레시피 검색, 여행 가이드, 학습 자료

### ⚠️ 조정이 필요한 경우

- **실시간 협업 도구**: 추가 에이전트 필요 (WebSocket 전문가)
- **게임**: Algorithm Engineer 강화, Game Designer 추가
- **소셜 네트워크**: Social Graph Expert, Moderation 전문가 추가

### ❌ 적합하지 않은 경우

- **하드웨어 연동 프로젝트**: IoT, 임베디드 시스템
- **운영체제/드라이버**: 시스템 프로그래밍
- **블록체인 DApp**: 완전히 다른 아키텍처 필요

---

## 📊 기대 효과

### 시간 절감

| 단계 | 전통적 방식 | 이 시스템 | 절감 |
|------|-----------|---------|------|
| 요구사항 정의 | 1-2주 | 1-2일 | **85%** |
| 아키텍처 설계 | 3-5일 | 1일 | **75%** |
| 데이터 파이프라인 | 1-2주 | 2-3일 | **70%** |
| 핵심 기능 구현 | 3-4주 | 1-1.5주 | **60%** |
| 품질 검증 | 1-2주 | 2-3일 | **75%** |
| **총 기간** | **8-14주** | **7-14일** | **80-90%** |

### 품질 향상

- ✅ **도메인 정확성**: 전문가 페르소나 검증으로 95% 이상 정확도
- ✅ **코드 품질**: TypeScript strict 모드, ESLint, Prettier 자동 적용
- ✅ **테스트 커버리지**: QA Lead가 체계적 테스트 전략 수립
- ✅ **문서화**: Technical Writer가 모든 문서 작성
- ✅ **보안**: Security & Compliance 에이전트가 검토

---

## 🛠️ 확장 및 커스터마이징

### 새로운 에이전트 추가

프로젝트 특성에 맞는 에이전트를 추가할 수 있습니다:

1. `agents/phase-X/` 디렉토리에 새 Markdown 파일 생성
2. 표준 템플릿 구조 사용:
   - 역할, 소요, 난이도
   - 입력 파일
   - 작업 Step-by-Step
   - 출력 파일
   - 완료 체크리스트
   - 다음 단계

**예시**: Mobile App Developer 추가
```markdown
# Mobile App Developer (MAD) - Phase 2

> **역할**: React Native UI 구현
> **소요**: 2-3시간
> **난이도**: ⭐⭐⭐☆☆

## 📥 입력 파일
- ✅ docs/specs/prd.md
- ✅ docs/specs/architecture.md

## 🔨 작업 Step-by-Step
[React Native 특화 작업...]

## 📤 출력 파일
- src/screens/*.tsx
- src/navigation/*.tsx

[...]
```

### Phase 재정렬

프로젝트에 따라 Phase 순서나 에이전트 조합을 변경할 수 있습니다:

- **빠른 프로토타입**: Phase 0 → Phase 2 (Phase 1 건너뛰기, 목업 데이터 사용)
- **데이터 우선**: Phase 0 → Phase 1 완전 완료 → Phase 2
- **디자인 우선**: Phase 0 → Designer 추가 → Phase 2

---

## 📚 추가 자료

### 템플릿

- [PRD 템플릿](templates/prd.md)
- [Architecture 템플릿](templates/architecture.md)
- [Domain Knowledge 템플릿](templates/domain-knowledge.md)
- [Review Report 템플릿](templates/review-report.md)

### 케이스 스터디

- [TriHanzi 실행 로그](examples/trihanzi/execution-log.md) (TODO)

### 이론 배경

이 시스템의 설계 원칙:

1. **Domain-Driven Design (DDD)**: 도메인 전문가를 중심으로 설계
2. **Phase-Gate Process**: 각 단계마다 품질 검증
3. **Separation of Concerns**: 각 에이전트는 단일 책임
4. **Executable Documentation**: 문서가 곧 실행 가능한 스크립트
5. **Evidence-Based Design**: TriHanzi 프로젝트 실증 데이터 기반

---

## 🤝 기여

이 시스템은 **오픈 컨셉**입니다. 다음 방식으로 개선할 수 있습니다:

1. **새로운 도메인 예시 추가**: `examples/[domain]/` 디렉토리에 실행 로그 기여
2. **에이전트 개선**: 기존 페르소나의 작업 지시사항 보완
3. **Phase 2-6 페르소나 완성**: 현재 Phase 0-1만 구현됨

---

## ⚖️ 라이선스

이 시스템은 **MIT 라이선스**로 배포됩니다. 자유롭게 사용, 수정, 배포하세요.

---

## 📞 문의

- **이슈**: GitHub Issues에 질문이나 버그 리포트 남기기
- **개선 제안**: Pull Request 환영

---

**Happy Building! 🚀**

이 시스템으로 여러분의 아이디어를 7일 안에 프로덕션 수준의 프로젝트로 만들어보세요.
