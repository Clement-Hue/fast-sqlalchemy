import time
import pytest
from pytest_mock import MockerFixture

from fast_sqlalchemy.logging.middlewares import RequestTimingMiddleware


@pytest.mark.asyncio
async def test_timing_middleware(caplog, mocker: MockerFixture):
    endpoint = '/custom'
    status = 200
    mocker.patch.object(time, "time", side_effect=[0, 1, 2, ])
    caplog.set_level("INFO")
    middleware = RequestTimingMiddleware(mocker.Mock())
    response = mocker.Mock(status_code=status)
    url = mocker.Mock(path=endpoint)
    await middleware.dispatch(mocker.Mock(url=url), mocker.AsyncMock(return_value=response))
    assert f"{status}" in caplog.text
    assert "1000.00ms" in caplog.text
    assert endpoint in caplog.text
