import pytest
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fast_alchemy.persistence.database import db
from fast_alchemy.persistence.context import _session

@pytest.fixture
def session_factory(mocker: MockerFixture):
    engine = create_engine("sqlite://", echo=False, future=True)
    mocker.patch.object(db, "session_factory", new=sessionmaker(bind=engine) )

def test_create_session_ctx(session_factory):
    assert _session.get() is None
    with db.session_ctx():
        assert isinstance(_session.get(), Session)
    assert _session.get() is None

def test_session_ctx_close_session(mocker: MockerFixture):
    session = mocker.Mock()
    mocker.patch.object(db, "session_factory", new=mocker.Mock(return_value=session) )
    with db.session_ctx():
        pass
    session.close.assert_called()

def test_get_current_session_from_context(session_factory,mocker: MockerFixture):
    session = mocker.Mock()
    token = _session.set(session)
    assert db.session == session
    _session.reset(token)

def test_create_session_if_not_set(mocker: MockerFixture):
    session = mocker.Mock()
    mocker.patch.object(db, "session_factory", new=mocker.Mock(return_value=session) )
    assert _session.get() is None
    assert db.session == session
    assert _session.get() == session
    _session.set(None)
