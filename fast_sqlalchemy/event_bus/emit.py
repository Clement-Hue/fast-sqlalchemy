import asyncio
import logging

from fast_sqlalchemy.event_bus.contexts import _event_queue, event_bus_store

logger = logging.getLogger(__name__)

def emit(event):
    """
    Emit a specific event. Call all sync handlers for this
    specific event and add the event to queue so that async
    handlers can be called when 'publish_event' function is called.

    :param event: Event object to emit
    """
    logger.debug(f"emit {event}")
    queue = _event_queue.get()
    queue.append(event)
    for event_bus in event_bus_store:
        event_bus.handle_event(event)

async def publish_events():
    """
    WARNING: The queue has to be initialized first

    Call all async handlers which are in the queue.
    This reset the queue of events.
    """
    logger.debug("publishing events")
    events = _event_queue.get()
    await asyncio.gather(*[event_bus.handle_async_events(events) for
                         event_bus in event_bus_store])
