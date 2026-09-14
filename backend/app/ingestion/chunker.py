"""Sentence-aware chunking with overlap.

Naive fixed-size character windows cut mid-sentence, which hurts both BM25
term coherence and embedding quality. Instead we split into sentences, then
greedily pack sentences into chunks targeting a token budget, carrying the
last sentence(s) of one chunk forward into the next as overlap so context
isn't lost at chunk boundaries.
"""

from dataclasses import dataclass

import nltk
import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")


def _ensure_punkt() -> None:
    for resource in ("tokenizers/punkt", "tokenizers/punkt_tab"):
        try:
            nltk.data.find(resource)
        except LookupError:
            name = resource.split("/")[-1]
            nltk.download(name, quiet=True)


def count_tokens(text: str) -> int:
    return len(_ENCODING.encode(text))


@dataclass
class ChunkDraft:
    chunk_index: int
    text: str
    page_start: int
    page_end: int
    token_count: int


def chunk_pages(
    pages: list[tuple[int, str]],
    target_tokens: int = 300,
    overlap_tokens: int = 50,
) -> list[ChunkDraft]:
    _ensure_punkt()

    sentences: list[tuple[str, int]] = []
    for page_num, text in pages:
        for sent in nltk.sent_tokenize(text):
            sent = sent.strip()
            if sent:
                sentences.append((sent, page_num))

    if not sentences:
        return []

    chunks: list[ChunkDraft] = []
    current: list[tuple[str, int]] = []
    current_tokens = 0
    idx = 0

    def flush() -> None:
        nonlocal current, current_tokens, idx
        if not current:
            return
        text = " ".join(s for s, _ in current)
        pages_in_chunk = [p for _, p in current]
        chunks.append(
            ChunkDraft(
                chunk_index=idx,
                text=text,
                page_start=min(pages_in_chunk),
                page_end=max(pages_in_chunk),
                token_count=current_tokens,
            )
        )
        idx += 1

    for sent, page_num in sentences:
        sent_tokens = count_tokens(sent)

        if current and current_tokens + sent_tokens > target_tokens:
            flush()
            # carry overlap: keep trailing sentences whose combined tokens <= overlap_tokens
            overlap: list[tuple[str, int]] = []
            overlap_count = 0
            for s, p in reversed(current):
                t = count_tokens(s)
                if overlap_count + t > overlap_tokens:
                    break
                overlap.insert(0, (s, p))
                overlap_count += t
            current = overlap
            current_tokens = overlap_count

        current.append((sent, page_num))
        current_tokens += sent_tokens

    flush()
    return chunks
