from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

AI_WORKSPACE = ROOT / "ai-workspace"
SPECS_DIR = AI_WORKSPACE / "specs"
PRD_PATH = SPECS_DIR / "prd.md"
CHECKPOINT_DIR = ROOT / ".checkpoints"
CHECKPOINT_DB_PATH = CHECKPOINT_DIR / "checkpoints.sqlite"
