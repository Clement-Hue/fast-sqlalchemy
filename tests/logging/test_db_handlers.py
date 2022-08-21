from logging import LogRecord

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import Table, MetaData, Column, String, select

from fast_sqlalchemy.logging.handlers import DatabaseHandler
from fast_sqlalchemy.persistence.database import Database

metadata = MetaData()

log_table = Table("logs", metadata,
          Column("time", String),
          Column("level", String),
          Column("message", String))

@pytest.fixture()
def db():
    db = Database("sqlite://")
    metadata.create_all(db.engine)
    return db


def test_db_handler(db, mocker: MockerFixture):
    def mapping(record: LogRecord):
        return {"level": record.levelname, "time": record.asctime, "message": record.message}
    handler = DatabaseHandler(db=db, table=log_table, mapping_logs=mapping)
    record_format = mocker.patch.object(handler, "format")
    time = "2022-10-01 08:10:12"
    message = "exception occurred"
    level = "INFO"
    record = mocker.Mock(levelname=level, asctime=time, message=message)
    with db.session_ctx():
        handler.emit(record)
        record_format.assert_called_with(record)
        logs = db.session.execute(select(log_table)).all()
        assert len(logs) == 1
        assert logs[0].level == level
        assert logs[0].message == message
        assert logs[0].time == time

