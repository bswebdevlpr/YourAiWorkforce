import operator
from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    _last_subgraph: str
    _approved_subagents: Annotated[list[str], operator.add]
    is_done: bool
