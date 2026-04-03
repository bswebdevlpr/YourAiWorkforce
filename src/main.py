from typing import Annotated, AsyncGenerator

from fastapi import Body, FastAPI
from fastapi.responses import StreamingResponse

from src.agent import graph
from src.schemas import PostBody

app = FastAPI(title="YourAiWorkforce", version="0.0.1", docs_url="/docs")
agent = graph()


async def generate_chat_responses(message: str) -> AsyncGenerator[str, None]:
    async for message_chunk, metadata in agent.astream(
        {"messages": [("user", message)]}, stream_mode="messages"
    ):
        content = str(message_chunk.content or "").strip()
        if content:
            yield message_chunk.content


@app.post("/")
async def root(body: Annotated[PostBody, Body(description="유저의 질문 메시지")]):
    return StreamingResponse(
        generate_chat_responses(body.message), media_type="text/event-stream"
    )
