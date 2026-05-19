from langchain_core.tools import tool

from src.libs.path import ARCHITECTURE_PATH, ROOT

ARCHITECTURE_REQUIRED_SECTIONS = [
    "## 1. 아키텍처 요구사항",
    "## 2. 기술 스택",
    "## 3. 프로젝트 구조",
    "## 4. 인프라 컴포넌트",
    "## 5. 개발 환경",
    "## 6. Architecture Decision Records",
]

ARCHITECTURE_PLACEHOLDER_MARKERS = [
    "[이름]",
    "[날짜]",
    "[Next.js / React",
    "[PostgreSQL / MongoDB",
    "[Vercel / Netlify",
    "[3-5줄 설명]",
    "[Tailwind / CSS Modules",
    "[Step ",
    "[선택한 기술",
    "[무엇을 선택",
    "[왜 선택",
    "[고려했지만",
    "[예상 영향]",
    "[필요한 만큼",
    "[Prisma / Drizzle",
    "[Redis / ...",
    "[호스팅 위치, 버전]",
    "[서비스, 구성]",
]

ADR_MARKER = "### ADR-"


def _validate_architecture(content: str) -> list[str]:
    """architecture.md 필수 섹션, placeholder 잔존, 최소 ADR 개수를 검증."""
    missing = [s for s in ARCHITECTURE_REQUIRED_SECTIONS if s not in content]
    if missing:
        return missing

    placeholders = [m for m in ARCHITECTURE_PLACEHOLDER_MARKERS if m in content]
    if placeholders:
        sample = ", ".join(placeholders[:3])
        more = f" (외 {len(placeholders) - 3}개)" if len(placeholders) > 3 else ""
        return [f"미작성 placeholder 잔존: {sample}{more}"]

    adr_count = content.count(ADR_MARKER)
    if adr_count < 3:
        return [f"ADR 부족: 최소 3개 필요, 현재 {adr_count}개"]

    return []


@tool(
    "save_architecture",
    description=(
        "Architecture 문서 저장. Step 1~5 (요구사항 도출 / 프레임워크 / DB·인프라 / "
        "디렉토리 구조 / 의존성 매니페스트) + 최소 3개 ADR이 대표님과 합의된 직후 1회만 호출. "
        "Step 중간(예: 프레임워크만 합의하고 DB 미합의) 호출 금지. 동일 턴 내 중복 호출 금지."
    ),
)
def save_architecture(content: str) -> str:
    """Architecture 문서를 검증 후 파일로 저장한다."""
    missing = _validate_architecture(content)
    if missing:
        return f"Architecture 저장 실패. 누락된 섹션: {', '.join(missing)}"

    try:
        ARCHITECTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARCHITECTURE_PATH.write_text(content, encoding="utf-8")
    except OSError as exc:
        return f"Architecture 저장 실패. 파일 쓰기 오류: {exc}"

    return f"Architecture 저장 완료: {ARCHITECTURE_PATH.relative_to(ROOT)}"
