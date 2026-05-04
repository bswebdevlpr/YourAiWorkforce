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
                    "query": {"type": "string", "description": "대표님이 직접 말씀하신 의도의 짧은 명사구 요약 (1줄, 60자 이내). AI가 사용자에게 할 질문·답변·지시문을 절대 작성하지 않는다. 의문문·명령문·'대표님!' 호칭·이모지 모두 금지."},
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
