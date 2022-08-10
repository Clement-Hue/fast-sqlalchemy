import contextlib
from typing import Iterable

import pytest

from fast_alchemy.event_bus import event_bus_store


@pytest.fixture
def event_bus_store_ctx():
    @contextlib.contextmanager
    def inner(bus: Iterable):
        event_bus_store.append(*bus)
        yield
        event_bus_store.clear()
    return inner
