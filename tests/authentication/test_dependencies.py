import pytest
from pytest_mock import MockerFixture

from fast_sqlalchemy.authentication.dependencies import get_user, authentication


class User:
    pass


@pytest.mark.asyncio
async def test_populate_user_state(mocker: MockerFixture):
    user = User()
    get_user = mocker.Mock(return_value=user)
    db_middleware = authentication(get_user)
    request = mocker.MagicMock()
    await db_middleware(request)
    assert request.state.user is user

@pytest.mark.asyncio
async def test_user_is_none(mocker: MockerFixture):
    get_user = mocker.Mock(return_value=None)
    db_middleware = authentication(get_user)
    request = mocker.MagicMock()
    await db_middleware(request)
    assert request.state.user is None

@pytest.mark.asyncio
async def test_get_user(mocker: MockerFixture):
    user = mocker.Mock()
    request = mocker.Mock()
    request.state.user = user
    assert await get_user(request) is user

@pytest.mark.asyncio
async def test_get_user_is_none(mocker: MockerFixture):
    request = mocker.Mock()
    request.state = None
    assert await get_user(request) is None

