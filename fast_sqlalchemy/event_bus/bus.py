import inspect, asyncio, logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable, List, Tuple, Iterable

logger = logging.getLogger(__name__)

class EventHandler:
    """
    A class representing an event handler.

    The event handler encapsulates a function and provides methods for handling events.

    :param func: The function to be called when handling events.
    :param on_publish: Flag indicating whether the handler should be executed during event publishing, defaults to False.
    **Example**:

    >>> def event_handler(data):
    ...     print("Event handler called with data:", data)
    ...
    >>> handler = EventHandler(event_handler)
    >>> handler.handle("Hello, world!")  # Event handler called with data: Hello, world!
    """
    def __init__(self, func, on_publish=False):
        self.func = func
        self.on_publish = on_publish

    def handle(self, event):
        """
        Handle an event by calling the encapsulated function.

        :param event: The event to be handled.
        """
        self.func(event)

    async def async_handle(self, event):
        """
        Asynchronously handle an event.

        If the encapsulated function is a coroutine function, it is awaited.
        Otherwise, it is executed in a separate thread using asyncio.to_thread.

        :param event: The event to be handled.
        """
        if inspect.iscoroutinefunction(self.func):
            await self.func(event)
        else:
            self.func(event)


class EventBus(ABC):
    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    async def async_handle_events(self, events: Iterable):
        pass

class LocalEventBus(EventBus):
    """
    An event bus implementation that handles local event subscriptions and publishes events.

    **Example**:
    >>> event_bus = EventBus()

    >>> @handler("event_type1", "event_type2")
    ... def my_handler(event_data):
    ...     print("Event handler called with data:", event_data)
    ...

    >>> event_bus.subscribe("event_type1", my_handler)
    >>> event_bus.subscribe("event_type2", my_handler)
    """
    def __init__(self):
        self.event_handlers = defaultdict(list)

    def subscribe(self, event_type_list, func: Callable, on_publish=False):
        """
        Register an event handler for one or multiple events.

        :param event_type_list: The event type(s) to subscribe to.
        :param func: The event handler function to be registered.
        :param on_publish: Indicates whether the handler is called on event publish (True) or event emission (False), defaults to False.
        """
        event_type_list = event_type_list if isinstance(event_type_list, (List, Tuple)) else [event_type_list]
        for event in event_type_list:
            self.event_handlers[event].append(EventHandler(func, on_publish=on_publish))

    def unsubscribe(self, event_type, func: Callable):
        """
        Unregister an event handler for an event.

        :param event_type: The event type to unsubscribe from.
        :param func: The event handler function to be unregistered.
        """
        self.event_handlers[event_type] = [handler for handler in self.event_handlers[event_type] if handler.func != func]

    def handler(self, *events, on_publish=False):
        """
        Decorator that adds a handler to specific events.

        The handler is called once the event is emitted.

        :param *events: The events to listen on.
        :param on_publish: Call the handler when the publish method is called
        :returns: The decorated function.
        :raises TypeError: If the decorated function is a coroutine function and on_publish is False
        """

        def decorate(fun: Callable):
            if not on_publish and asyncio.iscoroutinefunction(fun):
                raise TypeError("Coroutine functions are not allowed as event handlers.")
            self.subscribe(events, fun, on_publish=on_publish)
            return fun

        return decorate

    async def async_handle_events(self, events: Iterable):
        """
        Asynchronously handle a batch of events.

        This method processes the events using their respective event handlers.
        Coroutine handlers are awaited,

        :param events: The batch of events to handle.
        """
        logger.debug(f"local event bus call with {events}")
        coroutines = []
        for event in events:
            for handler in self.event_handlers.get(type(event), []):
                if handler.on_publish:
                    coroutines.append(handler.async_handle(event))
        await asyncio.gather(*coroutines)

    def handle_event(self, event):
        """
        Handle a single event.

        This method invokes the event handlers for the given event type.

        :param event: The event to handle.
        """
        for handler in self.event_handlers[type(event)]:
            if not handler.on_publish:
                handler.handle(event)


