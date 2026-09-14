from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    filename: str
    filetype: str
    upload_date: datetime
    status: str
    num_chunks: int
    error_message: str | None = None

    model_config = {"from_attributes": True}


class UploadResultItem(BaseModel):
    document_id: int
    filename: str
    status: str
    error_message: str | None = None


class UploadResponse(BaseModel):
    uploaded: list[UploadResultItem]


class DocumentListResponse(BaseModel):
    documents: list[DocumentOut]


class DeleteResponse(BaseModel):
    deleted: bool


class CitationOut(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    page_start: int | None
    page_end: int | None
    snippet: str
    score: float


class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    strategy: str = "hybrid"  # "hybrid" | "dense" | "bm25"


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationOut]
    strategy_used: str
    retrieval_ms: float
    generation_ms: float


class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    model: str
    embed_model: str


class ConfigResponse(BaseModel):
    llm_model: str
    embed_model: str
    reranker_model: str
    chunk_target_tokens: int
    chunk_overlap_tokens: int
