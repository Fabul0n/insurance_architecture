from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.dao import InsuranceUserDAO
from app.dao.session_maker import get_session
from app.services.auth import decode_access_token
from db.models import InsuranceUser

security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return int(payload["user_id"])


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> InsuranceUser:
    user = await InsuranceUserDAO._get(session, user_id, mute_not_found_exception=True)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
