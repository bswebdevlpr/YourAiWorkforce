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

_model = create_chat_model(MODEL_NAME_DEFAULT, role="orchestrator").bind_tools(ALL_TOOLS)
_system_prompt = load_persona(ORCHESTRATOR)


def _sanitize_query(query: str) -> str:
    """orchestrator가 query에 'AI가 사용자에게 할 말'을 작성하는 환각을 방어.

    - "대표님!" 같은 호칭 prefix 제거
    - 의문문/명령문 단서 제거 후 명사구로 정규화
    - 60자 초과 시 잘라냄
    """
    q = (query or "").strip()
    if not q:
        return q
    # AI가 사용자에게 말 거는 패턴 prefix 제거
    for prefix in ("대표님!", "대표님,", "대표님 "):
        if q.startswith(prefix):
            q = q[len(prefix):].lstrip()
            break
    # 흔한 trailing 의문/지시 패턴 잘라내기 (가장 마지막 마침표/물음표 이전까지 유지)
    for sentinel in (
        "어떤 형태",
        "어떻게 하시",
        "알려주세",
        "들려주세",
        "말씀해 주세",
        "여쭤",
        "?",
    ):
        idx = q.find(sentinel)
        if idx > 0:
            q = q[:idx].rstrip(" ,.!?·-")
    if len(q) > 60:
        q = q[:60].rstrip()
    return q


def _compose_brief(args: dict) -> str:
    query = _sanitize_query(args.get("query") or "")
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


def _build(checkpointer=None):
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
        builder.add_node(name, spec.graph_factory(checkpointer))

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


def _make_dev_checkpointer():
    """모듈 import 시점에 한 번만 호출 — sync I/O를 ASGI 이벤트 루프 밖에서 처리하기 위함.

    langgraph dev의 blockbuster 미들웨어가 핸들러 내부 sync I/O를 차단하므로
    graph() 호출 시점이 아닌 모듈 로드 시점에 sqlite 연결을 만든다.
    """
    import sqlite3

    from langgraph.checkpoint.sqlite import SqliteSaver

    from src.libs.path import CHECKPOINT_DB_PATH

    CHECKPOINT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    return SqliteSaver(conn)


_DEV_CHECKPOINTER = _make_dev_checkpointer()


def graph(config=None):
    """langgraph dev / Platform 진입점. 모듈 로드 시 만든 sync SqliteSaver를 재사용 (FastAPI와 같은 sqlite 파일 공유)."""
    return _build(_DEV_CHECKPOINTER).compile(checkpointer=_DEV_CHECKPOINTER)


def graph_with_checkpointer(checkpointer):
    """FastAPI 앱에서 AsyncSqliteSaver 주입용. subagent도 같은 checkpointer로 compile하여 state 공유."""
    return _build(checkpointer).compile(checkpointer=checkpointer)
