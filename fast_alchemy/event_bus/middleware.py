from typing import Iterable

from starlette.types import ASGIApp, Scope, Receive, Send

from fast_alchemy.event_bus.contexts import event_queue_ctx, event_bus_store
from fast_alchemy.event_bus.emit import publish_events


class EventBusMiddleware:
    def __init__(self, app: ASGIApp, handlers: Iterable):
        self.app = app
        self.register_handlers(handlers=handlers)

    def register_handlers(self, handlers: Iterable):
        event_bus_store.append(*handlers)

    def __del__(self):
        event_bus_store.clear()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        with event_queue_ctx():
            await self.app(scope, receive, send)
            await publish_events()

