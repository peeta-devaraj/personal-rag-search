"""Wraps the sentence-transformers embedding model.

BGE models are trained with an asymmetric retrieval objective: queries need an
instruction prefix but documents don't. Getting this backwards silently hurts
retrieval quality without erroring, so it's centralized here rather than left
to call sites to remember.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(settings.embed_model)


def embed_documents(texts: list[str]) -> np.ndarray:
    return _model().encode(texts, normalize_embeddings=True, show_progress_bar=False)


def embed_query(text: str) -> np.ndarray:
    return _model().encode(QUERY_PREFIX + text, normalize_embeddings=True, show_progress_bar=False)
