# Data Engineer Agent (DEN) - Phase 1

> **역할**: 데이터 소스 식별, 데이터 다운로드 스크립트 작성, 초기 데이터 로딩
> **소요**: 1-2시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: `docs/personas/[domain]-expert.md`
- ✅ **필수**: `prisma/schema.prisma` (Backend Developer가 먼저 작성)

---

## 🔨 작업 Step-by-Step

### Step 1: 데이터 소스 검토 및 우선순위 결정 (15분)

Domain Expert 문서에서 추천된 데이터 소스를 검토하고 우선순위를 정하세요.

**우선순위 기준**:

| 순위 | 타입 | 설명 | 예시 |
|------|------|------|------|
| **1차** | Primary | 핵심 엔티티 데이터, P0 기능에 필수 | Unihan (한자 기본 정보) |
| **2차** | Enrichment | 보조 데이터, 데이터 품질 향상 | CC-CEDICT (중국어 의미) |
| **3차** | Computed | 알고리즘으로 생성 가능한 데이터 | 유사도 점수, 추천 점수 |

**작업**:
1. Domain Expert 문서의 "데이터 소스" 섹션 읽기
2. PRD의 P0 기능에 필수적인 데이터 식별
3. 각 소스를 1차/2차/3차로 분류

**TriHanzi 예시**:
- **1차**: Unihan Database (한자 기본 정보, 10,000자)
- **2차**: CC-CEDICT (중국어 의미), KANJIDIC2 (일본어 읽기)
- **3차**: 발음 유사도, False Friends (알고리즘으로 계산)

**체크리스트**:
- [ ] 최소 1개의 1차 데이터 소스 식별
- [ ] 각 소스의 형식 확인 (JSON, CSV, XML, API 등)
- [ ] 각 소스의 라이선스 확인 (상업적 사용 가능 여부)

---

### Step 2: 데이터 다운로드 스크립트 작성 (20분)

외부 데이터 소스를 다운로드하는 스크립트를 작성하세요.

**파일 위치**: `scripts/download-data.sh`

**템플릿**:

```bash
#!/bin/bash

# 데이터 다운로드 스크립트
# 실행: ./scripts/download-data.sh

set -e  # 에러 발생 시 중단

# 데이터 디렉토리 생성
mkdir -p data/raw

echo "📥 데이터 소스 다운로드 시작..."

# 1차 데이터 소스
echo "1️⃣  [Primary Source] 다운로드 중..."
curl -o data/raw/primary-data.txt "https://example.com/data.txt"

# 2차 데이터 소스
echo "2️⃣  [Secondary Source] 다운로드 중..."
wget -P data/raw/ "https://example.com/secondary.zip"
unzip -q data/raw/secondary.zip -d data/raw/

echo "✅ 모든 데이터 다운로드 완료!"
echo ""
echo "📊 다운로드된 파일:"
ls -lh data/raw/
```

**TriHanzi 실제 스크립트** (`scripts/download-data.sh`):

```bash
#!/bin/bash
set -e

mkdir -p data/raw

echo "📥 Downloading CJK Character Data Sources..."

# Unihan Database
echo "1️⃣  Unihan Database (Unicode.org)..."
curl -o data/raw/Unihan.zip "https://www.unicode.org/Public/UNIDATA/Unihan.zip"
unzip -q data/raw/Unihan.zip -d data/raw/unihan/

# CC-CEDICT
echo "2️⃣  CC-CEDICT (Chinese-English Dictionary)..."
curl -o data/raw/cedict_1_0_ts_utf-8_mdbg.txt.gz \
  "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"
gunzip data/raw/cedict_1_0_ts_utf-8_mdbg.txt.gz

# KANJIDIC2
echo "3️⃣  KANJIDIC2 (Japanese Kanji Dictionary)..."
curl -o data/raw/kanjidic2.xml.gz \
  "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz"
gunzip data/raw/kanjidic2.xml.gz

echo "✅ All data sources downloaded!"
ls -lh data/raw/
```

**체크리스트**:
- [ ] `scripts/download-data.sh` 파일 생성
- [ ] 실행 권한 부여: `chmod +x scripts/download-data.sh`
- [ ] 스크립트 실행 성공 확인
- [ ] `data/raw/` 디렉토리에 파일 존재 확인

---

### Step 3: 초기 데이터 로딩 스크립트 작성 (30-45분)

다운로드한 데이터를 파싱하여 데이터베이스에 로드하는 스크립트를 작성하세요.

**파일 위치**: `scripts/migration/process-[source-name].ts`

**설계 원칙**:
1. **한 소스당 한 스크립트**: 유지보수 용이
2. **Idempotent**: 여러 번 실행해도 안전 (중복 삽입 방지)
3. **진행 상황 로깅**: 처리된 레코드 수 출력
4. **에러 핸들링**: 파싱 실패 시에도 계속 진행, 에러 로그 출력

**템플릿**:

```typescript
import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';

const prisma = new PrismaClient();

async function processPrimaryData() {
  console.log('📥 Processing Primary Data...');

  const rawData = fs.readFileSync('data/raw/primary-data.txt', 'utf-8');
  const lines = rawData.split('\n');

  let processed = 0;
  let errors = 0;

  for (const line of lines) {
    if (!line.trim() || line.startsWith('#')) continue;  // 빈 줄, 주석 건너뛰기

    try {
      // 데이터 파싱
      const [field1, field2, field3] = line.split('\t');

      // 데이터베이스에 삽입 (upsert로 중복 방지)
      await prisma.mainEntity.upsert({
        where: { id: field1 },
        update: { field2, field3 },
        create: { id: field1, field2, field3 },
      });

      processed++;
      if (processed % 100 === 0) {
        console.log(`  ✓ Processed ${processed} records...`);
      }
    } catch (error) {
      console.error(`  ✗ Error processing line: ${line}`);
      errors++;
    }
  }

  console.log(`✅ Completed: ${processed} records processed, ${errors} errors`);
}

async function main() {
  try {
    await processPrimaryData();
  } finally {
    await prisma.$disconnect();
  }
}

main();
```

**TriHanzi 실제 예시** (`scripts/migration/process-unihan.ts`, 348줄):

```typescript
import { PrismaClient, Country } from '@prisma/client';
import * as fs from 'fs';

const prisma = new PrismaClient();

async function processUnihan() {
  console.log('📥 Processing Unihan Database...');

  // Unihan_Readings.txt 파싱
  const readingsFile = 'data/raw/unihan/Unihan_Readings.txt';
  const content = fs.readFileSync(readingsFile, 'utf-8');
  const lines = content.split('\n');

  const characters = new Map<string, any>();

  for (const line of lines) {
    if (!line.trim() || line.startsWith('#')) continue;

    const [code, field, value] = line.split('\t');
    const char = String.fromCodePoint(parseInt(code.slice(2), 16));

    if (!characters.has(char)) {
      characters.set(char, { character: char });
    }

    const charData = characters.get(char)!;

    // kMandarin: 중국어 Pinyin
    if (field === 'kMandarin') {
      charData.mandarin = value.toLowerCase();
    }
    // kHangul: 한국어 발음
    else if (field === 'kHangul') {
      charData.hangul = value.split(':')[0];
    }
    // kJapaneseKun: 일본어 훈독
    else if (field === 'kJapaneseKun') {
      charData.kun = value.split(' ')[0];
    }
    // kJapaneseOn: 일본어 음독
    else if (field === 'kJapaneseOn') {
      charData.on = value.split(' ')[0];
    }
  }

  console.log(`  Found ${characters.size} characters`);

  // 데이터베이스에 삽입
  let inserted = 0;
  for (const [char, data] of characters) {
    await prisma.character.upsert({
      where: { character: char },
      update: {},
      create: { character: char },
    });

    // 발음 데이터 삽입
    if (data.mandarin) {
      await prisma.pronunciation.upsert({
        where: {
          character_country_type: {
            character: char,
            country: Country.CHINA,
            type: 'MANDARIN',
          },
        },
        update: { value: data.mandarin },
        create: {
          character: char,
          country: Country.CHINA,
          type: 'MANDARIN',
          value: data.mandarin,
        },
      });
    }

    // [한국어, 일본어 발음도 동일하게 처리...]

    inserted++;
    if (inserted % 1000 === 0) {
      console.log(`  ✓ Processed ${inserted} characters...`);
    }
  }

  console.log(`✅ Inserted ${inserted} characters from Unihan`);
}

async function main() {
  try {
    await processUnihan();
  } finally {
    await prisma.$disconnect();
  }
}

main();
```

**체크리스트**:
- [ ] 각 1차 데이터 소스에 대해 `process-[name].ts` 스크립트 작성
- [ ] 스크립트 실행: `tsx scripts/migration/process-[name].ts`
- [ ] 데이터베이스에 레코드 삽입 확인: `npx prisma studio`
- [ ] 예상 레코드 수와 실제 삽입 수 비교 (차이가 10% 이내여야 함)

---

### Step 4: Data Source Registry 문서화 (10분)

모든 데이터 소스를 문서화하세요.

**파일 위치**: `scripts/README.md`

**템플릿**:

```markdown
# Data Pipeline Scripts

이 디렉토리는 프로젝트의 모든 데이터 파이프라인 스크립트를 포함합니다.

---

## 📁 디렉토리 구조

```
scripts/
├── download-data.sh           # 외부 소스에서 원시 데이터 다운로드
├── migration/                 # 초기 데이터 로드 및 스키마 마이그레이션
│   ├── process-[source1].ts
│   ├── process-[source2].ts
│   └── ...
├── enrichment/                # 데이터 보강 (Phase 2+)
└── validation/                # 데이터 품질 검증 (Phase 5+)
```

---

## 🚀 실행 순서

### Phase 1: 초기 데이터 로딩

```bash
# 1. 데이터 다운로드
./scripts/download-data.sh

# 2. 데이터베이스 스키마 적용
npx prisma db push

# 3. 1차 데이터 로드
tsx scripts/migration/process-[source1].ts
tsx scripts/migration/process-[source2].ts
```

---

## 📊 데이터 소스

### 1. [Source 1 Name]

- **URL**: [다운로드 링크]
- **형식**: [JSON / CSV / XML / API]
- **라이선스**: [CC BY-SA 4.0 / MIT / Public Domain]
- **커버리지**: [X개 레코드]
- **품질**: ★★★★★ (5점 만점)
- **스크립트**: `process-[source1].ts`
- **예상 레코드**: ~X,XXX개
- **처리 시간**: ~X분

### 2. [Source 2 Name]
[...]

---

## 📈 데이터 통계

초기 로딩 후 예상 데이터:
- **[Entity 1]**: X,XXX개
- **[Entity 2]**: XX,XXX개
- **[Entity 3]**: XXX,XXX개
```

**체크리스트**:
- [ ] `scripts/README.md` 파일 생성
- [ ] 모든 데이터 소스 문서화 (URL, 라이선스, 커버리지)
- [ ] 실행 순서 명확히 기재
- [ ] 예상 데이터 통계 기재

---

## 📤 출력 파일

1. **`scripts/download-data.sh`**: 데이터 다운로드 스크립트
2. **`scripts/migration/process-[source].ts`**: 각 데이터 소스별 로딩 스크립트 (1-3개)
3. **`scripts/README.md`**: 데이터 소스 및 스크립트 문서
4. **`data/raw/`**: 다운로드된 원시 데이터 파일들

---

## ✅ 완료 체크리스트

- [ ] 데이터 다운로드 스크립트 작성 및 실행 성공
- [ ] `data/raw/` 디렉토리에 모든 원시 데이터 존재
- [ ] 각 1차 데이터 소스에 대해 `process-*.ts` 스크립트 작성
- [ ] 모든 로딩 스크립트 실행 성공
- [ ] `npx prisma studio`에서 데이터 확인
- [ ] `scripts/README.md` 문서 작성
- [ ] 예상 레코드 수의 80% 이상 로드 성공
- [ ] Git 커밋:
  ```bash
  git add scripts/ data/
  git commit -m "feat: 초기 데이터 파이프라인 및 1차 데이터 로딩 (Phase 1)"
  ```

**⚠️ 주의**: `data/raw/` 디렉토리는 크기가 클 수 있으므로 `.gitignore`에 추가:
```
data/raw/
```

---

## 🎬 다음 단계

Data Engineer Phase 1 작업을 완료했다면:

```
"agent-system/agents/phase-1/06-devops-engineer.md를 읽고 DOE로 작동해주세요"
```

(참고: Backend Developer는 Phase 1에서 두 번 등장 - 먼저 스키마 작성, 나중에 데이터 검증)

---

## 💡 TriHanzi 실제 데이터 파이프라인

**다운로드 스크립트**: `scripts/download-data.sh` (24줄)
- Unihan.zip (97,680자)
- CC-CEDICT.txt.gz (124,259항목)
- KANJIDIC2.xml.gz (13,108자)

**로딩 스크립트** (14개, Phase 1-2):
1. `process-unihan.ts` (348줄): 10,000자 로드
2. `process-cedict.ts` (289줄): 중국어 의미 26,832개
3. `process-kanjidic2.ts` (412줄): 일본어 읽기 13,108개
4. [Phase 2에서 11개 추가 스크립트...]

**결과 데이터**:
- Characters: 10,000개
- Pronunciations: 40,868개 (3개국 x 여러 타입)
- Meanings: 26,832개
- 처리 시간: 전체 ~15분

**Data Source Registry**: `scripts/README.md` (333줄)
- 5개 카테고리별 스크립트 분류
- 각 스크립트의 목적, 입출력, 실행 시간 명시
- 명확한 실행 순서 기재
