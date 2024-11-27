import json
from collections.abc import Generator
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

from src.core.ports.database.database import DatabaseInterface, WriteAheadLogInterface
from src.infrastructure.database.transaction import Transaction, TransactionFactory
from src.infrastructure.util import convert_keys_to_int

def object_to_dict(obj: object) -> dict[str, Any] | object:
    if is_dataclass(obj):
        return obj.to_dict()  # type: ignore
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return obj


class SimpleDatabase(DatabaseInterface):
    def __init__(self, wal: WriteAheadLogInterface):
        self.data = {}
        self._next_id = 0
        self._next_tid = 0
        self._next_lsn = 0
        self._transaction_factory = self._transaction_generator()
        self.wal = wal

    def sync(self):
        self.wal.apply_log(self)

    def set(self, key: int, value: object):
        self.data[key] = object_to_dict(value)

    def create(self, value: object) -> int:
        key = self.next_id
        self.data[key] = object_to_dict(value)
        return key

    def delete(self, key: int):
        if key in self.data:
            del self.data[key]

    def get(self, key: int) -> object:
        return self.data.get(key)

    def get_all(self) -> list[object]:
        return list(self.data.values())

    def _transaction_generator(self) -> Generator[Transaction, None, None]:
        transaction = None
        while True:
            if transaction is not None and not transaction._committed:
                transaction.commit()
            transaction = TransactionFactory.create(self.next_tid, self, {})
            yield transaction

    def begin_transaction(self):
        return next(self._transaction_factory)

    @property
    def next_id(self) -> int:
        id = self._next_id
        self._next_id += 1
        return id

    @property
    def next_tid(self) -> int:
        id = self._next_tid
        self._next_tid += 1
        return id

    @property
    def next_lsn(self) -> int:
        id = self._next_lsn
        self._next_lsn += 1
        return id


class JsonDatabase(DatabaseInterface):
    def __init__(self, json_filepath: str, wal: WriteAheadLogInterface):
        self.json_filepath = Path(json_filepath)
        self.wal = wal
        self._transaction_factory = self._transaction_generator()
        self._load_data()

    @property
    def next_id(self) -> int:
        id = self._next_id
        self._next_id += 1
        return id

    @property
    def next_tid(self) -> int:
        id = self._next_tid
        self._next_tid += 1
        return id

    @property
    def next_lsn(self) -> int:
        id = self._next_lsn
        self._next_lsn += 1
        return id

    def _load_data(self) -> None:
        if not self.json_filepath.exists():
            self.json_filepath.parent.mkdir(parents=True, exist_ok=True)
            self.json_filepath.touch(exist_ok=True)
            self.data = {}
            self._next_id = 0
            self._next_tid = 0
            self._next_lsn = 0
            return
        with open(self.json_filepath) as f:
            json_to_load = json.load(f)
            self.data = convert_keys_to_int(json_to_load["data"])
            self._next_id = json_to_load["next_id"]
            self._next_tid = json_to_load["next_tid"]
            self._next_lsn = json_to_load["next_lsn"]
        self.sync()

    def _save_data(self) -> None:
        try:
            json_to_save = {
                "data": self.data,
                "next_id": self._next_id,
                "next_tid": self._next_tid,
                "next_lsn": self._next_lsn,
            }
            with open(self.json_filepath, "w") as f:
                json.dump(json_to_save, f)
        except Exception as e:
            print("Error saving data\nTraceback:\n\t", e)

    def _transaction_generator(self) -> Generator[Transaction, None, None]:
        transaction = None
        while True:
            if transaction is not None:
                transaction.commit(transaction)
            transaction = Transaction(self.next_tid, self)
            yield transaction

    def begin_transaction(self) -> Transaction:
        return next(self._transaction_factory)

    def sync(self):
        self.wal.apply_log(self)

    def set(self, key: int, value: object):
        if key in self.data:
            self.data[key] = object_to_dict(value)
            self._save_data()
        else:
            raise KeyError(f"Key {key} not found in database")

    def create(self, value: object) -> int:
        key = self.next_id
        self.data[key] = object_to_dict(value)
        self._save_data()
        return key

    def delete(self, key: int):
        try:
            del self.data[key]
            self._save_data()
        except KeyError as exc:
            raise KeyError(f"Key {key} not found in database: {exc}") from exc

    def get(self, key: int):
        return self.data.get(key)

    def get_all(self) -> list[dict[str, Any] | object]:
        return list(self.data.values())
