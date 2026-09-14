import time

from app.generation.ollama_client import generate
from app.generation.prompt_templates import build_prompt
from app.retrieval.retrieve import retrieve


def answer_question(question: str, strategy: str = "hybrid", top_k: int = 5) -> dict:
    t0 = time.perf_counter()
    hits = retrieve(question, strategy=strategy, top_k=top_k)
    retrieval_ms = (time.perf_counter() - t0) * 1000

    citations = [
        {
            "chunk_id": h["chunk_id"],
            "document_id": h["document_id"],
            "filename": h["filename"],
            "page_start": h["page_start"],
            "page_end": h["page_end"],
            "snippet": h["text"][:400],
            "score": round(float(h["score"]), 4),
        }
        for h in hits
    ]

    if not hits:
        return {
            "answer": "No documents have been indexed yet, so I can't answer this from your notes.",
            "citations": [],
            "strategy_used": strategy,
            "retrieval_ms": retrieval_ms,
            "generation_ms": 0.0,
        }

    t1 = time.perf_counter()
    prompt = build_prompt(question, [h["text"] for h in hits])
    answer = generate(prompt)
    generation_ms = (time.perf_counter() - t1) * 1000

    return {
        "answer": answer,
        "citations": citations,
        "strategy_used": strategy,
        "retrieval_ms": retrieval_ms,
        "generation_ms": generation_ms,
    }
