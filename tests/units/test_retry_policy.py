from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import aiohttp
import pytest

from src.infra.messaging.consumer import send_webhook_consumer
from src.infra.messaging.events.emitted.events import PaymentProcessedEvent


@pytest.mark.asyncio
async def test_should_retry_webhook_and_send_successfully():
    event = PaymentProcessedEvent(
        id=uuid4(),
        event_id=uuid4(),
        amount=Decimal("100"),
        currency="USD",
        status="SUCCESS",
        webhook_url="https://example.com",
    )

    message = AsyncMock()

    response = AsyncMock()
    response.raise_for_status = MagicMock()

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = response
    context_manager.__aexit__.return_value = None

    http_client = MagicMock()

    http_client.post.side_effect = [aiohttp.ClientError(), context_manager]

    with patch("src.infra.messaging.consumer.asyncio.sleep", new_callable=AsyncMock) as sleep_mock:
        await send_webhook_consumer(event=event, http_client=http_client, message=message)

    assert http_client.post.call_count == 2

    sleep_mock.assert_awaited_once_with(2)

    message.ack.assert_awaited_once()
    message.nack.assert_not_awaited()
