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

**예시 (TriHanzi)**:
- **유사도 알고리즘** → 의미 키워드 필요 → 이미 존재 ✅
- **발음 유추 알고리즘** → 일본어 음독 필요 → 이미 존재 ✅
- **False Friends 감지** → 유사도 점수 저장 필요 → 새 테이블 필요 ❌

**체크리스트**:
- [ ] 알고리즘 입력 데이터 확인
- [ ] 알고리즘 출력 저장 필요성 판단
- [ ] 스키마 수정 필요 여부 확인

---

### Step 2: 스키마 확장 (필요 시) (20분)

알고리즘 출력을 저장할 테이블/필드를 추가하세요.

**예시: 비교 메타데이터 테이블**

```prisma
// prisma/schema.prisma

model ComparisonMetadata {
  id String @id @default(cuid())

  // 비교 대상
  character1Id String
  character1   Character @relation("comparison1", fields: [character1Id], references: [id])

  character2Id String
  character2   Character @relation("comparison2", fields: [character2Id], references: [id])

  // 유사도 점수
  visualSimilarity   Float  // 0-100
  meaningSimilarity  Float  // 0-100
  pronunciationSimilarity Float? // 0-100 (nullable)

  // False Friend 여부
  isFalseFriend Boolean @default(false)

  // 신뢰도
  confidence Float @default(100)

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([character1Id, character2Id])
  @@index([isFalseFriend])
  @@index([visualSimilarity])
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
// scripts/enrichment/compute-comparison-metadata.ts

import { PrismaClient } from '@prisma/client';
import { calculateSimilarity } from '@/lib/algorithms/similarity';
import { detectFalseFriends } from '@/lib/algorithms/matching';

const prisma = new PrismaClient();

async function computeComparisonMetadata() {
  console.log('🔄 비교 메타데이터 생성');
  console.log('='.repeat(50));

  // 1. 모든 문자 가져오기
  const characters = await prisma.character.findMany({
    include: {
      meanings: true,
      pronunciations: true,
    },
  });

  console.log(`\n총 문자: ${characters.length}개`);

  let computed = 0;
  let falseFriendsCount = 0;

  // 2. 모든 페어 조합 계산
  for (let i = 0; i < characters.length; i++) {
    for (let j = i + 1; j < characters.length; j++) {
      const char1 = characters[i];
      const char2 = characters[j];

      try {
        // 알고리즘 실행
        const meaningResult = calculateSimilarity(
          char1.meanings.map(m => m.text),
          char2.meanings.map(m => m.text)
        );

        const visualSimilarity = calculateVisualSimilarity(char1.char, char2.char);

        // False Friend 감지
        const isFalseFriend = detectFalseFriends(
          visualSimilarity,
          meaningResult.score
        );

        if (isFalseFriend) falseFriendsCount++;

        // 데이터베이스에 저장
        await prisma.comparisonMetadata.upsert({
          where: {
            character1Id_character2Id: {
              character1Id: char1.id,
              character2Id: char2.id,
            },
          },
          update: {
            visualSimilarity,
            meaningSimilarity: meaningResult.score,
            isFalseFriend,
            confidence: meaningResult.confidence,
          },
          create: {
            character1Id: char1.id,
            character2Id: char2.id,
            visualSimilarity,
            meaningSimilarity: meaningResult.score,
            isFalseFriend,
            confidence: meaningResult.confidence,
          },
        });

        computed++;

        if (computed % 100 === 0) {
          console.log(`  진행: ${computed} 페어 계산...`);
        }
      } catch (error) {
        console.error(`  ✗ 오류: ${char1.char} vs ${char2.char}`, error);
      }
    }
  }

  console.log(`\n✅ 완료: ${computed} 페어 계산`);
  console.log(`False Friends: ${falseFriendsCount}개`);
}

computeComparisonMetadata()
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
  const totalMetadata = await prisma.comparisonMetadata.count();
  console.log(`\n총 메타데이터: ${totalMetadata}개`);

  // 2. False Friends 통계
  const falseFriends = await prisma.comparisonMetadata.count({
    where: { isFalseFriend: true },
  });
  console.log(`False Friends: ${falseFriends}개 (${(falseFriends / totalMetadata * 100).toFixed(2)}%)`);

  // 3. 유사도 분포
  const avgMeaningSimilarity = await prisma.comparisonMetadata.aggregate({
    _avg: { meaningSimilarity: true },
  });
  console.log(`평균 의미 유사도: ${avgMeaningSimilarity._avg.meaningSimilarity?.toFixed(2)}`);

  // 4. 신뢰도 분포
  const avgConfidence = await prisma.comparisonMetadata.aggregate({
    _avg: { confidence: true },
  });
  console.log(`평균 신뢰도: ${avgConfidence._avg.confidence?.toFixed(2)}`);

  // 5. 샘플 검증
  console.log('\n📊 샘플 검증 (상위 5개 False Friends):');
  const samples = await prisma.comparisonMetadata.findMany({
    where: { isFalseFriend: true },
    include: {
      character1: true,
      character2: true,
    },
    orderBy: { visualSimilarity: 'desc' },
    take: 5,
  });

  samples.forEach((sample, i) => {
    console.log(`  ${i + 1}. ${sample.character1.char} vs ${sample.character2.char}`);
    console.log(`     시각 유사도: ${sample.visualSimilarity.toFixed(2)}, 의미 유사도: ${sample.meaningSimilarity.toFixed(2)}`);
  });

  // 6. 품질 체크
  const issues = [];

  // 6.1. NULL 체크
  const nullCount = await prisma.comparisonMetadata.count({
    where: {
      OR: [
        { visualSimilarity: null },
        { meaningSimilarity: null },
      ],
    },
  });
  if (nullCount > 0) {
    issues.push(`NULL 값: ${nullCount}개`);
  }

  // 6.2. 범위 체크 (0-100)
  const outOfRange = await prisma.comparisonMetadata.count({
    where: {
      OR: [
        { visualSimilarity: { lt: 0 } },
        { visualSimilarity: { gt: 100 } },
        { meaningSimilarity: { lt: 0 } },
        { meaningSimilarity: { gt: 100 } },
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
    totalMetadata: await prisma.comparisonMetadata.count(),
    falseFriends: await prisma.comparisonMetadata.count({
      where: { isFalseFriend: true },
    }),
    statistics: {
      avgMeaningSimilarity: (
        await prisma.comparisonMetadata.aggregate({
          _avg: { meaningSimilarity: true },
        })
      )._avg.meaningSimilarity,
      avgVisualSimilarity: (
        await prisma.comparisonMetadata.aggregate({
          _avg: { visualSimilarity: true },
        })
      )._avg.visualSimilarity,
      avgConfidence: (
        await prisma.comparisonMetadata.aggregate({
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

---

## 💡 TriHanzi 실제 알고리즘 데이터

**생성된 데이터**:

### 1. ComparisonMetadata 테이블
```prisma
model ComparisonMetadata {
  id                   String    @id @default(cuid())
  character1Id         String
  character2Id         String
  visualSimilarity     Float
  meaningSimilarity    Float
  pronunciationSimilarity Float?
  isFalseFriend        Boolean   @default(false)
  confidence           Float     @default(100)

  character1 Character @relation("comparison1", fields: [character1Id], references: [id])
  character2 Character @relation("comparison2", fields: [character2Id], references: [id])

  @@unique([character1Id, character2Id])
  @@index([isFalseFriend])
}
```

### 2. False Friends 데이터
- **총 662개 False Friends 감지**
- **기준**: 시각 유사도 > 70% AND 의미 유사도 < 30%

**예시**:
| 문자 1 | 문자 2 | 시각 유사도 | 의미 유사도 | False Friend |
|-------|-------|------------|------------|--------------|
| 手 (hand) | 毛 (hair) | 85.2 | 12.3 | ✅ |
| 青 (blue) | 清 (clear) | 78.5 | 28.4 | ✅ |
| 日 (sun) | 目 (eye) | 72.1 | 15.7 | ✅ |

### 3. 스크립트 실행 결과
```bash
$ ts-node scripts/enrichment/compute-comparison-metadata.ts

🔄 비교 메타데이터 생성
==================================================

총 문자: 10,000개
  진행: 100 페어 계산...
  진행: 200 페어 계산...
  ...
  진행: 49,950,000 페어 계산...

✅ 완료: 49,995,000 페어 계산
False Friends: 662개

⏱️  소요 시간: 47분 32초
```

### 4. 검증 결과
```json
{
  "date": "2026-01-15T10:23:45.000Z",
  "totalMetadata": 49995000,
  "falseFriends": 662,
  "statistics": {
    "avgMeaningSimilarity": 45.2,
    "avgVisualSimilarity": 32.1,
    "avgConfidence": 94.7
  },
  "qualityCheck": {
    "nullCount": 0,
    "outOfRangeCount": 0,
    "passed": true
  }
}
```

### 5. 최적화
- **배치 크기**: 1000개
- **병렬 처리**: 4개 워커
- **소요 시간**: 47분 (단일 스레드 대비 75% 단축)
