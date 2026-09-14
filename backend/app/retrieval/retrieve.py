"""Strategy dispatcher: routes a query to dense/bm25/hybrid retrieval.

Only "dense" is implemented in Phase 2. Phase 3 adds bm25 + hybrid (RRF) and
Phase 4 layers cross-encoder reranking on top of hybrid.
"""

from app.retrieval import embeddings, vector_store

STRATEGIES = ("dense", "bm25", "hybrid")


def retrieve(question: str, strategy: str = "dense", top_k: int = 5) -> list[dict]:
    if strategy == "dense":
        return _retrieve_dense(question, top_k)
    if strategy == "bm25":
        return _retrieve_bm25(question, top_k)
    if strategy == "hybrid":
        return _retrieve_hybrid(question, top_k)
    raise ValueError(f"Unknown retrieval strategy: {strategy!r}. Choose from {STRATEGIES}.")


def _retrieve_dense(question: str, top_k: int) -> list[dict]:
    query_vec = embeddings.embed_query(question)
    return vector_store.query(query_vec, top_k=top_k)


def _retrieve_bm25(question: str, top_k: int) -> list[dict]:
    try:
        from app.retrieval.bm25_index import search as bm25_search  # noqa: PLC0415
    except ImportError as exc:
        raise NotImplementedError("BM25 retrieval not available yet (Phase 3).") from exc
    return bm25_search(question, top_k=top_k)


def _retrieve_hybrid(question: str, top_k: int) -> list[dict]:
    try:
        from app.retrieval.hybrid import hybrid_search  # noqa: PLC0415
    except ImportError as exc:
        raise NotImplementedError("Hybrid retrieval not available yet (Phase 3/4).") from exc
    return hybrid_search(question, top_k=top_k)
