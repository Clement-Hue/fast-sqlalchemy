import pytest
from pytest_mock import MockerFixture

from fast_alchemy.persistence.database import db
from fast_alchemy.persistence import middleware
from fast_alchemy.persistence.middleware import DatabaseMiddleware

@pytest.fixture(autouse=True)
def init_session_factory():
    db.session_factory = None

def test_set_session_factory_config(mocker: MockerFixture):
    assert db.session_factory is None
    db_middleware = DatabaseMiddleware(mocker.Mock(),url="sqlite://", echo=True)
    assert db_middleware.url == "sqlite://"
    assert db_middleware.engine.echo is True
    assert db.session_factory is not None

@pytest.mark.asyncio
async def test_init_session_context(mocker: MockerFixture):
    db_mock = mocker.patch.object(middleware, "db")
    db_middleware = DatabaseMiddleware(mocker.Mock(), url="sqlite://", echo=True)
    call_next = mocker.AsyncMock()
    await db_middleware.dispatch(mocker.Mock(), call_next)
    db_mock.session_ctx.assert_called()
    call_next.assert_called()

@pytest.mark.asyncio
async def test_session_factory_defined(mocker: MockerFixture):
    db_middleware = DatabaseMiddleware(mocker.Mock(), url="sqlite://", echo=True)
    await db_middleware.dispatch(mocker.Mock(), mocker.AsyncMock())
