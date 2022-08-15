from contextvars import ContextVar
from typing import Optional
from sqlalchemy.orm import Session

_session: ContextVar[Optional[Session]] = ContextVar("session", default=None)

