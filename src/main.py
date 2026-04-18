import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, AsyncGenerator

from fastapi import Body, FastAPI
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

from src.agent import graph
from src.libs.path import AI_WORKSPACE
from src.schemas import PostBody

_DB_PATH = Path(os.environ.get("CHECKPOINT_DB", AI_WORKSPACE / "checkpoints.sqlite"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(_DB_PATH)) as checkpointer:
        app.state.agent = graph(checkpointer=checkpointer)
        yield


app = FastAPI(
    title="YourAiWorkforce", version="0.0.1", docs_url="/docs", lifespan=lifespan
)


async def generate_chat_responses(body: PostBody) -> AsyncGenerator[str, None]:
    agent = app.state.agent
    config = {"configurable": {"thread_id": body.thread_id}}

    snapshot = await agent.aget_state(config)
    is_interrupted = bool(snapshot.next)

    if is_interrupted:
        input_ = Command(resume={"type": body.type, "message": body.message})
    else:
        input_ = {"messages": [("user", body.message)]}

    async for chunk, _ in agent.astream(input_, config=config, stream_mode="messages"):
        content = str(chunk.content or "").strip()
        if content:
            yield chunk.content


@app.post("/")
async def root(body: Annotated[PostBody, Body(description="유저 입력")]):
    return StreamingResponse(
        generate_chat_responses(body), media_type="text/event-stream"
    )
