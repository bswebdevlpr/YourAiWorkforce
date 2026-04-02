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


def save_prd(content: str) -> str:
    """PRD를 검증 후 파일로 저장한다."""
    missing = _validate_prd(content)
    if missing:
        return f"PRD 저장 실패. 누락된 섹션: {', '.join(missing)}"

    PRD_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRD_PATH.write_text(content, encoding="utf-8")

    return f"PRD 저장 완료: {PRD_PATH.relative_to(ROOT)}"
