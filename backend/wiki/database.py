import os
from datetime import UTC, datetime
from pathlib import Path

from .model import Document, DocumentRequest, DocumentTitle


def load_document(title: str) -> Document:
    file_path = _title_to_path(title)
    return _file_to_document(file_path)


def _title_to_path(title: str) -> Path:
    return _document_folder() / (title + ".md")


def _file_to_document(path: Path) -> Document:
    if not path.exists():
        raise FileNotFoundError(f"{path=} not found")
    updated_at = datetime.fromtimestamp(os.path.getmtime(path), tz=UTC)
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    title = path.name[:-3]
    return Document(title, content, updated_at)


def _document_folder() -> Path:
    return Path(os.environ["WIKI_DOCUMENT_FOLDER"])


def list_documents() -> list[DocumentTitle]:
    folder = _document_folder()
    if not folder.is_dir():
        raise RuntimeError("Wrong document folder")
    result = []
    for file in folder.iterdir():
        if not (file.is_file() and file.name.endswith(".md")):
            continue
        doc = _file_to_document(file)
        result.append(DocumentTitle.from_document(doc))
    return result


def save_document(doc: DocumentRequest):
    file_path = _title_to_path(doc.title)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(doc.content)
