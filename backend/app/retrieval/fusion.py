"""Reciprocal Rank Fusion: combines multiple ranked lists without needing to
normalize each list's raw relevance scores (BM25 scores and cosine
similarities live on incomparable scales, so summing them directly would be
wrong - RRF sidesteps that by fusing on rank position instead).

score(d) = sum over lists containing d of 1 / (k + rank_in_that_list)
rank is 1-indexed; k=60 is the standard default from the original RRF paper.
"""

DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(ranked_lists: list[list[dict]], k: int = DEFAULT_RRF_K) -> list[dict]:
    fused_scores: dict[int, float] = {}
    hit_by_id: dict[int, dict] = {}

    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked, start=1):
            cid = hit["chunk_id"]
            fused_scores[cid] = fused_scores.get(cid, 0.0) + 1.0 / (k + rank)
            hit_by_id.setdefault(cid, hit)

    fused = [
        {**hit_by_id[cid], "score": score}
        for cid, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    return fused
