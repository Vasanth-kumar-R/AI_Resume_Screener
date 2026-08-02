"""
backend/vector_store.py
FAISS-based vector store for cosine similarity between JD and resumes.
Since embeddings are L2-normalised, inner product == cosine similarity.
"""
from __future__ import annotations

import numpy as np


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two normalised vectors.
    Because sentence-transformers returns unit-norm vectors,
    dot product is equivalent to cosine similarity.

    Returns a float in [0, 1].
    """
    vec_a = vec_a.astype(np.float32).flatten()
    vec_b = vec_b.astype(np.float32).flatten()
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def build_faiss_index(embeddings: np.ndarray):
    """
    Build a FAISS IndexFlatIP (inner product) index from a batch of embeddings.

    Args:
        embeddings: 2-D numpy array of shape (N, D).

    Returns:
        faiss.IndexFlatIP index ready for search.
    """
    import faiss

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))
    return index


def search_index(index, query_embedding: np.ndarray, top_k: int = 20):
    """
    Search the FAISS index for the top-k nearest neighbours.

    Args:
        index: FAISS index.
        query_embedding: 1-D array of shape (D,).
        top_k: Number of results to return.

    Returns:
        (distances, indices) — distances are cosine similarities in [0,1].
    """
    query = query_embedding.astype(np.float32).reshape(1, -1)
    distances, indices = index.search(query, top_k)
    return distances[0], indices[0]
