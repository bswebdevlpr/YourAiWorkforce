import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, AsyncGenerator

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

from src.agent import graph_with_checkpointer
from src.libs.path import CHECKPOINT_DB_PATH
from src.schemas import PostBody

_DB_PATH = Path(os.environ.get("CHECKPOINT_DB", CHECKPOINT_DB_PATH))


@asynccontextmanager
async def lifespan(app: FastAPI):
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(_DB_PATH)) as checkpointer:
        app.state.agent = graph_with_checkpointer(checkpointer)
        yield


app = FastAPI(
    title="YourAiWorkforce", version="0.0.1", docs_url="/docs", lifespan=lifespan
)


async def generate_chat_responses(agent, config, input_) -> AsyncGenerator[str, None]:
    async for chunk, _ in agent.astream(input_, config=config, stream_mode="messages"):
        content = str(chunk.content or "").strip()
        if content:
            yield chunk.content


@app.post("/")
async def root(body: Annotated[PostBody, Body(description="유저 입력")]):
    agent = app.state.agent
    config = {"configurable": {"thread_id": body.thread_id}}

    snapshot = await agent.aget_state(config)
    thread_exists = bool(snapshot.values)
    is_interrupted = bool(snapshot.next)

    if body.type == "new":
        if thread_exists:
            raise HTTPException(
                status_code=400,
                detail="thread_id already exists; issue a new thread_id for new work",
            )
        input_ = {"messages": [("user", body.message)]}
    elif is_interrupted:
        if body.type not in ("message", "reply", "complete", "reject", "approve"):
            raise HTTPException(
                status_code=400,
                detail=f"invalid type '{body.type}' for interrupted thread",
            )
        input_ = Command(resume={"type": body.type, "message": body.message})
    else:
        # fresh thread 또는 END 도달 후 이어서 진행 — message만 허용
        if body.type != "message":
            raise HTTPException(
                status_code=400,
                detail=f"non-interrupted thread requires type='message' or 'new', got '{body.type}'",
            )
        input_ = {"messages": [("user", body.message)]}

    return StreamingResponse(
        generate_chat_responses(agent, config, input_),
        media_type="text/event-stream",
    )
