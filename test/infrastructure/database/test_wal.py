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
    db = transaction._storage
    transaction.commit()
    log = db.wal.get_log()

    assert 0 in log
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


def test_apply_log(database):
    transaction = database.begin_transaction()
    transaction.create(value="test")
    transaction.create(value="test2")
    transaction.commit()
    assert database.wal.get_log() == transaction.to_dict()


def test_apply_log_with_many_transactions(database):
    result = {}
    transaction = database.begin_transaction()
    transaction.create(value="test")
    transaction.commit()
    result.update(transaction.to_dict())
    transaction = database.begin_transaction()
    transaction.create(value="test2")
    transaction.commit()
    result.update(transaction.to_dict())

    assert database.wal.get_log() == result


def test_from_file_nonexistent(log_filepath):
    write_ahead_log = WriteAheadLog(log_filepath)
    log = write_ahead_log._from_file()
    assert log == {}


def test_from_file_existing(log_filepath):
    log_data = {1: {1: {"operation": "test_operation", "data": "test_data"}}}
    with open(log_filepath, "w") as f:
        json.dump(log_data, f)

    write_ahead_log = WriteAheadLog(log_filepath)
    log = write_ahead_log._from_file()
    assert log == log_data


def test_sync_transaction(database):
    transaction = database.begin_transaction()
    transaction.create(value="test")
    transaction.create(value="test2")
    transaction.commit()
    database.data = {}
    database.sync()
    assert database.get_all() == ["test", "test2"]


def test_sync_with_many_transactions(database):
    transaction = database.begin_transaction()
    key_1_1 = transaction.create(value="test_transaction_1")
    transaction.create(value="test2_transaction_1")
    transaction.set(key=key_1_1, value="test1_transaction_1")
    transaction.commit()
    transaction = database.begin_transaction()
    transaction.create(value="test1_transaction_2")
    transaction.create(value="test2_transaction_2")
    transaction.commit()
    database.data = {}
    database.sync()
    assert database.get_all() == [
        "test1_transaction_1",
        "test2_transaction_1",
        "test1_transaction_2",
        "test2_transaction_2",
    ]
