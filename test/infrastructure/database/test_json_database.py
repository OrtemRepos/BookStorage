import pytest

from src.infrastructure.database.json_database import JsonDatabase
from src.infrastructure.database.write_ahead_logger import SimpleWAL


@pytest.fixture
def json_filepath(tmp_path):
    return tmp_path / "test_db.json"


@pytest.fixture
def wal():
    return SimpleWAL()


@pytest.fixture
def db(json_filepath, wal):
    return JsonDatabase(json_filepath, wal)


def test_initialization(db, json_filepath):
    assert db.next_id == 0
    assert db.next_tid == 0
    assert db.next_lsn == 0
    assert db.data == {}


def test_create(db):
    key = db.create({"name": "test"})
    assert key == 0
    assert db.data[0] == {"name": "test"}


def test_set(db):
    key = db.create({"name": "test"})
    db.set(key, {"name": "updated"})
    assert db.data[key] == {"name": "updated"}


def test_set_nonexistent_key(db):
    with pytest.raises(KeyError):
        db.set(999, {"name": "test"})


def test_delete(db):
    key = db.create({"name": "test"})
    db.delete(key)
    assert key not in db.data


def test_get(db):
    key = db.create({"name": "test"})
    value = db.get(key)
    assert value == {"name": "test"}


def test_get_nonexistent_key(db):
    value = db.get(999)
    assert value is None


def test_get_all(db):
    db.create({"name": "test1"})
    db.create({"name": "test2"})
    all_values = db.get_all()
    assert len(all_values) == 2
    assert {"name": "test1"} in all_values
    assert {"name": "test2"} in all_values


def test_transaction(db):
    transaction = db.begin_transaction()
    assert transaction.tid == 0
    assert transaction._storage == db


def test_sync(db, wal):
    transaction = db.begin_transaction()
    transaction.create(value={"name": "test"})
    transaction.commit()
    db.sync()
    assert db.data == {0: {"name": "test"}}


def test_load_data(db, json_filepath):
    transaction = db.begin_transaction()
    transaction.create(value={"name": "test"})
    transaction.commit()
    db._save_data()
    new_db = JsonDatabase(json_filepath, SimpleWAL())
    assert new_db.data == db.data
    assert new_db.next_id == db.next_id
    assert new_db.next_tid == db.next_tid
    assert new_db.next_lsn == db.next_lsn
