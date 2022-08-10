import contextlib
from contextvars import ContextVar

event_queue: ContextVar = ContextVar("event_queue", default=[])

@contextlib.contextmanager
def event_queue_ctx():
    token = event_queue.set([])
    yield
    event_queue.reset(token)
