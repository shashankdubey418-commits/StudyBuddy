"""
chunker.py
Splits long text into overlapping chunks so each piece fits comfortably
in a retrieval context and preserves meaning across boundaries.
"""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """
    Split text into overlapping chunks by character count.
    chunk_size/overlap are in characters (roughly 4 chars per token).

    Args:
        text: the full extracted document text
        chunk_size: max characters per chunk
        overlap: characters shared between consecutive chunks, to avoid
                  cutting a sentence or idea in half at a chunk boundary
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_len:
            break
        start = end - overlap  # step back so chunks overlap

    return chunks
