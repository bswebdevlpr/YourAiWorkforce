import re
import warnings
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph

from src.libs.nodes import make_check_done_node, make_wait_for_user_node
from src.libs.path import ROOT
from src.libs.persona import CONVERSATIONAL_PROTOCOL, load_persona
from src.subagents.state import SubagentState

_UNSET = object()

_TURN_END_RE = re.compile(r"`*\s*🛑?\s*\[?\s*턴\s*종료\s*\]?\s*`*", re.MULTILINE)
_EMPTY_FENCE_RE = re.compile(r"`{2,}\s*\n?\s*`{2,}", re.MULTILINE)
_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_GREETING_PREFIX_RE = re.compile(
    r"^(?:`+\s*\n?)*\s*대표님[!,]?\s*안녕하세요[^\n]*\n+",
    re.MULTILINE,
)
_EMPTY_FALLBACK = "(응답이 비어있어요, 같은 질문 한 번 더 부탁드릴게요!)"


def _estimate_tokens(text: str) -> int:
    """Rough token estimate. qwen 토크나이저 기준 한국어 1자 ≈ 1.2~1.3 토큰."""
    return int(len(text) * 1.3)


def _strip_system_artifacts(content: str, *, strip_greeting: bool = False) -> str:
    """모델이 페르소나의 시스템 마커/빈 코드블록/reasoning 토큰을 응답에 echo하는 경우 제거.

    잡는 패턴:
    - <think>...</think> reasoning 블록 (qwen3 thinking mode artifact)
    - 🛑 [턴 종료], [턴 종료], 백틱 wrapped 변형
    - 빈 fenced code block (``...`` 또는 ```...``` with 내용 없음)
    - strip_greeting=True 시 첫 줄의 "대표님! 안녕하세요, ..." 인사 prefix
    """
    cleaned = _THINK_BLOCK_RE.sub("", content)
    cleaned = _TURN_END_RE.sub("", cleaned)
    cleaned = _EMPTY_FENCE_RE.sub("", cleaned)
    if strip_greeting:
        cleaned = _GREETING_PREFIX_RE.sub("", cleaned, count=1)
    return cleaned.strip()


def build_conversational_subgraph(
    *,
    persona: str,
    model: BaseChatModel,
    save_tool: BaseTool,
    artifact_path: Path | None = None,
    existing_hint: str = "기존 산출물이 있다. 피드백이 있으면 해당 부분만 수정하고, 전체를 다시 작성하지 마라.",
    save_user_reply_threshold: int = 3,
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
    save_tool_name = save_tool.name
    model_with_save = model.bind_tools([save_tool])
    num_ctx = getattr(model, "num_ctx", None) or 4096

    if prologue is _UNSET:
        prologue = load_persona(CONVERSATIONAL_PROTOCOL)
    system_content = f"{prologue}\n\n---\n\n{persona}" if prologue else persona

    persona_label = (persona.splitlines() or [""])[0][:60].lstrip("# ").strip() or "subagent"
    system_estimated = _estimate_tokens(system_content)
    system_budget = int(num_ctx * 0.6)
    if system_estimated > system_budget:
        warnings.warn(
            f"[{persona_label}] system prompt ~{system_estimated} tokens가 "
            f"num_ctx={num_ctx}의 60% ({system_budget})를 초과. "
            "후반부 instruction이 잘릴 위험이 있습니다.",
            stacklevel=2,
        )

    _artifact_cache = {"mtime": None, "content": None}

    def _read_artifact() -> str | None:
        if artifact_path is None or not artifact_path.exists():
            return None
        mtime = artifact_path.stat().st_mtime
        if _artifact_cache["mtime"] != mtime:
            _artifact_cache["mtime"] = mtime
            _artifact_cache["content"] = artifact_path.read_text(encoding="utf-8")
        return _artifact_cache["content"]

    def _real_user_reply_count(state_messages) -> int:
        return sum(
            1
            for m in state_messages
            if isinstance(m, HumanMessage)
            and not (m.content or "").startswith("## 이번 작업 목표")
        )

    def call_model(state: SubagentState):
        entry_update = {}
        if state.get("_entry_count") is None:
            entry_update["_entry_count"] = len(state["messages"])

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

        if _real_user_reply_count(state["messages"]) >= save_user_reply_threshold:
            active_model = model_with_save
        else:
            active_model = model

        response = active_model.invoke(messages)

        if isinstance(getattr(response, "content", None), str):
            has_prior_ai = any(
                isinstance(m, AIMessage) for m in state["messages"]
            )
            response.content = _strip_system_artifacts(
                response.content, strip_greeting=has_prior_ai
            )
            if not response.content and not getattr(response, "tool_calls", None):
                response.content = _EMPTY_FALLBACK

        prompt_eval = (getattr(response, "response_metadata", None) or {}).get(
            "prompt_eval_count"
        )
        if prompt_eval and prompt_eval >= num_ctx:
            warnings.warn(
                f"[{persona_label}] prompt_eval_count={prompt_eval}이 "
                f"num_ctx={num_ctx}에 도달. 입력 프롬프트가 잘렸을 가능성. "
                "num_ctx를 더 크게 잡거나 페르소나/메시지 길이를 줄이세요.",
                stacklevel=2,
            )

        return {"messages": [response], **entry_update}

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

        if _real_user_reply_count(state["messages"]) < save_user_reply_threshold:
            return {
                "messages": [
                    ToolMessage(
                        content=(
                            "[저장 거절] 대표님과의 합의가 부족한 상태로 저장을 시도했습니다. "
                            "지금부터 당신의 다음 응답은 사용자(대표님)에게 직접 보내는 메시지입니다. "
                            "'저장 실패', '보완해주세요' 같은 시스템 메타 어휘를 절대 쓰지 말고, "
                            "페르소나의 첫 진입 멘트로 자연스럽게 응답하세요: "
                            "(1) 짧은 인사 (2) 이번 주제 한 줄 확인 (3) Step 1 첫 질문 1개. "
                            "PRD 통째 작성, 저장 도구 재호출 모두 금지."
                        ),
                        tool_call_id=tool_call["id"],
                        name=save_tool_name,
                    )
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

    def finalize(state: SubagentState):
        """subagent 종료 직전 청소 노드.

        _entry_count 이후 추가된 내부 messages 를 RemoveMessage 로 모두 청소하고,
        parent 에 노출할 짧은 요약 AIMessage 한 건을 남긴다. LangGraph subgraph→parent
        경계를 RemoveMessage 가 그대로 통과하므로 parent.messages 누적이 차단된다.
        """
        msgs = state["messages"]
        entry = state.get("_entry_count", 0)
        internal = [m for m in msgs[entry:] if getattr(m, "id", None)]

        last_ai = next(
            (
                m
                for m in reversed(msgs)
                if isinstance(m, AIMessage) and (m.content or "").strip()
            ),
            None,
        )
        summary_text = (last_ai.content if last_ai else "").strip()[:200]
        artifact_hint = ""
        if artifact_path is not None and artifact_path.exists():
            try:
                artifact_hint = f"산출물: {artifact_path.relative_to(ROOT)}"
            except ValueError:
                artifact_hint = f"산출물: {artifact_path}"

        summary_lines = [f"[{persona_label} 완료]"]
        if artifact_hint:
            summary_lines.append(artifact_hint)
        if summary_text:
            summary_lines.append(summary_text)
        summary = AIMessage(content="\n".join(summary_lines))

        return {
            "messages": [*(RemoveMessage(id=m.id) for m in internal), summary],
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
        if "실패" in content or "[저장 거절]" in content:
            return "model"
        return "check_done"

    def route_after_done(state: SubagentState):
        return "finalize" if state.get("is_done", True) else "wait_for_user"

    check_done = make_check_done_node(model)
    wait_for_user = make_wait_for_user_node(continue_goto="model", exit_goto="finalize")

    builder = StateGraph(SubagentState)
    builder.add_node("model", call_model)
    builder.add_node("save", call_save)
    builder.add_node("check_done", check_done)
    builder.add_node("finalize", finalize)
    builder.add_node("wait_for_user", wait_for_user, destinations=("model", "finalize"))

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
        {"wait_for_user": "wait_for_user", "finalize": "finalize"},
    )
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=checkpointer)
