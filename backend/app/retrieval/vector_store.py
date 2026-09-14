"""ChromaDB wrapper: persistent, embedded, no server process.

Chosen over raw FAISS because it bundles ID/metadata management alongside the
vector index, so this module stays focused on add/query/delete rather than
hand-rolled ID bookkeeping.
"""

import os
from functools import lru_cache

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb

from app.config import CHROMA_DIR

COLLECTION_NAME = "chunks"


@lru_cache(maxsize=1)
def _client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


@lru_cache(maxsize=1)
def _collection():
    return _client().get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(chunk_ids: list[int], embeddings, documents: list[str], metadatas: list[dict]) -> None:
    _collection().upsert(
        ids=[str(cid) for cid in chunk_ids],
        embeddings=embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def query(embedding, top_k: int = 10) -> list[dict]:
    """Returns [{chunk_id, score, text, filename, document_id, page_start, page_end}, ...] best-first."""
    emb = embedding.tolist() if hasattr(embedding, "tolist") else embedding
    result = _collection().query(query_embeddings=[emb], n_results=top_k)
    ids = result.get("ids", [[]])[0]
    distances = result.get("distances", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    hits = []
    for cid, dist, doc_text, meta in zip(ids, distances, documents, metadatas):
        hits.append(
            {
                "chunk_id": int(cid),
                "score": 1.0 - dist,  # cosine space in Chroma returns distance = 1 - cosine_similarity
                "text": doc_text,
                "document_id": meta.get("document_id"),
                "filename": meta.get("filename"),
                "page_start": meta.get("page_start"),
                "page_end": meta.get("page_end"),
            }
        )
    return hits


def delete_document_chunks(chunk_ids: list[int]) -> None:
    if not chunk_ids:
        return
    _collection().delete(ids=[str(cid) for cid in chunk_ids])
