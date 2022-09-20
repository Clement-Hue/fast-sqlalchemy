from typing import Callable, Any

from starlette.requests import Request


def authentication(get_user: Callable[[Request], Any]):
    async def inner(request: Request):
        request.state.user = get_user(request)

    return inner


async def get_user(request: Request):
    return getattr(request.state, "user", None)
