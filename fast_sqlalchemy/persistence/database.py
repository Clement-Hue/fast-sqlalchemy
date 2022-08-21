from __future__ import annotations
import contextlib

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from .context import _session


class Database:
    def __init__(self, url: URL | str , autoflush=False, autocommit=False, **engine_options):
        self.url = make_url(url)
        self.engine = create_engine(self.url, **engine_options)
        self._session_factory = sessionmaker(bind=self.engine, autoflush=autoflush, autocommit=autocommit)
    @property
    def session(self) -> Session:
        session = _session.get()
        assert session ,"Make sure to use the session within a session context"
        return session

    @contextlib.contextmanager
    def session_ctx(self):
        session = self._session_factory()
        token = _session.set(session)
        try:
            yield session
        finally:
            session.close()
            _session.reset(token)


