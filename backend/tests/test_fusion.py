from app.retrieval.fusion import reciprocal_rank_fusion


def test_fuses_two_lists_favoring_items_ranked_highly_in_both():
    dense = [{"chunk_id": 1, "text": "a"}, {"chunk_id": 2, "text": "b"}, {"chunk_id": 3, "text": "c"}]
    sparse = [{"chunk_id": 2, "text": "b"}, {"chunk_id": 3, "text": "c"}, {"chunk_id": 1, "text": "a"}]

    fused = reciprocal_rank_fusion([dense, sparse], k=60)
    fused_ids = [h["chunk_id"] for h in fused]

    # chunk 2 is rank 2 in dense and rank 1 in sparse -> best combined rank
    assert fused_ids[0] == 2
    assert set(fused_ids) == {1, 2, 3}


def test_item_only_in_one_list_still_included():
    dense = [{"chunk_id": 1, "text": "a"}]
    sparse = [{"chunk_id": 2, "text": "b"}]
    fused = reciprocal_rank_fusion([dense, sparse])
    assert {h["chunk_id"] for h in fused} == {1, 2}


def test_empty_lists_return_empty():
    assert reciprocal_rank_fusion([[], []]) == []
