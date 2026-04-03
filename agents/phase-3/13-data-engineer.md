# Data Engineer Agent (DEN) - Phase 3

> **역할**: 알고리즘 생성 데이터 준비 및 파생 메타데이터 생성
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `src/lib/algorithms/` (Phase 3 알고리즘 구현)
- ✅ **필수**: 데이터베이스 (Phase 2 데이터)
- ✅ **필수**: `docs/personas/[domain]-expert.md`

---

## 🔨 작업 Step-by-Step

### Step 1: 알고리즘 데이터 요구사항 분석 (15분)

구현된 알고리즘이 필요로 하는 데이터를 파악하세요.

**질문**:
1. 알고리즘 입력 데이터가 데이터베이스에 충분히 있는가?
2. 알고리즘 출력 데이터를 데이터베이스에 저장해야 하는가?
3. 사전 계산이 필요한 파생 데이터가 있는가?

**예시**:
- **유사도 알고리즘** → 비교 대상 데이터 필요 → 이미 존재 ✅
- **매칭 알고리즘** → 관련 속성 데이터 필요 → 이미 존재 ✅
- **이상 탐지 알고리즘** → 탐지 결과 저장 필요 → 새 테이블 필요 ❌

**체크리스트**:
- [ ] 알고리즘 입력 데이터 확인
- [ ] 알고리즘 출력 저장 필요성 판단
- [ ] 스키마 수정 필요 여부 확인

---

### Step 2: 스키마 확장 (필요 시) (20분)

알고리즘 출력을 저장할 테이블/필드를 추가하세요.

**예시: 파생 데이터 테이블**

```prisma
// prisma/schema.prisma

model [DerivedEntity] {
  id String @id @default(cuid())

  // 비교/연산 대상
  resource1Id String
  resource1   [Resource] @relation("derived1", fields: [resource1Id], references: [id])

  resource2Id String
  resource2   [Resource] @relation("derived2", fields: [resource2Id], references: [id])

  // 알고리즘 산출 점수
  similarityScore  Float  // 0-100
  matchScore       Float  // 0-100

  // 특이 케이스 여부
  isException Boolean @default(false)

  // 신뢰도
  confidence Float @default(100)

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([resource1Id, resource2Id])
  @@index([isException])
  @@index([similarityScore])
}
```

**마이그레이션**:

```bash
npx prisma migrate dev --name add_comparison_metadata
```

**체크리스트**:
- [ ] 스키마에 새 모델 추가 (필요 시)
- [ ] 인덱스 추가 (쿼리 성능)
- [ ] 마이그레이션 실행
- [ ] 스키마 검증

---

### Step 3: 알고리즘 실행 스크립트 작성 (45-60분)

모든 데이터에 대해 알고리즘을 실행하고 결과를 저장하세요.

```typescript
// scripts/enrichment/compute-derived-metadata.ts

import { PrismaClient } from '@prisma/client';
// ⚠️ 아래 함수들은 Phase 3 Algorithm Engineer(11)가 `src/lib/algorithms/`에 구현한 함수를 import한다.
// 실행 전 다음을 확인한다:
// 1. `src/lib/algorithms/` 디렉토리에서 export된 함수 목록을 확인한다
// 2. 함수명이 다를 경우 실제 export 이름에 맞게 import를 수정한다
// 3. 함수 시그니처(입력 타입, 반환 타입)를 확인하고 호출 코드를 맞춘다
import { [algorithmFunction1] } from '@/lib/algorithms/similarity';
import { [algorithmFunction2] } from '@/lib/algorithms/matching';

const prisma = new PrismaClient();

async function computeDerivedMetadata() {
  console.log('🔄 파생 메타데이터 생성');
  console.log('='.repeat(50));

  // 1. 모든 리소스 가져오기
  const resources = await prisma.[resource].findMany({
    include: {
      relatedData: true,
    },
  });

  console.log(`\n총 리소스: ${resources.length}개`);

  let computed = 0;
  let exceptionCount = 0;

  // ⚠️ **성능 주의**: 레코드 N개에 대해 N×(N-1)/2 쌍을 처리한다. N=10,000이면 ~5천만 쌍.
  // - N ≤ 1,000: 단일 스크립트로 처리 가능
  // - N > 1,000: 배치 처리 (1,000건 단위), `Promise.all` 대신 순차 처리로 메모리 관리
  // - 처리 시간을 로그로 출력하여 진행률을 추적한다

  // 2. 모든 페어 조합 계산
  for (let i = 0; i < resources.length; i++) {
    for (let j = i + 1; j < resources.length; j++) {
      const item1 = resources[i];
      const item2 = resources[j];

      try {
        // 알고리즘 실행
        const similarityResult = [algorithmFunction1](item1, item2);
        const matchScore = [algorithmFunction2](item1, item2);

        // 특이 케이스 탐지
        const isException = similarityResult.score > 70 && matchScore < 30;

        if (isException) exceptionCount++;

        // 데이터베이스에 저장
        await prisma.[derivedEntity].upsert({
          where: {
            resource1Id_resource2Id: {
              resource1Id: item1.id,
              resource2Id: item2.id,
            },
          },
          update: {
            similarityScore: similarityResult.score,
            matchScore,
            isException,
            confidence: similarityResult.confidence,
          },
          create: {
            resource1Id: item1.id,
            resource2Id: item2.id,
            similarityScore: similarityResult.score,
            matchScore,
            isException,
            confidence: similarityResult.confidence,
          },
        });

        computed++;

        if (computed % 100 === 0) {
          console.log(`  진행: ${computed} 페어 계산...`);
        }
      } catch (error) {
        console.error(`  ✗ 오류: ${item1.id} vs ${item2.id}`, error);
      }
    }
  }

  console.log(`\n✅ 완료: ${computed} 페어 계산`);
  console.log(`특이 케이스: ${exceptionCount}개`);
}

computeDerivedMetadata()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
```

**최적화 팁**:
- **배치 처리**: 1000개씩 묶어서 처리
- **병렬 처리**: `Promise.all`로 여러 계산 동시 실행
- **프로그레스 바**: `cli-progress` 패키지 사용
- **체크포인트**: 중간 결과 저장하여 재시작 가능

**체크리스트**:
- [ ] 알고리즘 실행 스크립트 작성
- [ ] 에러 핸들링 구현
- [ ] 진행 상황 로깅
- [ ] 배치/병렬 처리 최적화
- [ ] 스크립트 실행 및 결과 검증

---

### Step 4: 데이터 검증 (20분)

생성된 데이터의 품질을 검증하세요.

```typescript
// scripts/reporting/validate-computed-data.ts

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function validateComputedData() {
  console.log('🔍 계산 데이터 검증');
  console.log('='.repeat(50));

  // 1. 총 레코드 수
  const totalMetadata = await prisma.[derivedEntity].count();
  console.log(`\n총 메타데이터: ${totalMetadata}개`);

  // 2. 특이 케이스 통계
  const exceptions = await prisma.[derivedEntity].count({
    where: { isException: true },
  });
  console.log(`특이 케이스: ${exceptions}개 (${(exceptions / totalMetadata * 100).toFixed(2)}%)`);

  // 3. 유사도 분포
  const avgSimilarity = await prisma.[derivedEntity].aggregate({
    _avg: { similarityScore: true },
  });
  console.log(`평균 유사도: ${avgSimilarity._avg.similarityScore?.toFixed(2)}`);

  // 4. 신뢰도 분포
  const avgConfidence = await prisma.[derivedEntity].aggregate({
    _avg: { confidence: true },
  });
  console.log(`평균 신뢰도: ${avgConfidence._avg.confidence?.toFixed(2)}`);

  // 5. 샘플 검증
  console.log('\n📊 샘플 검증 (상위 5개 특이 케이스):');
  const samples = await prisma.[derivedEntity].findMany({
    where: { isException: true },
    include: {
      resource1: true,
      resource2: true,
    },
    orderBy: { similarityScore: 'desc' },
    take: 5,
  });

  samples.forEach((sample, i) => {
    console.log(`  ${i + 1}. ${sample.resource1.id} vs ${sample.resource2.id}`);
    console.log(`     유사도: ${sample.similarityScore.toFixed(2)}, 매칭: ${sample.matchScore.toFixed(2)}`);
  });

  // 6. 품질 체크
  const issues = [];

  // 6.1. NULL 체크
  const nullCount = await prisma.[derivedEntity].count({
    where: {
      OR: [
        { similarityScore: null },
        { matchScore: null },
      ],
    },
  });
  if (nullCount > 0) {
    issues.push(`NULL 값: ${nullCount}개`);
  }

  // 6.2. 범위 체크 (0-100)
  const outOfRange = await prisma.[derivedEntity].count({
    where: {
      OR: [
        { similarityScore: { lt: 0 } },
        { similarityScore: { gt: 100 } },
        { matchScore: { lt: 0 } },
        { matchScore: { gt: 100 } },
      ],
    },
  });
  if (outOfRange > 0) {
    issues.push(`범위 초과: ${outOfRange}개`);
  }

  if (issues.length === 0) {
    console.log('\n✅ 품질 검증 통과');
  } else {
    console.log('\n⚠️  품질 이슈:');
    issues.forEach(issue => console.log(`  - ${issue}`));
  }
}

validateComputedData()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
  });
```

**체크리스트**:
- [ ] 총 레코드 수 확인
- [ ] 통계 분포 확인
- [ ] NULL 값 검사
- [ ] 값 범위 검사 (0-100 등)
- [ ] 샘플 검증 (수동 확인)

---

### Step 5: 보고서 생성 (15분)

```typescript
// scripts/reporting/algorithm-data-report.ts

async function generateReport() {
  const report = {
    date: new Date().toISOString(),
    totalMetadata: await prisma.[derivedEntity].count(),
    exceptions: await prisma.[derivedEntity].count({
      where: { isException: true },
    }),
    statistics: {
      avgSimilarityScore: (
        await prisma.[derivedEntity].aggregate({
          _avg: { similarityScore: true },
        })
      )._avg.similarityScore,
      avgMatchScore: (
        await prisma.[derivedEntity].aggregate({
          _avg: { matchScore: true },
        })
      )._avg.matchScore,
      avgConfidence: (
        await prisma.[derivedEntity].aggregate({
          _avg: { confidence: true },
        })
      )._avg.confidence,
    },
    qualityCheck: {
      nullCount: 0,
      outOfRangeCount: 0,
      passed: true,
    },
  };

  fs.writeFileSync(
    'docs/reports/algorithm-data-report.json',
    JSON.stringify(report, null, 2)
  );

  console.log('\n📄 보고서 저장: docs/reports/algorithm-data-report.json');
}
```

---

## 📤 출력 파일

1. **스키마** (필요 시):
   - `prisma/schema.prisma` (업데이트)
   - `prisma/migrations/` (새 마이그레이션)

2. **스크립트**:
   - `scripts/enrichment/compute-comparison-metadata.ts`
   - `scripts/enrichment/compute-[other-metadata].ts`

3. **검증 스크립트**:
   - `scripts/reporting/validate-computed-data.ts`
   - `scripts/reporting/algorithm-data-report.ts`

4. **보고서**:
   - `docs/reports/algorithm-data-report.json`

5. **업데이트된 데이터베이스**

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| Algorithm 함수 import 실패 | `src/lib/algorithms/` 디렉토리 확인, 함수명 매핑표 작성 후 수정 |
| 연산 중 메모리 부족 | 배치 크기 축소 (1,000 → 100), 중간 결과를 DB에 저장 후 이어서 처리 |
| 파생 데이터 품질 < 80% | Algorithm Engineer에게 알고리즘 정확도 재검증 요청 |

## ✅ 완료 체크리스트

- [ ] 알고리즘 데이터 요구사항 분석 완료
- [ ] 스키마 확장 완료 (필요 시)
- [ ] 알고리즘 실행 스크립트 작성
- [ ] 모든 데이터에 대해 알고리즘 실행 완료
- [ ] 데이터 검증 완료
- [ ] NULL 값 없음
- [ ] 값 범위 정상
- [ ] 보고서 생성 완료
- [ ] Git 커밋:
  ```bash
  git add prisma/ scripts/enrichment/ docs/reports/
  git commit -m "feat: 알고리즘 생성 데이터 및 메타데이터 (Phase 3)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-2/10-qa-lead.md를 읽고 QLA로 작동해주세요 (Phase 3 품질 검증)"
```

