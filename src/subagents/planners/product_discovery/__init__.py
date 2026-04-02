from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from src.config import MODEL_NAME_PLANNER
from src.libs.model import create_chat_model
from src.libs.persona import PRODUCT_DISCOVERY, load_persona
from src.subagents.planners.product_discovery.tools import save_prd

product_discovery_agent = create_agent(
    model=create_chat_model(MODEL_NAME_PLANNER, temperature=1.0),
    system_prompt=load_persona(PRODUCT_DISCOVERY),
)


@tool(
    "product_discovery",
    description="원시 사용자 아이디어를 구조화된 제품 요구사항으로 변환할때 호출",
)
def call_product_discovery_agent(query: str, config: RunnableConfig) -> str:
    result = product_discovery_agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
    )
    content = result["messages"][-1].content
    save_result = save_prd(content)
    return f"{content}\n\n---\n{save_result}"
