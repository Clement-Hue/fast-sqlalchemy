from contextvars import ContextVar
from typing import Optional
from sqlalchemy.orm import Session, sessionmaker

_session: ContextVar[Optional[Session]] = ContextVar("session", default=None)
_session_factory: Optional[sessionmaker] = None
