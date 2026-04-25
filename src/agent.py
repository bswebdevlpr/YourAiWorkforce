from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from src.config import MODEL_NAME_DEFAULT
from src.libs.model import create_chat_model
from src.libs.nodes import make_approval_gate_node, review
from src.libs.persona import ORCHESTRATOR, load_persona
from src.state import AgentState
from src.subagents import ALL_TOOLS, SUBAGENT_REGISTRY
from src.tools import reset_project

_model = create_chat_model(MODEL_NAME_DEFAULT).bind_tools(ALL_TOOLS)
_system_prompt = load_persona(ORCHESTRATOR)


def _compose_brief(args: dict) -> str:
    query = (args.get("query") or "").strip()
    hints = (args.get("context_hints") or "").strip()
    refs = args.get("artifact_refs") or []

    parts = [f"## 이번 작업 목표\n{query}"]
    if hints:
        parts.append(f"## 고려할 맥락\n{hints}")
    if refs:
        parts.append("## 참고 산출물\n" + "\n".join(f"- {r}" for r in refs))
    return "\n\n".join(parts)


def orchestrator(state: AgentState):
    messages = [{"role": "system", "content": _system_prompt}] + state["messages"]
    response = _model.invoke(messages)
    return {"messages": [response]}


def route(state: AgentState):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        name = last.tool_calls[0]["name"]
        if name == "reset_project":
            return "approval_gate"
        if name in SUBAGENT_REGISTRY:
            return "bridge"
    return END


def bridge(state: AgentState):
    """orchestrator의 tool_call을 받아 brief HumanMessage로 변환하고 해당 subagent 노드로 라우팅.

    LangGraph의 subgraph-as-node 메커니즘을 그대로 사용하므로 subagent의 interrupt는
    parent로 자동 전파되고 resume 값도 자동으로 전달된다.
    """
    last = state["messages"][-1]
    if not (isinstance(last, AIMessage) and last.tool_calls):
        return state

    tc = last.tool_calls[0]
    target = tc["name"]
    if target not in SUBAGENT_REGISTRY:
        return state

    brief = _compose_brief(tc.get("args") or {})
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"({target}에 핸드오프)",
                    tool_call_id=tc["id"],
                    name=target,
                ),
                HumanMessage(content=brief),
            ],
            "_last_subgraph": target,
        },
        goto=target,
    )


def _build():
    builder = StateGraph(AgentState)

    subagent_names = tuple(SUBAGENT_REGISTRY.keys())

    builder.add_node("orchestrator", orchestrator)
    builder.add_node(
        "bridge", bridge, destinations=(*subagent_names, "orchestrator")
    )
    builder.add_node("review", review, destinations=("orchestrator",))
    builder.add_node("reset_project", reset_project)
    builder.add_node(
        "approval_gate",
        make_approval_gate_node(subagent_names),
        destinations=("bridge", "reset_project", "orchestrator"),
    )
    for name, spec in SUBAGENT_REGISTRY.items():
        builder.add_node(name, spec.graph_factory(None))

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges(
        "orchestrator",
        route,
        {
            "bridge": "bridge",
            "approval_gate": "approval_gate",
            "reset_project": "reset_project",
            END: END,
        },
    )
    builder.add_edge("reset_project", "orchestrator")
    for name in subagent_names:
        builder.add_edge(name, "review")
    builder.add_edge("review", "orchestrator")

    return builder


def graph(config=None):
    """langgraph dev / Platform 진입점. 플랫폼이 자체 checkpointer 주입."""
    return _build().compile()


def graph_with_checkpointer(checkpointer):
    """FastAPI 앱에서 AsyncSqliteSaver 주입용. parent compile 시 subagent 노드도 같은 checkpointer 자동 상속."""
    return _build().compile(checkpointer=checkpointer)
