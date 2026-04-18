from src.subagents.planners import planner_graphs
from src.subagents.spec import SubagentSpec

SUBAGENT_REGISTRY: dict[str, SubagentSpec] = {**planner_graphs}

SUBAGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": spec.description,
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "사용자 요청 내용"}},
                "required": ["query"],
            },
        },
    }
    for name, spec in SUBAGENT_REGISTRY.items()
]

UTILITY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "reset_project",
            "description": "사용자가 기존과 완전히 다른 새로운 아이디어를 제시했을 때 호출. 기존 산출물을 삭제하고 새 프로젝트를 시작한다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }
]

ALL_TOOLS = SUBAGENT_TOOLS + UTILITY_TOOLS
