"""
Splits long text into overlapping chunks suitable for embedding.

This is a simple recursive splitter: try to break on paragraph
boundaries first, then sentences, then just hard-cut on characters as
a last resort. No external library needed — the logic is fully
transparent and easy to explain in an interview.
"""
from typing import List


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[str]:
    text = text.strip()
    if not text:
        return []

    separators = ["\n\n", "\n", ". ", " "]
    chunks = _split_recursive(text, separators, chunk_size)
    return _apply_overlap(chunks, chunk_overlap, chunk_size)


def _split_recursive(text: str, separators: List[str], chunk_size: int) -> List[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    if not separators:
        # Hard cut as a last resort
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    sep, rest_separators = separators[0], separators[1:]
    parts = text.split(sep)

    chunks: List[str] = []
    current = ""
    for part in parts:
        candidate = (current + sep + part) if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(part) > chunk_size:
                chunks.extend(_split_recursive(part, rest_separators, chunk_size))
                current = ""
            else:
                current = part
    if current:
        chunks.append(current)

    return [c.strip() for c in chunks if c.strip()]


def _apply_overlap(chunks: List[str], overlap: int, chunk_size: int) -> List[str]:
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        prev_tail = chunks[i - 1][-overlap:]
        merged = (prev_tail + " " + chunks[i]).strip()
        overlapped.append(merged[: chunk_size + overlap])
    return overlapped
