from pathlib import Path


def load_artifact(path: Path) -> str | None:
    """아티팩트 파일이 존재하면 내용을 반환하고, 없으면 None을 반환한다."""
    return path.read_text(encoding="utf-8") if path.exists() else None
