import pytest, asyncio
from pytest_mock import MockerFixture

from fast_alchemy.event_bus import event_queue
from fast_alchemy.event_bus.bus import EventBus

@pytest.fixture(autouse=True)
def reset_events():
    event_queue.get().clear()

def test_register_handler_with_event(mocker: MockerFixture):
    event_bus = EventBus()
    handler = mocker.MagicMock(__name__="handler")
    class FalseEvent:
        pass

    with pytest.raises(KeyError):
        assert event_bus.events[FalseEvent]

    class CustomEvent:
        pass

    event_bus.subscribe(CustomEvent, handler)
    assert "handler" in event_bus.events[CustomEvent]

def test_sync_handler(mocker: MockerFixture):
    event_bus = EventBus()
    handler = mocker.MagicMock(__name__="handler")

    class CustomEvent:
        pass

    event_bus.subscribe(CustomEvent, handler)
    custom_event = CustomEvent()
    event_bus.emit(custom_event)
    handler.assert_called_with(custom_event)

def test_handler_with_multiple_events(mocker: MockerFixture):
    event_bus = EventBus()
    handler = mocker.MagicMock(__name__="handler")

    class CustomEvent1:
        pass

    class CustomEvent2:
        pass

    event_bus.subscribe([CustomEvent1, CustomEvent2], handler)
    event_1 = CustomEvent1()
    event_2 = CustomEvent2()
    event_bus.emit(event_1)
    handler.assert_called_with(event_1)
    event_bus.emit(event_2)
    handler.assert_called_with(event_2)

@pytest.mark.asyncio
async def test_event_queue(mocker: MockerFixture):
    event_bus = EventBus()
    handler = mocker.Mock(__name__="handler", __annotations__={})

    class CustomEvent:
        pass

    event_bus.init_queue()
    event_bus.async_handler(CustomEvent)(handler)
    e1 = CustomEvent()
    e2 = CustomEvent()
    event_bus.emit(e1)
    event_bus.emit(e2)
    handler.assert_not_called()
    await event_bus.publish_events()
    assert handler.call_count == 2
    assert event_queue.get() == []

@pytest.mark.asyncio
async def test_multiple_event_handler_decorator():
    event_bus = EventBus()
    class CustomEvent:
        pass

    @event_bus.async_handler(CustomEvent)
    def handler_1(e):
        pass

    @event_bus.async_handler(CustomEvent)
    def handler_2(e):
        pass

    event_bus.init_queue()
    e = CustomEvent()
    event_bus.emit(e)
    assert event_queue.get() == [e]
    await event_bus.publish_events()
    assert event_queue.get() == []


def test_unsubscribe(mocker: MockerFixture):
    event_bus = EventBus()
    handler = mocker.MagicMock(__name__="handler")

    class CustomEvent:
        pass

    event_bus.subscribe(CustomEvent, handler)
    custom_event = CustomEvent()
    event_bus.unsubscribe(CustomEvent, handler)
    event_bus.emit(custom_event)
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_context_queue():
    event_bus = EventBus()
    class CustomEvent:
        pass

    @event_bus.async_handler(CustomEvent)
    def handler(e):
        pass

    event_bus.async_handler(CustomEvent)(handler)
    e1 = CustomEvent()

    async def coroutine():
        event_bus.init_queue()
        event_bus.emit(e1)
        assert len(event_queue.get()) == 1
        assert event_queue.get() == [e1]

    task1 = asyncio.create_task(coroutine())

    task2 = asyncio.create_task(coroutine())

    await task1
    await task2
