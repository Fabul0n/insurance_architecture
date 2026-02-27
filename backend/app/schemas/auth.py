from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    team_uid: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInToken(BaseModel):
    user_id: int
    team_uid: str
    is_admin: bool
