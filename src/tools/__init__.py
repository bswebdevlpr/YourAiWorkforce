import shutil

from langchain_core.messages import AIMessage

from src.libs.path import AI_WORKSPACE
from src.state import AgentState


def reset_project(state: AgentState):
    """기존 프로젝트 산출물을 삭제하고 새 프로젝트를 시작한다."""
    if AI_WORKSPACE.exists():
        shutil.rmtree(AI_WORKSPACE)
    return {"messages": [AIMessage(content="프로젝트를 초기화했어요. 새 아이디어를 알려주세요!")]}
