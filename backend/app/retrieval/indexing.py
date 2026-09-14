"""Keeps the vector store (and, from Phase 3, the BM25 index) in sync with SQLite.

Called from the ingestion pipeline after chunks are persisted, and from the
document-delete route. Kept separate from vector_store.py/bm25_index.py so
each of those stays a thin wrapper around its own backend.
"""

from app.retrieval import embeddings, vector_store


def index_chunks(document_id: int, filename: str, chunks: list) -> None:
    if not chunks:
        return

    texts = [c.text for c in chunks]
    vecs = embeddings.embed_documents(texts)
    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "page_start": c.page_start or 0,
            "page_end": c.page_end or 0,
        }
        for c in chunks
    ]
    vector_store.add_chunks(
        chunk_ids=[c.id for c in chunks],
        embeddings=vecs,
        documents=texts,
        metadatas=metadatas,
    )
    _rebuild_bm25_if_available()


def remove_document(document_id: int) -> None:
    from app.db.session import SessionLocal  # noqa: PLC0415
    from app.db import crud  # noqa: PLC0415

    db = SessionLocal()
    try:
        chunks = crud.get_chunks_by_document(db, document_id)
        chunk_ids = [c.id for c in chunks]
    finally:
        db.close()

    vector_store.delete_document_chunks(chunk_ids)
    _rebuild_bm25_if_available()


def _rebuild_bm25_if_available() -> None:
    try:
        from app.retrieval.bm25_index import rebuild_index  # noqa: PLC0415
    except ImportError:
        return
    rebuild_index()
