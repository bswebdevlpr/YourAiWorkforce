from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class SubagentState(TypedDict, total=False):
    """서브에이전트 전용 상태 스키마.

    parent AgentState의 제어 필드(_last_subgraph, _approved_subagents, _subagent_threads 등)는
    스키마에서 제외되어 서브에이전트가 접근할 수 없다.

    단, `messages`는 add_messages로 parent와 공유되는 채널이라 서브에이전트 LLM은 진입 시점의
    parent messages를 그대로 본다(= inbound 격리는 아님, 브리핑 패킷으로 보완). 격리 효과는
    outbound 방향으로만 성립한다: 종료 직전 finalize가 `_entry_count` 이후 내부 messages를
    RemoveMessage로 청소해 parent thread 누적을 차단한다.
    """

    messages: Annotated[list, add_messages]
    is_done: bool
    _entry_count: int
