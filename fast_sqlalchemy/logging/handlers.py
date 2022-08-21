from logging import Handler, LogRecord
from typing import Callable

from sqlalchemy import insert, Table

from fast_sqlalchemy.persistence.database import Database


class DatabaseHandler(Handler):
    def __init__(self, db: Database, table: Table, mapping_logs: Callable[[LogRecord], dict[str, str]]):
        """

        :param db: The database object
        :param table_name: The table which will contain the logs
        :param values: The value
        """
        super().__init__()
        self.db = db
        self.table = table
        self.mapping_logs = mapping_logs

    def emit(self, record: LogRecord) -> None:
        try:
            self.format(record)
            with self.db.session_ctx():
                stmt = insert(self.table).values(**self.mapping_logs(record))
                self.db.session.execute(stmt)
                self.db.session.commit()
        except Exception:
            self.handleError(record)
