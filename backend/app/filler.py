"""Создаёт первого администратора при старте, если в БД нет ни одного пользователя с is_admin=True."""
import asyncio
from sqlalchemy import select
from db.database import async_session_maker
from db.models import User
from app.services.auth import hash_password
from app.config import get_settings


async def ensure_admin() -> None:
    settings = get_settings()
    team_uid = settings.ADMIN_TEAM_UID
    password = settings.ADMIN_PASSWORD
    team_name = settings.ADMIN_TEAM_NAME
    if not team_uid or not password:
        return
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.is_admin.is_(True)).limit(1))
        if result.scalar_one_or_none() is not None:
            return
        existing = await session.execute(select(User).where(User.team_uid == team_uid))
        if existing.scalar_one_or_none() is not None:
            return
        user = User(
            team_uid=team_uid,
            team_name=team_name,
            password_hash=hash_password(password),
            is_admin=True,
        )
        session.add(user)
        await session.commit()
