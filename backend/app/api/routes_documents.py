import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.config import UPLOADS_DIR
from app.db import crud
from app.db.session import get_db
from app.ingestion.loader import UnsupportedFileType
from app.ingestion.pipeline import ingest_file
from app.api.schemas import (
    DeleteResponse,
    DocumentListResponse,
    DocumentOut,
    UploadResponse,
    UploadResultItem,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_SUFFIXES = {".pdf", ".txt", ".md"}


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: list[UploadFile], db: Session = Depends(get_db)) -> UploadResponse:
    results: list[UploadResultItem] = []

    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            results.append(
                UploadResultItem(
                    document_id=-1,
                    filename=upload.filename or "unknown",
                    status="rejected",
                    error_message=f"Unsupported file type: {suffix or 'unknown'}",
                )
            )
            continue

        dest_name = f"{uuid.uuid4().hex}{suffix}"
        dest_path = UPLOADS_DIR / dest_name
        with dest_path.open("wb") as f:
            shutil.copyfileobj(upload.file, f)

        try:
            doc = await run_in_threadpool(
                ingest_file, db, dest_path, upload.filename or dest_name, suffix.lstrip(".")
            )
            results.append(
                UploadResultItem(document_id=doc.id, filename=doc.filename, status=doc.status)
            )
        except UnsupportedFileType as exc:
            results.append(
                UploadResultItem(
                    document_id=-1, filename=upload.filename or dest_name, status="failed", error_message=str(exc)
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                UploadResultItem(
                    document_id=-1, filename=upload.filename or dest_name, status="failed", error_message=str(exc)
                )
            )

    return UploadResponse(uploaded=results)


@router.get("", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)) -> DocumentListResponse:
    docs = crud.list_documents(db)
    return DocumentListResponse(documents=[DocumentOut.model_validate(d) for d in docs])


@router.delete("/{document_id}", response_model=DeleteResponse)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> DeleteResponse:
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        from app.retrieval.indexing import remove_document  # noqa: PLC0415

        remove_document(document_id)
    except ImportError:
        pass

    deleted = crud.delete_document(db, document_id)
    return DeleteResponse(deleted=deleted)
