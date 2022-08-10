import pytest

from pytest_mock import MockerFixture

from fast_alchemy.event_bus.contexts import event_queue_ctx, event_queue
from fast_alchemy.event_bus.emit import emit, publish_events


def test_emit(mocker: MockerFixture, event_bus_store_ctx):
    class CustomEvent:
        pass
    event = CustomEvent()
    event_bus = mocker.MagicMock()
    with event_bus_store_ctx([event_bus]), event_queue_ctx():
        emit(event)
        assert event_queue.get()[0] == event
        assert len(event_queue.get()) == 1
        event_bus.handle_event.assert_called()

@pytest.mark.asyncio
async def test_publish(mocker: MockerFixture, event_bus_store_ctx):
    event_bus = mocker.AsyncMock()
    with event_bus_store_ctx([event_bus]):
        await publish_events()
        event_bus.handle_async_events.assert_called_with(event_queue.get())
