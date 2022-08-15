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

## The database middlewares

The main middleware is the database middleware which is made to provide a sqlalchemy session accessible throughout your application. We use the ContextVar api of python to have unique session in the context of each request.

To use this middleware you must at first create a Database object where you must pass the url of your database and the engine options of SQLAlchemy:

```python
db = Database(
    URL.create(
        drivername="mariadb+pymysql", username = config["database"]["user"].get(str),
        password=config["database"]["password"].get(str),
        host =config["database"]["host"].get(str), database = config["database"]["name"].get(str)),
    autoflush=False
)
```
And then register the database middleware:

```python
fastapi = FastAPI()
fastapi.add_middleware(DatabaseMiddleware, db=db)
```
After that you can have access to the sqlalchemy session api, through the property session of the Database object in the entire application:
```python
db.session.query(User).first()
```
Note that if you want to have access to a sqlalchemy session outisde of a request context, you must create a session by using the session contextmanager of the Datbase object:

```python
with db.session_ctx():
    db.session.query(User).all()
```
The middleware is actually using this contextmanager for each requests.

## The event bus

To use the event bus within your application, you must create at least one event bus
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
There are two kinds of handler sync and async handler. Sync handlers are called once the event is emitted, whereas async handlers are called at the end of the request.
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



## The database testing class

## The yaml config reader

## Licence

This project is licensed under the terms of the MIT license.

