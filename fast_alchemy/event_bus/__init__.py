from typing import List

from fast_alchemy.event_bus.bus import LocalEventBus, EventBus

local_event_bus = LocalEventBus()
event_bus_store: List[EventBus] = []
