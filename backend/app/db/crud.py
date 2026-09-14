from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document


def create_document(db: Session, filename: str, filetype: str) -> Document:
    doc = Document(filename=filename, filetype=filetype, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def add_chunks(db: Session, document_id: int, chunks: list[dict]) -> list[Chunk]:
    rows = [
        Chunk(
            document_id=document_id,
            chunk_index=c["chunk_index"],
            text=c["text"],
            page_start=c.get("page_start"),
            page_end=c.get("page_end"),
            token_count=c.get("token_count", 0),
        )
        for c in chunks
    ]
    db.add_all(rows)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


def set_document_status(db: Session, document_id: int, status: str, error_message: str | None = None) -> None:
    doc = db.get(Document, document_id)
    if doc is None:
        return
    doc.status = status
    doc.error_message = error_message
    db.commit()


def list_documents(db: Session) -> list[Document]:
    return list(db.scalars(select(Document).order_by(Document.upload_date.desc())))


def get_document(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)


def delete_document(db: Session, document_id: int) -> bool:
    doc = db.get(Document, document_id)
    if doc is None:
        return False
    db.delete(doc)
    db.commit()
    return True


def get_all_chunks(db: Session) -> list[Chunk]:
    return list(db.scalars(select(Chunk)))


def get_chunk(db: Session, chunk_id: int) -> Chunk | None:
    return db.get(Chunk, chunk_id)


def get_chunks_by_document(db: Session, document_id: int) -> list[Chunk]:
    return list(db.scalars(select(Chunk).where(Chunk.document_id == document_id)))
