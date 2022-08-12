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
        db.session_factory = sessionmaker(bind=self.engine, autoflush=autoflush, autocommit=autocommit)

    async def dispatch( self, request: Request, call_next: RequestResponseEndpoint ) -> Response:
        with db.session_ctx():
            return await call_next(request)

