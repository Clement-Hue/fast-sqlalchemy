from __future__ import annotations
import contextlib
from typing import Optional, TypeVar, Type, TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from .context import _session
if TYPE_CHECKING:
    from .repository import EntityRepository

T = TypeVar('T') 

class Database:
    def __init__(self, url: URL | str, repositories: list[Type[EntityRepository]] = None
                 , autoflush=False, autocommit=False, **engine_options):
        self.url = make_url(url)
        self.engine = create_engine(self.url, **engine_options)
        self._session_factory = sessionmaker(bind=self.engine, autoflush=autoflush, autocommit=autocommit)
        self.repositories = self._create_repositories(repositories)

    def _create_repositories(self, repositories: Optional[list[Type[EntityRepository]]]):
        return {repository: repository(db=self) for repository in repositories} if repositories else {}
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
            yield session
        finally:
            session.close()
            _session.reset(token)

    def get_repository(self, repository: Type[T]) -> T:
        try :
            return self.repositories[repository]
        except KeyError:
            raise RuntimeError(f"The repository {repository} is not registered")


