from pytest_mock import MockerFixture

from fast_sqlalchemy.authentication.dependencies import get_user


def test_get_user(mocker: MockerFixture):
    user = mocker.Mock()
    request = mocker.Mock()
    request.state.user = user
    assert get_user(request) is user

def test_get_user_is_none(mocker: MockerFixture):
    request = mocker.Mock()
    request.state = None
    assert get_user(request) is None

