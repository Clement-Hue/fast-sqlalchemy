import contextlib

from sqlalchemy.orm import Session
from .context import _session, _session_factory


class Database:

    @property
    def session(self) -> Session:
        assert _session_factory is not None, "Make sure that the database middleware is " \
                                             "installed"
        session = _session.get()
        if session is None:
            session = _session_factory()
            _session.set(session)

        return session

    @contextlib.contextmanager
    def session_ctx(self):
        assert _session_factory is not None, "Make sure that the database middleware is " \
                                             "installed and well configured"
        session = _session_factory()
        token = _session.set(session)
        yield
        session.close()
        _session.reset(token)


db = Database()
