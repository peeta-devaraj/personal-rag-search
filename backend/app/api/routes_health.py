import urllib.error
import urllib.request

from fastapi import APIRouter

from app.config import settings
from app.api.schemas import ConfigResponse, HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


def _ollama_reachable() -> bool:
    try:
        with urllib.request.urlopen(f"{settings.ollama_host}/api/tags", timeout=2):
            return True
    except (urllib.error.URLError, TimeoutError):
        return False


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        ollama_reachable=_ollama_reachable(),
        model=settings.ollama_model,
        embed_model=settings.embed_model,
    )


@router.get("/config", response_model=ConfigResponse)
def config() -> ConfigResponse:
    return ConfigResponse(
        llm_model=settings.ollama_model,
        embed_model=settings.embed_model,
        reranker_model=settings.reranker_model,
        chunk_target_tokens=settings.chunk_target_tokens,
        chunk_overlap_tokens=settings.chunk_overlap_tokens,
    )
