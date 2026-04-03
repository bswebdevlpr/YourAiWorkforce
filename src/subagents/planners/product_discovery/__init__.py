from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from src.config import MODEL_NAME_PLANNER
from src.libs.model import create_chat_model
from src.libs.path import PRD_PATH
from src.libs.persona import PRODUCT_DISCOVERY, load_persona
from src.state import AgentState
from src.subagents.planners.product_discovery.tools import save_prd

_model = create_chat_model(MODEL_NAME_PLANNER, temperature=1.0)
_system_prompt = load_persona(PRODUCT_DISCOVERY)


def _call_model(state: AgentState):
    messages = [{"role": "system", "content": _system_prompt}]

    if PRD_PATH.exists():
        existing_prd = PRD_PATH.read_text(encoding="utf-8")
        messages.append({
            "role": "system",
            "content": f"기존 PRD가 있다. 피드백이 있으면 해당 부분만 수정하고, 전체를 다시 작성하지 마라.\n\n---\n{existing_prd}",
        })

    messages += state["messages"]
    response = _model.invoke(messages)
    return {"messages": [response]}


def _postprocess(state: AgentState):
    content = state["messages"][-1].content
    result = save_prd(content)
    return {"messages": [AIMessage(content=result)]}


_builder = StateGraph(AgentState)
_builder.add_node("model", _call_model)
_builder.add_node("postprocess", _postprocess)
_builder.add_edge(START, "model")
_builder.add_edge("model", "postprocess")
_builder.add_edge("postprocess", END)

product_discovery_graph = _builder.compile()
