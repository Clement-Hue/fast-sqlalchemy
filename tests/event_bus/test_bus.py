import pytest, asyncio
from pytest_mock import MockerFixture

from fast_sqlalchemy.event_bus.contexts import _event_queue, event_queue_ctx
from fast_sqlalchemy.event_bus.bus import LocalEventBus
from fast_sqlalchemy.event_bus.emit import emit, publish_events


def test_register_handler_with_event(mocker: MockerFixture):
    event_bus = LocalEventBus()
    handler = mocker.MagicMock(__name__="handler")
    class FalseEvent:
        pass

    assert event_bus.event_handlers[FalseEvent] == []

    class CustomEvent:
        pass

    event_bus.subscribe(CustomEvent, handler)
    assert len(event_bus.event_handlers[CustomEvent]) == 1
    assert event_bus.event_handlers[CustomEvent][0].func == handler

def test_sync_handler(mocker: MockerFixture):
    event_bus = LocalEventBus()
    handler = mocker.MagicMock(__name__="handler")

    class CustomEvent:
        pass

    event_bus.subscribe(CustomEvent, handler)
    custom_event = CustomEvent()
    event_bus.handle_event(custom_event)
    handler.assert_called_with(custom_event)

def test_handler_with_multiple_events(mocker: MockerFixture):
    event_bus = LocalEventBus()
    handler = mocker.MagicMock(__name__="handler")

    class CustomEvent1:
        pass

    class CustomEvent2:
        pass

    event_bus.subscribe([CustomEvent1, CustomEvent2], handler)
    event_1 = CustomEvent1()
    event_2 = CustomEvent2()
    event_bus.handle_event(event_1)
    handler.assert_called_with(event_1)
    event_bus.handle_event(event_2)
    handler.assert_called_with(event_2)

@pytest.mark.asyncio
async def test_event_queue(mocker: MockerFixture, event_bus_store_ctx):
    event_bus = LocalEventBus()
    handler = mocker.Mock(__name__="handler", __annotations__={})

    class CustomEvent:
        pass

    with event_bus_store_ctx([event_bus]), event_queue_ctx():
        event_bus.async_handler(CustomEvent)(handler)
        e1 = CustomEvent()
        e2 = CustomEvent()
        emit(e1)
        emit(e2)
        assert handler.call_count == 0
        await publish_events()
        assert handler.call_count == 2
        assert handler.call_args_list == [((e1,),), ((e2,),)]
    assert _event_queue.get() == []

@pytest.mark.asyncio
async def test_multiple_event_handler_decorator(event_bus_store_ctx):
    event_bus = LocalEventBus()
    class CustomEvent:
        pass

    @event_bus.async_handler(CustomEvent)
    def handler_1(e):
        pass

    @event_bus.async_handler(CustomEvent)
    def handler_2(e):
        pass

    with event_queue_ctx(), event_bus_store_ctx([event_bus]):
        e = CustomEvent()
        emit(e)
        assert _event_queue.get() == [e]
        await publish_events()
    assert _event_queue.get() == []


def test_unsubscribe(mocker: MockerFixture):
    event_bus = LocalEventBus()
    handler = mocker.MagicMock(__name__="handler")

    class CustomEvent:
        pass

    event_bus.subscribe(CustomEvent, handler)
    assert len(event_bus.event_handlers[CustomEvent]) == 1
    event_bus.unsubscribe(CustomEvent, handler)
    assert len(event_bus.event_handlers[CustomEvent]) == 0
    event_bus.handle_event(CustomEvent())
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_event_queue_context():
    class CustomEvent:
        pass

    e1 = CustomEvent()

    async def coroutine():
        with event_queue_ctx():
            emit(e1)
            assert len(_event_queue.get()) == 1
            assert _event_queue.get() == [e1]

    await asyncio.gather(coroutine(), coroutine())
    assert _event_queue.get() == []

def test_event_queue_clear_when_error():
    try:
        with event_queue_ctx():
            _event_queue.set(["custom event"])
            raise RuntimeError
    except RuntimeError:
        pass
    assert _event_queue.get() == []

def test_error_if_coroutine_use_as_handler():
    event_bus = LocalEventBus()
    class CustomEvent:
        pass

    with pytest.raises(TypeError):
        @event_bus.handler(CustomEvent)
        async def handler(e):
            pass
