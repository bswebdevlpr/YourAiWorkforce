from src.config import MODEL_NAME_PLANNER
from src.libs.model import create_chat_model
from src.libs.path import ARCHITECTURE_PATH
from src.libs.persona import SYSTEM_ARCHITECT, load_persona
from src.libs.subgraph import build_conversational_subgraph
from src.subagents.planners.system_architect.tools import save_architecture


def build_system_architect(checkpointer=None):
    return build_conversational_subgraph(
        persona=load_persona(SYSTEM_ARCHITECT),
        # 페르소나에 디렉토리 트리/패키지 매니페스트 예시 코드블록이 많아 ~14k 토큰. 32k로 여유 확보.
        model=create_chat_model(MODEL_NAME_PLANNER, temperature=0.3, num_ctx=32768),
        save_tool=save_architecture,
        artifact_path=ARCHITECTURE_PATH,
        checkpointer=checkpointer,
    )
