import pytest
from pytest_mock import MockerFixture

from fast_alchemy.persistence.middlewares import DatabaseMiddleware, AutocommitMiddleware



@pytest.mark.asyncio
async def test_init_session_context(mocker: MockerFixture):
    db_mock = mocker.MagicMock()
    db_middleware = DatabaseMiddleware(mocker.Mock(), db=db_mock)
    call_next = mocker.AsyncMock()
    await db_middleware.dispatch(mocker.Mock(), call_next)
    db_mock.session_ctx.assert_called()
    call_next.assert_called()

@pytest.mark.asyncio
async def test_autocommit_middleware(mocker: MockerFixture):
    db_mock = mocker.MagicMock()
    autocommit_middleware = AutocommitMiddleware(mocker.Mock(), db=db_mock)
    response = mocker.Mock(status_code=200)
    call_next = mocker.AsyncMock(return_value=response)
    await autocommit_middleware.dispatch(mocker.Mock(), call_next)
    call_next.assert_called()
    db_mock.session.commit.assert_called()

@pytest.mark.asyncio
async def test_no_autocommit_middleware_if_status_above_400(mocker: MockerFixture):
    db_mock = mocker.MagicMock()
    autocommit_middleware = AutocommitMiddleware(mocker.Mock(), db=db_mock)
    response = mocker.Mock(status_code=400)
    call_next = mocker.AsyncMock(return_value=response)
    await autocommit_middleware.dispatch(mocker.Mock(), call_next)
    call_next.assert_called()
    db_mock.session.commit.assert_not_called()
