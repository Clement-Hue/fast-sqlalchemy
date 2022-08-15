from typing import Iterable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from fast_sqlalchemy.event_bus.contexts import event_queue_ctx, event_bus_store
from fast_sqlalchemy.event_bus.emit import publish_events


class EventBusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, buses: Iterable):
        super().__init__(app)
        self.register_buses(buses=buses)

    def register_buses(self, buses: Iterable):
        event_bus_store.add(*buses)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        with event_queue_ctx():
            response = await call_next(request)
            if response.status_code < 400:
                await publish_events()
        return response

