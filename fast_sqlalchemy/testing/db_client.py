from __future__ import annotations
import contextlib
import inspect
import logging
from types import ModuleType
from typing import TYPE_CHECKING, Optional

from alembic import command
from alembic.config import Config
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.exc import InternalError
import sqlalchemy_utils

if TYPE_CHECKING:
    from fast_sqlalchemy.persistence.database import Database

logger = logging.getLogger(__name__)


class TestDatabase:
    __test__ = False

    def __init__(self, db: Database, factories_modules: list[ModuleType] = None, workerinput=None,
                 **engine_options):
        """
        Create a testing database client.

        :param db: The Database object use in the application
        :param factories_modules: A list of modules which contains factories from factory_boy's library
            to wire them with the testing session
        :param workerinput: The workerinput get from the request.config object from pytest when using pytest-xdist
            library, so that every worker have their own isolated database
        :param engine_options: Sqlalchemy engine parameters
        """
        self.db = db
        self._workerinput = workerinput
        self.db.url = self.db.url.set(database="test_" + self.db.url.database) if self.db.url.database else self.db.url
        self.factories = self._load_factories(factories_modules) if factories_modules else None
        self.engine = self._create_engine(**engine_options)
        self.connection: Optional[Connection] = None
        logger.debug("Engine and sessionmaker created")

    @contextlib.contextmanager
    def start_connection(self, alembic_ini_path:str, drop_database=True):
        """
        Start connection to the database. Create the database if it doesn't exist and
        release connection at the end, optionally drop the database.

        :param alembic_ini_path: Path to alembic ini configuration
        :param drop_database: If true, drop the database when the connection is released
        """
        if not sqlalchemy_utils.database_exists(self.db.url):
            sqlalchemy_utils.create_database(self.db.url)
            logger.debug("Testing database created")
        alembic_config = Config(file_=alembic_ini_path)
        command.upgrade(alembic_config, "head")
        self.connection = self.engine.connect()
        yield self
        self.release(drop_database=drop_database)

    def _create_engine(self, **engine_options):
        engine = create_engine(self.db.url, **engine_options)
        # Put a suffix like _gw0, _gw1 etc on xdist processes
        if engine.url.database != ':memory:' and self._workerinput is not None:
            logger.debug("Creating engine for each worker")
            xdist_suffix = self._workerinput.get('workerid')
            xdist_url = self.db.url.set(database='{}_{}'.format(engine.url.database, xdist_suffix))
            engine = create_engine(xdist_url, **engine_options)  # override engine
        return engine

    def release(self, drop_database=True):
        """
        Release connection, engine and optionally dropping the current testing database

        :param drop_database: Flag to drop the current testing database
        """
        if self.connection:
            self.connection.close()

        self.engine.dispose()
        if drop_database:
            logger.debug("Testing database dropped")
            sqlalchemy_utils.drop_database(self.db.url)
        logger.debug("Releasing resources")

    def _load_factories(self, factories_modules: list[ModuleType]):
        factories = []
        for module in factories_modules:
            factories.extend([cls for _, cls in inspect.getmembers(module, inspect.isclass)
                               if issubclass(cls, SQLAlchemyModelFactory) and cls != SQLAlchemyModelFactory])
        return factories

    @contextlib.contextmanager
    def start_session(self):
        """
        Create a session wrapped in a transaction so that every commit to the database
        will be rollback in order to have isolated tests.
        """
        assert self.connection, "Make sure to create a connection to the database " \
                                "before creating a testing session"
        transaction = self.connection.begin()
        logger.debug("Transaction has started")
        self.db._session_factory.configure(bind=self.connection)
        with self.db.session_ctx() as session:
            for factory in self.factories or []:
                factory._meta.sqlalchemy_session = session
                factory._meta.sqlalchemy_session_persistence = "commit"

            dialect_name = self.db.url.get_dialect().name
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
