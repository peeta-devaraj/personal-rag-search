"""Orchestrates the full hybrid pipeline: dense + BM25 -> RRF fusion -> cross-encoder rerank -> top-k.

This is the core retrieval strategy the eval harness compares against the
single-strategy baselines (dense-only, bm25-only).
"""

from app.retrieval import bm25_index, embeddings, vector_store
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.reranker import rerank

FUSION_CANDIDATE_N = 20


def hybrid_search(question: str, top_k: int = 5, rerank_results: bool = True) -> list[dict]:
    query_vec = embeddings.embed_query(question)
    dense_hits = vector_store.query(query_vec, top_k=FUSION_CANDIDATE_N)
    sparse_hits = bm25_index.search(question, top_k=FUSION_CANDIDATE_N)

    fused = reciprocal_rank_fusion([dense_hits, sparse_hits])

    if not rerank_results:
        return fused[:top_k]

    candidates = fused[:FUSION_CANDIDATE_N]
    return rerank(question, candidates, top_k=top_k)
