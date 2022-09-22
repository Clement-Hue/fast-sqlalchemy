import sys, os, logging.config
from fast_sqlalchemy.config.yaml import Configuration
from fast_sqlalchemy.persistence.database import Database

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

config = Configuration(os.path.join(ROOT_DIR, "config"), env_path=os.path.join(ROOT_DIR, ".env"))
config.load_config(config="test" if 'pytest' in sys.modules else os.getenv("CONFIG", None))
logging.config.dictConfig(config.get("logging"))

if config.get("mode") == "prod":
    logging.raiseExceptions = False

db = Database(**config.get("db"))