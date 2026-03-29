from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware

from src.config import MODEL_NAME_DEFUALT
from src.libs.model import create_chat_model
from src.libs.persona import ORCHESTRATOR, load_persona
from src.subagents import subagents


def graph():
    return create_agent(
        model=create_chat_model(MODEL_NAME_DEFUALT),
        system_prompt=load_persona(ORCHESTRATOR),
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "product_discovery": True,
                }
            )
        ],
        tools=subagents,
    )
