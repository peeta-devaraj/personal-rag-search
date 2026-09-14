from app.eval.metrics import (
    dcg_at_k,
    evaluate_run,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_at_k_hit_and_miss():
    ranked = [10, 20, 30, 40]
    assert precision_at_k(ranked, {20}, k=4) == 0.25
    assert precision_at_k(ranked, {99}, k=4) == 0.0
    assert precision_at_k([], {20}, k=4) == 0.0


def test_recall_at_k_single_relevant():
    ranked = [10, 20, 30]
    assert recall_at_k(ranked, {20}, k=2) == 1.0
    assert recall_at_k(ranked, {20}, k=1) == 0.0
    assert recall_at_k(ranked, set(), k=5) == 0.0


def test_reciprocal_rank():
    assert reciprocal_rank([10, 20, 30], {20}) == 0.5
    assert reciprocal_rank([10, 20, 30], {10}) == 1.0
    assert reciprocal_rank([10, 20, 30], {99}) == 0.0
    assert reciprocal_rank([10, 20, 30], {30}, cutoff=2) == 0.0


def test_ndcg_perfect_ranking_is_one():
    ranked = [1, 2, 3]
    relevance = {1: 1.0}
    assert ndcg_at_k(ranked, relevance, k=3) == 1.0


def test_ndcg_worse_rank_is_lower_but_positive():
    relevance = {1: 1.0}
    best = ndcg_at_k([1, 2, 3], relevance, k=3)
    worse = ndcg_at_k([2, 1, 3], relevance, k=3)
    assert worse < best
    assert worse > 0


def test_dcg_zero_when_nothing_relevant():
    assert dcg_at_k([1, 2, 3], {}, k=3) == 0.0


def test_evaluate_run_averages_across_queries():
    ranked_lists = [[1, 2, 3], [5, 4, 6]]
    relevant = [{1}, {4}]
    results = evaluate_run(ranked_lists, relevant, k_values=[1, 3])
    assert results["P@1"] == 0.5  # hit for query 1, miss for query 2
    assert results["MRR"] == (1.0 + 0.5) / 2
