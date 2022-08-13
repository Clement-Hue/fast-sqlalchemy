from __future__ import annotations
import importlib
import inspect
from typing import TYPE_CHECKING

from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import InternalError
import sqlalchemy_utils

if TYPE_CHECKING:
    from fast_alchemy.persistence.database import Database


"""
@pytest.fixture()
def transaction(connection):
    transaction = connection.begin()
    yield transaction
    transaction.rollback()


@pytest.fixture()
def sqla_session(connection, transaction, factories):
    sqla_db._session_factory = sessionmaker(bind=connection, autoflush=False)
    with sqla_db.session_ctx():
        for factory in factories:
            factory._meta.sqlalchemy_session = sqla_db.session
            factory._meta.sqlalchemy_session_persistence = "commit"

        nested = connection.begin_nested()
        @event.listens_for(sqla_db.session, "after_transaction_end")
        def end_savepoint(session, transaction):
            nonlocal nested
            if not nested.is_active:
                nested = connection.begin_nested()

        yield sqla_db.session
"""


class TestDatabase:
    __test__ = False
    def __init__(self, db: Database, factories_module=None, workerinput=None):
        self.db = db
        self._workerinput = workerinput
        self.url = self.db.url.set(database="test_" + self.db.url.database) if self.db.url.database else self.db.url
        self.factories = self._load_factories(factories_module) if factories_module else None
        self.engine = self._create_engine()
        self.connection = self.engine.connect()

    def create_test_database(self, metadata: MetaData):
        try:
            if not sqlalchemy_utils.database_exists(self.url):
                sqlalchemy_utils.create_database(self.url)
                metadata.create_all(bind=self.engine)
        except InternalError:
            pass

    def _create_engine(self):
        engine = create_engine(self.url)
        # Put a suffix like _gw0, _gw1 etc on xdist processes
        if engine.url.database != ':memory:' and self._workerinput is not None:
            xdist_suffix = self._workerinput.get('workerid')
            xdist_url = self.url.set(database='{}_{}'.format(engine.url.database, xdist_suffix))
            engine = create_engine(xdist_url)  # override engine
        return engine

    def __del__(self):
        self.connection.close()
        self.engine.dispose()
        sqlalchemy_utils.drop_database(self.url)

    def _load_factories(self, factories_modules: str):
        return [cls for _, cls in inspect.getmembers(importlib.import_module(factories_modules),
                                                     inspect.isclass)
                if issubclass(cls, SQLAlchemyModelFactory) and cls != SQLAlchemyModelFactory]
