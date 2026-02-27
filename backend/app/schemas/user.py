from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    team_uid: str = Field(..., min_length=1, max_length=64)
    team_name: str = Field(..., min_length=1, max_length=256)
    password: str = Field(..., min_length=1)
    password_confirm: str = Field(..., min_length=1)
    team_members: str | None = None
    educational_org: str | None = None


class UserCreateDB(BaseModel):
    team_uid: str
    team_name: str
    password_hash: str
    team_members: str | None = None
    educational_org: str | None = None


class UserResponse(BaseModel):
    id: int
    team_uid: str
    team_name: str
    team_members: str | None
    educational_org: str | None
    lock_team_name: bool
    lock_team_members: bool
    lock_educational_org: bool
    is_frozen: bool
    is_admin: bool

    model_config = {"from_attributes": True}


class UserUpdateProfile(BaseModel):
    team_name: str | None = Field(None, min_length=1, max_length=256)
    team_members: str | None = None
    educational_org: str | None = None


class UserUpdateAdmin(BaseModel):
    team_uid: str | None = Field(None, min_length=1, max_length=64)
    team_name: str | None = Field(None, min_length=1, max_length=256)
    team_members: str | None = None
    educational_org: str | None = None
    lock_team_name: bool | None = None
    lock_team_members: bool | None = None
    lock_educational_org: bool | None = None
    is_frozen: bool | None = None


class FreezeBody(BaseModel):
    is_frozen: bool
