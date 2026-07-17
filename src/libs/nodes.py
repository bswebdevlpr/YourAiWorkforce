import re

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import Command, interrupt

from src.state import AgentState

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

# 완료 판정 프롬프트. HITL 안전 편향: 애매하면 NO(계속)로 떨어뜨린다.
# 조기 종료(false YES)는 사용자가 맥락을 잃는 값비싼 실수지만, 한 번 더 묻는
# 것(false NO)은 값싸다. no-think critic이 암묵적 요청을 "완료"로 뭉개는 경향이
# 있어(eval_check_done.py 참고) 임계값을 NO 쪽으로 낮췄다.
CHECK_DONE_SYSTEM = (
    "직전 대화에서 사용자가 작업을 계속 이어가길 원하는지 판단한다.\n"
    "- 다음 중 하나라도 있으면 NO: 명시적 추가·수정·보완 요청, 질문, 재검토 요청, "
    "또는 주저·미완결·불만족을 비치는 뉘앙스.\n"
    "- 사용자가 명확히 만족·승인했고 더 다룰 것이 없을 때만 YES.\n"
    "판단이 애매하면 NO(계속). YES/NO 한 단어로만 답한다."
)


def make_check_done_node(model: BaseChatModel):
    """작업 완료 여부를 LLM에게 자가판정시키는 노드.

    기본 편향은 "계속(NO)"이다 — HITL에서 조기 종료보다 한 번 더 묻는 게 안전하므로,
    애매하면 NO로 떨어뜨린다(CHECK_DONE_SYSTEM 참고). 명확한 만족·승인일 때만 YES.

    단, 첫 턴 강행 저장(= bridge가 만든 brief 외에 진짜 user reply가 한 번도 없는 상태)
    인 경우 LLM 판정을 건너뛰고 무조건 wait_for_user 로 떨어뜨린다.

    `model` 은 판정용 critic 모델 (가능하면 temperature=0, reasoning=False). qwen3
    thinking 모델은 <think>...</think> 블록을 본문에 echo하므로 그 부분을 먼저 떼어내고
    YES/NO 만 본다. 그렇지 않으면 thinking 안의 "NO"가 오판정을 일으킨다.
    """

    def check_done(state: AgentState):
        real_user_replies = [
            m
            for m in state["messages"]
            if isinstance(m, HumanMessage)
            and not (m.content or "").startswith("## 이번 작업 목표")
        ]
        if not real_user_replies:
            return {"is_done": False}

        judge = model.invoke(
            [
                SystemMessage(CHECK_DONE_SYSTEM),
                *state["messages"],
            ]
        )
        raw = judge.content or ""
        verdict = _THINK_BLOCK_RE.sub("", raw).strip().upper()
        return {"is_done": "NO" not in verdict}

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
      - {"type": "approve"}            → 통과 (orchestrator로 복귀)
      - {"type": "reject", "message"?} → 피드백을 parent messages에 주입 후 orchestrator로 복귀
    그 외 payload는 안전을 위해 reject로 취급한다. orchestrator가 피드백을 보고 재호출 여부를 결정한다.
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
    target = state.get("_last_subgraph") or "담당 포지션"
    return Command(
        update={
            "messages": [
                HumanMessage(content=f"[{target} 재작업 요청] {feedback}")
            ]
        },
        goto="orchestrator",
    )
