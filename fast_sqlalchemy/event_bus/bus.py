import inspect, asyncio, logging
from abc import ABC, abstractmethod
from typing import Callable, List, Tuple, Iterable

logger = logging.getLogger(__name__)

class EventHandler:
    def __init__(self, func, on_publish=False):
        self.func = func
        self.on_publish = on_publish

    def handle(self, event):
        self.func(event)

    async def async_handle(self, event):
        if inspect.iscoroutinefunction(self.func):
            await self.func(event)
        else:
            async def to_async():
                return self.func(event)
            await to_async()


class EventBus(ABC):
    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    async def handle_async_events(self, events: Iterable):
        pass

class LocalEventBus(EventBus):
    def __init__(self):
        self.event_handlers = {}

    def subscribe(self, event_type_list, func: Callable, on_publish=False):
        """
        Register an event handler for one or multiple events
        """
        event_type_list = event_type_list if isinstance(event_type_list, (List, Tuple)) else [event_type_list]
        for event in event_type_list:
            self.event_handlers.setdefault(event, []).append(EventHandler(func, on_publish=on_publish))

    def unsubscribe(self, event_type, func: Callable):
        """
        Unregistered an event handler for an event
        """
        self.event_handlers[event_type] = list(
            filter(lambda handler: handler.func != func, self.event_handlers[event_type]))

    def async_handler(self, *events):
        """
        Decorator of function which add a handler to a specific event.
        The handler is called when publish_event method is called.
        The handler can be a coroutine

        :param events: The events to listen on
        """

        def decorate(fun: Callable):
            self.subscribe(events, fun, on_publish=True)
            return fun

        return decorate

    def handler(self, *events):
        """
        Decorator of function which add a handler to a specific event.
        The handler is called once the event is emitted.
        The handler can't be a coroutine

        :param events: The events to listen on
        """

        def decorate(fun: Callable):
            self.subscribe(events, fun, on_publish=False)
            return fun

        return decorate

    async def handle_async_events(self, events: Iterable):
        logger.debug(f"local event bus call with {events}")
        coroutines = []
        for event in events:
            for handler in self.event_handlers.get(type(event), []):
                if handler.on_publish:
                    coroutines.append(handler.async_handle(event))
        await asyncio.gather(*coroutines)

    def handle_event(self, event):
        for handler in self.event_handlers.get(type(event), []):
            if not handler.on_publish:
                handler.handle(event)


