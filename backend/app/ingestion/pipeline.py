"""Orchestrates ingestion: load -> chunk -> persist -> (Phase 2+) embed & index."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.db import crud
from app.db.models import Document
from app.ingestion.chunker import chunk_pages
from app.ingestion.loader import load_pages


def ingest_file(db: Session, path: Path, filename: str, filetype: str) -> Document:
    doc = crud.create_document(db, filename=filename, filetype=filetype)
    try:
        pages = load_pages(path)
        drafts = chunk_pages(
            pages,
            target_tokens=settings.chunk_target_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        )
        chunk_dicts = [
            {
                "chunk_index": d.chunk_index,
                "text": d.text,
                "page_start": d.page_start,
                "page_end": d.page_end,
                "token_count": d.token_count,
            }
            for d in drafts
        ]
        chunks = crud.add_chunks(db, document_id=doc.id, chunks=chunk_dicts)

        _index_chunks_if_available(doc.id, doc.filename, chunks)

        crud.set_document_status(db, doc.id, status="ready")
    except Exception as exc:  # noqa: BLE001 - surface any ingestion failure on the document row
        crud.set_document_status(db, doc.id, status="failed", error_message=str(exc))
        raise
    db.refresh(doc)
    return doc


def _index_chunks_if_available(document_id: int, filename: str, chunks: list) -> None:
    """Embeds/indexes chunks into the vector + BM25 stores, once those modules exist (Phase 2/3)."""
    try:
        from app.retrieval.indexing import index_chunks  # noqa: PLC0415
    except ImportError:
        return
    index_chunks(document_id=document_id, filename=filename, chunks=chunks)
