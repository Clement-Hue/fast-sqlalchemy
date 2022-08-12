import contextlib

from sqlalchemy.orm import Session, sessionmaker

from .context import _session


class Database:
    def __init__(self, session_factory: sessionmaker = None):
        self.session_factory = session_factory

    @property
    def session(self) -> Session:
        assert self.session_factory is not None, "Make sure that the database middleware is " \
                                             "installed"
        session = _session.get()
        if session is None:
            session = self.session_factory()
            _session.set(session)

        return session

    @contextlib.contextmanager
    def session_ctx(self):
        assert self.session_factory is not None, "Make sure that the database middleware is " \
                                             "installed and well configured"
        session = self.session_factory()
        token = _session.set(session)
        yield
        session.close()
        _session.reset(token)


db = Database()
