from typing import Any, cast

from src.core.ports.database import Operation, TransactionInterface


class SetOperation(Operation):
    def __init__(
        self, key: int, value: object, transaction: TransactionInterface, lsn: int | None = None
    ):
        self.key = key
        self.value = value
        self.previous_value: object | None = None
        self._transaction = transaction
        self._lsn: int = lsn or self._transaction._storage.next_lsn

    def execute(
        self,
    ):
        self.previous_value = self.previous_value or self._transaction.get(self.key)
        if self.previous_value is None:
            raise ValueError("No previous value. Did you mean to create?")
        self._transaction._temp_data[self.key] = self.value

    def undo(self):
        self._transaction._temp_data[self.key] = self.previous_value

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
    def from_dict(cls, lsn: int, transaction: TransactionInterface, **kwargs) -> "SetOperation":
        key = kwargs["key"]
        value = kwargs["value"]
        previous_value = kwargs.get("previous_value")
        op = cls(key, value, transaction, lsn)
        op.previous_value = previous_value
        return op


class CreateOperation(Operation):
    def __init__(self, value: object, transaction: TransactionInterface, lsn: int | None = None):
        self.key: int | None = None
        self.value = value
        self._transaction = transaction
        self._lsn = lsn or self._transaction._storage.next_lsn

    def execute(self) -> int:
        if self.key is None:
            self.key = self._transaction.block_id
        self._transaction._temp_data[self.key] = self.value
        return self.key

    def undo(self):
        if self.key in self._transaction._temp_data:
            self._transaction._temp_data.pop(self.key)

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {self._lsn: {"operation": "create", "value": self.value, "key": self.key}}

    @classmethod
    def from_dict(cls, lsn: int, transaction: TransactionInterface, **kwargs) -> "CreateOperation":
        key = kwargs.get("key")
        value = kwargs["value"]
        op = cls(value, transaction, lsn)
        op.key = key
        return op


class DeleteOperation(Operation):
    def __init__(self, key: int, transaction: TransactionInterface, lsn: int | None = None):
        self.key = key
        self._transaction = transaction
        self._lsn: int = lsn or self._transaction._storage.next_lsn
        self.previous_value: object | None = None

    def execute(self) -> None:
        self.previous_value = self.previous_value or self._transaction.get(self.key)
        if self.previous_value is None:
            raise ValueError("No previous value. Maybe you want to create?")
        self._transaction._temp_data[self.key] = None

    def undo(self):
        if self.previous_value is None:
            raise ValueError("No previous value to undo")
        else:
            self._transaction._temp_data[self.key] = self.previous_value

    def to_dict(self) -> dict[int, dict[str, Any]]:
        return {
            self._lsn: {
                "operation": "delete",
                "key": self.key,
                "previous_value": self.previous_value,
            }
        }

    @classmethod
    def from_dict(cls, lsn: int, transaction: TransactionInterface, **kwargs) -> "DeleteOperation":
        key = kwargs["key"]
        previous_value = kwargs.get("previous_value")
        op = cls(key, transaction, lsn)
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
    def from_dict(cls, lsn: int, transaction: TransactionInterface, **kwargs) -> "SimpleOperation":
        key = kwargs["key"]
        value = kwargs["value"]
        op = cls(key, lsn, value)
        return op


class OperationFactory[OperationType: Operation]:
    @staticmethod
    def create(
        lsn: int, operation_type: str, transaction: TransactionInterface, **kwargs
    ) -> OperationType:
        if operation_type == "set":
            return cast(
                OperationType, SetOperation.from_dict(lsn=lsn, transaction=transaction, **kwargs)
            )
        elif operation_type == "delete":
            return cast(
                OperationType, DeleteOperation.from_dict(lsn=lsn, transaction=transaction, **kwargs)
            )
        elif operation_type == "create":
            return cast(
                OperationType, CreateOperation.from_dict(lsn=lsn, transaction=transaction, **kwargs)
            )
        else:
            raise ValueError(f"Invalid operation type: {operation_type}")
