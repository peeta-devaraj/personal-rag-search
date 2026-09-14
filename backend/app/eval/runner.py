from sqlalchemy.orm import Session

from app.db.models import EvalQuestion
from app.eval.metrics import evaluate_run
from app.retrieval.retrieve import retrieve

STRATEGIES = ("bm25", "dense", "hybrid")
RETRIEVAL_CUTOFF = 20


def run_eval(db: Session, k_values: list[int] | None = None) -> dict:
    k_values = k_values or [1, 3, 5, 10]
    questions = db.query(EvalQuestion).all()
    if not questions:
        return {"results": {}, "num_queries": 0}

    results: dict[str, dict] = {}
    for strategy in STRATEGIES:
        per_query_ranked: list[list[int]] = []
        per_query_relevant: list[set[int]] = []
        for q in questions:
            hits = retrieve(q.question_text, strategy=strategy, top_k=RETRIEVAL_CUTOFF)
            per_query_ranked.append([h["chunk_id"] for h in hits])
            per_query_relevant.append({q.chunk_id})
        results[strategy] = evaluate_run(per_query_ranked, per_query_relevant, k_values, mrr_cutoff=RETRIEVAL_CUTOFF)

    return {"results": results, "num_queries": len(questions)}
