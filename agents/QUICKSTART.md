# 5분 퀵스타트 가이드

> 아이디어를 입력하고 5분 안에 첫 번째 문서(PRD)를 생성하세요!

---

## ⚡ 즉시 시작

### 1. 아이디어 준비 (1분)

한 문장으로 아이디어를 작성하세요:

```
"한중일 한자를 비교하는 웹사이트를 만들고 싶어"
```

또는:

```
"AI 기반 음식 추천 앱"
"부동산 검색 플랫폼"
"운동 루틴 추천 서비스"
```

---

### 2. Product Discovery Agent 실행 (3분)

Claude Code에게 다음과 같이 요청:

```
agent-system/agents/phase-0/01-product-discovery.md를 읽고
Product Discovery Agent로 작동해주세요.

아이디어: [여기에 아이디어 입력]
```

**예시**:
```
agent-system/agents/phase-0/01-product-discovery.md를 읽고
Product Discovery Agent로 작동해주세요.

아이디어: 한중일 한자를 비교하는 웹사이트를 만들고 싶어
```

---

### 3. 결과 확인 (1분)

다음 파일이 생성됩니다:

```
docs/specs/prd.md
```

**내용**:
- ✅ 타겟 사용자 페르소나 3-5개
- ✅ 기능 우선순위 (P0/P1/P2/P3)
- ✅ 성공 지표
- ✅ 범위 경계
- ✅ Phase 마일스톤

---

## 🎯 다음 단계

PRD가 만족스럽다면, Phase 0를 계속 진행하세요:

### Step 2: System Architect (아키텍처 설계)

```
agent-system/agents/phase-0/02-system-architect.md를 읽고
System Architect Agent로 작동해주세요.
```

**생성 파일**:
- `docs/specs/architecture.md` - 기술 스택 및 아키텍처
- `package.json` - 의존성 목록
- 프로젝트 디렉토리 구조

---

### Step 3: Domain Expert Generator (도메인 전문가 생성)

```
agent-system/agents/phase-0/03-domain-expert-generator.md를 읽고
Domain Expert Generator로 작동해주세요.
```

**생성 파일**:
- `docs/personas/[domain]-expert.md` - 도메인 지식 백과사전

---

## 🚀 Phase 0 완료 후

Phase 1 (Foundation)으로 진행:

```
agent-system/agents/phase-1/04-data-engineer.md를 읽고
Data Engineer로 작동해주세요.
```

그 다음:
- Backend Developer → DB 스키마 및 API
- DevOps Engineer → 빌드 시스템

---

## 📋 전체 워크플로우 요약

```
Phase 0 (1-2일)
├─ Product Discovery → docs/specs/prd.md
├─ System Architect → docs/specs/architecture.md + package.json
└─ Domain Expert → docs/personas/[domain]-expert.md
         ↓
Phase 1 (1-2일)
├─ Data Engineer → 데이터 다운로드 및 로딩
├─ Backend Developer → DB + API
└─ DevOps → 빌드 시스템
         ↓
Phase 2 (2-3일)
└─ Frontend Developer → P0 UI 구현
         ↓
Phase 3 (1-2일)
└─ Algorithm Engineer → 도메인 특화 알고리즘
         ↓
Phase 4 (1일)
└─ Frontend Developer → SEO, 성능, i18n
         ↓
Phase 5 (1일)
└─ Domain Expert → 품질 검증
         ↓
Phase 6 (0.5일)
└─ DevOps → 프로덕션 배포
```

**총 기간**: 7-14일

---

## 💡 팁

### 1. 한 번에 하나씩

각 에이전트를 순차적으로 실행하세요. 병렬로 실행하지 마세요.

### 2. 출력 파일 확인

각 에이전트가 완료되면 "출력 파일" 섹션에 명시된 파일들이 생성되었는지 확인하세요.

### 3. 체크리스트 검증

각 에이전트의 "완료 체크리스트"를 확인하고 모든 항목을 체크하세요.

### 4. Git 커밋

각 에이전트 완료 후 제안된 커밋 메시지로 커밋하세요:

```bash
git add docs/specs/prd.md
git commit -m "feat: Product Requirements Document (Phase 0)"
```

---

## 🎓 더 알아보기

- [전체 문서](README.md) - 시스템 전체 개요 및 이론
- [템플릿 디렉토리](templates/) - PRD, Architecture 등 템플릿
- [TriHanzi 케이스 스터디](examples/trihanzi/) - 실제 실행 예시

---

## ❓ FAQ

### Q: API가 필요한가요?

**A**: 아니요! 이 시스템은 Markdown 페르소나 문서만으로 작동합니다. Claude Code와 대화하며 각 단계를 실행하면 됩니다.

---

### Q: 모든 Phase를 다 거쳐야 하나요?

**A**: 프로토타입만 원한다면 Phase 0-2만 실행해도 됩니다. 프로덕션 배포가 목표라면 Phase 6까지 진행하세요.

---

### Q: 내 도메인에 맞는 에이전트가 없다면?

**A**: Domain Expert Generator가 자동으로 도메인 전문가를 생성합니다. 한자, 음식, 부동산 등 어떤 도메인이든 작동합니다.

---

### Q: Phase 중간에 막히면?

**A**: 해당 Phase의 에이전트 페르소나 파일을 다시 읽어보세요. "작업 Step-by-Step" 섹션에 구체적인 지시사항이 있습니다.

---

## 🚀 지금 시작하세요!

```
agent-system/agents/phase-0/01-product-discovery.md를 읽고
Product Discovery Agent로 작동해주세요.

아이디어: [여기에 아이디어]
```

**행운을 빕니다! 🎉**
