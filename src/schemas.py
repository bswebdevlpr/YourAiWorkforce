from pydantic import BaseModel


class PostBody(BaseModel):
    message: str
