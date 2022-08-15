# Welcom to fast-alchemy

This project was first made to provide some tools to use Fastapi with SQLAlchemy with ease.
## Contents

- [Installation](#installation)
- [The database middlewares](#the-database-middlewares)
    - [The DatabaseMiddleware](#the-databasemiddleware)
    - [The AutocomitMiddleware](#the-autocomitmiddleware)
- [The event bus](#the-event-bus)
- [The yaml config reader](#the-yaml-config-reader)

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
Fast-alchemy provide multiple middlewares to use SQLAlchemy with Fastapi easily

### The DatabaseMiddleware
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
After that you can have access to the sqlalchemy session of the current request, through the property session of the Database object in the entire application:

```python
db.session.query(User).first()
```
Note that if you want to have access to a sqlalchemy session outisde of a request context, you must create a session by using the session contextmanager of the Datbase object:

```python
with db.session_ctx():
    db.session.query(User).all()
```
The middleware is actually using this contextmanager for each requests.

### The AutocomitMiddleware
The auto commit middleware as its name suggest is a middleware which automatically commit at the end of each request. It must be used with the database middleware and must be registered before otherwise it won't work:

```python
fastapi = Fastapi()
fastapi.add_middleware(AutocommitMiddleware, db=db)
fastapi.add_middleware(DatabaseMiddleware, db=db)
```

## The event bus
The even tbus provide you a way to emit event in your application and register handlers to handle them. This allow you to create an event-driven architecture for your application. 

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
There are two kinds of handler sync and async handler. Sync handlers are called once the event is emitted, whereas async handlers are called at the end of the current request.
To register an async handler is nearly the same as above

```python
@local_event_bus.async_handler(EmailChanged, OtherEvent)
def check_email_uniqueness(e: EmailChanged | OtherEvent):
    # some logic
    pass
```
Note that an handler can handle multiple types of event

After that you can emit events wherever you want in your Fastapi application:

```python
emit(EmailChanged(email=email))
```

## The database testing class

Fast-alchemy provide an utility class named TestDatabase which can be used to test your Fastapi application with SQLAlchemy with ease. This class allow you to have isolated test by having each test wrapped in a transaction that is rollback at the end of each test, so that each test have a fresh database.

To use it with pytest, you can simply create two fixtures.
A primary fixture with a scope of 'session' which will create a connection to the database and create the database if it doesn't exist (A testing database is created with the same name of your application's databse prefixed with 'test_'). 
The testing database is then dropped at the end (You can optionally turn if off).

```python
from my_app import factories

@pytest.fixture(scope="session")
def db_client():
    db_client = TestDatabase(db=app_db, factories_modules=[factories])
    with db_client.start_connection(metadata=metadata):
        yield db_client
```
Note that this class is compatible with the library factory_boy, you can register as shown in the example above a list of modules which contains your factory class so that each factory wil be bound to the session provided by the TestDatabase object.

After that you can create a second fixture:

```python
@pytest.fixture()
def sqla_session(db_client):
    with db_client.start_session() as session:
        yield session
```
This fixture will provide a sqlalchemy session to your tests:

```python
def test_create_user(sqla_session):
    user = UserFactory()
    assert sqla_session.query(User).first().id == user.id
```

## The yaml config reader

Fast-alchemy provide a class named Configuration which allow you to have your application's configuration store in yaml files:

```python
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config = Configuration(os.path.join(ROOT_DIR, "config"))
config.load_config(os.path.join(ROOT_DIR, ".env"))
```
When you're creating the object you must specify the path of your configuration directory, this directory will contains all of your yaml files
Then you can load these configurations file by calling __load_config__, this method accept an env_path which corresponds to a .env file.
After that you can create your yaml configuration files. Note that you can use your environment variables within your yaml files, these variables will be parsed.

```yaml
project_name: ${PROJECT_NAME}
secret_key: ${SECRET_KEY}
local: fr_FR
```
Then you can have access to your configuration within your application like this:

```python
config["project_name"].get(str)
```
Note that, the library confuse is used underneath, check out here to have more details https://github.com/beetbox/confuse

## Licence

This project is licensed under the terms of the MIT license.

