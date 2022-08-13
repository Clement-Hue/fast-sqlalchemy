import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session, sessionmaker

from fast_alchemy.persistence.context import _session
from fast_alchemy.persistence.database import Database

@pytest.fixture()
def db():
    return Database("sqlite://")


def test_create_session_ctx(db):
    assert _session.get() is None
    with db.session_ctx():
        assert isinstance(_session.get(), Session)
    assert _session.get() is None

def test_session_ctx_close_session(db, mocker: MockerFixture):
    session = mocker.Mock()
    mocker.patch.object(db, "_session_factory", new=mocker.Mock(return_value=session) )
    with db.session_ctx():
        pass
    session.close.assert_called()

def test_get_current_session_from_context(db,mocker: MockerFixture):
    session = mocker.Mock()
    token = _session.set(session)
    assert db.session == session
    _session.reset(token)

def test_close_session_even_with_exception(db, mocker: MockerFixture):
    session = mocker.Mock()
    mocker.patch.object(db, "_session_factory", new=mocker.Mock(return_value=session) )
    try:
        with db.session_ctx():
            raise RuntimeError()
    except RuntimeError:
        pass
    session.close.assert_called()

def test_set_session_config():
    db = Database("sqlite://", echo=True)
    assert db.url == "sqlite://"
    assert db.engine.echo is True
    assert isinstance(db._session_factory, sessionmaker)
