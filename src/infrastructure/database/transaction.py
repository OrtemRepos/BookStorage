from typing import Any, cast

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


def _remove_none(dictionary: dict) -> dict:
        return dict(filter(lambda item: item[1] is not None, dictionary.items()))

class Transaction(TransactionInterface):
    def __init__(self, tid: int, storage: DatabaseInterface):
        self._storage = storage
        self.tid = tid
        self._operations: list[Operation] = []
        self._temp_data: dict[int, dict[str, Any] | object] = {}
        self._block_id: int | None = None
        self._last_processed_operation: Operation | None = None

    @property
    def block_id(self) -> int:
        if self._block_id is None:
            self._block_id = self._storage._next_id
        id = self._block_id
        self._block_id += 1
        return id

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

    def set(self, key: int, value: object) -> None:
        operation = SetOperation(key, value, self)
        self._operations.append(operation)

    def delete(self, key: int) -> None:
        operation = DeleteOperation(key, self)
        self._operations.append(operation)


    def create(self, value: object) -> int:
        operation = CreateOperation(value, self)
        key = self.block_id
        operation.key = key
        self._operations.append(operation)
        return key

    def get(self, key: int) -> object:
        if key in self._temp_data:
            return self._temp_data[key]
        return self._storage.get(key)

    def get_all(self) -> list[object]:
        data = self._storage.data.copy()
        data.update(self._temp_data)
        return list(_remove_none(data).values())

    def flush(self):
        for operation in self._operations:
            operation.execute()

    def commit(self, with_wal: bool = True):
        try:
            self.flush()
            old_data = self._storage.data.copy()
            old_data.update(self._temp_data)
            self._storage._next_id = self._block_id
            self._storage.data = _remove_none(old_data)
            if with_wal:
                self._storage.wal.write_log(self)
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
            self._storage._next_id = self._block_id
            self._temp_data = {}
        else:
            print("Error during commit transaction", exc_type, exc_val, exc_tb)
            self.rollback()


class TransactionProxy:
    def __init__(self, transaction: TransactionInterface):
        self._transaction = transaction
        self._committed = False

    def __getattr__(self, name: str) -> Any:
        if not self._committed:
            if name == "commit":
                self._committed = True
                return self._transaction.commit
            return getattr(self._transaction, name)
        elif name == "to_dict":
            return self._transaction.to_dict
        else:
            raise AttributeError(f"Transaction committed. No further actions allowed for {name}.")

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in ["_transaction", "_committed"]:
            super().__setattr__(__name, __value)
        elif not self._committed:
            setattr(self._transaction, __name, __value)
        else:
            raise AttributeError(f"Transaction committed. No further actions allowed for {__name}.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            print("Error during commit transaction", exc_type, exc_val, exc_tb)
            try:
                self.rollback()
            except Exception as e:
                raise RuntimeError(f"Error during rollback transaction: \n\t{e}") from e


class TransactionFactory:
    @classmethod
    def create(cls, tid: int, db, operations_dict: dict[int, dict[str, Any]]) -> Transaction:
        operations = []
        transaction = Transaction(tid, db)
        proxy_transaction = TransactionProxy(transaction)
        for lsn, operation_dict in operations_dict.items():
            op: Operation = OperationFactory.create(
                lsn, operation_dict["operation"], transaction, **operation_dict
            )
            operations.append(op)

        proxy_transaction._operations = operations
        return cast(Transaction, proxy_transaction)
