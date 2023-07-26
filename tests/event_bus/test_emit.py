import pytest

from pytest_mock import MockerFixture

from fast_sqlalchemy.event_bus.bus import LocalEventBus
from fast_sqlalchemy.event_bus.contexts import event_queue_ctx, _event_queue
from fast_sqlalchemy.event_bus.emit import emit, publish_events


def test_emit(mocker: MockerFixture, event_bus_store_ctx):
    class CustomEvent:
        pass
    event = CustomEvent()
    event_bus = mocker.MagicMock()
    with event_bus_store_ctx([event_bus]), event_queue_ctx():
        emit(event)
        assert _event_queue.get()[0] == event
        assert len(_event_queue.get()) == 1
        event_bus.handle_event.assert_called()

@pytest.mark.asyncio
async def test_publish(mocker: MockerFixture, event_bus_store_ctx):
    event_bus = mocker.AsyncMock()
    with event_bus_store_ctx([event_bus]):
        await publish_events()
        event_bus.async_handle_events.assert_called_with(_event_queue.get())


@pytest.mark.asyncio
async def test_exec_event_handler(mocker: MockerFixture, event_bus_store_ctx):
    event_bus = LocalEventBus()
    handler = mocker.MagicMock()
    class CustomEvent:
        pass
    event_bus.subscribe([CustomEvent], handler, on_publish=True)
    with event_bus_store_ctx([event_bus]):
        event = CustomEvent()
        emit(event)
        handler.assert_not_called()
        await publish_events()
        handler.assert_called_with(event)
