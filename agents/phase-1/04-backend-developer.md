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

**예시**:
- P0 기능: "음식 검색", "영양 정보 표시", "추천"
- 엔티티: **Food**, **Ingredient**, **NutritionInfo**, **UserPreference**

#### 1.2 관계 모델링

엔티티 간 관계를 정의하세요:

| 관계 타입 | Prisma 문법 | 예시 |
|---------|-----------|------|
| **1:N** | `model A { bs B[] }`<br>`model B { a A @relation(fields: [aId], references: [id]) }` | Post → Comment[] |
| **M:N** | `model A { bs B[] }`<br>`model B { as A[] }` | Recipe ←→ Ingredient (재료 여러 개, 재료도 여러 레시피에 사용) |
| **1:1** | `model A { b B? }`<br>`model B { a A @relation(fields: [aId], references: [id]) }` | User ←→ Profile |

#### 1.3 Enum 타입 정의

범주형 데이터는 Enum으로 정의하세요:

**예시**:
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

// 핵심 엔티티 모델
model [MainEntity] {
  id        String   @id @default(cuid())
  name      String   @unique
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // 관계
  details   [RelatedEntity][]

  // 인덱스
  @@index([name])
}

model [RelatedEntity] {
  id             String       @id @default(cuid())
  value          String
  type           String

  // 관계
  [mainEntity]   [MainEntity] @relation(fields: [[mainEntityId]], references: [id])
  [mainEntityId] String

  // 복합 유니크 제약: 동일 엔티티+타입 조합 중복 방지
  @@unique([[mainEntityId], type])
  @@index([[mainEntityId]])
}
```

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

**최소 API 정의**: P0 기능당 최소 1개의 GET 엔드포인트. 구체적으로:
- 목록 조회 API: `GET /api/[resource]?limit=20&offset=0`
- 상세 조회 API: `GET /api/[resource]/[id]`
- (검색 기능이 P0인 경우) 검색 API: `GET /api/search?q=[query]`

#### 3.1 API 설계

**REST 패턴**:

| 기능 | 메서드 | 경로 | 설명 |
|------|--------|------|------|
| 목록 조회 | GET | `/api/[resources]` | 페이지네이션된 목록 |
| 상세 조회 | GET | `/api/[resources]/[id]` | 특정 리소스 상세 정보 |
| 검색 | GET | `/api/search?q=[query]` | 쿼리 기반 검색 |
| 자동완성 | GET | `/api/[resources]/autocomplete?q=[query]` | 검색 제안 |

#### 3.2 API 구현 (Next.js App Router 예시)

**파일 위치**: `src/app/api/[resources]/route.ts`

**템플릿**:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET /api/[resources]?page=1&limit=20
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const skip = (page - 1) * limit;

    // 데이터 조회
    const [items, total] = await Promise.all([
      prisma.[mainEntity].findMany({
        take: limit,
        skip,
        include: {
          details: true,
        },
        orderBy: { name: 'asc' },
      }),
      prisma.[mainEntity].count(),
    ]);

    return NextResponse.json({
      data: items,
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

**파일 위치**: `src/app/api/[resources]/[id]/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET /api/[resources]/[id]
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    const item = await prisma.[mainEntity].findUnique({
      where: { id },
      include: {
        details: true,
      },
    });

    if (!item) {
      return NextResponse.json(
        { error: 'Resource not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ data: item });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
```

**체크리스트**:
- [ ] `/api/[resources]` (목록) 구현
- [ ] `/api/[resources]/[id]` (상세) 구현
- [ ] `/api/search` (검색) 구현
- [ ] 모든 API가 JSON 응답 반환
- [ ] 에러 핸들링 구현 (404, 500)
- [ ] `http://localhost:3000/api/[resources]`에서 테스트 성공

---

### Step 4: 데이터 검증 (10분)

> ⚠️ 이 Step은 Data Engineer(05)가 데이터 로드를 완료한 후 실행한다. DEN 미완료 시 Step 3까지만 완료하고 DEN에게 넘긴다.

Data Engineer가 로드한 데이터를 API로 확인하세요.

**테스트 체크리스트**:

```bash
# 서버 실행
pnpm dev

# 테스트 쿼리 (curl 또는 브라우저)
curl http://localhost:3000/api/[resources]?limit=5
curl http://localhost:3000/api/[resources]/[id]  # 실제 존재하는 리소스로 테스트
```

**확인 사항**:
- [ ] API가 실제 데이터 반환 (빈 배열 ❌)
- [ ] 관계 데이터가 포함됨
- [ ] 페이지네이션 작동 (`page=2` 테스트)
- [ ] 존재하지 않는 ID 요청 시 404 반환

---

## 📤 출력 파일

1. **`prisma/schema.prisma`**: 데이터베이스 스키마 (모든 모델, 관계, 인덱스)
2. **`src/app/api/[resources]/route.ts`**: 목록 API
3. **`src/app/api/[resources]/[id]/route.ts`**: 상세 API
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

## ⚠️ 실패 대응

| 상황 | 조치 |
|------|------|
| Prisma migration 실패 | `npx prisma migrate reset --force` 후 스키마 수정, 재시도 |
| DB 연결 실패 | `.env`의 `DATABASE_URL` 확인, PostgreSQL 서비스 상태 확인 |
| API 엔드포인트 500 에러 | 서버 로그 확인, Prisma Client 재생성 (`npx prisma generate`) |

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
"agent-system/agents/phase-1/05-data-engineer.md를 읽고 DEN으로 작동해주세요"
```

DevOps Engineer가 빌드 시스템과 환경 구성을 설정합니다.

---

## 💡 핵심 설계 결정

**ADR-001: Prisma ORM 선택**
- 이유: TypeScript 타입 안전성, 마이그레이션 관리, 복잡한 관계 쿼리 지원
- 대안: Drizzle (더 가벼움), TypeORM (더 성숙)
- 결과: 개발 속도 향상, 타입 에러 조기 발견

**ADR-002: Composite Key (`@@unique`) 사용**
- 이유: 동일 엔티티+타입 조합 중복 방지
- 결과: 데이터 무결성 보장

**ADR-003: `onDelete: Cascade` 사용**
- 이유: 부모 엔티티 삭제 시 관련 자식 레코드 자동 삭제
- 대안: `onDelete: SetNull` (orphan 레코드 생성)
- 결과: 데이터 정합성 유지, 수동 정리 불필요
