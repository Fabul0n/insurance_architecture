import logging
from pydantic import BaseModel
from sqlalchemy import select, delete, Select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.database import Base

logger = logging.getLogger(__name__)


class BaseDAO[T: Base]:
    model: type

    def __init_subclass__(cls) -> None:
        for base in cls.__orig_bases__:
            if hasattr(base, "__args__") and base.__args__:
                cls.model = base.__args__[0]
                break

    @classmethod
    def _options_select_in_load(cls, relationship_names: list[str] | None) -> list:
        if not relationship_names:
            return []
        return [selectinload(getattr(cls.model, name)) for name in relationship_names if hasattr(cls.model, name)]

    @classmethod
    def _query_select_in_load(cls, query: Select, relationship_names: list[str] | None) -> Select:
        opts = cls._options_select_in_load(relationship_names or [])
        return query.options(*opts) if opts else query

    @classmethod
    def _filter(cls, **kwargs) -> Select:
        query = select(cls.model)
        for key, value in kwargs.items():
            if value is not None:
                query = query.filter_by(**{key: value})
        return query

    @classmethod
    async def _get_one(
        cls,
        session: AsyncSession,
        *,
        select_in_load: list[str] | None = None,
        mute_not_found_exception: bool = False,
        **filters,
    ) -> T | None:
        try:
            query = cls._filter(**filters)
            query = cls._query_select_in_load(query, select_in_load)
            obj = await session.scalar(query)
            if obj is None and not mute_not_found_exception:
                logger.critical("Object was not found. Model=%s filters=%s", cls.model, filters)
                raise ValueError("Object not found")
            return obj
        except SQLAlchemyError as e:
            logger.error("Error: %s", e)
            raise

    @classmethod
    async def _get(
        cls,
        session: AsyncSession,
        obj_id: int,
        select_in_load: list[str] | None = None,
        mute_not_found_exception: bool = False,
    ) -> T | None:
        return await cls._get_one(
            session, select_in_load=select_in_load, mute_not_found_exception=mute_not_found_exception, id=obj_id
        )

    @classmethod
    async def _get_many(
        cls,
        session: AsyncSession,
        *,
        page: int = 0,
        count: int = 0,
        select_in_load: list[str] | None = None,
        order_by: str | None = "id",
        order_desc: bool = False,
        **filters,
    ) -> list[T]:
        try:
            query = cls._filter(**filters)
            query = cls._query_select_in_load(query, select_in_load)
            if order_by and hasattr(cls.model, order_by):
                col = getattr(cls.model, order_by)
                query = query.order_by(col.desc() if order_desc else col.asc())
            if count > 0:
                query = query.offset(page * count).limit(count)
            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error("Error: %s", e)
            raise

    @classmethod
    async def _create(cls, session: AsyncSession, obj_schema: BaseModel) -> T:
        obj: T = cls.model(**obj_schema.model_dump(exclude_unset=True))
        session.add(obj)
        try:
            await session.flush()
            await session.refresh(obj)
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Error: %s", e)
            raise
        return obj

    @classmethod
    async def _update_obj(
        cls,
        session: AsyncSession,
        obj: T,
        data: BaseModel | dict,
        write_none: bool = False,
    ) -> T:
        try:
            d = data.model_dump() if hasattr(data, "model_dump") else data
            for key, value in d.items():
                if not hasattr(obj, key):
                    continue
                if not write_none and value is None:
                    continue
                setattr(obj, key, value)
            session.add(obj)
            await session.flush()
            return obj
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Error: %s", e)
            raise

    @classmethod
    async def _update(
        cls,
        session: AsyncSession,
        object_id: int,
        data: BaseModel | dict,
        write_none: bool = False,
        mute_not_found_exception: bool = False,
    ) -> T | None:
        obj = await cls._get(session, object_id, mute_not_found_exception=mute_not_found_exception)
        if obj is None:
            return None
        await cls._update_obj(session, obj, data, write_none)
        await session.refresh(obj)
        return obj

    @classmethod
    async def _delete_obj(cls, session: AsyncSession, obj: T) -> None:
        try:
            await session.delete(obj)
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Error: %s", e)
            raise

    @classmethod
    async def _delete(cls, session: AsyncSession, data_id: int) -> int:
        obj = await cls._get(session, data_id, mute_not_found_exception=True)
        if obj is None:
            return 0
        await cls._delete_obj(session, obj)
        return 1
