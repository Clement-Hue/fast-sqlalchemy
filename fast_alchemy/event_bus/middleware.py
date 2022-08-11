import logging
from typing import Iterable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

from fast_alchemy.event_bus.contexts import event_queue_ctx, event_bus_store
from fast_alchemy.event_bus.emit import publish_events
logger = logging.getLogger(__name__)


class EventBusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, handlers: Iterable):
        super().__init__(app)
        self.register_handlers(handlers=handlers)

    def register_handlers(self, handlers: Iterable):
        event_bus_store.add(*handlers)

    async def dispatch(self, request, call_next):
        with event_queue_ctx():
            response = await call_next(request)
            await publish_events()
        return response

