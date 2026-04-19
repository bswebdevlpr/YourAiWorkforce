from src.config import MODEL_NAME_PLANNER
from src.libs.model import create_chat_model
from src.libs.path import PRD_PATH
from src.libs.persona import PRODUCT_DISCOVERY, load_persona
from src.libs.subgraph import build_conversational_subgraph
from src.subagents.planners.product_discovery.tools import save_prd


def build_product_discovery(checkpointer=None):
    return build_conversational_subgraph(
        persona=load_persona(PRODUCT_DISCOVERY),
        model=create_chat_model(MODEL_NAME_PLANNER, temperature=1.0),
        save_tool=save_prd,
        artifact_path=PRD_PATH,
        checkpointer=checkpointer,
    )
