from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSPORT_PATTERN = r"^\d{4} \d{6}$"


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=255)
    passport_data: str = Field(pattern=PASSPORT_PATTERN)
    birth_date: date
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    pdn_consent: Literal[True]

    @field_validator("passport_data")
    @classmethod
    def validate_passport_data(cls, value: str) -> str:
        if len(value) != 11 or value[4] != " " or not value.replace(" ", "").isdigit():
            raise ValueError("Паспорт должен быть в формате 1234 123456")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value.year < 1900 or value > date.today():
            raise ValueError("Некорректная дата рождения")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=64)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    full_name: str
    passport_data: str
    birth_date: date
    email: EmailStr

    model_config = {"from_attributes": True}


class UserCreateDB(BaseModel):
    full_name: str
    passport_data: str
    birth_date: date
    email: EmailStr
    password_hash: str


class InsuranceInfoResponse(BaseModel):
    title: str
    paragraphs: list[str]
    note_for_guests: str


class PersonalDataPolicyResponse(BaseModel):
    title: str
    updated_at: str
    sections: list[str]


class CreateApplicationRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=255)
    passport_data: str = Field(pattern=PASSPORT_PATTERN)
    birth_date: date
    email: EmailStr
    workplace: str = Field(min_length=2, max_length=255)
    insurance_object: str = Field(min_length=2, max_length=255)
    insurance_period_months: int = Field(ge=1, le=240)
    insurance_cases: list[str] = Field(min_length=1)
    payout_amount: Decimal = Field(gt=0)
    pdn_consent: Literal[True]

    @field_validator("passport_data")
    @classmethod
    def validate_passport_data(cls, value: str) -> str:
        if len(value) != 11 or value[4] != " " or not value.replace(" ", "").isdigit():
            raise ValueError("Паспорт должен быть в формате 1234 123456")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value.year < 1900 or value > date.today():
            raise ValueError("Некорректная дата рождения")
        return value


class ApplicationResponse(BaseModel):
    id: int
    status: str
    full_name: str
    passport_data: str
    birth_date: date
    email: EmailStr
    workplace: str
    insurance_object: str
    insurance_period_months: int
    insurance_cases: list[str]
    payout_amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationCreateDB(BaseModel):
    user_id: int
    full_name: str
    passport_data: str
    birth_date: date
    email: EmailStr
    workplace: str
    insurance_object: str
    insurance_period_months: int
    insurance_cases: str
    payout_amount: Decimal
    status: str = "awaiting_payment"


class PaymentRequest(BaseModel):
    application_id: int
    payment_method: Literal["sbp", "card"]
    card_number: str | None = None
    card_holder: str | None = None
    card_expiry: str | None = None
    card_cvc: str | None = None


class PaymentResponse(BaseModel):
    payment_id: int
    application_id: int
    status: Literal["failed", "success"]
    message: str


class PaymentCreateDB(BaseModel):
    application_id: int
    payment_method: Literal["sbp", "card"]
    card_last4: str | None = None
    amount: Decimal
    status: Literal["failed", "success"]
    fail_reason: str | None = None


class ContractResponse(BaseModel):
    id: int
    contract_number: str
    application_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractCreateDB(BaseModel):
    user_id: int
    application_id: int
    contract_number: str
