from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, class_mapper
import asyncio

from db.config import settings


engine = create_async_engine(settings.ASYNC_DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, autoflush=True, expire_on_commit=False, autocommit=False
)


class Base(DeclarativeBase):
    
    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}

async def get_async_session():
    async with async_session_maker() as session:
        yield session

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print('DATABASE MODEL INITIALISED')


def run_init_models():
    asyncio.run(init_models())