"""Ingests the bundled sample corpus so the app is demoable immediately.

Run with: python -m app.seed_corpus
Skips files whose name is already an indexed document, so it's safe to
re-run after adding your own files to data/sample_corpus/.
"""

from app.config import SAMPLE_CORPUS_DIR
from app.db import crud
from app.db.session import SessionLocal, init_db
from app.ingestion.pipeline import ingest_file


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        existing_filenames = {d.filename for d in crud.list_documents(db)}
        files = sorted(SAMPLE_CORPUS_DIR.glob("*"))
        if not files:
            print(f"No files found in {SAMPLE_CORPUS_DIR}")
            return

        for path in files:
            if path.name in existing_filenames:
                print(f"skip (already indexed): {path.name}")
                continue
            suffix = path.suffix.lower().lstrip(".")
            doc = ingest_file(db, path, filename=path.name, filetype=suffix)
            print(f"ingested: {doc.filename} -> {doc.num_chunks} chunks ({doc.status})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
