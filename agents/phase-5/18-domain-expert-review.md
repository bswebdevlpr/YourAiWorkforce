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
    highFrequency: await prisma.character.findMany({
      where: {
        // 도메인별 고빈도 기준 (예: HSK 1급, JLPT N5)
        OR: [
          { hskLevel: 1 },
          { jlptLevel: 5 },
        ],
      },
      take: 50,
      include: {
        pronunciations: true,
        meanings: true,
      },
    }),

    // 중간 빈도
    mediumFrequency: await prisma.character.findMany({
      where: {
        OR: [
          { hskLevel: { gte: 2, lte: 4 } },
          { jlptLevel: { gte: 3, lte: 4 } },
        ],
      },
      take: 30,
      include: {
        pronunciations: true,
        meanings: true,
      },
    }),

    // 저빈도 (희귀)
    lowFrequency: await prisma.character.findMany({
      where: {
        OR: [
          { hskLevel: { gte: 5 } },
          { jlptLevel: { lte: 2 } },
        ],
      },
      take: 20,
      include: {
        pronunciations: true,
        meanings: true,
      },
    }),

    // 엣지 케이스 (변형, 특수 케이스)
    edgeCases: await prisma.character.findMany({
      where: {
        OR: [
          { variants: { some: {} } },
          { pronunciations: { none: {} } }, // 발음 누락
          { meanings: { none: {} } }, // 의미 누락
        ],
      },
      take: 20,
      include: {
        pronunciations: true,
        meanings: true,
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
    ['ID', 'Character', 'Pronunciations', 'Meanings', 'Category', 'Notes'].join(','),
    ...allSamples.map((s) => [
      s.id,
      s.char,
      s.pronunciations.map(p => p.text).join(';'),
      s.meanings.map(m => m.text).join(';'),
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
   - 발음이 정확한가?
   - 의미가 정확한가?
   - 분류가 올바른가?
3. 오류 발견 시 Notes 컬럼에 기록

**체크리스트**:
- [ ] 계층화 샘플링 스크립트 실행
- [ ] 최소 100개 샘플 추출
- [ ] 수동 검증 완료
- [ ] 오류율 계산 (< 5% 목표)

---

### Step 3: 알고리즘 출력 검증 (30-45분)

Phase 3에서 구현된 알고리즘의 출력을 검증하세요.

**예시 (TriHanzi - 발음 유추 알고리즘)**:

```typescript
// scripts/reporting/verify-algorithm-output.ts

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function verifyAlgorithmOutput() {
  console.log('🔬 알고리즘 출력 검증');

  // 발음 유추 결과 샘플
  const samples = await prisma.pronunciation.findMany({
    where: {
      source: 'jp_inference', // 알고리즘 생성
      confidence: { gte: 60 }, // 신뢰도 60% 이상만
    },
    take: 100,
    include: {
      character: {
        include: {
          pronunciations: {
            where: {
              country: 'KOREA',
              source: { not: 'jp_inference' }, // 원본 데이터
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
    const inferredPronunciation = sample.text;
    const actualPronunciations = sample.character.pronunciations.map(p => p.text);

    // 일치 여부 확인
    if (actualPronunciations.includes(inferredPronunciation)) {
      correct++;
    } else {
      incorrect++;
      errors.push({
        character: sample.character.char,
        inferred: inferredPronunciation,
        actual: actualPronunciations,
        confidence: sample.confidence,
      });
    }
  });

  const accuracy = (correct / (correct + incorrect)) * 100;

  console.log(`\n정확도: ${accuracy.toFixed(2)}% (${correct}/${correct + incorrect})`);

  if (errors.length > 0) {
    console.log(`\n⚠️  오류 케이스 (상위 10개):`);
    errors.slice(0, 10).forEach((e) => {
      console.log(`  ${e.character}: 유추=${e.inferred}, 실제=${e.actual.join('/')}`);
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

**프로젝트**: TriHanzi - CJK Character Comparison
**리뷰어**: Dr. Lee Hanja (비교 언어학 전문가)
**날짜**: 2026-02-16
**Phase**: 5 - Quality Improvement

---

## 요약

| 카테고리 | 점수 | 비고 |
|---------|------|------|
| 데이터 정확성 | 28/30 | 발음 커버리지 우수 |
| 알고리즘 품질 | 22/25 | 정확도 목표 달성 |
| 도메인 적합성 | 18/20 | 용어 정확, 컨텍스트 우수 |
| 사용성 | 14/15 | 직관적인 인터페이스 |
| 문서화 | 10/10 | 출처 명확, 배경 상세 |
| **총점** | **92/100 (A)** | **프로덕션 품질** |

---

## 1. 데이터 정확성 (28/30)

### 1.1 핵심 데이터 정확성 (14/15)

**검증 방법**: 100개 샘플 수동 검증 (계층화 샘플링)

**결과**:
- ✅ 발음 정확도: 97% (97/100)
- ✅ 의미 정확도: 95% (95/100)
- ✅ 분류 정확도: 100% (100/100)

**오류 사례**:
- 발음: "樂" → 한국어 "악"만 있고 "락/낙" 누락
- 의미: "間" → "room" 의미 누락

**추천**:
- [ ] 다음 발음 추가: 樂(락/낙), 便(변/편)
- [ ] 의미 보강: 間(room, interval, space)

**점수 근거**: 경미한 오류 3%, 전반적으로 매우 정확

---

### 1.2 데이터 커버리지 (9/10)

**통계**:
- 총 문자: 10,000개
- 발음 커버리지: 73.0%
- 의미 커버리지: 82.1%
- 교육 레벨 커버리지: 68.5%

**장점**:
- ✅ 상용 한자 (HSK 1-6, JLPT N5-N1) 100% 커버
- ✅ 3개국 발음 균형 (한국 73%, 일본 95%, 중국 98%)

**개선 필요**:
- ⚠️  한국어 발음 커버리지가 상대적으로 낮음 (73%)
- ⚠️  교육 레벨 누락 (31.5%)

**추천**:
- [ ] 한국어 발음 추가 보강 (목표 85%)
- [ ] 교육 레벨 데이터 추가 (한국 교육용 한자)

**점수 근거**: 커버리지 양호하나 한국 데이터 보강 필요

---

### 1.3 데이터 출처 신뢰성 (5/5)

**출처**:
- Unihan Database (Unicode Consortium) - 공식, 신뢰도 100%
- CC-CEDICT - 오픈소스, 124,259 항목, 신뢰도 95%
- KANJIDIC2 - 공식, 13,108자, 신뢰도 100%

**점수 근거**: 모든 출처가 신뢰할 수 있고 명시됨

---

## 2. 알고리즘 품질 (22/25)

### 2.1 알고리즘 정확도 (13/15)

**발음 유추 알고리즘** (중고음 대응):
- 테스트 샘플: 499개
- 정확도: 86.1%
- 신뢰도: 평균 92.3

**도메인 전문가 의견**:
- ✅ 중고음 재구 기반 접근법은 학술적으로 타당
- ✅ 입성음 복원 (く → 곡, つ → 촬) 정확도 높음
- ⚠️  일부 예외 케이스 (역사적 음운 변화) 미처리

**Jaccard 유사도** (False Friends):
- 662개 False Friends 감지
- 샘플 검증: 150개 중 147개 정확 (98%)

**점수 근거**: 정확도 우수하나 엣지 케이스 개선 여지

---

### 2.2 엣지 케이스 처리 (4/5)

**처리 케이스**:
- ✅ NULL 발음/의미 처리
- ✅ Youon 구개음화 처리 (42개 매핑)
- ✅ 신뢰도 점수 출력

**미처리 케이스**:
- ⚠️  한국 한자음의 두음법칙 (예: 女 → 녀/여)
- ⚠️  일본 한자의 특수 음독 (湯桶読み, 重箱読み)

**추천**:
- [ ] 두음법칙 규칙 추가
- [ ] 특수 음독 케이스 문서화

**점수 근거**: 주요 케이스 처리되나 일부 누락

---

### 2.3 투명성 (5/5)

- ✅ 모든 발음에 출처 명시 (source 필드)
- ✅ 신뢰도 점수 제공 (0-100)
- ✅ 알고리즘 문서화 (`docs/algorithms.md`)

**점수 근거**: 완벽한 투명성

---

## 3. 도메인 적합성 (18/20)

### 3.1 용어 정확성 (9/10)

- ✅ "False Friends" 용어 적절
- ✅ 국가별 용어 정확 (한자/漢字/汉字)
- ✅ 발음 타입 정확 (KUN/ON/MANDARIN/CANTONESE)

**개선**:
- ⚠️  "中古音" → "Middle Chinese" 번역 추가

**점수 근거**: 용어 대부분 정확

---

### 3.2 분류 체계 (4/5)

- ✅ HSK 레벨 (1-6) 정확
- ✅ JLPT 레벨 (N5-N1) 정확
- ⚠️  한국 교육용 한자 분류 누락

**추천**:
- [ ] 한국 교육용 기초/상용/준상용 분류 추가

**점수 근거**: 중국/일본 분류 완벽, 한국 누락

---

### 3.3 컨텍스트 이해 (5/5)

- ✅ 국가별 의미 차이 반영 (예: 手紙)
- ✅ False Friends 컨텍스트 명확
- ✅ 역사적 음운 변화 이해

**점수 근거**: 도메인 컨텍스트 완벽 이해

---

## 4. 사용성 (14/15)

### 4.1 사용자 플로우 (7/8)

- ✅ 검색 → 상세 → 비교 플로우 직관적
- ✅ False Friends 경고 명확
- ⚠️  발음 재생 기능 없음 (음성)

**추천**:
- [ ] 발음 오디오 추가 (향후)

**점수 근거**: 플로우 우수하나 음성 기능 부재

---

### 4.2 정보 표시 (7/7)

- ✅ 국가별 색상 코딩 명확
- ✅ 발음/의미 구분 명확
- ✅ 신뢰도 점수 표시

**점수 근거**: 정보 표시 완벽

---

## 5. 문서화 (10/10)

- ✅ 도메인 지식 문서 (412줄)
- ✅ 모든 데이터 출처 명시
- ✅ 알고리즘 설명 상세
- ✅ 제한사항 명시

**점수 근거**: 문서화 완벽

---

## 종합 평가

**총점**: 92/100 (A)

**강점**:
- 데이터 정확성 매우 높음 (97%)
- 알고리즘 학술적으로 타당
- 투명성 완벽
- 문서화 우수

**개선 필요**:
- 한국어 발음 커버리지 보강 (73% → 85%)
- 두음법칙 처리
- 한국 교육용 한자 분류 추가
- 경미한 발음/의미 오류 수정

**결론**: ✅ **프로덕션 품질 달성**

이 프로젝트는 도메인 전문가 관점에서 프로덕션에 배포 가능한 수준입니다. 제안된 개선사항은 선택적이며, 현재 상태로도 사용자에게 큰 가치를 제공할 수 있습니다.

---

**리뷰어 서명**: Dr. Lee Hanja
**날짜**: 2026-02-16
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

## 💡 TriHanzi 실제 도메인 전문가 리뷰

**리뷰 이력**:
1. **1차 리뷰 (B+)**: 87.5/100 - 발음 커버리지 부족
2. **2차 리뷰 (A-)**: 91.0/100 - 발음 개선, 교육 데이터 추가
3. **3차 리뷰 (A)**: 93.5/100 - 문서 개선
4. **4차 리뷰 (A+)**: 95.0/100 - 모든 개선 완료

**최종 점수 분해**:
- 데이터 정확성: 28/30 (93%)
- 알고리즘 품질: 23/25 (92%)
- 도메인 적합성: 19/20 (95%)
- 사용성: 15/15 (100%)
- 문서화: 10/10 (100%)

**개선 이력**:
- 발음 커버리지: 51.4% → 73.0% (21.6%p)
- 의미 커버리지: 68.2% → 82.1% (13.9%p)
- 알고리즘 정확도: 73.2% → 86.1% (12.9%p)
