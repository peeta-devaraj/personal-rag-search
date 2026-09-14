"""Extracts raw text per page from an uploaded file.

Returns a list of (page_number, text) tuples so downstream chunking can
attribute each chunk to the page(s) it came from (needed for citations).
Plain text/markdown files have no page concept, so the whole file is page 1.
"""

from pathlib import Path

import fitz  # PyMuPDF


class UnsupportedFileType(ValueError):
    pass


def load_pages(path: Path) -> list[tuple[int, str]]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(path)
    if suffix in (".txt", ".md"):
        return _load_text(path)
    raise UnsupportedFileType(f"Unsupported file type: {suffix}")


def _load_pdf(path: Path) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append((i, text))
    return pages


def _load_text(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return [(1, text)] if text else []
