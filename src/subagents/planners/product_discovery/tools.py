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


def _validate_prd(content: str) -> list[str]:
    """PRD 필수 섹션 누락 여부를 검증한다."""
    missing = []
    for section in PRD_REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)
    return missing


@tool(
    "save_prd",
    description=(
        "PRD를 파일로 저장하는 도구. **반드시 Step 1~6 전 구간이 대표님과의 대화로 합의된 직후 단 한 번만** 호출한다. "
        "다음 경우에는 절대 호출하지 않는다: "
        "(1) 작업 진입 첫 턴(인사·주제 확인 단계), "
        "(2) 대표님의 추가 응답이 한 번도 없는 상태, "
        "(3) Step 중간(예: 페르소나만 합의되고 P0/P1 미합의), "
        "(4) 동일 PRD를 같은 턴에 두 번 저장(중복 호출 금지). "
        "유저와의 합의 없이 호출하면 시스템이 거절하고 다시 대화로 돌아간다."
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
