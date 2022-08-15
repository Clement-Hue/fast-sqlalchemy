import contextlib, logging
from contextvars import ContextVar
from typing import Set
from fast_sqlalchemy.event_bus.bus import EventBus

logger = logging.getLogger(__name__)


_event_queue: ContextVar = ContextVar("event_queue", default=[])

event_bus_store: Set[EventBus] = set()

@contextlib.contextmanager
def event_queue_ctx():
    logger.debug("event queue set")
    token = _event_queue.set([])
    yield
    logger.debug("event queue reset")
    _event_queue.reset(token)


