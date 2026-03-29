from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool

from src.config import MODEL_NAME_PLANNER
from src.libs.model import create_chat_model
from src.libs.persona import PRODUCT_DISCOVERY, load_persona
from src.subagents.planners.product_discovery.tools import save_prd

product_discovery_agent = create_agent(
    model=create_chat_model(MODEL_NAME_PLANNER, temperature=1.0),
    system_prompt=load_persona(PRODUCT_DISCOVERY),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "save_prd": True,  # PRD 저장 전 사용자 승인 필요
            }
        )
    ],
    tools=[save_prd],
)


@tool(
    "product_discovery",
    description="원시 사용자 아이디어를 구조화된 제품 요구사항으로 변환할때 호출",
)
def call_product_discovery_agent(query: str):
    result = product_discovery_agent.invoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    return result["messages"][-1].content
