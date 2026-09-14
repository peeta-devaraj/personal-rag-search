"""Cross-encoder reranking: scores (query, passage) pairs jointly, which is
more accurate than the bi-encoder cosine similarity used for initial
retrieval, but too slow to run over the whole corpus - so it only rescores
the fused candidate set from RRF.
"""

from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.config import settings


@lru_cache(maxsize=1)
def _model() -> CrossEncoder:
    return CrossEncoder(settings.reranker_model)


def rerank(query: str, candidates: list[dict], top_k: int) -> list[dict]:
    if not candidates:
        return []
    pairs = [(query, c["text"]) for c in candidates]
    scores = _model().predict(pairs)
    reranked = [
        {**c, "score": float(score)}
        for c, score in sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    ]
    return reranked[:top_k]
