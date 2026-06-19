from src.domains.payments.domain.constraints import PaymentStatusEnum


def test_should_change_pending_status(payment_factory):
    payment = payment_factory()

    payment.set_status(PaymentStatusEnum.SUCCESS)

    assert payment.status.value == PaymentStatusEnum.SUCCESS


def test_should_not_change_success_status(payment_factory):
    payment = payment_factory()

    payment.set_status(PaymentStatusEnum.SUCCESS)
    payment.set_status(PaymentStatusEnum.FAILED)

    assert payment.status.value == PaymentStatusEnum.SUCCESS


def test_should_not_change_failed_status(payment_factory):
    payment = payment_factory()

    payment.set_status(PaymentStatusEnum.FAILED)
    payment.set_status(PaymentStatusEnum.SUCCESS)

    assert payment.status.value == PaymentStatusEnum.FAILED
