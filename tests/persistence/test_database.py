import pytest
from pytest_mock import MockerFixture
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from fast_sqlalchemy.persistence.context import _session
from fast_sqlalchemy.persistence.database import Database


@pytest.fixture()
def db():
    return Database("sqlite://")


def test_create_session_ctx(db):
    assert _session.get() is None
    with db.session_ctx() as session:
        assert isinstance(_session.get(), Session)
        assert session == _session.get()
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
    test_db = Database("sqlite://", echo=True)
    assert test_db.url == make_url( "sqlite://")
    assert test_db.engine.echo is True
    assert isinstance(test_db._session_factory, sessionmaker)


