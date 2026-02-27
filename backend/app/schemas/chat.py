from pydantic import BaseModel, Field
from datetime import datetime


class MessageIn(BaseModel):
    content: str = Field(..., min_length=1)
    llm_id: str = Field(..., pattern="^llm_[123]$")


class ChatMessageCreate(BaseModel):
    user_id: int
    llm_id: str
    role: str
    content: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSendRequest(BaseModel):
    content: str = Field(..., min_length=1)
    llm_id: str = Field(..., pattern="^llm_[123]$")
    file_ids: list[int] = Field(default_factory=list)
