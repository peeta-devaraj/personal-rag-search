RAG_PROMPT = """You are a helpful assistant answering questions using ONLY the provided source passages from the user's own notes/documents.

Rules:
- Answer using only information found in the passages below. If the passages don't contain the answer, say so plainly.
- Cite sources inline using the bracketed number of the passage, e.g. [1], [2]. Cite every claim you make.
- Be concise and direct.

Passages:
{context}

Question: {question}

Answer:"""


def build_context(passages: list[str]) -> str:
    return "\n\n".join(f"[{i + 1}] {text}" for i, text in enumerate(passages))


def build_prompt(question: str, passages: list[str]) -> str:
    return RAG_PROMPT.format(context=build_context(passages), question=question)
