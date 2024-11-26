from abc import ABC, abstractmethod
from typing import Any, Protocol


class Operation(ABC):
    _lsn: int

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def to_dict(self) -> dict[int, dict[str, Any]]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, **kwargs):
        pass


class TransactionInterface(Protocol):
    tid: int

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def to_dict(self) -> dict[int, dict[int, dict[str, Any]]]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, tid: int, db: "DatabaseInterface", operations: dict[int, dict[str, Any]]):
        pass


class DatabaseInterface[ValueType, TransactionType: TransactionInterface](Protocol):
    wal: "WriteAheadLogInterface"
    data: dict[int, object | dict[str, Any]]

    def set(self, key: int, value: ValueType):
        pass

    def create(self, value: object) -> int:
        pass

    def delete(self, key: int):
        pass

    def get(self, key: int) -> ValueType:
        pass

    def get_all(self) -> list[ValueType]:
        pass

    def begin_transaction(
        self,
    ) -> TransactionType:
        pass

    @property
    def next_id(self) -> int:
        pass

    @property
    def next_tid(self) -> int:
        pass

    @property
    def next_lsn(self) -> int:
        pass


class WriteAheadLogInterface(Protocol):
    @abstractmethod
    def write_log[TransactionType: TransactionInterface](self, transaction: TransactionType):
        pass

    @abstractmethod
    def get_log(self) -> dict[int, dict[int, dict[str, Any]]]:
        pass

    @abstractmethod
    def clear_log(self):
        pass

    @abstractmethod
    def apply_log(self, database: DatabaseInterface):
        pass
