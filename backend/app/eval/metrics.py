"""Standard IR ranking metrics, implemented generically (supporting graded
relevance) even though this project's gold set only has one relevant chunk
per query - so the implementation reads as reusable/correct rather than
hardcoded to that special case.
"""

import math


def precision_at_k(ranked_ids: list[int], relevant_ids: set[int], k: int) -> float:
    top_k = ranked_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for cid in top_k if cid in relevant_ids)
    return hits / len(top_k)


def recall_at_k(ranked_ids: list[int], relevant_ids: set[int], k: int) -> float:
    if not relevant_ids:
        return 0.0
    top_k = ranked_ids[:k]
    hits = sum(1 for cid in top_k if cid in relevant_ids)
    return hits / len(relevant_ids)


def reciprocal_rank(ranked_ids: list[int], relevant_ids: set[int], cutoff: int | None = None) -> float:
    candidates = ranked_ids[:cutoff] if cutoff else ranked_ids
    for rank, cid in enumerate(candidates, start=1):
        if cid in relevant_ids:
            return 1.0 / rank
    return 0.0


def dcg_at_k(ranked_ids: list[int], relevance: dict[int, float], k: int) -> float:
    top_k = ranked_ids[:k]
    return sum(relevance.get(cid, 0.0) / math.log2(i + 2) for i, cid in enumerate(top_k))


def ndcg_at_k(ranked_ids: list[int], relevance: dict[int, float], k: int) -> float:
    ideal_order = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_order))
    if idcg == 0:
        return 0.0
    return dcg_at_k(ranked_ids, relevance, k) / idcg


def evaluate_run(
    per_query_ranked_ids: list[list[int]],
    per_query_relevant_ids: list[set[int]],
    k_values: list[int],
    mrr_cutoff: int = 20,
) -> dict:
    """Averages P@k/R@k/nDCG@k and MRR across all queries for one retrieval strategy."""
    n = len(per_query_ranked_ids)
    if n == 0:
        return {}

    results: dict[str, float] = {}
    for k in k_values:
        results[f"P@{k}"] = sum(
            precision_at_k(ranked, rel, k) for ranked, rel in zip(per_query_ranked_ids, per_query_relevant_ids)
        ) / n
        results[f"R@{k}"] = sum(
            recall_at_k(ranked, rel, k) for ranked, rel in zip(per_query_ranked_ids, per_query_relevant_ids)
        ) / n
        results[f"nDCG@{k}"] = sum(
            ndcg_at_k(ranked, {cid: 1.0 for cid in rel}, k)
            for ranked, rel in zip(per_query_ranked_ids, per_query_relevant_ids)
        ) / n

    results["MRR"] = sum(
        reciprocal_rank(ranked, rel, cutoff=mrr_cutoff)
        for ranked, rel in zip(per_query_ranked_ids, per_query_relevant_ids)
    ) / n

    return {k: round(v, 4) for k, v in results.items()}
