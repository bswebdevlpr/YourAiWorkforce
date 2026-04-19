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

_SUBAGENT_GRAPHS: dict = {}


def _get_subagent(name: str):
    if name not in _SUBAGENT_GRAPHS:
        _SUBAGENT_GRAPHS[name] = SUBAGENT_REGISTRY[name].graph_factory(None)
    return _SUBAGENT_GRAPHS[name]


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


def _summarize_for_parent(name: str, sub_messages: list) -> str:
    last = sub_messages[-1] if sub_messages else None
    text = getattr(last, "content", "") if last else ""
    text = str(text or "").strip()
    truncated = text[:200] + ("..." if len(text) > 200 else "")
    return f"[{name} 완료]\n{truncated}" if truncated else f"[{name} 완료]"


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
    last = state["messages"][-1]
    if not (isinstance(last, AIMessage) and last.tool_calls):
        return state

    tc = last.tool_calls[0]
    target = tc["name"]
    if target not in SUBAGENT_REGISTRY:
        return state

    brief = _compose_brief(tc.get("args") or {})
    subgraph = _get_subagent(target)

    try:
        result = subgraph.invoke({"messages": [HumanMessage(content=brief)]})
        summary = _summarize_for_parent(target, result.get("messages") or [])
    except Exception as exc:
        summary = f"[{target} 실행 실패] {exc}"

    tool_msg = ToolMessage(content=summary, tool_call_id=tc["id"], name=target)
    return Command(
        update={"messages": [tool_msg], "_last_subgraph": target},
        goto="review",
    )


def _build():
    builder = StateGraph(AgentState)

    subagent_names = tuple(SUBAGENT_REGISTRY.keys())

    builder.add_node("orchestrator", orchestrator)
    builder.add_node("bridge", bridge, destinations=("review", "orchestrator"))
    builder.add_node("review", review, destinations=("orchestrator",))
    builder.add_node("reset_project", reset_project)
    builder.add_node(
        "approval_gate",
        make_approval_gate_node(subagent_names),
        destinations=("bridge", "reset_project", "orchestrator"),
    )

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
    builder.add_edge("review", "orchestrator")

    return builder


def graph(config=None):
    """langgraph dev / Platform 진입점. 플랫폼이 자체 checkpointer 주입."""
    return _build().compile()


def graph_with_checkpointer(checkpointer):
    """FastAPI 앱에서 AsyncSqliteSaver 주입용."""
    return _build().compile(checkpointer=checkpointer)
