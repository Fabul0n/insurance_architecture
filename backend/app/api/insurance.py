from io import BytesIO

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.session_maker import get_session
from app.loggers.document_logger import get_document_logger
from app.misc.auth_depends import get_current_user
from app.schemas.insurance import (
    ApplicationResponse,
    ContractResponse,
    CreateApplicationRequest,
    InsuranceInfoResponse,
    PersonalDataPolicyResponse,
    LoginRequest,
    PaymentRequest,
    PaymentResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import create_access_token
from app.services.insurance import (
    application_to_response,
    build_contract_docx_from_template,
    build_contract_pdf_from_template,
    create_application as create_application_service,
    get_contract_for_user,
    get_last_application as get_last_application_service,
    get_personal_data_policy,
    list_applications as list_applications_service,
    get_public_content as get_public_content_service,
    list_contracts as list_contracts_service,
    login_user,
    make_payment,
    register_user,
)
from db.models import InsuranceUser

document_logger = get_document_logger()

router = APIRouter(prefix="/insurance", tags=["insurance"])


@router.get("/content", response_model=InsuranceInfoResponse)
async def get_public_content() -> InsuranceInfoResponse:
    return InsuranceInfoResponse(**get_public_content_service())


@router.get("/policy", response_model=PersonalDataPolicyResponse)
async def get_policy() -> PersonalDataPolicyResponse:
    return PersonalDataPolicyResponse(**get_personal_data_policy())


@router.post("/auth/register", response_model=TokenResponse)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user = await register_user(session, body)
    token = create_access_token({"user_id": user.id, "email": user.email})
    return TokenResponse(access_token=token)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user = await login_user(session, body.email, body.password)
    token = create_access_token({"user_id": user.id, "email": user.email})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user: InsuranceUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)


@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    body: CreateApplicationRequest,
    user: InsuranceUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse:
    application = await create_application_service(
        session,
        user,
        full_name=body.full_name,
        passport_data=body.passport_data,
        birth_date=body.birth_date,
        email=body.email,
        workplace=body.workplace,
        insurance_object=body.insurance_object,
        insurance_period_months=body.insurance_period_months,
        insurance_cases=body.insurance_cases,
        payout_amount=body.payout_amount,
    )
    return application_to_response(application)


@router.get("/applications/last", response_model=ApplicationResponse | None)
async def get_last_application(
    user: InsuranceUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse | None:
    application = await get_last_application_service(session, user.id)
    if not application:
        return None
    return application_to_response(application)


@router.get("/applications", response_model=list[ApplicationResponse])
async def get_applications(
    user: InsuranceUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ApplicationResponse]:
    applications = await list_applications_service(session, user.id)
    return [application_to_response(item) for item in applications]


@router.post("/payments", response_model=PaymentResponse)
async def pay_for_application(
    body: PaymentRequest,
    user: InsuranceUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PaymentResponse:
    return await make_payment(session, user, body)


@router.get("/contracts", response_model=list[ContractResponse])
async def list_contracts(
    user: InsuranceUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ContractResponse]:
    contracts = await list_contracts_service(session, user.id)
    return [
        ContractResponse(
            id=item.application_id,
            contract_number=item.contract_number,
            application_id=item.application_id,
            created_at=item.created_at,
        )
        for item in contracts
    ]


@router.get("/contracts/{contract_id}/download")
async def download_contract(
    contract_id: int,
    request: Request,
    format: str = Query(default="pdf", pattern="^(pdf|docx)$"),
    user: InsuranceUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    contract, application = await get_contract_for_user(session, contract_id, user.id)
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    if format == "pdf":
        buffer = BytesIO(build_contract_pdf_from_template(contract, application))
        document_logger.info(
            "event=%s user_id=%s contract_id=%s application_id=%s format=%s ip=%s user_agent=%s",
            "contract_download",
            user.id,
            contract.id,
            application.id,
            "pdf",
            client_ip,
            user_agent,
        )
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="contract-{contract.contract_number}.pdf"'
            },
        )

    doc_buffer = BytesIO(build_contract_docx_from_template(contract, application))
    document_logger.info(
        "event=%s user_id=%s contract_id=%s application_id=%s format=%s ip=%s user_agent=%s",
            "contract_download",
            user.id,
            contract.id,
            application.id,
            "docx",
            client_ip,
            user_agent,
        )
    return StreamingResponse(
        doc_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="contract-{contract.contract_number}.docx"'},
    )
