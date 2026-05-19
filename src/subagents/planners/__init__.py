from src.subagents.planners.product_discovery import build_product_discovery
from src.subagents.planners.system_architect import build_system_architect
from src.subagents.spec import SubagentSpec

planner_graphs = {
    "product_discovery": SubagentSpec(
        graph_factory=build_product_discovery,
        description="사용자가 만들고 싶은 서비스/앱/제품을 구체적으로 설명했을 때만 호출. 인사, 질문, 잡담에는 호출하지 않는다.",
    ),
    "system_architect": SubagentSpec(
        graph_factory=build_system_architect,
        description=(
            "PRD가 저장된 직후, PRD를 기반으로 기술 스택·데이터베이스·디렉토리 구조·"
            "주요 의존성·ADR을 정의해 architecture.md를 작성한다. "
            "PRD가 없으면 호출 금지. 인사·잡담·구현 단계 진입 시점에는 호출하지 않는다."
        ),
    ),
}
