from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from fast_alchemy.persistence.database import db


class DatabaseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, url: URL | str, autoflush=False, autocommit=False, **engine_options):
        super().__init__(app)
        self.url = url
        self.engine = create_engine(self.url, **engine_options)
        db._session_factory = sessionmaker(bind=self.engine, autoflush=autoflush, autocommit=autocommit)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        with db.session_ctx():
            return await call_next(request)


"""
@WARNING Make sure to use this middleware with the DatabaseMiddleware after it in the
middleware stack.
This middleware autocommit at the end of the request. 
If the status code is above 400, the commit is cancelled. 
"""
class AutocommitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch( self, request: Request, call_next: RequestResponseEndpoint ) -> Response:
        response = await call_next(request)
        if response.status_code < 400:
            db.session.commit()
        return response
