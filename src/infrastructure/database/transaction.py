from typing import Any

from src.core.ports.database.database import (
    DatabaseInterface,
    TransactionInterface,
)
from src.core.ports.database.operation import Operation
from src.infrastructure.database.operation import DeleteOperation, SetOperation


class Transaction(TransactionInterface):
    def __init__(self, db: DatabaseInterface, tid: int):
        self._db = db
        self.tid = tid
        self._operations: list[Operation] = []
        self._last_processed_operation: Operation | None = None

    def to_dict(self) -> dict[int, dict[int, dict[str, Any]]]:
        dict_transaction = {}
        dict_operations = {}
        for operation in self._operations:
            dict_operations[operation._lsn] = operation.to_dict()
        dict_transaction[self.tid] = dict_operations
        return dict_transaction

    def set(self, key: int, value: object):
        operation = SetOperation(self.tid, key, value, self._db)
        self._operations.append(operation)

    def delete(self, key: int):
        operation = DeleteOperation(self.tid, key, self._db)
        operation._tid = self.tid
        self._operations.append(operation)

    def commit(self):
        try:
            sorted_operations = sorted(self._operations, key=lambda op: op._lsn)
            for operation in sorted_operations:
                operation.execute()
                self._last_processed_operation = operation
        except Exception as e:
            self.rollback()
            msg = f"Error during commit transaction {self.tid}\nTraceback: {e}"
            raise RuntimeError(msg) from e

    def rollback(self):
        try:
            sorted_operations = sorted(self._operations, reverse=True, key=lambda op: op._lsn)
            if self._last_processed_operation is not None:
                last_last_operation_index = sorted_operations.index(self._last_processed_operation)
                sorted_operations = sorted_operations[last_last_operation_index:]
            for operation in sorted_operations:
                operation.undo()
            self._last_processed_operation = None
        except Exception as e:
            msg = f"Error during rollback transaction {self.tid}\nTraceback: {e}"
            raise RuntimeError(msg) from e
