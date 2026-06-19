from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Header, status

from src.app.dto.payments import PaymentCreateRequestDTO, PaymentCreateResponseDTO, PaymentGetResponseDTO
from src.app.use_cases.create_payment import CreatePaymentUseCase
from src.app.use_cases.get_payment import GetPaymentUseCase
from src.core.security.security import require_api_key

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"], route_class=DishkaRoute)


@router.get(
    path="/{payment_id}",
    response_model=PaymentGetResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_api_key)],
)
async def get_payment(payment_id: UUID, use_case: FromDishka[GetPaymentUseCase]) -> PaymentGetResponseDTO:
    return await use_case.execute(payment_id)


@router.post(
    path="/",
    response_model=PaymentCreateResponseDTO,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_api_key)],
)
async def create_payment(
    payment: PaymentCreateRequestDTO,
    use_case: FromDishka[CreatePaymentUseCase],
    idempotency_key: UUID = Header(..., alias="Idempotency-Key"),
) -> PaymentCreateResponseDTO:
    return await use_case.execute(idempotency_key=idempotency_key, payment=payment)
