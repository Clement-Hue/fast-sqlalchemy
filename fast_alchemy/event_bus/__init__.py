from contextvars import ContextVar

event_queue: ContextVar = ContextVar("event_queue", default=[])
