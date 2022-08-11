import contextlib, logging
from contextvars import ContextVar
from typing import Set

from fast_alchemy.event_bus.bus import EventBus
logger = logging.getLogger(__name__)


event_queue: ContextVar = ContextVar("event_queue", default=[])

@contextlib.contextmanager
def event_queue_ctx():
    logger.debug("event queue set")
    token = event_queue.set([])
    yield
    logger.debug("event queue reset")
    event_queue.reset(token)


event_bus_store: Set[EventBus] = set()
