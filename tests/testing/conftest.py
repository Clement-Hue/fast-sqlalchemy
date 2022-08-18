import logging
from fast_sqlalchemy.persistence.database import Database

logging.getLogger("alembic.runtime.migration").disabled = True
alembic_db = Database("sqlite:///test.db")
