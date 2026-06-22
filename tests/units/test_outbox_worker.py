import pytest

from src.infra.outbox.schemes import OutboxMessageScheme


@pytest.mark.asyncio
async def test_should_publish_all_messages(outbox_worker, outbox_uow, outbox_repository, broker):
    msg1 = OutboxMessageScheme(body={"id": 1}, topic="payments.new")
    msg2 = OutboxMessageScheme(body={"id": 2}, topic="payments.new")

    outbox_repository.get_unpublished.return_value = [msg1, msg2]
    await outbox_worker.process_message()

    assert broker.publish.await_count == 2
    assert outbox_repository.mark_as_published.await_count == 2
    outbox_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_commit_when_no_messages(outbox_worker, outbox_uow, outbox_repository, broker):
    outbox_repository.get_unpublished.return_value = []

    await outbox_worker.process_message()

    broker.publish.assert_not_awaited()
    outbox_repository.mark_as_published.assert_not_awaited()

    outbox_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_not_commit_when_publish_failed(outbox_worker, outbox_uow, outbox_repository, broker):
    msg = OutboxMessageScheme(body={"id": 1}, topic="payments.new")

    outbox_repository.get_unpublished.return_value = [msg]
    broker.publish.side_effect = Exception("RabbitMQ is down")

    with pytest.raises(Exception):
        await outbox_worker.process_message()

    outbox_repository.mark_as_published.assert_not_awaited()
    outbox_uow.commit.assert_not_awaited()
