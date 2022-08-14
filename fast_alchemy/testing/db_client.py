from __future__ import annotations

import contextlib
import importlib
import inspect
import logging
from types import ModuleType
from typing import TYPE_CHECKING

from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.exc import InternalError
import sqlalchemy_utils

if TYPE_CHECKING:
    from fast_alchemy.persistence.database import Database

logger = logging.getLogger(__name__)


class TestDatabase:
    __test__ = False

    def __init__(self, db: Database, factories_module: list[ModuleType] = None, workerinput=None,
                 **engine_options):
        self.db = db
        self._workerinput = workerinput
        self.url = self.db.url.set(database="test_" + self.db.url.database) if self.db.url.database else self.db.url
        self.factories = self._load_factories(factories_module) if factories_module else None
        self.engine = self._create_engine(**engine_options)
        self.connection = None
        logger.debug("Engine and sessionmaker created")

    @contextlib.contextmanager
    def start_connection(self, metadata: MetaData, drop_database=True):
        """
        Start connection to the database. Create the database if it doesn't exist and
        release connection at the end, optionally drop the database

        :param metadata: The sqlalchemy metadata
        :param drop_database: drop or not the database when the connection is released
        """
        try:
            if not sqlalchemy_utils.database_exists(self.url):
                sqlalchemy_utils.create_database(self.url)
            metadata.create_all(bind=self.engine)
            self.connection = self.engine.connect()
        except InternalError:
            pass
        yield self
        self.release(drop_database=drop_database)

    def _create_engine(self, **engine_options):
        engine = create_engine(self.url, **engine_options)
        # Put a suffix like _gw0, _gw1 etc on xdist processes
        if engine.url.database != ':memory:' and self._workerinput is not None:
            logger.debug("Creating engine for each worker")
            xdist_suffix = self._workerinput.get('workerid')
            xdist_url = self.url.set(database='{}_{}'.format(engine.url.database, xdist_suffix))
            engine = create_engine(xdist_url, **engine_options)  # override engine
        return engine

    def release(self, drop_database=True):
        """
        Release connection, engine and dropping the current testing database
        """
        if self.connection:
            self.connection.close()

        self.engine.dispose()
        if drop_database:
            logger.debug("Drop database")
            sqlalchemy_utils.drop_database(self.url)
        logger.debug("Releasing resources")

    def _load_factories(self, factories_modules: list[ModuleType]):
        factories = []
        for module in factories_modules:
            factories.extend([cls for _, cls in inspect.getmembers(module, inspect.isclass)
                               if issubclass(cls, SQLAlchemyModelFactory) and cls != SQLAlchemyModelFactory])
        return factories

    @contextlib.contextmanager
    def start_session(self):
        assert self.connection, "Make sure to create the database before creating a testing session"
        transaction = self.connection.begin()
        logger.debug("Transaction has started")
        self.db._session_factory.configure(bind=self.connection)
        with self.db.session_ctx() as session:
            for factory in self.factories or []:
                factory._meta.sqlalchemy_session = session
                factory._meta.sqlalchemy_session_persistence = "commit"

            dialect_name = self.url.get_dialect().name
            if dialect_name != "sqlite":
                nested = self.connection.begin_nested()  # allow rollback within the test

                @event.listens_for(session, "after_transaction_end")
                def end_savepoint(session, transaction):
                    nonlocal nested
                    if not nested.is_active:
                        nested = self.connection.begin_nested()

            yield session
        transaction.rollback()
        logger.debug("Transaction rollback")
