"""Builds a synthetic labeled eval set: for each chunk, ask the local LLM to
write one question that chunk uniquely answers, and record (question,
source_chunk_id) as a gold pair - a standard synthetic-query-generation
technique used when no real query history exists yet.

Known bias worth documenting: synthetic questions tend to be lexically close
to their source passage (the LLM often echoes the passage's own wording),
which can inflate BM25's apparent performance relative to how it would do on
real, more loosely-worded user queries. This is called out explicitly in the
README rather than hidden, since acknowledging it is itself a mark of
evaluation rigor.
"""

import random

from sqlalchemy.orm import Session

from app.db import crud
from app.db.models import EvalQuestion
from app.generation.ollama_client import generate

QUESTION_PROMPT = """Given the passage below, write exactly one specific question that this \
passage directly and uniquely answers. The question must be answerable only from this passage, \
not a generic question. Return only the question text, nothing else.

Passage:
{chunk_text}

Question:"""

MIN_QUESTION_LEN = 10
REFUSAL_MARKERS = ("i cannot", "i can't", "i'm sorry", "as an ai", "i am unable")


def _is_valid_question(text: str) -> bool:
    text = text.strip()
    if len(text) < MIN_QUESTION_LEN:
        return False
    lowered = text.lower()
    if any(marker in lowered for marker in REFUSAL_MARKERS):
        return False
    return True


def _clean_question(text: str) -> str:
    text = text.strip().strip('"').strip()
    if text.lower().startswith("question:"):
        text = text[len("question:") :].strip()
    return text


def generate_qa_set(db: Session, sample_size: int = 100, force_regenerate: bool = False) -> int:
    if force_regenerate:
        db.query(EvalQuestion).delete()
        db.commit()

    all_chunks = crud.get_all_chunks(db)
    if not all_chunks:
        return 0

    already_covered = {q.chunk_id for q in db.query(EvalQuestion).all()}
    candidates = [c for c in all_chunks if c.id not in already_covered]

    if len(candidates) > sample_size:
        candidates = random.sample(candidates, sample_size)

    generated = 0
    for chunk in candidates:
        try:
            raw = generate(QUESTION_PROMPT.format(chunk_text=chunk.text))
        except RuntimeError:
            break
        question = _clean_question(raw)
        if not _is_valid_question(question):
            continue
        db.add(EvalQuestion(chunk_id=chunk.id, question_text=question))
        generated += 1

    db.commit()
    return generated
