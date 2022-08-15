# Welcom to fast-alchemy

This project was first made to provide some tools to use Fastapi with SQLAlchemy with ease.

## Installation

Installation using pip:
```shell
pip install fast_alchemy
```

Or with poetry:
```shell
poetry add fast_alchemy
```

## The event bus

To use the event bus within your application, you must at first create at least one event bus
and register the event bus middleware to the fastapi middlewares stack
```python
fastapi = FastAPI()
event_bus = LocalEventBus()
fastapi.add_middleware(EventBusMiddleware, buses=[event_bus])
```
Once the middleware is registered with an event bus you can start creating events and event handlers.
Event can be any python object, the most practical way is to create dataclass object:

```python
@dataclass
class EmailChanged:
    email: str
```
Then you can add an event handler for this event:

```python
@local_event_bus.handler(EmailChanged)
def check_email_uniqueness(e: EmailChanged):
    # some logic
    pass
```
There are two kinds of handler sync and async. Sync handlers are called once the event is emitted, whereas async handlers are called at the end of the request.
To register an async handler is nearly the same as above

```python
@local_event_bus.async_handler(EmailChanged, OtherEvent)
def check_email_uniqueness(e: EmailChanged | OtherEvent):
    # some logic
    pass
```
Note that an handler can handle multiple type of event

After that you can emit events wherever in your Fastapi application:

```python
emit(EmailChanged(email=email))
```

## The database middlewares

## The database testing class

## The yaml config reader

## Licence

This project is licensed under the terms of the MIT license.

