from langchain_core.tools import tool

from src.libs.path import PRD_PATH, ROOT

PRD_REQUIRED_SECTIONS = [
    "## 1. 문제 정의",
    "## 2. 타겟 사용자",
    "## 3. 기능 우선순위",
    "## 4. 성공 지표",
    "## 5. 범위 경계",
    "## 6. Phase 마일스톤",
]

PRD_PLACEHOLDER_MARKERS = [
    "[Step ",
    "[아이디어 파싱",
    "[해결하려는",
    "[페르소나명]",
    "[기능명]",
    "[측정 가능한",
    "[목표값]",
    "[메트릭명]",
    "[In/Out of Scope]",
    "[Phase별 마일스톤]",
    "[포함되는",
    "[제외되는",
    "[날짜]",
    "[이름]",
    "[나이, 직업]",
    "[1-2줄 설명]",
]


def _validate_prd(content: str) -> list[str]:
    """PRD 필수 섹션 누락 + 미작성 placeholder 잔존 여부를 검증한다."""
    missing = []
    for section in PRD_REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)
    if missing:
        return missing

    placeholders = [m for m in PRD_PLACEHOLDER_MARKERS if m in content]
    if placeholders:
        sample = ", ".join(placeholders[:3])
        more = f" (외 {len(placeholders) - 3}개)" if len(placeholders) > 3 else ""
        return [f"미작성 placeholder 잔존: {sample}{more}"]
    return []


@tool(
    "save_prd",
    description=(
        "PRD 파일 저장. Step 1~6 전 구간이 대표님과 합의된 직후 1회만 호출. "
        "Step 중간(예: 페르소나만 합의되고 P0/P1 미합의) 호출 금지. 동일 턴 내 중복 호출 금지."
    ),
)
def save_prd(content: str) -> str:
    """PRD를 검증 후 파일로 저장한다."""
    missing = _validate_prd(content)
    if missing:
        return f"PRD 저장 실패. 누락된 섹션: {', '.join(missing)}"

    try:
        PRD_PATH.parent.mkdir(parents=True, exist_ok=True)
        PRD_PATH.write_text(content, encoding="utf-8")
    except OSError as exc:
        return f"PRD 저장 실패. 파일 쓰기 오류: {exc}"

    return f"PRD 저장 완료: {PRD_PATH.relative_to(ROOT)}"
