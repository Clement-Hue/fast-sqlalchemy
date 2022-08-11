import contextlib
from contextvars import ContextVar
from typing import List

from fast_alchemy.event_bus.bus import EventBus

event_queue: ContextVar = ContextVar("event_queue", default=[])

@contextlib.contextmanager
def event_queue_ctx():
    token = event_queue.set([])
    yield
    event_queue.reset(token)


event_bus_store: List[EventBus] = []
