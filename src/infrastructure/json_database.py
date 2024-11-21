import json
import shutil
from dataclasses import asdict, is_dataclass
from functools import wraps
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from uuid import UUID

from src.core.ports.base_session import SessionInterface


def key_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as exc:
            raise KeyError(
                f"Key {kwargs.get('key')} not found in database: {exc}"
            ) from exc

    return wrapper


def object_to_dict(obj: object) -> dict[str, Any]:
    if is_dataclass(obj):
        return asdict(obj)  # type: ignore
    else:
        return obj.__dict__


class JsonSession(SessionInterface):
    def __init__(self, id: UUID, db: "JsonDatabase"):
        self._id = id
        self._db = db
        self._transaction_data: dict[int, Any] = {}

    @key_exception
    def add(self, key: int, value: object):
        self._transaction_data[key] = object_to_dict(value)

    @key_exception
    def get(self, key: int):
        return self._transaction_data[key]

    @key_exception
    def delete(self, key: int):
        del self._transaction_data[key]

    @key_exception
    def update(self, key: int, value: object):
        self._transaction_data[key] = object_to_dict(value)

    def commit(self):
        original_data = self._db.get_data()
        try:
            updated_data = original_data.copy()
            updated_data.update(self._transaction_data)
            self._db._save_data(updated_data)
            self._transaction_data = {}
        except Exception as e:
            raise RuntimeError("Commit failed") from e

    def rollback(self):
        self._db._save_data(self._old_data)
        self._transaction_data = {}


class JsonDatabase:
    def __init__(self, filepath: str):
        self._filepath = filepath
        self._data: dict[str, Any] = self._load_data()
        self._sessions: dict[UUID, JsonSession] = {}

    def get_data(self) -> dict[str, Any]:
        self._data.update
        return self._data

    def _load_data(self) -> dict[str, Any]:
        if Path(self.filepath).exists():
            with open(self.filepath, "r") as f:
                return json.load(f)
        else:
            return {}

    def _save_data(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f)

    def begin_transaction(self) -> JsonSession:
        pass

    def add(self, key: str, value: object):
        self.data[key] = self._object_to_dict(value)

    @key_exception
    def get(self, key: str):
        return self.data[key]

    @key_exception
    def delete(self, key: str):
        del self.data[key]

    @key_exception
    def update(self, key: str, value: object):
        self.data[key] = value
