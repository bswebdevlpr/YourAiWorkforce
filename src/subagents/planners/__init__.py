from src.subagents.planners.product_discovery import build_product_discovery
from src.subagents.spec import SubagentSpec

planner_graphs = {
    "product_discovery": SubagentSpec(
        graph_factory=build_product_discovery,
        description="사용자가 만들고 싶은 서비스/앱/제품을 구체적으로 설명했을 때만 호출. 인사, 질문, 잡담에는 호출하지 않는다.",
    ),
}
