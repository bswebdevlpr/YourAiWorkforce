from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class SubagentState(TypedDict, total=False):
    """서브에이전트 전용 격리 상태.

    parent AgentState와 별개로, 서브에이전트는 자기 대화 messages와 완료 여부만 본다.
    parent의 _last_subgraph, _approved_subagents, _subagent_threads 등에 접근 불가.
    """

    messages: Annotated[list, add_messages]
    is_done: bool
