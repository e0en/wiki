from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    title: str
    content: str
    modified_at: datetime


@dataclass
class DocumentTitle:
    title: str
    modified_at: datetime

    @classmethod
    def from_document(cls, d: Document) -> DocumentTitle:
        return DocumentTitle(d.title, d.modified_at)


@dataclass
class DocumentRequest:
    title: str
    content: str
