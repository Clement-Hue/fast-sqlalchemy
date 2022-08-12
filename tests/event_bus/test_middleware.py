import pytest
from pytest_mock import MockerFixture

from fast_alchemy.event_bus.contexts import event_bus_store
from fast_alchemy.event_bus.bus import local_event_bus
from fast_alchemy.event_bus.middleware import EventBusMiddleware


def test_register_handlers(mocker: MockerFixture, event_bus_store_ctx):
    assert len(event_bus_store) == 0
    with event_bus_store_ctx():
        middleware = EventBusMiddleware(mocker.MagicMock(), [local_event_bus])
        assert len(event_bus_store) == 1
        assert list(event_bus_store)[0] == local_event_bus

@pytest.mark.asyncio
async def test_publish_events(mocker: MockerFixture, event_bus_store_ctx):
    publish_mock = mocker.patch("fast_alchemy.event_bus.middleware.publish_events")
    assert len(event_bus_store) == 0
    event_bus = mocker.AsyncMock()
    with event_bus_store_ctx():
        middleware = EventBusMiddleware(mocker.AsyncMock(), [event_bus])
        assert len(event_bus_store) == 1
        await middleware.dispatch(mocker.MagicMock(), mocker.AsyncMock())
        publish_mock.assert_called()

@pytest.mark.asyncio
async def test_publish_not_call_if_status_is_above_400(mocker: MockerFixture, event_bus_store_ctx):
    publish_mock = mocker.patch("fast_alchemy.event_bus.middleware.publish_events")
    event_bus = mocker.AsyncMock()
    response = mocker.MagicMock(status_code=400)
    call_next = mocker.AsyncMock(return_value=response)
    with event_bus_store_ctx():
        middleware = EventBusMiddleware(mocker.AsyncMock(), [event_bus])
        await middleware.dispatch(mocker.MagicMock(), call_next)
        publish_mock.assert_not_called()

