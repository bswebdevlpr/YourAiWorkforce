from langchain_core.messages import AIMessage, HumanMessage
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


def orchestrator(state: AgentState):
    messages = [{"role": "system", "content": _system_prompt}] + state["messages"]
    response = _model.invoke(messages)
    return {"messages": [response]}


def route(state: AgentState):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        name = last.tool_calls[0]["name"]
        approved = state.get("_approved_subagents") or []
        if name == "reset_project":
            return "approval_gate"
        if name in SUBAGENT_REGISTRY:
            if name in approved:
                return name  # bridge 직행
            return "approval_gate"
    return END


def bridge(state: AgentState):
    last = state["messages"][-1]
    if not (isinstance(last, AIMessage) and last.tool_calls):
        return state

    tc = last.tool_calls[0]
    target = tc["name"]
    query = tc["args"].get("query", "")

    return Command(
        update={"messages": [HumanMessage(content=query)], "_last_subgraph": target},
        goto=target,
    )


def graph(checkpointer=None):
    builder = StateGraph(AgentState)

    subgraph_names = tuple(SUBAGENT_REGISTRY.keys())

    builder.add_node("orchestrator", orchestrator)
    builder.add_node("bridge", bridge, destinations=(*subgraph_names, "orchestrator"))
    builder.add_node("review", review, destinations=(*subgraph_names, "orchestrator"))
    builder.add_node("reset_project", reset_project)
    builder.add_node(
        "approval_gate",
        make_approval_gate_node(subgraph_names),
        destinations=("bridge", "reset_project", "orchestrator"),
    )
    for name, spec in SUBAGENT_REGISTRY.items():
        builder.add_node(name, spec.graph)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges(
        "orchestrator",
        route,
        {name: "bridge" for name in SUBAGENT_REGISTRY}
        | {"approval_gate": "approval_gate", "reset_project": "reset_project", END: END},
    )
    builder.add_edge("reset_project", "orchestrator")
    for name in SUBAGENT_REGISTRY:
        builder.add_edge(name, "review")
    builder.add_edge("review", "orchestrator")

    return builder.compile(checkpointer=checkpointer)
