from typing import Literal

from fastapi import FastAPI, Response, status

from .database import list_documents, load_document, save_document
from .model import Document, DocumentRequest, DocumentTitle

app = FastAPI()


FieldName = Literal["time", "title"]


@app.get("/documents/{title}")
async def read_document(title: str) -> Document:
    return load_document(title)


@app.get("/documents")
async def list_document(
    response: Response,
    sort_by: FieldName | None = None,
    title_only: bool = True,
) -> list[Document] | list[DocumentTitle]:
    if not title_only:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return []

    documents = list_documents()
    match sort_by:
        case "time":
            documents.sort(key=lambda x: x.modified_at)
        case "title":
            documents.sort(key=lambda x: x.title)
        case None:
            documents.sort(key=lambda x: x.title)
    return documents


@app.post("/documents/")
async def add_document(doc: DocumentRequest) -> Document:
    save_document(doc)
    return load_document(doc.title)


@app.put("/documents/{title}")
async def edit_document(doc: DocumentRequest) -> Document:
    save_document(doc)
    return load_document(doc.title)
