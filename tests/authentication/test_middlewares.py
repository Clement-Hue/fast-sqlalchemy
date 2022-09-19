import pytest
from pytest_mock import MockerFixture

from fast_sqlalchemy.authentication.middlewares import AuthenticationMiddleware


class User:
    pass


@pytest.mark.asyncio
async def test_populate_user_state(mocker: MockerFixture):
    user = User()
    get_user = mocker.Mock(return_value=user)
    db_middleware = AuthenticationMiddleware(mocker.Mock(), get_user)
    call_next = mocker.AsyncMock()
    request = mocker.MagicMock()
    await db_middleware.dispatch(request, call_next)
    call_next.assert_called()
    assert request.state.user is user

@pytest.mark.asyncio
async def test_user_is_none(mocker: MockerFixture):
    get_user = mocker.Mock(return_value=None)
    db_middleware = AuthenticationMiddleware(mocker.Mock(), get_user)
    call_next = mocker.AsyncMock()
    request = mocker.MagicMock()
    await db_middleware.dispatch(request, call_next)
    call_next.assert_called()
    assert request.state.user is None
