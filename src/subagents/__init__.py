from src.subagents.planners import planner_graphs

SUBAGENT_REGISTRY = {**planner_graphs}

SUBAGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "사용자 요청 내용"}},
                "required": ["query"],
            },
        },
    }
    for name, (_, desc, _) in SUBAGENT_REGISTRY.items()
]
