import operator
from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    _last_subgraph: str
    _approved_subagents: Annotated[list[str], operator.add]
    _subagent_threads: Annotated[dict[str, str], operator.or_]
    _active_subagent: str
    _active_subagent_thread: str
    is_done: bool
