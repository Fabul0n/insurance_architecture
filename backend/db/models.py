from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class InsuranceUser(Base):
    __tablename__ = "insurance_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255))
    passport_data: Mapped[str] = mapped_column(String(128))
    birth_date: Mapped[date] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    applications: Mapped[list["InsuranceApplication"]] = relationship(
        "InsuranceApplication", back_populates="user", cascade="all, delete-orphan"
    )
    contracts: Mapped[list["InsuranceContract"]] = relationship(
        "InsuranceContract", back_populates="user", cascade="all, delete-orphan"
    )


class InsuranceApplication(Base):
    __tablename__ = "insurance_applications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("insurance_users.id", ondelete="CASCADE"))

    full_name: Mapped[str] = mapped_column(String(255))
    passport_data: Mapped[str] = mapped_column(String(128))
    birth_date: Mapped[date] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String(255))

    workplace: Mapped[str] = mapped_column(String(255))
    insurance_object: Mapped[str] = mapped_column(String(255))
    insurance_period_months: Mapped[int]
    insurance_cases: Mapped[str] = mapped_column(Text)
    payout_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(32), default="awaiting_payment", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["InsuranceUser"] = relationship("InsuranceUser", back_populates="applications")
    payments: Mapped[list["InsurancePayment"]] = relationship(
        "InsurancePayment", back_populates="application", cascade="all, delete-orphan"
    )
    contract: Mapped["InsuranceContract | None"] = relationship(
        "InsuranceContract", back_populates="application", uselist=False
    )


class InsurancePayment(Base):
    __tablename__ = "insurance_payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("insurance_applications.id", ondelete="CASCADE"), index=True
    )
    payment_method: Mapped[str] = mapped_column(String(16))
    card_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(16))
    fail_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    application: Mapped["InsuranceApplication"] = relationship(
        "InsuranceApplication", back_populates="payments"
    )


class InsuranceContract(Base):
    __tablename__ = "insurance_contracts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("insurance_users.id", ondelete="CASCADE"))
    application_id: Mapped[int] = mapped_column(
        ForeignKey("insurance_applications.id", ondelete="CASCADE"), unique=True
    )
    contract_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["InsuranceUser"] = relationship("InsuranceUser", back_populates="contracts")
    application: Mapped["InsuranceApplication"] = relationship(
        "InsuranceApplication", back_populates="contract"
    )