from datetime import datetime
from pydantic import BaseModel


class RequestLogCreate(BaseModel):
    user_id: int
    llm_id: str
    request_text: str
    response_text: str | None = None
    file_ids: str | None = None


class RequestLogOut(BaseModel):
    id: int
    user_id: int
    llm_id: str
    request_text: str
    response_text: str | None
    file_ids: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
