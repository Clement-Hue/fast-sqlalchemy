import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

class RequestTimingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        response = await call_next(request)
        end = time.time()
        duration = "{:.2f}".format((end - start) * 1000)
        logger.info(f"Request {request.url.path}: duration {duration}ms, status {response.status_code}")
        return response
