"""Pure-Python BM25 sparse retrieval (rank_bm25.BM25Okapi).

The index is small enough for a personal corpus to rebuild from scratch on
every document add/delete rather than supporting incremental updates -
simpler and fast enough at this scale.
"""

import pickle
import re

from rank_bm25 import BM25Okapi

from app.config import BM25_INDEX_PATH

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Small hardcoded stopword list to avoid an nltk data-download dependency here.
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he",
    "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "were",
    "will", "with", "this", "these", "those", "but", "or", "not", "can", "could",
    "would", "should", "do", "does", "did", "have", "had", "if", "then", "than",
    "so", "such", "no", "nor", "too", "very", "s", "t", "just", "into", "about",
    "which", "who", "whom", "what", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "own", "same", "we",
    "you", "i", "they", "them", "their", "our", "your", "his", "her", "she",
    "him", "my", "me", "us", "am", "been", "being", "up", "down", "out", "over",
    "under", "again", "further", "once", "here", "there",
}


def tokenize(text: str) -> list[str]:
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS]


class BM25Store:
    def __init__(self, chunk_ids: list[int], bm25: BM25Okapi):
        self.chunk_ids = chunk_ids
        self.bm25 = bm25

    def search(self, query: str, top_k: int) -> list[tuple[int, float]]:
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(zip(self.chunk_ids, scores), key=lambda x: x[1], reverse=True)
        return [(cid, float(score)) for cid, score in ranked[:top_k] if score > 0]


def rebuild_index() -> None:
    from app.db.session import SessionLocal  # noqa: PLC0415
    from app.db import crud  # noqa: PLC0415

    db = SessionLocal()
    try:
        chunks = crud.get_all_chunks(db)
        chunk_ids = [c.id for c in chunks]
        corpus = [tokenize(c.text) for c in chunks]
    finally:
        db.close()

    if not chunk_ids:
        if BM25_INDEX_PATH.exists():
            BM25_INDEX_PATH.unlink()
        return

    bm25 = BM25Okapi(corpus)
    with BM25_INDEX_PATH.open("wb") as f:
        pickle.dump({"chunk_ids": chunk_ids, "bm25": bm25}, f)


_cache: dict = {"mtime": None, "store": None}


def _load_store() -> BM25Store | None:
    """Cached by the index file's mtime, so a rebuild is picked up automatically
    without re-unpickling the whole corpus on every single query - unpickling a
    corpus of thousands of chunks on every call made batch operations (like the
    eval harness running dozens of queries) far slower than necessary."""
    if not BM25_INDEX_PATH.exists():
        _cache["mtime"] = None
        _cache["store"] = None
        return None

    mtime = BM25_INDEX_PATH.stat().st_mtime
    if _cache["store"] is not None and _cache["mtime"] == mtime:
        return _cache["store"]

    with BM25_INDEX_PATH.open("rb") as f:
        data = pickle.load(f)
    store = BM25Store(chunk_ids=data["chunk_ids"], bm25=data["bm25"])
    _cache["mtime"] = mtime
    _cache["store"] = store
    return store


def search(query: str, top_k: int = 10) -> list[dict]:
    """Returns hits in the same shape as vector_store.query(): includes text/filename/pages."""
    store = _load_store()
    if store is None:
        return []
    ranked = store.search(query, top_k)
    if not ranked:
        return []

    from app.db.session import SessionLocal  # noqa: PLC0415
    from app.db import crud  # noqa: PLC0415

    db = SessionLocal()
    try:
        hits = []
        for chunk_id, score in ranked:
            chunk = crud.get_chunk(db, chunk_id)
            if chunk is None:
                continue
            hits.append(
                {
                    "chunk_id": chunk.id,
                    "score": score,
                    "text": chunk.text,
                    "document_id": chunk.document_id,
                    "filename": chunk.document.filename,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                }
            )
        return hits
    finally:
        db.close()
