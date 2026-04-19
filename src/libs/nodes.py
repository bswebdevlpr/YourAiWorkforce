from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import Command, interrupt

from src.state import AgentState


def make_check_done_node(model: BaseChatModel):
    """작업 완료 여부를 LLM에게 자가판정시키는 노드.

    기본 편향은 "완료"다. 명시적으로 추가 작업이 필요하다는 신호가 있을 때만 NO.
    """

    def check_done(state: AgentState):
        judge = model.invoke(
            [
                SystemMessage(
                    "직전 대화에서 사용자가 추가 요청을 명시했는지 판단한다. "
                    "추가 요청이 명시적으로 있으면 NO, 그렇지 않으면 YES 한 단어로만 답한다."
                ),
                *state["messages"],
            ]
        )
        return {"is_done": "NO" not in (judge.content or "").upper()}

    return check_done


def make_wait_for_user_node(continue_goto: str, exit_goto: str = END):
    """서브그래프 내부에서 유저 입력을 받는 노드.

    resume payload 컨벤션:
      - {"type": "reply", "message": "..."}    → continue_goto (대화 이어감)
      - {"type": "complete"}                   → exit_goto (작업 완료 종료)
      - {"type": "reject", "message"?}         → exit_goto (중단 맥락 첨부)
    그 외 type/형식은 오류로 처리하여 model 노드에 돌려보낸다.
    """

    def wait_for_user(state: AgentState):
        last = state["messages"][-1].content
        decision = interrupt(
            {"result": last, "options": ["reply", "complete", "reject"]}
        )

        if not isinstance(decision, dict):
            return Command(
                update={
                    "messages": [
                        AIMessage(
                            content=(
                                f"[잘못된 resume payload] dict가 아닌 값이 전달됨: {decision!r}"
                            )
                        )
                    ]
                },
                goto=continue_goto,
            )

        dtype = decision.get("type")
        if dtype == "complete":
            return Command(goto=exit_goto)
        if dtype == "reject":
            reason = decision.get("message", "사용자가 작업을 중단했습니다.")
            return Command(
                update={"messages": [AIMessage(content=f"[작업 중단] {reason}")]},
                goto=exit_goto,
            )
        if dtype == "reply":
            text = decision.get("message", "")
            return Command(
                update={"messages": [HumanMessage(content=text)]},
                goto=continue_goto,
            )

        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=(
                            f"[알 수 없는 resume type: {dtype!r}] "
                            f"허용: reply/complete/reject. payload={decision!r}"
                        )
                    )
                ]
            },
            goto=continue_goto,
        )

    return wait_for_user


def make_approval_gate_node(subagent_names: tuple[str, ...]):
    """파괴적/중대 tool_call 전에 사용자 승인을 받는 게이트.

    resume payload:
      - {"type": "approve"}             → 해당 tool 목적지로 진행
      - {"type": "reject", "message"?}  → ToolMessage로 거절 피드백 주입 + orchestrator 복귀
    그 외 payload는 안전을 위해 reject와 동일하게 취급한다.
    """

    def approval_gate(state: AgentState):
        last = state["messages"][-1]
        tc = last.tool_calls[0]
        tool_name = tc["name"]

        decision = interrupt(
            {
                "type": "approval_request",
                "tool": tool_name,
                "args": tc.get("args", {}),
                "options": ["approve", "reject"],
            }
        )

        dtype = decision.get("type") if isinstance(decision, dict) else None
        if dtype != "approve":
            reason = (
                decision.get("message", "사용자가 승인을 거절했습니다.")
                if isinstance(decision, dict)
                else f"잘못된 승인 payload: {decision!r}"
            )
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=f"[승인 거절] {reason}",
                            tool_call_id=tc["id"],
                            name=tool_name,
                        )
                    ]
                },
                goto="orchestrator",
            )

        if tool_name == "reset_project":
            return Command(goto="reset_project")
        if tool_name in subagent_names:
            return Command(
                update={"_approved_subagents": [tool_name]},
                goto="bridge",
            )
        return Command(goto="orchestrator")

    return approval_gate


def review(state: AgentState):
    """외부 그래프에서 산출물을 사용자에게 최종 확인받는 노드.

    resume payload:
      - {"type": "approve"}            → 통과
      - {"type": "reject", "message"?} → 직전 subgraph로 피드백과 함께 복귀
    그 외 payload는 안전을 위해 reject로 취급한다.
    """
    last_content = state["messages"][-1].content
    decision = interrupt(
        {
            "result": last_content,
            "options": ["approve", "reject"],
        }
    )
    dtype = decision.get("type") if isinstance(decision, dict) else None
    if dtype == "approve":
        return state

    feedback = (
        decision.get("message", "다시 작업해주세요.")
        if isinstance(decision, dict)
        else f"잘못된 resume payload: {decision!r}"
    )
    return Command(
        update={"messages": [HumanMessage(content=feedback)]},
        goto=state.get("_last_subgraph") or END,
    )
