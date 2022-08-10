import inspect, asyncio, functools
from typing import Callable, List, Tuple

from fast_alchemy.event_bus import event_queue


class EventBus:
    def __init__(self):
        self.events = {}

    def subscribe(self, event_list, func: Callable, on_publish=False):
        """
        Register an event handler for one or multiple events
        """
        event_list = event_list if isinstance(event_list, (List, Tuple)) else [event_list]
        for event in event_list:
            self.events.setdefault(event, {})[func.__name__] = {"func": func, "on_publish": on_publish}

    def unsubscribe(self, event, func: Callable):
        """
        Unregistered an event handler for an event
        """
        self.events[event][func.__name__] = None

    def emit(self, event):
        """
        Emit a specific event. Call all sync handlers for this
        specific event and add the event to queue so that async
        handlers can be called when 'publish_event' function is called.

        :param event: Event object to emit
        """
        queue = event_queue.get()
        queue.append(event)
        for name, handler in self.events.get(type(event), {}).items():
            if handler is not None and not handler["on_publish"]:
                handler["func"](event)

    def init_queue(self):
        event_queue.set([])

    def clear_queue(self):
        event_queue.get().clear()

    def async_handler(self, *args):
        """
        Decorator of function which add a handler to a specific event.
        The handler is called when publish_event method is called.
        The handler can be a coroutine
        :param events: The events to listen on
        """

        def decorate(fun: Callable):
            self.subscribe(args, fun, on_publish=True)
            return fun

        return decorate

    def handler(self, *args):
        """
        Decorator of function which add a handler to a specific event.
        The handler is called once the event is emitted.
        The handler can't be a coroutine
        :param events: The events to listen on
        """

        def decorate(fun: Callable):
            self.subscribe(args, fun, on_publish=False)
            return fun

        return decorate

    async def publish_events(self):
        """
        WARNING: The queue has to be initialized first

        Call all async handlers which are in the queue.
        This reset the queue of events.
        """
        for event in event_queue.get():
            for name, handler in self.events[type(event)].items():
                if handler is not None and handler['on_publish']:
                    if inspect.iscoroutinefunction(handler["func"]):
                        await handler["func"](event)
                    else:
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, functools.partial(handler["func"], event))
        self.clear_queue()
