from pydantic import BaseModel


class TweetStreamRequest(BaseModel):
    action: str


class TweetStreamResponse(BaseModel):
    message: str
