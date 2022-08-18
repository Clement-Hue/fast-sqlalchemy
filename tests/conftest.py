import logging

pytest_plugins = ["pytester"]
logging.getLogger("alembic.runtime.migration").disabled = True