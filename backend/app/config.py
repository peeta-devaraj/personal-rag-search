from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
SAMPLE_CORPUS_DIR = DATA_DIR / "sample_corpus"
CHROMA_DIR = DATA_DIR / "chroma_db"
BM25_INDEX_PATH = DATA_DIR / "bm25_index.pkl"
SQLITE_PATH = DATA_DIR / "app.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b-instruct-q4_K_M"
    embed_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    chunk_target_tokens: int = 300
    chunk_overlap_tokens: int = 50


settings = Settings()

for d in (DATA_DIR, UPLOADS_DIR, SAMPLE_CORPUS_DIR, CHROMA_DIR):
    d.mkdir(parents=True, exist_ok=True)
