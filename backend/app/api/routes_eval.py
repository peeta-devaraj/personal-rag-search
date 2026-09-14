import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.eval.generate_qa_pairs import generate_qa_set
from app.eval.runner import run_eval
from app.eval.storage import get_run, list_runs, save_run

router = APIRouter(prefix="/api/eval", tags=["eval"])

# In-memory job status for the QA-generation background task. Fine for a
# single-process local app; no need for a task queue at this scale.
_jobs: dict[str, dict] = {}


class GenerateQaSetRequest(BaseModel):
    sample_size: int = 100
    force_regenerate: bool = False


class RunEvalRequest(BaseModel):
    k_values: list[int] = [1, 3, 5, 10]


def _run_generation_job(job_id: str, sample_size: int, force_regenerate: bool) -> None:
    db = SessionLocal()
    try:
        _jobs[job_id]["status"] = "running"
        count = generate_qa_set(db, sample_size=sample_size, force_regenerate=force_regenerate)
        _jobs[job_id] = {"status": "done", "generated_count": count}
    except Exception as exc:  # noqa: BLE001
        _jobs[job_id] = {"status": "failed", "error": str(exc)}
    finally:
        db.close()


@router.post("/generate-qa-set")
def start_generate_qa_set(req: GenerateQaSetRequest, background_tasks: BackgroundTasks) -> dict:
    job_id = uuid.uuid4().hex
    _jobs[job_id] = {"status": "queued"}
    background_tasks.add_task(_run_generation_job, job_id, req.sample_size, req.force_regenerate)
    return {"job_id": job_id, "status": "queued"}


@router.get("/generate-qa-set/status/{job_id}")
def generate_qa_set_status(job_id: str) -> dict:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job id")
    return {"job_id": job_id, **job}


@router.post("/run")
def trigger_run(req: RunEvalRequest, db: Session = Depends(get_db)) -> dict:
    outcome = run_eval(db, k_values=req.k_values)
    if outcome["num_queries"] == 0:
        raise HTTPException(
            status_code=400,
            detail="No eval questions found. Call POST /api/eval/generate-qa-set first.",
        )
    run = save_run(db, results=outcome["results"], num_queries=outcome["num_queries"])
    return {
        "run_id": run.id,
        "results": outcome["results"],
        "num_queries": outcome["num_queries"],
        "timestamp": run.timestamp.isoformat(),
    }


@router.get("/runs")
def get_runs(db: Session = Depends(get_db)) -> dict:
    return {"runs": list_runs(db)}


@router.get("/runs/{run_id}")
def get_run_detail(run_id: int, db: Session = Depends(get_db)) -> dict:
    run = get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
