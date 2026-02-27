from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.schemas.insurance import ApplicationCreateDB, ContractCreateDB, PaymentCreateDB, UserCreateDB
from db.models import InsuranceApplication, InsuranceContract, InsurancePayment, InsuranceUser


class InsuranceUserDAO(BaseDAO[InsuranceUser]):
    @classmethod
    async def get_by_email(
        cls,
        session: AsyncSession,
        email: str,
        mute_not_found_exception: bool = False,
    ) -> InsuranceUser | None:
        return await cls._get_one(
            session,
            email=email,
            mute_not_found_exception=mute_not_found_exception,
        )

    @classmethod
    async def create_user(cls, session: AsyncSession, data: UserCreateDB) -> InsuranceUser:
        return await cls._create(session, data)


class InsuranceApplicationDAO(BaseDAO[InsuranceApplication]):
    @classmethod
    async def create_application(
        cls, session: AsyncSession, data: ApplicationCreateDB
    ) -> InsuranceApplication:
        return await cls._create(session, data)

    @classmethod
    async def get_last_for_user(
        cls, session: AsyncSession, user_id: int
    ) -> InsuranceApplication | None:
        query = (
            select(InsuranceApplication)
            .where(InsuranceApplication.user_id == user_id)
            .order_by(InsuranceApplication.id.desc())
            .limit(1)
        )
        return await session.scalar(query)

    @classmethod
    async def get_for_user(
        cls, session: AsyncSession, application_id: int, user_id: int
    ) -> InsuranceApplication | None:
        query = select(InsuranceApplication).where(
            InsuranceApplication.id == application_id,
            InsuranceApplication.user_id == user_id,
        )
        return await session.scalar(query)

    @classmethod
    async def list_for_user(cls, session: AsyncSession, user_id: int) -> list[InsuranceApplication]:
        return await cls._get_many(session, user_id=user_id, order_by="id", order_desc=True)


class InsurancePaymentDAO(BaseDAO[InsurancePayment]):
    @classmethod
    async def create_payment(cls, session: AsyncSession, data: PaymentCreateDB) -> InsurancePayment:
        return await cls._create(session, data)


class InsuranceContractDAO(BaseDAO[InsuranceContract]):
    @classmethod
    async def create_contract(cls, session: AsyncSession, data: ContractCreateDB) -> InsuranceContract:
        return await cls._create(session, data)

    @classmethod
    async def list_for_user(cls, session: AsyncSession, user_id: int) -> list[InsuranceContract]:
        return await cls._get_many(session, user_id=user_id, order_by="id", order_desc=True)

    @classmethod
    async def get_for_user(
        cls, session: AsyncSession, contract_id: int, user_id: int
    ) -> InsuranceContract | None:
        query = select(InsuranceContract).where(
            InsuranceContract.user_id == user_id,
            or_(
                InsuranceContract.id == contract_id,
                InsuranceContract.application_id == contract_id,
            ),
        )
        return await session.scalar(query)
