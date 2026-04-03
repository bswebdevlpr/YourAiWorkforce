# Algorithm Engineer Agent (AEA) - Phase 3

> **역할**: 도메인 특화 알고리즘 설계, 구현 및 벤치마킹
> **소요**: 2-3시간
> **난이도**: ⭐⭐⭐⭐⭐

## 📥 입력 파일

- ✅ **필수**: `docs/personas/[domain]-expert.md`
- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: `prisma/schema.prisma`
- ✅ **필수**: 데이터베이스 (Phase 2에서 로드된 데이터)

---

## 🔨 작업 Step-by-Step

### Step 1: 알고리즘 요구사항 식별 (20분)

PRD에서 알고리즘이 필요한 기능을 추출하고 알고리즘 패밀리에 매핑하세요.

**기능 동사 → 알고리즘 매핑**:

| 기능 동사 | 알고리즘 패밀리 | 예시 |
|-------------|-----------------|----------|
| Compare | 유사도 메트릭 | Jaccard, Cosine, Levenshtein, Embedding distance |
| Recommend | 추천 시스템 | 콘텐츠 기반, 협업 필터링, 하이브리드 |
| Search | 정보 검색 | Full-text, Fuzzy, Semantic, Faceted |
| Match | 매칭 알고리즘 | 규칙 기반, 패턴 매칭, ML 분류기 |
| Score | 점수 함수 | 가중 합, 정규화, 백분위수 순위 |
| Detect | 이상 탐지 | 규칙 기반, 통계적 임계값, ML |
| Classify | 분류 | 결정 트리, 규칙 기반, 분류기 |
| Predict | 예측 | 회귀, 시계열, ML 모델 |

**알고리즘 선택 기준**: 동일 목적의 알고리즘이 여러 개일 때:
1. Domain Expert 문서에서 권장하는 방법을 우선한다
2. 권장이 없으면 구현 복잡도가 낮은 쪽을 선택한다
3. 벤치마크 실행 후 정확도 차이가 5% 이내이면 단순한 쪽을 유지한다

**체크리스트**:
- [ ] PRD에서 알고리즘 필요 기능 3-5개 식별
- [ ] 각 기능에 적합한 알고리즘 패밀리 선택
- [ ] Domain Expert 문서에서 도메인 특화 제약사항 확인

---

### Step 2: 알고리즘 명세 작성 (30분)

각 알고리즘에 대해 다음 구조로 명세를 작성하세요:

```markdown
## 알고리즘 1: [알고리즘명]

**목적**: [1-2줄 설명]

**입력**:
- `param1`: [타입] - [설명]
- `param2`: [타입] - [설명]

**출력**:
- `result`: [타입] - [설명]
- `confidence`: number (0-100) - 신뢰도 점수

**알고리즘 접근법**:
1. [단계 1 설명]
2. [단계 2 설명]
3. [단계 3 설명]

**복잡도**: O(n log n)

**정확도 목표**: >= 80%

**엣지 케이스**:
- [ ] 빈 입력 처리
- [ ] null 값 처리
- [ ] 극값 처리
```

**체크리스트**:
- [ ] 모든 알고리즘에 대해 명세 작성
- [ ] 입출력 타입 명확히 정의
- [ ] 정확도 목표 설정 (Domain Expert와 협의)

---

### Step 3: 알고리즘 구현 (60-90분)

**디렉토리 구조**:

```
src/lib/algorithms/
├── similarity.ts         # 유사도 계산
├── scoring.ts            # 점수 함수
├── matching.ts           # 매칭 로직
└── utils/
    ├── normalize.ts      # 정규화 유틸리티
    └── distance.ts       # 거리 메트릭
```

**구현 템플릿**:

```typescript
// src/lib/algorithms/similarity.ts

/**
 * [알고리즘명]
 *
 * @description [1-2줄 설명]
 * @param {Type} param1 - [설명]
 * @param {Type} param2 - [설명]
 * @returns {Object} - { result: number, confidence: number }
 */
export function calculateSimilarity(
  item1: Item,
  item2: Item
): { score: number; confidence: number } {
  // 1. 입력 검증
  if (!item1 || !item2) {
    return { score: 0, confidence: 0 };
  }

  // 2. 데이터 정규화
  const normalized1 = normalize(item1);
  const normalized2 = normalize(item2);

  // 3. 핵심 알고리즘 로직
  const score = computeScore(normalized1, normalized2);

  // 4. 신뢰도 계산
  const confidence = calculateConfidence(item1, item2);

  return { score, confidence };
}

/**
 * 정규화 헬퍼 함수
 */
function normalize(item: Item): NormalizedItem {
  // 정규화 로직
  return {
    // ...
  };
}

/**
 * 신뢰도 계산
 */
function calculateConfidence(item1: Item, item2: Item): number {
  // 데이터 완전성 기반 신뢰도
  const completeness1 = getCompleteness(item1);
  const completeness2 = getCompleteness(item2);

  return Math.min(completeness1, completeness2);
}
```

**체크리스트**:
- [ ] 모든 알고리즘 구현 완료
- [ ] 입력 검증 포함
- [ ] 엣지 케이스 처리
- [ ] 신뢰도/점수 출력 (투명성)
- [ ] JSDoc 주석 추가
- [ ] TypeScript strict 모드 통과

---

### Step 4: 단위 테스트 작성 (30분)

```typescript
// src/lib/algorithms/__tests__/similarity.test.ts

import { describe, it, expect } from 'vitest';
import { calculateSimilarity } from '../similarity';

describe('calculateSimilarity', () => {
  it('should return 100 for identical items', () => {
    const item1 = { /* ... */ };
    const item2 = { /* ... */ };

    const result = calculateSimilarity(item1, item2);

    expect(result.score).toBe(100);
    expect(result.confidence).toBeGreaterThan(90);
  });

  it('should return 0 for completely different items', () => {
    const item1 = { /* ... */ };
    const item2 = { /* ... */ };

    const result = calculateSimilarity(item1, item2);

    expect(result.score).toBe(0);
  });

  it('should handle null inputs gracefully', () => {
    const result = calculateSimilarity(null, null);

    expect(result.score).toBe(0);
    expect(result.confidence).toBe(0);
  });

  it('should calculate partial similarity correctly', () => {
    const item1 = { /* ... */ };
    const item2 = { /* ... */ };

    const result = calculateSimilarity(item1, item2);

    expect(result.score).toBeGreaterThan(30);
    expect(result.score).toBeLessThan(70);
  });
});
```

**체크리스트**:
- [ ] 각 알고리즘에 최소 5개 테스트 케이스
- [ ] 엣지 케이스 테스트 (null, 빈 입력, 극값)
- [ ] 알려진 입출력 쌍 검증
- [ ] 모든 테스트 통과

---

### Step 5: 벤치마크 및 정확도 검증 (30-45분)

**벤치마크 스크립트**:

```typescript
// scripts/reporting/algorithm-benchmark.ts

import { PrismaClient } from '@prisma/client';
import { calculateSimilarity } from '../src/lib/algorithms/similarity';
import * as fs from 'fs';

const prisma = new PrismaClient();

async function benchmarkAlgorithm() {
  console.log('🔬 알고리즘 벤치마크');
  console.log('='.repeat(50));

  // 1. 테스트 데이터셋 준비 (계층화 샘플링)
  const testCases = await prepareTestDataset();

  /**
   * **벤치마크 데이터셋 생성 방법**:
   * 1. 데이터베이스에서 대표 샘플 추출 (최소 100건, 다양한 카테고리 포함)
   * 2. Domain Expert 문서의 "알려진 예외 사항"에서 엣지 케이스 10-20건 수동 생성
   * 3. 각 샘플에 `expectedScore`를 부여: Domain Expert 문서의 품질 기준을 근거로 산출
   * 4. 데이터셋을 `data/benchmark/[algorithm-name].json`에 저장
   */

  console.log(`\n테스트 케이스: ${testCases.length}개`);

  // 2. 알고리즘 실행
  const results = [];
  let correct = 0;
  let total = 0;

  for (const testCase of testCases) {
    const { input1, input2, expectedScore, tolerance } = testCase;

    const result = calculateSimilarity(input1, input2);

    // 정확도 체크 (허용 오차 내)
    const isCorrect = Math.abs(result.score - expectedScore) <= tolerance;

    if (isCorrect) correct++;
    total++;

    results.push({
      input1: input1.id,
      input2: input2.id,
      expected: expectedScore,
      actual: result.score,
      confidence: result.confidence,
      correct: isCorrect,
    });

    if (total % 50 === 0) {
      console.log(`  진행: ${total}/${testCases.length}`);
    }
  }

  // 3. 정확도 계산
  const accuracy = (correct / total) * 100;

  console.log(`\n✅ 정확도: ${accuracy.toFixed(2)}% (${correct}/${total})`);

  // 4. 신뢰도 분포
  const avgConfidence = results.reduce((sum, r) => sum + r.confidence, 0) / results.length;
  console.log(`평균 신뢰도: ${avgConfidence.toFixed(2)}`);

  // 5. 실패 케이스 분석
  const failures = results.filter(r => !r.correct);
  if (failures.length > 0) {
    console.log(`\n⚠️  실패 케이스: ${failures.length}개`);
    failures.slice(0, 5).forEach(f => {
      console.log(`  - ${f.input1} vs ${f.input2}: 예상 ${f.expected}, 실제 ${f.actual}`);
    });
  }

  // 6. 보고서 저장
  const report = {
    date: new Date().toISOString(),
    algorithm: 'calculateSimilarity',
    totalCases: total,
    correct,
    accuracy: `${accuracy.toFixed(2)}%`,
    avgConfidence: avgConfidence.toFixed(2),
    failures: failures.length,
    passed: accuracy >= 80, // 목표 임계값
  };

  fs.writeFileSync(
    'docs/reports/algorithm-benchmark.json',
    JSON.stringify(report, null, 2)
  );

  console.log('\n📄 보고서 저장: docs/reports/algorithm-benchmark.json');

  if (accuracy < 80) {
    console.log('\n❌ 정확도 목표 미달 (< 80%)');
    process.exit(1);
  }
}

async function prepareTestDataset() {
  // 계층화 샘플링으로 테스트 케이스 준비
  // Domain Expert가 레이블링한 데이터 또는 규칙 기반 예상값
  return [
    // ...
  ];
}

benchmarkAlgorithm()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
```

**체크리스트**:
- [ ] 테스트 데이터셋 준비 (최소 50개 샘플)
- [ ] 계층화 샘플링 (다양한 케이스 커버)
- [ ] 정확도 계산
- [ ] 실패 케이스 분석
- [ ] 벤치마크 보고서 저장
- [ ] 정확도 >= 80% (또는 Domain Expert 승인)

---

### Step 6: 알고리즘 문서화 (15분)

```markdown
# 알고리즘 문서

## 개요

이 문서는 [프로젝트명]에서 사용하는 핵심 알고리즘을 설명합니다.

## 알고리즘 1: [알고리즘명]

### 목적
[1-2줄 설명]

### 접근법
[알고리즘 설명]

### 정확도
- **목표**: >= 80%
- **실제**: 86.1% (499 샘플 기준)
- **신뢰도**: 평균 92.3

### 제한사항
- [제한사항 1]
- [제한사항 2]

### 개선 방향
- [개선 아이디어 1]
- [개선 아이디어 2]

---

## 알고리즘 2: [알고리즘명]

...
```

**체크리스트**:
- [ ] 모든 알고리즘 문서화
- [ ] 정확도 메트릭 포함
- [ ] 제한사항 명시
- [ ] 개선 방향 제시

---

## 📤 출력 파일

1. **알고리즘 구현**:
   - `src/lib/algorithms/similarity.ts`
   - `src/lib/algorithms/scoring.ts`
   - `src/lib/algorithms/matching.ts`
   - `src/lib/algorithms/utils/normalize.ts`
   - `src/lib/algorithms/utils/distance.ts`

2. **테스트**:
   - `src/lib/algorithms/__tests__/similarity.test.ts`
   - `src/lib/algorithms/__tests__/scoring.test.ts`

3. **벤치마크 스크립트**:
   - `scripts/reporting/algorithm-benchmark.ts`

4. **보고서**:
   - `docs/reports/algorithm-benchmark.json`

5. **문서**:
   - `docs/algorithms.md`

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| 정확도 목표(80%) 미달 | 알고리즘 파라미터 튜닝 → 대안 알고리즘 시도 → 목표 하향 조정 (사용자 승인 필요) |
| 벤치마크 데이터 부족 | Domain Expert 문서에서 추가 케이스 도출, 최소 50건까지 확보 |
| 실행 시간 > 10초/건 | 배치 처리로 전환, 캐싱 적용, 알고리즘 최적화 |

## ✅ 완료 체크리스트

- [ ] 알고리즘 요구사항 식별 완료 (3-5개)
- [ ] 알고리즘 명세 작성 완료
- [ ] 모든 알고리즘 구현 완료
- [ ] 단위 테스트 작성 및 통과
- [ ] 벤치마크 실행 완료
- [ ] 정확도 >= 80% (또는 Domain Expert 승인)
- [ ] 알고리즘 문서화 완료
- [ ] TypeScript strict 모드 통과
- [ ] ESLint 에러 없음
- [ ] Git 커밋:
  ```bash
  git add src/lib/algorithms/ scripts/reporting/ docs/
  git commit -m "feat: 도메인 특화 알고리즘 구현 및 벤치마크 (Phase 3)"
  ```

---

## 🎬 다음 단계

알고리즘 구현이 완료되면 다음 에이전트로 진행하세요:

```
"agent-system/agents/phase-3/12-frontend-developer.md를 읽고 FDA로 작동해주세요"
```

