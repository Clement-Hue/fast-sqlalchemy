import contextlib
from typing import Iterable

import pytest

from fast_sqlalchemy.event_bus.contexts import event_bus_store


@pytest.fixture
def event_bus_store_ctx():
    @contextlib.contextmanager
    def inner(bus: Iterable = None):
        if bus:
            event_bus_store.add(*bus)
        yield
        event_bus_store.clear()
    return inner
