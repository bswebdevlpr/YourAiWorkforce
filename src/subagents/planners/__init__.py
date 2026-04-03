from src.subagents.planners.product_discovery import product_discovery_graph

planner_graphs = {
    "product_discovery": (
        product_discovery_graph,
        "사용자가 만들고 싶은 서비스/앱/제품을 구체적으로 설명했을 때만 호출. 인사, 질문, 잡담에는 호출하지 않는다.",
        True,  # interrupt 필요
    ),
}
