import pytest
from pytest_mock import MockerFixture

from fast_sqlalchemy.event_bus.bus import LocalEventBus
from fast_sqlalchemy.event_bus.contexts import event_bus_store
from fast_sqlalchemy.event_bus.middlewares import EventBusMiddleware


def test_register_handlers(mocker: MockerFixture, event_bus_store_ctx):
    bus = LocalEventBus()
    assert len(event_bus_store) == 0
    with event_bus_store_ctx():
        EventBusMiddleware(mocker.Mock(), [bus])
        assert len(event_bus_store) == 1
        assert list(event_bus_store)[0] == bus

@pytest.mark.asyncio
async def test_publish_events(mocker: MockerFixture, event_bus_store_ctx):
    publish_mock = mocker.patch("fast_sqlalchemy.event_bus.middlewares.publish_events")
    assert len(event_bus_store) == 0
    event_bus = mocker.AsyncMock()
    response = mocker.MagicMock(status_code=201)
    with event_bus_store_ctx():
        middleware = EventBusMiddleware(mocker.Mock(), [event_bus])
        assert len(event_bus_store) == 1
        await middleware.dispatch(mocker.MagicMock(), mocker.AsyncMock(return_value=response))
        publish_mock.assert_called()

@pytest.mark.asyncio
async def test_publish_not_call_if_status_is_above_400(mocker: MockerFixture, event_bus_store_ctx):
    publish_mock = mocker.patch("fast_sqlalchemy.event_bus.middlewares.publish_events")
    event_bus = mocker.AsyncMock()
    response = mocker.MagicMock(status_code=400)

    with event_bus_store_ctx():
        middleware = EventBusMiddleware(mocker.Mock(), [event_bus])
        await middleware.dispatch(mocker.MagicMock(), mocker.AsyncMock(return_value=response))
        publish_mock.assert_not_called()

