from typing import Any

from src.core.ports.database.operation import Operation
from src.infrastructure.database.json_database import DatabaseInterface


class SetOperation(Operation):
    def __init__(self, lsn: int, key: int, value: object, storage: DatabaseInterface):
        self.key = key
        self.value = value
        self.previous_value: object | None = None
        self._storage = storage
        self._lsn: int = lsn

    def execute(
        self,
    ):
        self.previous_value = self._storage.get(self.key)
        self._storage.set(self.key, self.value)

    def undo(self):
        if self.previous_value is None:
            del self._storage._data[self.key]
        else:
            self._storage.set(self.key, self.previous_value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": "set",
            "key": self.key,
            "value": self.value,
            "previous_value": self.previous_value,
        }


class DeleteOperation(Operation):
    def __init__(self, lsn: int, key: int, storage: DatabaseInterface):
        self.key = key
        self._storage = storage
        self._lsn: int = lsn
        self.previous_value: object | None = None

    def execute(self):
        self.previous_value = self._storage.get(self.key)
        self._storage.delete(self.key)

    def undo(self):
        if self.previous_value is None:
            raise ValueError("No previous value to undo")
        else:
            self._storage.set(self.key, self.previous_value)

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {
            "operation": "delete",
            "key": self.key,
            "previous_value": self.previous_value,
        }


class OperationFactory:
    @staticmethod
    def create[OperationType: Operation](
        lsn: int, operation_type: str, storage: DatabaseInterface, **kwargs
    ) -> OperationType:
        if operation_type == "set":
            key = kwargs["key"]
            value = kwargs["value"]
            return SetOperation(lsn, key, value, storage)
        elif operation_type == "delete":
            key = kwargs["key"]
            return DeleteOperation(lsn, key, storage)
        else:
            raise ValueError(f"Invalid operation type: {operation_type}")
