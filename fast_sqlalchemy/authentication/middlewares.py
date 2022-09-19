from typing import Callable

from starlette.middleware.base import RequestResponseEndpoint, BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Population the state of the request with the user
    """

    def __init__(self, app: ASGIApp, get_user: Callable[[Request], any]):
        super().__init__(app)
        self.get_user = get_user

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        user = self.get_user(request)
        request.state.user = user
        response = await call_next(request)
        return response
