import pytest
from pytest_mock import MockerFixture
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from fast_alchemy.persistence.database import Database
from fast_alchemy.testing.client import TestDatabase
from tests.testing.factories_stub import UserFactory, AccountFactory
import sqlalchemy_utils


@pytest.fixture
def db():
    return Database("sqlite://")

def test_db_engine(db):
    test_db = TestDatabase(db=db)
    assert test_db.engine.url == db.url
    assert isinstance(test_db.engine, Engine)

def test_load_factory(db):
    test_db = TestDatabase(db=db, factories_module="tests.testing.factories_stub")
    assert test_db.factories == [AccountFactory, UserFactory]

def test_db_client_create_database(db, mocker:MockerFixture):
    create_database = mocker.patch.object(sqlalchemy_utils, "create_database")
    mocker.patch.object(sqlalchemy_utils, "database_exists", return_value=False)
    metadata = mocker.Mock()
    test_db = TestDatabase(db=db)
    test_db.create_test_database(metadata)
    metadata.create_all.assert_called()
    create_database.assert_called_with(db.url)

def test_db_client_release_resources(db, mocker: MockerFixture):
    drop_database = mocker.patch.object(sqlalchemy_utils, "drop_database")
    test_db = TestDatabase(db=db)
    engine = mocker.patch.object(test_db, "engine")
    connection = mocker.patch.object(test_db, "connection")
    test_db.__del__()
    engine.dispose.assert_called()
    connection.close.assert_called()
    drop_database.assert_called_with(db.url)

def test_db_client_in_test(mocker: MockerFixture, pytester):
    pytester.makepyfile(
    """
    import pytest
    from fast_alchemy.persistence.database import Database
    from fast_alchemy.testing.client import TestDatabase
    
    @pytest.fixture
    def db_client():
        db = Database("sqlite://")
        return TestDatabase(db=db)
    """
    )
    pytester.runpytest()