"""
backend/embedder.py
Sentence-Transformers embedding using all-MiniLM-L6-v2.
Model is loaded once and cached at module level.
"""
from __future__ import annotations

import numpy as np

_MODEL = None
MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Lazy-load and cache the sentence-transformer model."""
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL


def embed_text(text: str) -> np.ndarray:
    """
    Embed a single text string into a normalised float32 vector.

    Args:
        text: Input text to embed.

    Returns:
        1-D numpy array of shape (384,).
    """
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
    return np.array(embedding, dtype=np.float32)


def embed_batch(texts: list[str]) -> np.ndarray:
    """
    Embed multiple texts at once (more efficient than calling embed_text in a loop).

    Args:
        texts: List of strings.

    Returns:
        2-D numpy array of shape (N, 384).
    """
    model = _get_model()
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=32,
    )
    return np.array(embeddings, dtype=np.float32)
