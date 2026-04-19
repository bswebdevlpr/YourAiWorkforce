from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph

from src.libs.nodes import make_check_done_node, make_wait_for_user_node
from src.libs.persona import CONVERSATIONAL_PROTOCOL, load_persona
from src.subagents.state import SubagentState

_UNSET = object()


def build_conversational_subgraph(
    *,
    persona: str,
    model: BaseChatModel,
    save_tool: BaseTool,
    artifact_path: Path | None = None,
    existing_hint: str = "기존 산출물이 있다. 피드백이 있으면 해당 부분만 수정하고, 전체를 다시 작성하지 마라.",
    prologue: str | None = _UNSET,  # type: ignore[assignment]
    checkpointer=None,
):
    """내부 루프형 대화 서브그래프 빌더.

    흐름:
      START → model → [tool_call(save_tool)?]
                         ├─ 있음 → save → [저장 성공?]
                         │                  ├─ 실패 → model (재작성)
                         │                  └─ 성공 → check_done → [is_done?]
                         │                                           ├─ YES → END
                         │                                           └─ NO  → wait_for_user
                         └─ 없음 → wait_for_user → [resume type?]
                                        ├─ complete/reject → END
                                        └─ message         → model
    """
    bound_model = model.bind_tools([save_tool])
    save_tool_name = save_tool.name

    if prologue is _UNSET:
        prologue = load_persona(CONVERSATIONAL_PROTOCOL)
    system_content = f"{prologue}\n\n---\n\n{persona}" if prologue else persona

    _artifact_cache = {"mtime": None, "content": None}

    def _read_artifact() -> str | None:
        if artifact_path is None or not artifact_path.exists():
            return None
        mtime = artifact_path.stat().st_mtime
        if _artifact_cache["mtime"] != mtime:
            _artifact_cache["mtime"] = mtime
            _artifact_cache["content"] = artifact_path.read_text(encoding="utf-8")
        return _artifact_cache["content"]

    def call_model(state: SubagentState):
        messages = [{"role": "system", "content": system_content}]

        existing = _read_artifact()
        if existing:
            messages.append(
                {
                    "role": "system",
                    "content": f"{existing_hint}\n\n---\n{existing}",
                }
            )

        messages += state["messages"]
        response = bound_model.invoke(messages)
        return {"messages": [response]}

    def call_save(state: SubagentState):
        last = state["messages"][-1]
        tool_call = next(
            (tc for tc in last.tool_calls if tc["name"] == save_tool_name),
            None,
        )
        if tool_call is None:
            return {
                "messages": [
                    AIMessage(content=f"[내부 오류] {save_tool_name} tool_call 누락")
                ]
            }
        try:
            result = save_tool.invoke(tool_call["args"])
        except Exception as exc:
            result = f"저장 실패: {exc}"
        return {
            "messages": [
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            ]
        }

    def route_after_model(state: SubagentState):
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            if any(tc["name"] == save_tool_name for tc in last.tool_calls):
                return "save"
        return "wait_for_user"

    def route_after_save(state: SubagentState):
        last = state["messages"][-1]
        content = getattr(last, "content", "") or ""
        if "실패" in content:
            return "model"
        return "check_done"

    def route_after_done(state: SubagentState):
        return END if state.get("is_done", True) else "wait_for_user"

    check_done = make_check_done_node(model)
    wait_for_user = make_wait_for_user_node(continue_goto="model", exit_goto=END)

    builder = StateGraph(SubagentState)
    builder.add_node("model", call_model)
    builder.add_node("save", call_save)
    builder.add_node("check_done", check_done)
    builder.add_node("wait_for_user", wait_for_user, destinations=("model", END))

    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model",
        route_after_model,
        {"save": "save", "wait_for_user": "wait_for_user"},
    )
    builder.add_conditional_edges(
        "save",
        route_after_save,
        {"model": "model", "check_done": "check_done"},
    )
    builder.add_conditional_edges(
        "check_done",
        route_after_done,
        {"wait_for_user": "wait_for_user", END: END},
    )

    return builder.compile(checkpointer=checkpointer)
