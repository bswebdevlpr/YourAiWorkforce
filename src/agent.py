from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from src.config import MODEL_NAME_DEFAULT
from src.libs.model import create_chat_model
from src.libs.persona import ORCHESTRATOR, load_persona
from src.state import AgentState
from src.subagents import SUBAGENT_REGISTRY, SUBAGENT_TOOLS

_model = create_chat_model(MODEL_NAME_DEFAULT).bind_tools(SUBAGENT_TOOLS)
_system_prompt = load_persona(ORCHESTRATOR)


def orchestrator(state: AgentState):
    messages = [{"role": "system", "content": _system_prompt}] + state["messages"]
    response = _model.invoke(messages)
    return {"messages": [response]}


def route(state: AgentState):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        name = last.tool_calls[0]["name"]
        if name in SUBAGENT_REGISTRY:
            return name
    return END


def bridge(state: AgentState):
    last = state["messages"][-1]
    if not (isinstance(last, AIMessage) and last.tool_calls):
        return state

    tc = last.tool_calls[0]
    target = tc["name"]
    query = tc["args"].get("query", "")

    _, _, needs_interrupt = SUBAGENT_REGISTRY[target]
    if needs_interrupt:
        decision = interrupt({
            "agent": target,
            "query": query,
            "message": f"{target}을(를) 호출할게요. 승인하시겠어요?",
        })
        if isinstance(decision, dict) and decision.get("type") == "reject":
            reason = decision.get("message", "사용자가 거절했습니다.")
            return Command(
                update={"messages": [AIMessage(content=reason)]},
                goto="orchestrator",
            )

    return Command(
        update={"messages": [HumanMessage(content=query)], "_last_subgraph": target},
        goto=target,
    )


def review(state: AgentState):
    last_content = state["messages"][-1].content
    decision = interrupt({
        "result": last_content,
        "message": "산출물을 확인해주세요.",
        "options": ["approve", "reject"],
    })
    if isinstance(decision, dict) and decision.get("type") == "reject":
        feedback = decision.get("message", "다시 작업해주세요.")
        return Command(
            update={"messages": [HumanMessage(content=feedback)]},
            goto=state["_last_subgraph"],
        )
    return state


def graph():
    builder = StateGraph(AgentState)

    subgraph_names = tuple(SUBAGENT_REGISTRY.keys())

    builder.add_node("orchestrator", orchestrator)
    builder.add_node(
        "bridge", bridge, destinations=(*subgraph_names, "orchestrator")
    )
    builder.add_node(
        "review", review, destinations=(*subgraph_names, "orchestrator")
    )
    for name, (subgraph, _, _) in SUBAGENT_REGISTRY.items():
        builder.add_node(name, subgraph)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges(
        "orchestrator",
        route,
        {name: "bridge" for name in SUBAGENT_REGISTRY} | {END: END},
    )
    for name in SUBAGENT_REGISTRY:
        builder.add_edge(name, "review")
    builder.add_edge("review", "orchestrator")

    return builder.compile()
