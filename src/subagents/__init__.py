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
                "properties": {
                    "query": {"type": "string", "description": "이번 작업의 핵심 요청. 대표님이 방금 말씀하신 의도를 한 문장으로 정리."},
                    "context_hints": {"type": "string", "description": "이번 작업에 참고할 결정사항/제약/배경 맥락 요약. 직전 대화에서 드러난 선호/방향/제약을 한두 단락으로 정리. 없으면 빈 문자열."},
                    "artifact_refs": {"type": "array", "items": {"type": "string"}, "description": "이번 작업에 참고할 산출물 파일 경로 목록 (예: ai-workspace/specs/prd.md). 없으면 빈 배열."},
                },
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
