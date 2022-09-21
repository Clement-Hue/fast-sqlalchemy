# Welcome to fast-sqlalchemy

This project was first made to provide some tools to use Fastapi with SQLAlchemy with ease.
## Contents

- [Installation](#installation)
- [The database middlewares](#the-database-middlewares)
    - [The DatabaseMiddleware](#the-databasemiddleware)
    - [The AutocommitMiddleware](#the-autocommitmiddleware)
- [The event bus](#the-event-bus)
- [The yaml config reader](#the-yaml-configuration-loader)
- [Pydantic i18n](#pydantic-i18n)

## Installation

Installation using pip:
```shell
pip install fast_sqlalchemy
```

Or with poetry:
```shell
poetry add fast_sqlalchemy
```

## The database middlewares
Fast-sqlalchemy provide multiple middlewares to use SQLAlchemy with Fastapi easily

### The DatabaseMiddleware
The main middleware is the database middleware which is made to provide a sqlalchemy session accessible throughout your
application. We use the ContextVar api of python to have unique session in the context of each request.

To use this middleware you must at first create a Database object where you must pass the url of your database and the 
engine options of SQLAlchemy:

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
Note that if you want to have access to a sqlalchemy session outside a request context, you must create a session by 
using the session contextmanager of the Database object:

```python
with db.session_ctx():
    db.session.query(User).all()
```
The middleware is actually using this contextmanager for each request.

### The AutocommitMiddleware
The auto commit middleware as its name suggest is a middleware which automatically commit at the end of each request. 
It must be used with the database middleware and must be registered before otherwise it won't work:

```python
fastapi = Fastapi()
fastapi.add_middleware(AutocommitMiddleware, db=db)
fastapi.add_middleware(DatabaseMiddleware, db=db)
```

## The event bus
The event bus provide you a way to emit event in your application and register handlers to handle them. This allows
you to create an event-driven architecture for your application. 

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
There are two kinds of handler sync and async handler. Sync handlers are called once the event is emitted, 
whereas async handlers are called at the end of the current request.
To register an async handler is nearly the same as above

```python
@local_event_bus.async_handler(EmailChanged, OtherEvent)
def check_email_uniqueness(e: EmailChanged | OtherEvent):
    # some logic
    pass
```
Note that a handler can handle multiple types of event

After that you can emit events wherever you want in your Fastapi application:

```python
emit(EmailChanged(email=email))
```

## The database testing class

Fast-sqlalchemy provide a utility class named TestDatabase which can be used to test your Fastapi application with 
SQLAlchemy with ease. This class allow you to have isolated test by having each test wrapped in a transaction that is 
rollback at the end of each test, so that each test have a fresh database.

To use it with pytest, you can simply create two fixtures.
A primary fixture with a scope of 'session' which will create a connection to the database and create the database if it 
doesn't exist (A testing database is created with the same name of your application's database prefixed with 'test_'). 
The testing database is then dropped at the end (You can optionally turn if off).

```python
from my_app import factories

@pytest.fixture(scope="session")
def db_client():
    db_client = TestDatabase(db=app_db, factories_modules=[factories])
    with db_client.start_connection(metadata=metadata):
        yield db_client
```
Note that this class is compatible with the library factory_boy, you can register as shown in the example above a list 
of modules which contains your factory classes so that each factory wil be bound to the session provided by the TestDatabase object.

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

## The yaml configuration loader

Fast-sqlalchemy provide a class named Configuration which allow you to have your application's configuration store in yaml files:

```python
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config = Configuration(os.path.join(ROOT_DIR, "config"), env_path=os.path.join(ROOT_DIR, ".env"))
config.load_config(config="test")
```
When you're creating the object you must specify the path of your configuration directory, this directory will contain all of your yaml files.
You can also specify a .env file which will be read thanks to the dotenv library.
Then you can load these configurations file by calling __load_config__, you can specify a config name, this config name must
match a subdirectory within the configuration directory. This subdirectory should contain yaml files that will be merged
with the yaml files present at the root of the configuration directory. This way you can have multiple configurations witch 
will share the same base configuration.
The configuration folder may look like this:
```
+-- config
|   +-- base.yaml
|   +-- other.yaml
|   +-- test
|    |   +-- base.yaml
|   +-- prod
|    |   +-- base.yaml
```

Note that you can use your environment variables within your yaml files, these variables will be parsed.

```yaml
project_name: ${PROJECT_NAME}
secret_key: ${SECRET_KEY}
local: fr_FR
```
Then you can have access to your configuration within your application like this:

```python
config["general"]["project_name"]
```
or with the __get__ method witch accept dot-separated notation and a default
value as second parameter.
```python
config.get("general.project_name", "default_name")
```
Note that, if a key is not found in yaml files, as fallback we'll try to find the
key in environment or raise a KeyError exception if not present. 

## Pydantic i18n
This utility class allow you to translate all error messages of pydantic.
You can specify a translation for a specific pydantic's error code.
for instance:
```python
translations = {
  "fr_FR": {
    "value_error.any_str.max_length": "Ce champs doit faire {0} caractères",
    "value_error.any_str.min_length": "Ce {1} doit faire plus de {0} caractères",
  }
}
```
You can even organize it with a nested structure:
```python
translations = {
"fr_FR": {
    "value_error": {
      "any_str": {
        "max_length": "Ce champs doit faire {0} caractères",
      }
    } 
  }
}
```
The error's context can be accessible through the placeholders '{\d}' like the __format__ python's function
Then you can use these translations this way:
```python
tr = PydanticI18n(translations, local="fr_FR")
```
And create a middleware in Fastapi
```python
async def request_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=tr.translate(exc.errors()))
```

## Licence

This project is licensed under the terms of the MIT license.


