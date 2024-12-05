from dataclasses import dataclass, field
from os import environ


def get_env_variable(name: str, default: str | None = None) -> str:
    value = environ.get(name, default)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    return value


@dataclass
class WALConfig:
    filepath: str = field(
        default_factory=lambda: get_env_variable("WAL_FILEPATH", "test_data/wal.json")
    )


@dataclass
class DatabaseConfig:
    filepath: str = field(
        default_factory=lambda: get_env_variable(
            "DATABASE_FILEPATH", "test_data/database_data.json"
        )
    )


@dataclass
class Config:
    wal: WALConfig = field(default_factory=lambda: WALConfig())
    database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig())
