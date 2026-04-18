from typing import Literal

from pydantic import BaseModel


class PostBody(BaseModel):
    message: str
    thread_id: str
    type: Literal["message", "complete", "reject"] = "message"
