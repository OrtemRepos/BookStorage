from typing import Any, cast

from src.core.ports.database.database import DatabaseInterface, Operation


class SetOperation(Operation):
    def __init__(self, key: int, value: object, storage: DatabaseInterface, lsn: int | None = None):
        self.key = key
        self.value = value
        self.previous_value: object | None = None
        self._storage = storage
        self._lsn: int = lsn or self._storage.next_lsn

    def execute(
        self,
    ):
        self.previous_value = self.previous_value or self._storage.get(self.key)
        if self.previous_value is None:
            raise ValueError("No previous value. Did you mean to create?")
        self._storage.set(self.key, self.value)

    def undo(self):
        self._storage.set(self.key, self.previous_value)

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {
            self._lsn: {
                "operation": "set",
                "key": self.key,
                "value": self.value,
                "previous_value": self.previous_value,
            }
        }

    @classmethod
    def from_dict(cls, **kwargs) -> "SetOperation":
        key = kwargs["key"]
        value = kwargs["value"]
        previous_value = kwargs.get("previous_value")
        storage = kwargs["storage"]
        lsn = kwargs["lsn"]
        op = cls(key, value, storage, lsn)
        op.previous_value = previous_value
        return op


class CreateOperation(Operation):
    def __init__(self, value: object, storage: DatabaseInterface, lsn: int | None = None):
        self.key = None
        self.value = value
        self._storage = storage
        self._lsn = lsn or self._storage.next_lsn

    def execute(self):
        if self.key is None:
            self.key = self._storage.create(self.value)
        else:
            self._storage.set(self.key, self.value)

    def undo(self):
        if self.key is not None:
            self._storage.delete(self.key)

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {self._lsn: {"operation": "create", "value": self.value, "key": self.key}}

    @classmethod
    def from_dict(cls, **kwargs) -> "CreateOperation":
        key = kwargs.get("key")
        value = kwargs["value"]
        storage = kwargs["storage"]
        lsn = kwargs["lsn"]
        op = cls(value, storage, lsn)
        op.key = key
        return op


class DeleteOperation(Operation):
    def __init__(self, key: int, storage: DatabaseInterface, lsn: int | None = None):
        self.key = key
        self._storage = storage
        self._lsn: int = lsn or self._storage.next_lsn
        self.previous_value: object | None = None

    def execute(self):
        self.previous_value = self.previous_value or self._storage.get(self.key)
        self._storage.delete(self.key)

    def undo(self):
        if self.previous_value is None:
            raise ValueError("No previous value to undo")
        else:
            self._storage.set(self.key, self.previous_value)

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {
            self._lsn: {
                "operation": "delete",
                "key": self.key,
                "previous_value": self.previous_value,
            }
        }

    @classmethod
    def from_dict(cls, **kwargs) -> "DeleteOperation":
        key = kwargs["key"]
        previous_value = kwargs.get("previous_value")
        storage = kwargs["storage"]
        lsn = kwargs["lsn"]
        op = cls(key, storage, lsn)
        op.previous_value = previous_value
        return op


class SimpleOperation(Operation):
    def __init__(self, key: int, lsn: int, value: object):
        self.key = key
        self.value = value
        self._lsn = lsn

    def execute(self):
        print("Executing test operation")

    def undo(self):
        print("Undoing test operation")

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {
            self._lsn: {
                "operation": "test",
                "key": self.key,
                "value": self.value,
            }
        }

    @classmethod
    def from_dict(cls, **kwargs) -> "SimpleOperation":
        key = kwargs["key"]
        value = kwargs["value"]
        lsn = kwargs["lsn"]
        op = cls(key, lsn, value)
        return op


class OperationFactory[OperationType: Operation]:
    @staticmethod
    def create(
        lsn: int, operation_type: str, storage: DatabaseInterface, **kwargs
    ) -> OperationType:
        if operation_type == "set":
            return cast(OperationType, SetOperation.from_dict(lsn=lsn, storage=storage, **kwargs))
        elif operation_type == "delete":
            return cast(
                OperationType, DeleteOperation.from_dict(lsn=lsn, storage=storage, **kwargs)
            )
        elif operation_type == "create":
            return cast(
                OperationType, CreateOperation.from_dict(lsn=lsn, storage=storage, **kwargs)
            )
        else:
            raise ValueError(f"Invalid operation type: {operation_type}")
