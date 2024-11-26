import pytest

from src.infrastructure.database.json_database import SimpleDatabase
from src.infrastructure.database.operation import CreateOperation, DeleteOperation, SetOperation
from src.infrastructure.database.write_ahead_logger import SimpleWAL


@pytest.fixture
def database():
    wal = SimpleWAL()
    db = SimpleDatabase(wal)
    return db


@pytest.fixture
def transaction(database):
    return database.begin_transaction()


def test_set_operation(transaction):
    transaction.set(key=1, value="value1")
    assert len(transaction._operations) == 1
    assert isinstance(transaction._operations[0], SetOperation)


def test_delete_operation(transaction):
    transaction.delete(key=1)
    assert len(transaction._operations) == 1
    assert isinstance(transaction._operations[0], DeleteOperation)


def test_create_operation(transaction):
    transaction.create(value="value1")
    assert len(transaction._operations) == 1
    assert isinstance(transaction._operations[0], CreateOperation)


def test_commit(database):
    transaction = database.begin_transaction()
    transaction.create(value="value1")
    transaction.commit()
    assert database.get_all() == ["value1"]


def test_rollback(transaction, database):
    transaction.create(value="value1")
    transaction.commit()
    transaction.rollback()
    assert database.get_all() == []


def test_commit_with_error(transaction, database):
    transaction.set(key=1, value="value1")
    transaction.commit()
    assert database.get(1) is None


def test_rollback_with_error(transaction, database):
    transaction.create(value="value1")
    transaction._operations[0].undo = lambda: (1 / 0)
    with pytest.raises(RuntimeError):
        transaction.rollback()
    assert database.get_all() == []


def test_transaction_context_manager(transaction):
    with transaction as session:
        session.create(value="value1")
    assert transaction._db.get_all() == ["value1"]


def test_transaction_context_manager_with_error(transaction):
    with transaction:
        transaction.set(key=1, value="value1")
        transaction._operations[0].execute = lambda: (1 / 0)
    assert transaction._db.get(1) is None


def test_many_operations(transaction):
    transaction.create(value="value1")
    transaction.create(value="value2")
    transaction.delete(key=1)
    assert len(transaction._operations) == 3
    transaction.commit()
    assert transaction._db.get_all() == ["value2"]


def test_many_transactions(database):
    transaction = database.begin_transaction()
    transaction.create(value="value1")
    transaction.commit()
    transaction = database.begin_transaction()
    transaction.create(value="value2")
    transaction.commit()
    assert database.get_all() == ["value1", "value2"]


def test_competitiveness_operations(database):
    transaction = database.begin_transaction()
    transaction.create(value="value1")
    transaction.set(key=1, value="value2")
    transaction.commit()
    assert database.get(1) == "value2"


def test_competitiveness_operations_with_error(database):
    transaction = database.begin_transaction()
    
    transaction.set(key=1, value="value2")
    transaction.create(value="value1")
   
    assert database.get_all() == []