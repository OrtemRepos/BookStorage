from abc import ABC, abstractmethod
from typing import Any, Protocol


class Operation(ABC):
    _lsn: int

    @abstractmethod
    def execute(self) -> Any:
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def to_dict(self) -> dict[int, dict[str, Any]]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, lsn: int, transaction: "TransactionInterface", **kwargs):
        pass


class TransactionInterface(Protocol):
    tid: int
    _storage: "DatabaseInterface"
    _temp_data: dict[int, dict[str, Any] | object]

    @property
    def block_id(self) -> int:
        pass

    @abstractmethod
    def commit(self, with_wal: bool = True):
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

    @abstractmethod
    def set(self, key: int, value: object):
        pass

    @abstractmethod
    def delete(self, key: int):
        pass

    @abstractmethod
    def get(self, key: int) -> object:
        pass

    @abstractmethod
    def get_all(self) -> list[object]:
        pass

    @abstractmethod
    def create(self, value: object) -> int:
        pass


class DatabaseInterface[ValueType, TransactionType: TransactionInterface](Protocol):
    wal: "WriteAheadLogInterface"
    data: dict[int, object | dict[str, Any]]
    _next_id: int
    _next_tid: int
    _next_lsn: int

    @abstractmethod
    def sync(self) -> None:
        pass

    @abstractmethod
    def set(self, key: int, value: ValueType):
        pass

    @abstractmethod
    def create(self, value: object) -> int:
        pass

    @abstractmethod
    def delete(self, key: int):
        pass

    @abstractmethod
    def get(self, key: int) -> ValueType:
        pass

    @abstractmethod
    def get_all(self) -> list[ValueType]:
        pass

    @abstractmethod
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
