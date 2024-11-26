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


def test_set_operation(database):
    key = database.create("value")
    op = SetOperation(key, "test", database)
    op.execute()
    assert database.get(key) == "test"
    op.undo()
    assert database.get(key) == "value"


def test_create_operation(database):
    op = CreateOperation("test", database)
    op.execute()
    key = op.key
    assert database.get(key) == "test"
    op.undo()
    assert database.get(key) is None


def test_delete_operation(database):
    key = database.create("value")
    op = DeleteOperation(key, database)
    op.execute()
    assert database.get(key) is None
    op.undo()
    assert database.get(key) == "value"


def test_operation_factory_set(database):
    key = database.create("test")
    data = {"key": key, "value": "test", "previous_value": "prev_value"}
    op = OperationFactory.create(1, "set", database, **data)
    op.execute()
    assert database.get(key) == "test"
    op.undo()
    assert database.get(key) == "prev_value"

    data["previous_value"] = "value1"

    op = OperationFactory.create(key, "set", database, **data)
    op.execute()
    assert database.get(key) == "test"
    op.undo()
    assert database.get(key) == "value1"


def test_operation_factory_create(database):
    data = {"value": "test"}

    op = OperationFactory.create(1, "create", database, **data)
    op.execute()
    assert database.get(1) == "test"
    op.undo()
    assert database.get(1) is None

    data = {"value": "test2", "key": 5}

    op = OperationFactory.create(2, "create", database, **data)
    op.execute()
    assert database.get(5) == "test2"
    op.undo()
    assert database.get(5) is None


def test_operation_factory_delete(database):
    database.set(1, "value1")
    data = {"key": 1}
    op = OperationFactory.create(lsn=1, operation_type="delete", storage=database, **data)
    op.execute()
    assert database.get(1) is None
    op.undo()
    assert database.get(1) == "value1"

    data = {"key": 5, "previous_value": "value2"}

    op = OperationFactory.create(lsn=2, operation_type="delete", storage=database, **data)
    op.undo()
    assert database.get(5) == "value2"


def test_operation_factory_invalid_type(database):
    with pytest.raises(ValueError):
        OperationFactory.create(1, "invalid", database, **{})


def test_idempotency(database):
    key = database.create("previous_value")

    set_op = SetOperation(key, "text", database)
    set_op.execute()
    assert database.get(key) == "text"

    set_op.execute()
    assert database.get_all() == ["text"]

    set_op.undo()
    assert database.get(key) == "previous_value"
    set_op.undo()
    assert database.get_all() == ["previous_value"]

    assert database.get_all() == ["previous_value"]

    create_op = CreateOperation("text", database)
    create_op.execute()
    assert database.get_all() == ["previous_value", "text"]

    create_op.execute()
    assert database.get_all() == ["previous_value", "text"]

    create_op.undo()
    assert database.get_all() == ["previous_value"]
    create_op.undo()
    assert database.get_all() == ["previous_value"]

    delete_op = DeleteOperation(key, database)
    delete_op.execute()
    assert database.get_all() == []

    delete_op.execute()
    assert database.get_all() == []

    delete_op.undo()
    assert database.get_all() == ["previous_value"]
    delete_op.undo()
    assert database.get_all() == ["previous_value"]
