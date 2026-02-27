from datetime import datetime
from pydantic import BaseModel


class UploadedFileCreate(BaseModel):
    user_id: int
    original_filename: str
    stored_path: str
    mime_type: str | None = None


class UploadedFileOut(BaseModel):
    id: int
    original_filename: str
    stored_path: str
    mime_type: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
