# Domain Expert Review Agent (DEA) - Phase 5

> **역할**: 도메인 전문가 관점에서 프로젝트 전체 검증
> **소요**: 2-3시간
> **난이도**: ⭐⭐⭐⭐⭐

## 📥 입력 파일

- ✅ **필수**: `docs/personas/[domain]-expert.md` (자신의 페르소나 문서)
- ✅ **필수**: 프로젝트 전체 (코드, 데이터, 문서)
- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: Phase 3 알고리즘 벤치마크 보고서

---

## 🔨 작업 Step-by-Step

### Step 1: 리뷰 루브릭 정의 (20min)

도메인별 평가 기준을 정의하세요. 총점 100점 기준:

```markdown
# 도메인 전문가 리뷰 루브릭

## 카테고리 및 배점

### 1. 데이터 정확성 (30점)
- **핵심 데이터 정확성** (15점): 도메인 핵심 데이터가 정확한가?
- **데이터 커버리지** (10점): 충분한 범위의 데이터가 있는가?
- **데이터 출처 신뢰성** (5점): 신뢰할 수 있는 소스에서 데이터를 가져왔는가?

### 2. 알고리즘 품질 (25점)
- **알고리즘 정확도** (15점): 알고리즘이 도메인 기대치를 충족하는가?
- **엣지 케이스 처리** (5점): 특수한 경우를 올바르게 처리하는가?
- **투명성** (5점): 알고리즘 결과가 설명 가능한가?

### 3. 도메인 적합성 (20점)
- **용어 정확성** (10점): 도메인 전문 용어가 정확한가?
- **분류 체계** (5점): 도메인의 분류 체계를 따르는가?
- **컨텍스트 이해** (5점): 도메인 특유의 컨텍스트를 반영하는가?

### 4. 사용성 (15점)
- **사용자 플로우** (8점): 도메인 전문가/학습자가 쉽게 사용할 수 있는가?
- **정보 표시** (7점): 중요한 도메인 정보가 명확하게 표시되는가?

### 5. 문서화 (10점)
- **도메인 지식 문서** (5점): 도메인 배경이 잘 설명되어 있는가?
- **데이터 출처 귀속** (5점): 모든 데이터 출처가 명시되어 있는가?

## 점수 해석

- **95-100 (A+)**: 탁월함. 도메인 전문가도 즐겨 사용할 수준
- **90-94 (A)**: 우수함. 프로덕션 품질
- **85-89 (A-)**: 양호함. 경미한 개선 필요
- **80-84 (B+)**: 보통. 중요한 개선 필요
- **70-79 (B)**: 미흡. 주요 이슈 해결 필요
- **< 70 (C 이하)**: 불충분. 재작업 필요
```

**체크리스트**:
- [ ] 5개 카테고리별 세부 기준 정의
- [ ] 각 기준에 점수 배정
- [ ] 점수 해석 기준 명시

---

### Step 2: 데이터 샘플링 및 검증 (45-60분)

**계층화 샘플링**:

```typescript
// scripts/reporting/domain-data-sampling.ts

import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';

const prisma = new PrismaClient();

async function stratifiedSampling() {
  console.log('📊 계층화 샘플링');

  // 카테고리별로 샘플 추출
  const samples = {
    // 고빈도 데이터
    highFrequency: await prisma.[resource].findMany({
      where: {
        // 도메인별 고빈도 기준 (예: level 1, category A)
        OR: [
          { level: 1 },
          { category: 'primary' },
        ],
      },
      take: 50,
      include: {
        details: true,
        metadata: true,
      },
    }),

    // 중간 빈도
    mediumFrequency: await prisma.[resource].findMany({
      where: {
        OR: [
          { level: { gte: 2, lte: 4 } },
          { category: 'secondary' },
        ],
      },
      take: 30,
      include: {
        details: true,
        metadata: true,
      },
    }),

    // 저빈도 (희귀)
    lowFrequency: await prisma.[resource].findMany({
      where: {
        OR: [
          { level: { gte: 5 } },
          { category: 'rare' },
        ],
      },
      take: 20,
      include: {
        details: true,
        metadata: true,
      },
    }),

    // 엣지 케이스 (변형, 특수 케이스)
    edgeCases: await prisma.[resource].findMany({
      where: {
        OR: [
          { variants: { some: {} } },
          { details: { none: {} } }, // 상세 정보 누락
          { metadata: { none: {} } }, // 메타데이터 누락
        ],
      },
      take: 20,
      include: {
        details: true,
        metadata: true,
        variants: true,
      },
    }),
  };

  // CSV로 저장
  const allSamples = [
    ...samples.highFrequency,
    ...samples.mediumFrequency,
    ...samples.lowFrequency,
    ...samples.edgeCases,
  ];

  const csv = [
    ['ID', 'Name', 'Details', 'Metadata', 'Category', 'Notes'].join(','),
    ...allSamples.map((s) => [
      s.id,
      s.name,
      s.details.map(d => d.text).join(';'),
      s.metadata.map(m => m.value).join(';'),
      '', // Category (수동 입력)
      '', // Notes (수동 입력)
    ].join(',')),
  ].join('\n');

  fs.writeFileSync('docs/reports/domain-samples.csv', csv);

  console.log(`\n✅ 샘플 추출 완료: ${allSamples.length}개`);
  console.log('📄 저장: docs/reports/domain-samples.csv');
}

stratifiedSampling()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
  });
```

**수동 검증**:

1. `docs/reports/domain-samples.csv` 열기
2. 각 샘플에 대해 도메인 지식을 활용하여 검증:
   - 핵심 데이터가 정확한가?
   - 분류가 올바른가?
   - 메타데이터가 완전한가?
3. 오류 발견 시 Notes 컬럼에 기록

**체크리스트**:
- [ ] 계층화 샘플링 스크립트 실행
- [ ] 최소 100개 샘플 추출
- [ ] 수동 검증 완료
- [ ] 오류율 계산 (< 5% 목표)

---

### Step 3: 알고리즘 출력 검증 (30-45분)

Phase 3에서 구현된 알고리즘의 출력을 검증하세요.

**예시 (도메인 알고리즘 출력 검증)**:

```typescript
// scripts/reporting/verify-algorithm-output.ts

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function verifyAlgorithmOutput() {
  console.log('🔬 알고리즘 출력 검증');

  // 알고리즘 생성 결과 샘플
  const samples = await prisma.[result].findMany({
    where: {
      source: 'algorithm', // 알고리즘 생성
      confidence: { gte: 60 }, // 신뢰도 60% 이상만
    },
    take: 100,
    include: {
      [resource]: {
        include: {
          groundTruth: {
            where: {
              source: { not: 'algorithm' }, // 원본 데이터
            },
          },
        },
      },
    },
  });

  let correct = 0;
  let incorrect = 0;
  const errors: any[] = [];

  samples.forEach((sample) => {
    const inferred = sample.value;
    const actuals = sample.[resource].groundTruth.map(g => g.value);

    // 일치 여부 확인
    if (actuals.includes(inferred)) {
      correct++;
    } else {
      incorrect++;
      errors.push({
        resource: sample.[resource].name,
        inferred,
        actual: actuals,
        confidence: sample.confidence,
      });
    }
  });

  const accuracy = (correct / (correct + incorrect)) * 100;

  console.log(`\n정확도: ${accuracy.toFixed(2)}% (${correct}/${correct + incorrect})`);

  if (errors.length > 0) {
    console.log(`\n⚠️  오류 케이스 (상위 10개):`);
    errors.slice(0, 10).forEach((e) => {
      console.log(`  ${e.resource}: 유추=${e.inferred}, 실제=${e.actual.join('/')}`);
    });
  }

  // 도메인 전문가 판단
  console.log(`\n🤔 도메인 전문가 의견:`);
  console.log(`  정확도 ${accuracy.toFixed(2)}%는 ${accuracy >= 80 ? '✅ 수용 가능' : '❌ 개선 필요'}`);
}

verifyAlgorithmOutput()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
  });
```

**체크리스트**:
- [ ] 알고리즘 출력 샘플 추출
- [ ] 수동 검증 (최소 50개)
- [ ] 정확도 계산
- [ ] 도메인 전문가 기대치 충족 여부 판단

---

### Step 4: 종합 리뷰 보고서 작성 (45-60분)

```markdown
# 도메인 전문가 리뷰 보고서

**프로젝트**: [project-name]
**리뷰어**: [Domain Expert] ([domain] 전문가)
**날짜**: [날짜]
**Phase**: 5 - Quality Improvement

---

## 요약

| 카테고리 | 점수 | 비고 |
|---------|------|------|
| 데이터 정확성 | [N]/30 | [비고] |
| 알고리즘 품질 | [N]/25 | [비고] |
| 도메인 적합성 | [N]/20 | [비고] |
| 사용성 | [N]/15 | [비고] |
| 문서화 | [N]/10 | [비고] |
| **총점** | **[N]/100 ([등급])** | **[판정]** |

---

## 1. 데이터 정확성 ([N]/30)

### 1.1 핵심 데이터 정확성 ([N]/15)

**검증 방법**: 100개 샘플 수동 검증 (계층화 샘플링)

**결과**:
- [domain accuracy metric]: [N]% ([N]/100)
- 분류 정확도: [N]% ([N]/100)

**오류 사례**:
- [구체적 오류 사례 기록]

**추천**:
- [ ] [개선 사항]

**채점 시 필수 기록**: 각 카테고리에서 감점이 있으면 최소 2-3문장으로 근거를 기록한다. 예:
- "데이터 30건 중 2건이 공식 소스와 불일치. -2점"
- 점수는 정수로 반올림한다 (소수점은 보고서에 참고용으로 기록)

**점수 근거**: [근거]

---

### 1.2 데이터 커버리지 ([N]/10)

**통계**:
- 총 레코드: [N]개
- [metric] 커버리지: [N]%

**장점**:
- ✅ [장점 기록]

**개선 필요**:
- ⚠️  [개선 필요 항목]

**추천**:
- [ ] [개선 사항]

**점수 근거**: [근거]

---

### 1.3 데이터 출처 신뢰성 ([N]/5)

**출처**:
- [출처 1] - [신뢰도]
- [출처 2] - [신뢰도]

**점수 근거**: [근거]

---

## 2. 알고리즘 품질 ([N]/25)

### 2.1 알고리즘 정확도 ([N]/15)

**[알고리즘 이름]**:
- 테스트 샘플: [N]개
- 정확도: [N]%
- 신뢰도: 평균 [N]

**도메인 전문가 의견**:
- ✅ [긍정 평가]
- ⚠️  [개선 필요 사항]

**점수 근거**: [근거]

---

### 2.2 엣지 케이스 처리 ([N]/5)

**처리 케이스**:
- ✅ NULL/누락 데이터 처리
- ✅ 신뢰도 점수 출력

**미처리 케이스**:
- ⚠️  [미처리 항목]

**점수 근거**: [근거]

---

### 2.3 투명성 ([N]/5)

- ✅ 모든 결과에 출처 명시 (source 필드)
- ✅ 신뢰도 점수 제공 (0-100)
- ✅ 알고리즘 문서화 (`docs/algorithms.md`)

**점수 근거**: [근거]

---

## 3. 도메인 적합성 ([N]/20)

### 3.1 용어 정확성 ([N]/10)

- [도메인 용어 정확성 평가]

**점수 근거**: [근거]

---

### 3.2 분류 체계 ([N]/5)

- [분류 체계 평가]

**점수 근거**: [근거]

---

### 3.3 컨텍스트 이해 ([N]/5)

- [도메인 컨텍스트 이해 평가]

**점수 근거**: [근거]

---

## 4. 사용성 ([N]/15)

### 4.1 사용자 플로우 ([N]/8)

- [사용자 플로우 평가]

**점수 근거**: [근거]

---

### 4.2 정보 표시 ([N]/7)

- [정보 표시 평가]

**점수 근거**: [근거]

---

## 5. 문서화 ([N]/10)

- [문서화 평가]

**점수 근거**: [근거]

---

## 종합 평가

**총점**: [N]/100 ([등급])

**강점**:
- [강점]

**개선 필요**:
- [개선 사항]

**결론**: [판정]

---

**리뷰어 서명**: [Domain Expert]
**날짜**: [날짜]
```

**체크리스트**:
- [ ] 모든 카테고리 점수 산정
- [ ] 구체적인 근거 제시
- [ ] 개선 사항 목록 작성
- [ ] 총점 및 등급 산출
- [ ] 결론 및 승인 여부 명시

---

## 📤 출력 파일

1. **샘플링**:
   - `docs/reports/domain-samples.csv`
   - `scripts/reporting/domain-data-sampling.ts`

2. **알고리즘 검증**:
   - `scripts/reporting/verify-algorithm-output.ts`

3. **리뷰 보고서**:
   - `docs/reports/domain-expert-review.md`

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| 샘플 데이터가 편향됨 (특정 카테고리 과다) | 샘플링 비율 재조정, 카테고리별 균등 추출 |
| 도메인 전문가와 알고리즘 저자 간 판단 불일치 | 양측 근거를 보고서에 병기, Orchestrator가 사용자에게 중재 요청 |
| 검증 점수 < 70 (Phase 3 복귀 대상) | 감점 항목을 우선순위별로 정리, 복귀 시 수정 범위를 명시 |

## ✅ 완료 체크리스트

- [ ] 리뷰 루브릭 정의 (5개 카테고리)
- [ ] 계층화 샘플링 완료 (100개 이상)
- [ ] 데이터 수동 검증 완료
- [ ] 알고리즘 출력 검증 완료
- [ ] 종합 리뷰 보고서 작성
- [ ] 총점 >= 85 (A- 이상)
- [ ] 개선 사항 목록 제공
- [ ] Git 커밋:
  ```bash
  git add docs/reports/ scripts/reporting/
  git commit -m "docs: 도메인 전문가 리뷰 완료 (Phase 5)"
  ```

---

## 🎬 다음 단계

- **점수 >= 85**: Phase 6 진행
- **점수 70-84**: Phase 5 내 반복 (개선 후 재리뷰)
- **점수 < 70**: Phase 3 복귀 (주요 재작업)

```
"agent-system/agents/phase-5/19-qa-final.md를 읽고 QLA로 작동해주세요"
```

---

