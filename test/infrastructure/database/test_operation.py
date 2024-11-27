import pytest

from src.infrastructure.database.json_database import SimpleDatabase
from src.infrastructure.database.operation import (
    CreateOperation,
    DeleteOperation,
    OperationFactory,
    SetOperation,
)
from src.infrastructure.database.write_ahead_logger import SimpleWAL


@pytest.fixture
def database():
    wal = SimpleWAL()
    return SimpleDatabase(wal)


@pytest.fixture
def transaction(database):
    return database.begin_transaction()


def test_set_operation(transaction):
    key = transaction.create("value")
    op = SetOperation(key, "test", transaction)
    transaction.flush()
    op.execute()
    assert transaction.get(key) == "test"
    op.undo()
    assert transaction.get(key) == "value"


def test_create_operation(transaction):
    op = CreateOperation("test", transaction)
    op.execute()
    key = op.key
    assert transaction.get(key) == "test"
    op.undo()
    assert transaction.get(key) is None


def test_delete_operation(transaction):
    key = transaction.create("value")
    op = DeleteOperation(key, transaction)
    transaction.flush()
    op.execute()
    assert transaction.get(key) is None
    op.undo()
    assert transaction.get(key) == "value"


def test_operation_factory_set(transaction):
    key = transaction.create("test")
    data = {"key": key, "value": "test", "previous_value": "prev_value"}
    op = OperationFactory.create(1, "set", transaction, **data)
    transaction.flush()
    op.execute()
    assert transaction.get(key) == "test"
    op.undo()
    assert transaction.get(key) == "prev_value"

    data["previous_value"] = "value1"

    op = OperationFactory.create(key, "set", transaction, **data)
    op.execute()
    assert transaction.get(key) == "test"
    op.undo()
    assert transaction.get(key) == "value1"


def test_operation_factory_create(transaction):
    data = {"value": "test"}

    op = OperationFactory.create(1, "create", transaction, **data)
    op.execute()
    assert transaction.get(0) == "test"
    op.undo()
    assert transaction.get(0) is None

    data = {"value": "test2", "key": 5}

    op = OperationFactory.create(2, "create", transaction, **data)
    op.execute()
    assert transaction.get(5) == "test2"
    op.undo()
    assert transaction.get(5) is None


def test_operation_factory_delete(transaction):
    key = transaction.create("value1")
    transaction.flush()
    data = {"key": key}
    op = OperationFactory.create(lsn=1, operation_type="delete", transaction=transaction, **data)
    op.execute()
    assert transaction.get(key) is None
    op.undo()
    assert transaction.get(key) == "value1"

    data = {"key": 5, "previous_value": "value2"}

    op = OperationFactory.create(lsn=2, operation_type="delete", transaction=transaction, **data)
    op.undo()
    assert transaction.get(5) == "value2"


def test_operation_factory_invalid_type(transaction):
    with pytest.raises(ValueError):
        OperationFactory.create(1, "invalid", transaction, **{})


def test_idempotency(transaction):
    key = transaction._storage.create("previous_value")
    set_op = SetOperation(key, "text", transaction)
    set_op.execute()
    assert transaction.get(key) == "text"

    set_op.execute()
    assert transaction.get_all() == ["text"]

    set_op.undo()
    assert transaction.get(key) == "previous_value"
    set_op.undo()
    assert transaction.get_all() == ["previous_value"]

    create_op = CreateOperation("text", transaction)
    create_op.execute()
    assert transaction.get_all() == ["previous_value", "text"]

    create_op.execute()
    assert transaction.get_all() == ["previous_value", "text"]

    create_op.undo()
    assert transaction.get_all() == ["previous_value"]
    create_op.undo()
    assert transaction.get_all() == ["previous_value"]

    delete_op = DeleteOperation(key, transaction)
    delete_op.execute()
    assert transaction.get_all() == []

    delete_op.execute()
    assert transaction.get_all() == []

    delete_op.undo()
    assert transaction.get_all() == ["previous_value"]
    delete_op.undo()
    assert transaction.get_all() == ["previous_value"]
