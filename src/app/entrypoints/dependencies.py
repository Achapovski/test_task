from dishka import Provider, Scope, provide

from src.app.use_cases.change_payment_status import ChangePaymentStatusUseCase
from src.app.use_cases.create_payment import CreatePaymentUseCase
from src.app.use_cases.get_payment import GetPaymentUseCase
from src.app.use_cases.set_payment_delivery import SetPaymentDeliveryUseCase


class UseCaseProvider(Provider):
    scope: Scope = Scope.REQUEST

    create_payment_use_case: CreatePaymentUseCase = provide(CreatePaymentUseCase)
    get_payment_use_case: GetPaymentUseCase = provide(GetPaymentUseCase)
    change_payment_status_uce_case: ChangePaymentStatusUseCase = provide(ChangePaymentStatusUseCase)
    set_payment_delivery_use_case: SetPaymentDeliveryUseCase = provide(SetPaymentDeliveryUseCase)
