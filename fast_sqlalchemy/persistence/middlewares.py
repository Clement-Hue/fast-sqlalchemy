from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from fast_sqlalchemy.persistence.database import  Database


class DatabaseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, db: Database):
        super().__init__(app)
        self.db = db

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        with self.db.session_ctx():
            return await call_next(request)


class AutocommitMiddleware(BaseHTTPMiddleware):
    """
    @WARNING Make sure to use this middleware with the DatabaseMiddleware after it in the
    middlewares stack.
    This middleware autocommit at the end of the request.
    If the status code is above 400, the commit is cancelled.
    """

    def __init__(self, app: ASGIApp, db: Database):
        super().__init__(app)
        self.db = db

    async def dispatch( self, request: Request, call_next: RequestResponseEndpoint ) -> Response:
        response = await call_next(request)
        if response.status_code < 400:
            self.db.session.commit()
        return response
