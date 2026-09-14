import json

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import EvalRun


def save_run(db: Session, results: dict, num_queries: int) -> EvalRun:
    config = {
        "embed_model": settings.embed_model,
        "reranker_model": settings.reranker_model,
        "chunk_target_tokens": settings.chunk_target_tokens,
        "chunk_overlap_tokens": settings.chunk_overlap_tokens,
    }
    run = EvalRun(
        num_queries=num_queries,
        config_json=json.dumps(config),
        results_json=json.dumps(results),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def list_runs(db: Session) -> list[dict]:
    runs = db.query(EvalRun).order_by(EvalRun.timestamp.desc()).all()
    return [
        {
            "run_id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "num_queries": r.num_queries,
            "summary_metrics": json.loads(r.results_json),
        }
        for r in runs
    ]


def get_run(db: Session, run_id: int) -> dict | None:
    run = db.get(EvalRun, run_id)
    if run is None:
        return None
    return {
        "run_id": run.id,
        "timestamp": run.timestamp.isoformat(),
        "num_queries": run.num_queries,
        "config": json.loads(run.config_json),
        "results": json.loads(run.results_json),
    }
