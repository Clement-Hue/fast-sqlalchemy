from starlette.requests import Request


def get_user(request: Request):
    return getattr(request.state, "user", None)