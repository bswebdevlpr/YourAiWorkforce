# Backend Developer Agent (BDA) - Phase 1

> **역할**: 데이터베이스 스키마 설계, 기본 API 엔드포인트 구현
> **소요**: 1.5-2시간
> **난이도**: ⭐⭐⭐⭐☆

## 📥 입력 파일

- ✅ **필수**: `docs/specs/prd.md`
- ✅ **필수**: `docs/specs/architecture.md`
- ✅ **필수**: `docs/personas/[domain]-expert.md`

---

## 🔨 작업 Step-by-Step

### Step 1: 데이터베이스 스키마 설계 (30-45분)

PRD와 Domain Expert 문서를 읽고 Prisma 스키마를 설계하세요.

#### 1.1 핵심 엔티티 추출

PRD의 P0 기능에서 핵심 **명사(엔티티)**를 식별하세요:

**예시 (TriHanzi)**:
- P0 기능: "한자 정보 표시", "검색", "3개국 발음"
- 엔티티: **Character** (한자), **Pronunciation** (발음), **Meaning** (의미)

**예시 (음식 추천)**:
- P0 기능: "음식 검색", "영양 정보 표시", "추천"
- 엔티티: **Food**, **Ingredient**, **NutritionInfo**, **UserPreference**

#### 1.2 관계 모델링

엔티티 간 관계를 정의하세요:

| 관계 타입 | Prisma 문법 | 예시 |
|---------|-----------|------|
| **1:N** | `model A { bs B[] }`<br>`model B { a A @relation(fields: [aId], references: [id]) }` | Character → Pronunciation[] |
| **M:N** | `model A { bs B[] }`<br>`model B { as A[] }` | Recipe ←→ Ingredient (재료 여러 개, 재료도 여러 레시피에 사용) |
| **1:1** | `model A { b B? }`<br>`model B { a A @relation(fields: [aId], references: [id]) }` | User ←→ Profile |

**TriHanzi 관계**:
```
Character (1) ←→ (N) Pronunciation
Character (1) ←→ (N) Meaning
Character (1) ←→ (N) Variant
Character (1) ←→ (1) ComparisonMetadata (optional)
```

#### 1.3 Enum 타입 정의

범주형 데이터는 Enum으로 정의하세요:

**TriHanzi 예시**:
```prisma
enum Country {
  CHINA
  JAPAN
  KOREA
}

enum PronunciationType {
  MANDARIN      // 중국어 표준어
  CANTONESE     // 광동어
  KUN           // 일본어 훈독
  ON            // 일본어 음독
  HANGUL        // 한국어 한자음
}
```

**음식 추천 예시**:
```prisma
enum DietaryRestriction {
  VEGAN
  VEGETARIAN
  GLUTEN_FREE
  DAIRY_FREE
  HALAL
  KOSHER
}

enum AllergenType {
  PEANUTS
  TREE_NUTS
  MILK
  EGGS
  FISH
  SHELLFISH
  SOY
  WHEAT
}
```

#### 1.4 Prisma 스키마 작성

**파일 위치**: `prisma/schema.prisma`

**템플릿**:

```prisma
// This is your Prisma schema file
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"  // 또는 mysql, sqlite
  url      = env("DATABASE_URL")
}

// Enum 정의
enum Country {
  CHINA
  JAPAN
  KOREA
}

// 핵심 엔티티 모델
model Character {
  id        String   @id @default(cuid())
  character String   @unique  // 실제 한자 (예: "愛")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // 관계
  pronunciations Pronunciation[]
  meanings       Meaning[]

  // 인덱스
  @@index([character])
}

model Pronunciation {
  id        String            @id @default(cuid())
  character String
  country   Country
  type      PronunciationType
  value     String            // 실제 발음 (예: "ài", "あい", "애")

  // 관계
  char Character @relation(fields: [character], references: [character], onDelete: Cascade)

  // 복합 유니크 제약: 동일 문자+국가+타입 조합 중복 방지
  @@unique([character, country, type])
  @@index([character])
  @@index([country])
}

model Meaning {
  id        String @id @default(cuid())
  character String
  language  String  // "en", "zh", "ja", "ko"
  value     String @db.Text  // 의미가 길 수 있음

  char Character @relation(fields: [character], references: [character], onDelete: Cascade)

  @@index([character])
  @@index([language])
}
```

**TriHanzi 실제 스키마** (`prisma/schema.prisma`, 148줄):
- 6개 주요 모델: Character, Pronunciation, Meaning, Variant, ComparisonMetadata, FalseFriendDetail
- 2개 독립 모델: KoreanUsage, JapaneseKokuji
- 4개 Enum: Country, PronunciationType, Language, VariantType
- 15개 인덱스 (쿼리 최적화)

**체크리스트**:
- [ ] 모든 P0 엔티티 모델 정의
- [ ] 관계 명확히 정의 (1:N, M:N)
- [ ] Enum 타입 정의
- [ ] 인덱스 추가 (검색 대상 필드)
- [ ] `@@unique` 제약 추가 (중복 방지)

---

### Step 2: 데이터베이스 마이그레이션 (5분)

스키마를 데이터베이스에 적용하세요.

**명령어**:

```bash
# 환경 변수 설정
echo "DATABASE_URL=postgresql://user:password@localhost:5432/dbname" > .env

# 스키마 푸시 (개발 환경)
npx prisma db push

# Prisma Client 생성
npx prisma generate

# 데이터베이스 확인
npx prisma studio
```

**체크리스트**:
- [ ] `.env` 파일에 `DATABASE_URL` 설정
- [ ] `npx prisma db push` 성공
- [ ] Prisma Studio에서 모든 테이블 확인
- [ ] `.env`를 `.gitignore`에 추가 (⚠️ 시크릿 노출 방지)

---

### Step 3: 기본 API 엔드포인트 구현 (45-60분)

P0 기능에 필요한 최소한의 API를 구현하세요.

#### 3.1 API 설계

**REST 패턴**:

| 기능 | 메서드 | 경로 | 설명 |
|------|--------|------|------|
| 목록 조회 | GET | `/api/characters` | 페이지네이션된 목록 |
| 상세 조회 | GET | `/api/characters/[id]` | 특정 문자 상세 정보 |
| 검색 | GET | `/api/search?q=愛` | 쿼리 기반 검색 |
| 자동완성 | GET | `/api/characters/autocomplete?q=ai` | 검색 제안 |

#### 3.2 API 구현 (Next.js App Router 예시)

**파일 위치**: `src/app/api/characters/route.ts`

**템플릿**:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET /api/characters?page=1&limit=20
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const skip = (page - 1) * limit;

    // 데이터 조회
    const [characters, total] = await Promise.all([
      prisma.character.findMany({
        take: limit,
        skip,
        include: {
          pronunciations: true,
          meanings: true,
        },
        orderBy: { character: 'asc' },
      }),
      prisma.character.count(),
    ]);

    return NextResponse.json({
      data: characters,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

**파일 위치**: `src/app/api/characters/[id]/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET /api/characters/愛
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    const character = await prisma.character.findUnique({
      where: { character: id },
      include: {
        pronunciations: true,
        meanings: true,
      },
    });

    if (!character) {
      return NextResponse.json(
        { error: 'Character not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ data: character });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

**TriHanzi 실제 API 구조**:
```
src/app/api/
├── characters/
│   ├── route.ts                    # GET 목록
│   ├── [id]/
│   │   ├── route.ts                # GET 상세
│   │   ├── analysis/route.ts       # GET 분석 데이터
│   │   └── similar/route.ts        # GET 유사 문자
│   └── autocomplete/route.ts       # GET 자동완성
├── search/
│   ├── route.ts                    # GET 검색
│   └── suggestions/route.ts        # GET 검색 제안
├── compare/route.ts                # GET 비교
├── false-friends/route.ts          # GET False Friends
├── statistics/route.ts             # GET 통계
└── korean-usage/route.ts           # GET 한국 특화 사용법
```

**체크리스트**:
- [ ] `/api/characters` (목록) 구현
- [ ] `/api/characters/[id]` (상세) 구현
- [ ] `/api/search` (검색) 구현
- [ ] 모든 API가 JSON 응답 반환
- [ ] 에러 핸들링 구현 (404, 500)
- [ ] `http://localhost:3000/api/characters`에서 테스트 성공

---

### Step 4: 데이터 검증 (10분)

Data Engineer가 로드한 데이터를 API로 확인하세요.

**테스트 체크리스트**:

```bash
# 서버 실행
pnpm dev

# 테스트 쿼리 (curl 또는 브라우저)
curl http://localhost:3000/api/characters?limit=5
curl http://localhost:3000/api/characters/愛  # 실제 존재하는 문자로 테스트
```

**확인 사항**:
- [ ] API가 실제 데이터 반환 (빈 배열 ❌)
- [ ] `pronunciations`와 `meanings`가 포함됨
- [ ] 페이지네이션 작동 (`page=2` 테스트)
- [ ] 존재하지 않는 ID 요청 시 404 반환

---

## 📤 출력 파일

1. **`prisma/schema.prisma`**: 데이터베이스 스키마 (모든 모델, 관계, 인덱스)
2. **`src/app/api/characters/route.ts`**: 목록 API
3. **`src/app/api/characters/[id]/route.ts`**: 상세 API
4. **`src/app/api/search/route.ts`**: 검색 API (선택적, Phase 2로 연기 가능)
5. **`.env.example`**: 환경 변수 템플릿

**`.env.example` 내용**:

```bash
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# Optional (Phase 1+)
# REDIS_URL="redis://localhost:6379"
# UPSTASH_REDIS_REST_URL=""
# UPSTASH_REDIS_REST_TOKEN=""
```

---

## ✅ 완료 체크리스트

- [ ] Prisma 스키마 작성 완료 (모든 P0 엔티티 포함)
- [ ] `npx prisma db push` 성공
- [ ] 최소 2개 API 엔드포인트 구현 (목록, 상세)
- [ ] API가 실제 데이터 반환 확인
- [ ] `.env.example` 파일 생성
- [ ] TypeScript 에러 없음: `pnpm build`
- [ ] Git 커밋:
  ```bash
  git add prisma/ src/app/api/ .env.example
  git commit -m "feat: 데이터베이스 스키마 및 기본 API (Phase 1)"
  ```

---

## 🎬 다음 단계

Backend Developer Phase 1 작업을 완료했다면:

```
"agent-system/agents/phase-1/09-devops-engineer.md를 읽고 DOE로 작동해주세요"
```

DevOps Engineer가 빌드 시스템과 환경 구성을 설정합니다.

---

## 💡 TriHanzi 실제 스키마 & API

### Prisma 스키마 (`prisma/schema.prisma`, 148줄)

```prisma
model Character {
  character String @id  // "愛"
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  pronunciations      Pronunciation[]
  meanings            Meaning[]
  variants            Variant[]
  comparisonMetadata  ComparisonMetadata?
  falseFriendDetails  FalseFriendDetail[]

  @@index([character])
}

model Pronunciation {
  id                 String            @id @default(cuid())
  character          String
  country            Country
  type               PronunciationType
  value              String
  romanization       String?
  source             String?
  confidence         Int               @default(100)

  char Character @relation(fields: [character], references: [character], onDelete: Cascade)

  @@unique([character, country, type])
  @@index([character])
  @@index([country])
  @@index([type])
}

model Meaning {
  id        String   @id @default(cuid())
  character String
  language  Language
  value     String   @db.Text

  char Character @relation(fields: [character], references: [character], onDelete: Cascade)

  @@index([character])
  @@index([language])
}

enum Country {
  CHINA
  JAPAN
  KOREA
}

enum PronunciationType {
  MANDARIN
  CANTONESE
  KUN
  ON
  HANGUL
}
```

### API 엔드포인트 (8개 라우트 그룹)

1. `/api/characters` - 목록 (페이지네이션)
2. `/api/characters/[id]` - 상세 (모든 발음+의미)
3. `/api/characters/[id]/analysis` - 분석 (유사도, 변형)
4. `/api/characters/autocomplete` - 자동완성
5. `/api/search` - 전체 검색
6. `/api/compare` - 문자 비교
7. `/api/false-friends` - False Friends 목록
8. `/api/statistics` - 통계

### 핵심 설계 결정

**ADR-001: Prisma ORM 선택**
- 이유: TypeScript 타입 안전성, 마이그레이션 관리, 복잡한 관계 쿼리 지원
- 대안: Drizzle (더 가벼움), TypeORM (더 성숙)
- 결과: 개발 속도 향상, 타입 에러 조기 발견

**ADR-002: Composite Key (`@@unique`) 사용**
- 이유: 동일 문자+국가+타입 조합 중복 방지
- 예: "愛"의 중국 Mandarin 발음은 하나만 존재해야 함
- 결과: 데이터 무결성 보장

**ADR-003: `onDelete: Cascade` 사용**
- 이유: Character 삭제 시 관련 Pronunciation, Meaning 자동 삭제
- 대안: `onDelete: SetNull` (orphan 레코드 생성)
- 결과: 데이터 정합성 유지, 수동 정리 불필요
