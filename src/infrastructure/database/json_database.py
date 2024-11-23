from dataclasses import asdict, is_dataclass
from functools import wraps
from typing import Any

from src.core.ports.database.database import DatabaseInterface


def key_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as exc:
            raise KeyError(f"Key {kwargs.get('key')} not found in database: {exc}") from exc

    return wrapper


def object_to_dict(obj: object) -> dict[str, Any]:
    if is_dataclass(obj):
        return asdict(obj)  # type: ignore
    else:
        return obj.__dict__


class JsonDatabase(DatabaseInterface):
    def __init__(self, json_filepath: str, log_filepath: str, state_filepath: str):
        self._next_id, self._next_tid = self._load_state()

    @property
    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id

    @property
    def next_tid(self) -> int:
        self._next_tid += 1
        return self._next_tid
