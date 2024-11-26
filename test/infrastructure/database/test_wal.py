import json

import pytest

from src.infrastructure.database.json_database import SimpleDatabase
from src.infrastructure.database.write_ahead_logger import WriteAheadLog


@pytest.fixture
def log_filepath(tmp_path):
    return tmp_path / "test_log.json"


@pytest.fixture
def wal(log_filepath):
    return WriteAheadLog(log_filepath)


@pytest.fixture
def database(wal):
    return SimpleDatabase(wal)


@pytest.fixture
def transaction(database):
    return database.begin_transaction()


def test_write_log(transaction):
    transaction.create(value="test")
    db = transaction._db
    transaction.commit()
    log = db.wal.get_log()

    assert 1 in log
    assert log == transaction.to_dict()


def test_get_log(wal):
    log = wal.get_log()
    assert isinstance(log, dict)


def test_clear_log(wal, transaction):
    transaction.create(value="test")
    wal.write_log(transaction)
    assert wal.get_log() == transaction.to_dict()
    wal.clear_log()
    assert wal.get_log() == {}


def test_apply_log(wal, database):
    transaction = database.begin_transaction()
    transaction.create(value="test")
    transaction.create(value="test2")
    wal.write_log(transaction)
    wal.apply_log(database)
    assert database.get_all() == ["test", "test2"]


def test_from_file_nonexistent(log_filepath):
    write_ahead_log = WriteAheadLog(log_filepath)
    log, last_tid = write_ahead_log._from_file()
    assert log == {}
    assert last_tid is None


def test_from_file_existing(log_filepath):
    log_data = {"log": {1: {1: {"operation": "test_operation", "data": "test_data"}}}, "tid": 1}
    with open(log_filepath, "w") as f:
        json.dump(log_data, f)

    write_ahead_log = WriteAheadLog(log_filepath)
    log, last_tid = write_ahead_log._from_file()
    assert log == log_data["log"]
    assert last_tid == 1
