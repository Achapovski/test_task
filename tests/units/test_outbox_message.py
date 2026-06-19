from infra.outbox.enums import OutboxMessageStatusEnum
from src.infra.outbox.schemes import OutboxMessageScheme


def test_should_create_outbox_message():
    message = OutboxMessageScheme(body={"payment_id": "123"}, topic="payments.new")

    assert message.id is not None
    assert message.body == {"payment_id": "123"}
    assert message.topic == "payments.new"
    assert message.status == OutboxMessageStatusEnum.PENDING
    assert message.created_at is not None


def test_should_allow_explicit_status():
    message = OutboxMessageScheme(
        body={"payment_id": "123"}, topic="payments.new", status=OutboxMessageStatusEnum.SUCCESS
    )

    assert message.status == OutboxMessageStatusEnum.SUCCESS


def test_should_preserve_body_and_topic():
    body = {"payment_id": "123", "status": "SUCCESS"}
    topic = "payments.new"

    message = OutboxMessageScheme(body=body, topic=topic)

    assert message.body == body
    assert message.topic == topic
