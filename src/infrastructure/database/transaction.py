from typing import Any

from src.core.ports.database.database import (
    DatabaseInterface,
    Operation,
    TransactionInterface,
)
from src.infrastructure.database.operation import (
    CreateOperation,
    DeleteOperation,
    OperationFactory,
    SetOperation,
)


class Transaction(TransactionInterface):
    def __init__(self, tid: int, db: DatabaseInterface):
        self._db = db
        self.tid = tid
        self._operations: list[Operation] = []
        self._last_processed_operation: Operation | None = None

    def to_dict(self) -> dict[int, dict[int, dict[str, Any]]]:
        dict_transaction = {}
        dict_operations = {}
        for operation in self._operations:
            dict_operations.update(operation.to_dict())
        dict_transaction[self.tid] = dict_operations
        return dict_transaction

    @classmethod
    def from_dict(
        cls, tid: int, db: DatabaseInterface, operations: dict[int, dict[str, Any]]
    ) -> "Transaction":
        return TransactionFactory.create(tid, db, operations)

    def set(self, key: int, value: object):
        operation = SetOperation(key, value, self._db)
        self._operations.append(operation)

    def delete(self, key: int):
        operation = DeleteOperation(key, self._db)
        self._operations.append(operation)

    def create(self, value: object):
        operation = CreateOperation(value, self._db)
        self._operations.append(operation)

    def commit(self):
        try:
            for operation in self._operations:
                operation.execute()
            self._db.wal.write_log(self)
        except Exception:
            self.rollback()

    def rollback(self):
        try:
            for operation in self._operations:
                operation.undo()
        except Exception as e:
            raise RuntimeError(f"Error during rollback transaction: \n\t{e}") from e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            try:
                print("Error during commit transaction", exc_type, exc_val, exc_tb)
                self.rollback()
            except Exception as e:
                raise RuntimeError(f"Error during rollback transaction: \n\t{e}") from e


class TransactionFactory:
    @classmethod
    def create(
        cls, tid: int, db: DatabaseInterface, operations_dict: dict[int, dict[str, Any]]
    ) -> Transaction:
        operations = []
        for lsn, operation_dict in operations_dict.items():
            op: Operation = OperationFactory.create(
                lsn, operation_dict["operation"], db, **operation_dict
            )
            operations.append(op)

        transaction = Transaction(tid, db)
        transaction._operations = operations
        return transaction
