from typing import Literal
from sqlalchemy.orm.attributes import InstrumentedAttribute as TableAttr

type UserRelationships = list[Literal["messages", "uploaded_files", "request_logs"]] | None
type ChatMessageRelationships = list[Literal["user"]] | None
type UploadedFileRelationships = list[Literal["user"]] | None
type RequestLogRelationships = list[Literal["user"]] | None
