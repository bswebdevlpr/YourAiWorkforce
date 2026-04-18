from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
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
      - {"type": "complete"}             → exit_goto (루프 종료)
      - {"type": "reject", "message"?}   → exit_goto (중단 맥락 첨부)
      - {"type": "message", "message"}   → continue_goto (루프 지속)
      - 그 외 dict/문자열                → continue_goto (message로 폴백)
    """

    def wait_for_user(state: AgentState):
        last = state["messages"][-1].content
        decision = interrupt(
            {"result": last, "options": ["reply", "complete", "reject"]}
        )

        if isinstance(decision, dict):
            dtype = decision.get("type")
            if dtype == "complete":
                return Command(goto=exit_goto)
            if dtype == "reject":
                reason = decision.get("message", "사용자가 작업을 중단했습니다.")
                return Command(
                    update={"messages": [AIMessage(content=f"[작업 중단] {reason}")]},
                    goto=exit_goto,
                )
            text = decision.get("message", "")
        else:
            text = str(decision)

        return Command(
            update={"messages": [HumanMessage(content=text)]},
            goto=continue_goto,
        )

    return wait_for_user


def review(state: AgentState):
    """외부 그래프에서 산출물을 사용자에게 최종 확인받는 노드."""
    last_content = state["messages"][-1].content
    decision = interrupt(
        {
            "result": last_content,
            "options": ["approve", "reject"],
        }
    )
    if isinstance(decision, dict) and decision.get("type") == "reject":
        feedback = decision.get("message", "다시 작업해주세요.")
        return Command(
            update={"messages": [HumanMessage(content=feedback)]},
            goto=state.get("_last_subgraph") or END,
        )
    return state
