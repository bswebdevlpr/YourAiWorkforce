# QA Final Review Agent (QLA) - Phase 5

> **역할**: 최종 품질 검증 및 회귀 테스트
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/reports/domain-expert-review.md`
- ✅ **필수**: Phase 5에서 수정된 코드/데이터
- ✅ **필수**: 기존 테스트 스위트

---

## 🔨 작업 Step-by-Step

### Step 1: 도메인 전문가 이슈 확인 (15분)

도메인 전문가 리뷰에서 제기된 이슈가 해결되었는지 확인하세요.

```markdown
# 도메인 전문가 이슈 추적

| # | 이슈 | 상태 | 해결 방법 | 검증 |
|---|------|------|-----------|------|
| 1 | [데이터 누락 항목 A] | ✅ | `update-data.ts` 실행 | 쿼리 확인 |
| 2 | [데이터 누락 항목 B] | ✅ | `enrich-data.ts` 실행 | 데이터 확인 |
| 3 | [알고리즘 이슈] | ✅ | 알고리즘 규칙 추가 | 테스트 확인 |
| 4 | [분류 누락] | ⏳ | 데이터 소스 조사 중 | - |

**이슈 요약**:
- ✅ 해결: 3개
- ⏳ 진행 중: 1개
- ❌ 미해결: 0개
```

**체크리스트**:
- [ ] 모든 이슈 추적 테이블 작성
- [ ] 해결된 이슈 검증
- [ ] 미해결 이슈 이유 문서화

---

### Step 2: 회귀 테스트 (30-45분)

Phase 5 수정사항이 기존 기능을 깨뜨리지 않았는지 확인하세요.

```bash
# 모든 테스트 실행
npm run test          # 단위 테스트
npm run test:e2e      # E2E 테스트
npm run test:api      # API 통합 테스트
```

**회귀 테스트 체크리스트**:

```markdown
## 회귀 테스트 결과

### 단위 테스트
- **총 테스트**: 120개
- **통과**: 120개
- **실패**: 0개
- **건너뜀**: 0개

### E2E 테스트
- **총 테스트**: 28개
- **통과**: 28개
- **실패**: 0개

### API 통합 테스트
- **총 테스트**: 15개
- **통과**: 15개
- **실패**: 0개

✅ **모든 테스트 통과**
```

**새로운 테스트 추가** (Phase 5 수정사항):

```typescript
// test/unit/domain-algorithm.test.ts

import { describe, it, expect } from 'vitest';
import { applyDomainRule } from '@/lib/algorithms/[domain]';

describe('Domain-specific Algorithm', () => {
  it('should apply rule for standard case', () => {
    const result = applyDomainRule('input-a', 'context-1');
    expect(result).toBe('expected-output-a');
  });

  it('should apply rule for variant case', () => {
    const result = applyDomainRule('input-b', 'context-1');
    expect(result).toBe('expected-output-b');
  });

  it('should not apply rule in excluded context', () => {
    const result = applyDomainRule('input-a', 'context-2');
    expect(result).toBe('input-a');
  });

  it('should handle edge case: exception rule', () => {
    const result = applyDomainRule('input-c', 'exception');
    expect(result).toBe('input-c'); // 예외
  });
});
```

**체크리스트**:
- [ ] 모든 기존 테스트 통과
- [ ] Phase 5 수정사항에 대한 새 테스트 추가
- [ ] 회귀 테스트 결과 문서화

---

### Step 3: 데이터 품질 재검증 (30분)

Phase 5에서 추가/수정된 데이터의 품질을 검증하세요.

```typescript
// scripts/reporting/final-data-quality.ts

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function finalDataQuality() {
  console.log('📊 최종 데이터 품질 검증');
  console.log('='.repeat(50));

  // 1. 커버리지 메트릭
  const totalRecords = await prisma.[resource].count();

  const categoryCoverage = {
    categoryA: await prisma.[detail].count({
      where: { category: 'A' },
    }),
    categoryB: await prisma.[detail].count({
      where: { category: 'B' },
    }),
  };

  const metadataCoverage = await prisma.[metadata].count();

  console.log(`\n총 레코드: ${totalRecords}개`);
  console.log(`카테고리별 커버리지:`);
  console.log(`  카테고리 A: ${(categoryCoverage.categoryA / totalRecords * 100).toFixed(2)}%`);
  console.log(`  카테고리 B: ${(categoryCoverage.categoryB / totalRecords * 100).toFixed(2)}%`);
  console.log(`메타데이터 커버리지: ${(metadataCoverage / totalRecords * 100).toFixed(2)}%`);

  // 2. 품질 이슈 체크
  const issues = [];

  // NULL 체크
  const nullDetails = await prisma.[resource].count({
    where: {
      details: { none: {} },
    },
  });

  if (nullDetails > 0) {
    issues.push(`상세 정보 누락: ${nullDetails}개 레코드`);
  }

  // 중복 체크
  const duplicates = await prisma.$queryRaw`
    SELECT "value", "category", COUNT(*) as count
    FROM "[Detail]"
    GROUP BY "value", "category", "[resourceId]"
    HAVING COUNT(*) > 1
  `;

  if ((duplicates as any[]).length > 0) {
    issues.push(`중복 데이터: ${(duplicates as any[]).length}개`);
  }

  // 3. 신뢰도 분포
  const avgConfidence = await prisma.[detail].aggregate({
    _avg: { confidence: true },
    where: {
      confidence: { not: null },
    },
  });

  console.log(`\n평균 신뢰도: ${avgConfidence._avg.confidence?.toFixed(2)}`);

  // 4. 품질 게이트
  console.log(`\n품질 게이트:`);

  const gates = [
    {
      name: '[metric] 커버리지 (카테고리 A)',
      value: (categoryCoverage.categoryA / totalRecords) * 100,
      threshold: 70,
    },
    {
      name: '메타데이터 커버리지',
      value: (metadataCoverage / totalRecords) * 100,
      threshold: 80,
    },
    {
      name: '평균 신뢰도',
      value: avgConfidence._avg.confidence || 0,
      threshold: 85,
    },
    {
      name: '품질 이슈',
      value: issues.length,
      threshold: 5,
      inverse: true, // 낮을수록 좋음
    },
  ];

  let allPassed = true;

  gates.forEach((gate) => {
    const passed = gate.inverse
      ? gate.value <= gate.threshold
      : gate.value >= gate.threshold;

    console.log(
      `  ${passed ? '✅' : '❌'} ${gate.name}: ${gate.value.toFixed(2)} ${gate.inverse ? '<=' : '>='} ${gate.threshold}`
    );

    if (!passed) allPassed = false;
  });

  if (allPassed) {
    console.log('\n✅ 모든 품질 게이트 통과');
  } else {
    console.log('\n❌ 품질 게이트 실패');
    process.exit(1);
  }

  // 품질 기준 미달 시 빌드 실패
  if (accuracy < 0.95 || coverage < 0.80) {
    console.error('❌ 품질 기준 미달. 위 항목을 수정 후 재실행하세요.');
    process.exit(1);
  }
  console.log('✅ 모든 품질 기준 통과');
}

finalDataQuality()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
```

**체크리스트**:
- [ ] 커버리지 메트릭 확인
- [ ] NULL/중복 데이터 체크
- [ ] 신뢰도 분포 확인
- [ ] 모든 품질 게이트 통과

---

### Step 4: 성능 벤치마크 (20분)

Phase 5 수정사항이 성능에 영향을 주지 않았는지 확인하세요.

```bash
# Lighthouse 재실행
lhci autorun

# 응답 시간 체크
npm run test:perf
```

**성능 벤치마크**:

```typescript
// test/performance/api-benchmark.ts

import { describe, it, expect } from 'vitest';

describe('API Performance', () => {
  it('should respond within 200ms for search', async () => {
    const start = Date.now();
    const response = await fetch('http://localhost:3000/api/search?q=keyword');
    const duration = Date.now() - start;

    expect(response.status).toBe(200);
    expect(duration).toBeLessThan(200);
  });

> 성능 테스트는 10회 실행하여 95th percentile 기준으로 판단한다. 단일 실행 결과로 판정하지 않는다.

  it('should respond within 100ms for resource detail', async () => {
    const start = Date.now();
    const response = await fetch('http://localhost:3000/api/[resources]/clx123456');
    const duration = Date.now() - start;

    expect(response.status).toBe(200);
    expect(duration).toBeLessThan(100);
  });
});
```

**체크리스트**:
- [ ] Lighthouse 점수 유지 (Performance >= 85)
- [ ] API 응답 시간 확인 (< 200ms)
- [ ] 페이지 로드 시간 확인 (< 3s)

---

### Step 5: 최종 품질 보고서 (15분)

```markdown
# Phase 5 최종 품질 보고서

**날짜**: 2026-02-16
**Phase**: 5 - Quality Improvement

---

## 도메인 전문가 이슈 해결

| 이슈 | 상태 | 해결 방법 |
|------|------|-----------|
| [데이터 누락 항목 A] | ✅ | 데이터 추가 |
| [데이터 누락 항목 B] | ✅ | 데이터 추가 |
| [알고리즘 이슈] | ✅ | 알고리즘 추가 |
| [분류 누락] | ⏳ | 향후 추가 |

**해결률**: 75% (3/4)

---

## 회귀 테스트 결과

| 테스트 스위트 | 총 | 통과 | 실패 |
|--------------|-----|------|------|
| 단위 테스트 | 120 | 120 | 0 |
| E2E 테스트 | 28 | 28 | 0 |
| API 통합 테스트 | 15 | 15 | 0 |

✅ **모든 테스트 통과 (100%)**

---

## 데이터 품질

| 메트릭 | 값 | 목표 | 결과 |
|--------|-----|------|------|
| [metric] 커버리지 (카테고리 A) | [N]% | >= [N]% | ✅ |
| [metric] 커버리지 (카테고리 B) | [N]% | >= [N]% | ✅ |
| 메타데이터 커버리지 | [N]% | >= [N]% | ✅ |
| 평균 신뢰도 | [N] | >= [N] | ✅ |
| 품질 이슈 | [N] | <= 5 | ✅ |

✅ **모든 품질 게이트 통과**

---

## 성능 벤치마크

| 메트릭 | 값 | 목표 | 결과 |
|--------|-----|------|------|
| Lighthouse Performance | 92 | >= 85 | ✅ |
| Lighthouse Accessibility | 100 | >= 85 | ✅ |
| Lighthouse SEO | 100 | >= 90 | ✅ |
| API 응답 시간 (평균) | 87ms | < 200ms | ✅ |
| 페이지 로드 시간 | 1.8s | < 3s | ✅ |

✅ **모든 성능 목표 달성**

---

## Phase 5 변경 사항

### 데이터 개선
- 데이터 추가: [N]개 레코드
- 커버리지 향상: [metric] +[N]%

### 알고리즘 개선
- [도메인 규칙] 처리 추가
- 정확도 향상: [N]% -> [N]% (+[N]%p)

### 버그 수정
- 중복 데이터 제거: [N]건
- 데이터 정규화: [N]건

---

## 최종 승인

✅ **Phase 5 완료**

- 도메인 전문가 점수: **[N]/100 ([등급])**
- 모든 테스트 통과
- 모든 품질 게이트 통과
- 성능 목표 달성

**Phase 6 진행 승인**

---

**QA Lead**: [이름]
**날짜**: 2026-02-16
```

---

## 📤 출력 파일

1. **이슈 추적**:
   - `docs/reports/phase-5-issues.md`

2. **테스트 보고서**:
   - `docs/reports/regression-test-results.md`

3. **데이터 품질**:
   - `scripts/reporting/final-data-quality.ts`

4. **최종 보고서**:
   - `docs/reports/phase-5-final-report.md`

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| 회귀 테스트 실패 | Phase 5 변경사항과 실패 테스트의 관계를 분석, 변경으로 인한 회귀인지 기존 결함인지 구분 |
| 성능 벤치마크 미달 | `EXPLAIN ANALYZE`로 쿼리 분석, 인덱스 추가 또는 캐시 적용 |
| Phase 4 테스트와 Phase 5 결과 불일치 | 테스트 환경(데이터, 설정) 차이 확인, 동일 환경에서 재실행 |

## ✅ 완료 체크리스트

- [ ] 도메인 전문가 이슈 추적 완료
- [ ] 해결된 이슈 검증 완료
- [ ] 모든 회귀 테스트 통과
- [ ] Phase 5 수정사항에 대한 새 테스트 추가
- [ ] 데이터 품질 재검증 완료
- [ ] 모든 품질 게이트 통과
- [ ] 성능 벤치마크 완료
- [ ] 최종 품질 보고서 작성
- [ ] Git 커밋:
  ```bash
  git add docs/reports/ test/
  git commit -m "test: Phase 5 최종 품질 검증 완료"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-6/20-technical-writer.md를 읽고 TWA로 작동해주세요"
```

---

