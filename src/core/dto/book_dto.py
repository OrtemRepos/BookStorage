from dataclasses import asdict, dataclass
from typing import Any

from src.core.domain.book import BookStatus


@dataclass
class BookDTO:
    title: str
    author: str
    year: int
    status: BookStatus

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReadBookDTO(BookDTO):
    id: int
