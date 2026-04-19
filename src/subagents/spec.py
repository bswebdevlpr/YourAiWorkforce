from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SubagentSpec:
    graph_factory: Callable[[Any], Any]  # (checkpointer) -> CompiledGraph
    description: str
