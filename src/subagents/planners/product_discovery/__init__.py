from src.config import MODEL_NAME_PLANNER
from src.libs.model import create_chat_model
from src.libs.path import PRD_PATH
from src.libs.persona import PRODUCT_DISCOVERY, load_persona
from src.libs.subgraph import build_conversational_subgraph
from src.subagents.planners.product_discovery.tools import save_prd


def build_product_discovery(checkpointer=None):
    return build_conversational_subgraph(
        persona=load_persona(PRODUCT_DISCOVERY),
        # 페르소나 ~10.5k 토큰 + 대화 누적 여유 → 20k. PRD 템플릿/Step 가이드가 후반부에 위치해 잘림 방지.
        model=create_chat_model(MODEL_NAME_PLANNER, temperature=0.5, num_ctx=20480),
        save_tool=save_prd,
        artifact_path=PRD_PATH,
        checkpointer=checkpointer,
    )
