import contextlib

from sqlalchemy.orm import Session, sessionmaker

from .context import _session


class Database:
    def __init__(self, session_factory: sessionmaker = None):
        self._session_factory = session_factory

    @property
    def session(self) -> Session:
        session = _session.get()
        assert session ,"Make sure to use the session within a session context"
        return session

    @contextlib.contextmanager
    def session_ctx(self):
        assert self._session_factory is not None, "Make sure that the database middleware is " \
                                                  "installed and well configured"
        session = self._session_factory()
        token = _session.set(session)
        try:
            yield
        finally:
            session.close()
            _session.reset(token)


db = Database()
