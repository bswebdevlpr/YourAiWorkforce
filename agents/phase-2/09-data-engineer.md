# Data Engineer Agent (DEN) - Phase 2

> **역할**: 데이터 보강, 품질 개선, 파생 데이터 생성
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/personas/[domain]-expert.md`
- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: 데이터베이스 — Phase 1 Data Engineer가 로드한 1차 데이터. 스키마는 `prisma/schema.prisma` 참조.
- ✅ **필수**: `scripts/migration/` (Phase 1 스크립트)

---

## 🔨 작업 Step-by-Step

### Step 1: 데이터 품질 분석 (15분)

현재 데이터의 완전성과 품질을 평가하세요.

**품질 검증 스크립트**:

```typescript
// scripts/reporting/data-quality-report.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function generateQualityReport() {
  console.log('📊 Data Quality Report');
  console.log('='.repeat(50));

  // 1. 총 레코드 수
  const totalRecords = await prisma.resource.count();
  console.log(`\n총 레코드: ${totalRecords}개`);

  // 2. NULL 필드 분석
  const missingData = await prisma.resource.count({
    where: {
      OR: [
        { title: null },
        { description: null },
      ],
    },
  });
  console.log(`\n데이터 누락: ${missingData}개 (${(missingData / totalRecords * 100).toFixed(2)}%)`);

  // 3. 관계 데이터 커버리지
  const withRelations = await prisma.resource.count({
    where: {
      relatedData: {
        some: {},
      },
    },
  });
  console.log(`\n관계 데이터 커버리지: ${withRelations}/${totalRecords} (${(withRelations / totalRecords * 100).toFixed(2)}%)`);

  // 4. 중복 데이터 검출
  const duplicates = await prisma.$queryRaw`
    SELECT title, COUNT(*) as count
    FROM "Resource"
    GROUP BY title
    HAVING COUNT(*) > 1
  `;
  console.log(`\n중복 레코드: ${(duplicates as any[]).length}개`);
}

generateQualityReport()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
  });
```

**체크리스트**:
- [ ] 총 레코드 수 확인
- [ ] NULL 필드 비율 계산 (< 5% 목표)
- [ ] 관계 데이터 커버리지 확인
- [ ] 중복 데이터 검출

---

### Step 2: 2차 데이터 소스 통합 (30-45분)

Domain Expert가 추천한 2차 데이터 소스를 통합하여 데이터를 보강하세요.

**보강 스크립트 템플릿**:

```typescript
// scripts/enrichment/enrich-from-source2.ts
import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';

const prisma = new PrismaClient();

async function enrichFromSource2() {
  console.log('🔄 데이터 보강: Source 2');

  // 2차 소스 읽기
  // 2차 데이터 소스의 위치와 포맷은 Domain Expert 문서(`docs/personas/[domain]-expert.md`)의 "데이터 소스" 섹션에 정의되어 있다. 해당 섹션을 참조하여 경로를 결정한다.
  const rawData = fs.readFileSync('data/raw/source2.json', 'utf-8');
  const source2Data = JSON.parse(rawData);

  let enriched = 0;
  let notFound = 0;

  for (const item of source2Data) {
    try {
      // 기존 레코드 찾기
      const existing = await prisma.resource.findUnique({
        where: { id: item.id },
      });

      if (existing) {
        // 보강 데이터 업데이트
        await prisma.resource.update({
          where: { id: item.id },
          data: {
            additionalField1: item.field1,
            additionalField2: item.field2,
            // 관계 데이터 추가
            relatedData: {
              create: {
                type: item.type,
                value: item.value,
              },
            },
          },
        });

        enriched++;
      } else {
        notFound++;
      }

      if (enriched % 100 === 0) {
        console.log(`  ✓ ${enriched} 레코드 보강...`);
      }
    } catch (error) {
      console.error(`  ✗ 오류: ${item.id}`, error);
    }
  }

  console.log(`\n✅ 완료: ${enriched} 보강, ${notFound} 미발견`);
}

enrichFromSource2()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
  });
```

**체크리스트**:
- [ ] 2차 소스 다운로드
- [ ] 보강 스크립트 작성
- [ ] 스크립트 실행 및 로그 확인
- [ ] 보강 전후 데이터 비교

---

### Step 3: 파생 데이터 생성 (30-45분)

알고리즘 또는 계산을 통해 파생 데이터를 생성하세요.

**예시 1: 통계 데이터 생성**:

```typescript
// scripts/enrichment/compute-statistics.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function computeStatistics() {
  console.log('📈 통계 데이터 생성');

  const resources = await prisma.resource.findMany({
    include: { relatedData: true },
  });

  for (const resource of resources) {
    const stats = {
      relatedCount: resource.relatedData.length,
      // 추가 통계 계산
      averageValue: resource.relatedData.reduce((sum, r) => sum + r.value, 0) / resource.relatedData.length,
    };

    await prisma.resource.update({
      where: { id: resource.id },
      data: {
        statistics: stats,
      },
    });
  }

  console.log(`✅ ${resources.length}개 레코드 통계 생성`);
}

computeStatistics()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
  });
```

**예시 2: 검색 인덱스 생성**:

```typescript
// scripts/enrichment/create-search-index.ts
async function createSearchIndex() {
  // 검색을 위한 정규화된 텍스트 생성
  const resources = await prisma.resource.findMany();

  for (const resource of resources) {
    const searchText = [
      resource.title,
      resource.description,
      // 추가 검색 가능 필드
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();

    await prisma.resource.update({
      where: { id: resource.id },
      data: { searchText },
    });
  }

  console.log('✅ 검색 인덱스 생성 완료');
}
```

**체크리스트**:
- [ ] 통계 데이터 생성 (카운트, 평균 등)
- [ ] 검색 인덱스 생성
- [ ] 파생 관계 데이터 생성

---

### Step 4: 데이터 검증 및 정리 (20분)

**중복 제거**:

```typescript
// scripts/enrichment/remove-duplicates.ts
async function removeDuplicates() {
  console.log('🧹 중복 데이터 제거');

  // 중복 찾기
  const duplicates = await prisma.$queryRaw`
    SELECT title, array_agg(id) as ids
    FROM "Resource"
    GROUP BY title
    HAVING COUNT(*) > 1
  `;

  let removed = 0;

  for (const dup of duplicates as any[]) {
    // 첫 번째 ID만 유지, 나머지 삭제
    const [keep, ...remove] = dup.ids;

    for (const id of remove) {
      await prisma.resource.delete({ where: { id } });
      removed++;
    }
  }

  console.log(`✅ ${removed}개 중복 레코드 제거`);
}
```

**데이터 정규화**:

```typescript
// scripts/enrichment/normalize-data.ts
async function normalizeData() {
  console.log('📐 데이터 정규화');

  const resources = await prisma.resource.findMany();

  for (const resource of resources) {
    await prisma.resource.update({
      where: { id: resource.id },
      data: {
        // 제목 정규화 (trim, lowercase)
        title: resource.title.trim(),
        // 날짜 형식 통일
        // 단위 통일
      },
    });
  }

  console.log(`✅ ${resources.length}개 레코드 정규화`);
}
```

**체크리스트**:
- [ ] 중복 데이터 제거
- [ ] 데이터 정규화 (trim, lowercase, 형식 통일)
- [ ] 유효하지 않은 데이터 삭제

---

### Step 5: 최종 품질 보고서 생성 (10분)

```typescript
// scripts/reporting/final-quality-report.ts
async function finalQualityReport() {
  console.log('\n📊 최종 데이터 품질 보고서');
  console.log('='.repeat(50));

  const total = await prisma.resource.count();

  // 완전성
  const complete = await prisma.resource.count({
    where: {
      AND: [
        { title: { not: null } },
        { description: { not: null } },
        // 필수 필드 체크
      ],
    },
  });

  // 커버리지
  const withRelations = await prisma.resource.count({
    where: {
      relatedData: { some: {} },
    },
  });

  console.log(`\n총 레코드: ${total}개`);
  console.log(`완전성: ${complete}/${total} (${(complete / total * 100).toFixed(2)}%)`);
  console.log(`관계 커버리지: ${withRelations}/${total} (${(withRelations / total * 100).toFixed(2)}%)`);

  // 목표 달성 여부
  const completeness = (complete / total) * 100;
  const coverage = (withRelations / total) * 100;

  if (completeness >= 95 && coverage >= 80) {
    console.log('\n✅ 품질 목표 달성!');
  } else {
    console.log('\n⚠️  품질 목표 미달성');
    if (completeness < 95) console.log(`   - 완전성: ${completeness.toFixed(2)}% < 95%`);
    if (coverage < 80) console.log(`   - 커버리지: ${coverage.toFixed(2)}% < 80%`);
  }

  // 보고서 파일로 저장
  const report = {
    date: new Date().toISOString(),
    total,
    completeness: `${completeness.toFixed(2)}%`,
    coverage: `${coverage.toFixed(2)}%`,
    passed: completeness >= 95 && coverage >= 80,
  };

  fs.writeFileSync(
    'docs/reports/data-quality-report.json',
    JSON.stringify(report, null, 2)
  );

  console.log('\n📄 보고서 저장: docs/reports/data-quality-report.json');
}
```

---

## 📤 출력 파일

1. **보강 스크립트**:
   - `scripts/enrichment/enrich-from-source2.ts`
   - `scripts/enrichment/compute-statistics.ts`
   - `scripts/enrichment/create-search-index.ts`
   - `scripts/enrichment/normalize-data.ts`
   - `scripts/enrichment/remove-duplicates.ts`

2. **보고서**:
   - `docs/reports/data-quality-report.json`

3. **업데이트된 데이터베이스**

---

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| 보강 성공률 < 50% | 보강 중단, 2차 소스 품질 확인. Domain Expert에게 대체 소스 요청 |
| 보강 스크립트 중간 실패 | `upsert` 사용으로 재실행 안전. 오류 레코드만 `data/errors/`에 분리 |
| 보강 후 기존 데이터 품질 저하 | 보강 전 스냅샷과 비교, 저하 항목은 롤백 |

## ✅ 완료 체크리스트

- [ ] 데이터 품질 초기 분석 완료
- [ ] 2차 소스 통합 (보강률 > 50%)
- [ ] 파생 데이터 생성 (통계, 인덱스)
- [ ] 중복 데이터 제거
- [ ] 데이터 정규화
- [ ] 최종 품질 보고서 생성
- [ ] 품질 목표 달성:
  - 완전성 > 95%
  - 관계 커버리지 > 80%
- [ ] Git 커밋:
  ```bash
  git add scripts/enrichment/ docs/reports/
  git commit -m "feat: 데이터 보강 및 품질 개선 (Phase 2)"
  ```

---

## 🎬 다음 단계

```
"agent-system/agents/phase-2/10-qa-lead.md를 읽고 QLA로 작동해주세요"
```

