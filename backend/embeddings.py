"""
Wraps a Hugging Face sentence-transformers model for generating embeddings.

The model is loaded lazily (only when first needed) and cached after
that, since loading it is the slow part (a second or two) — we don't
want to repeat that on every single request.
"""
from functools import lru_cache
from typing import List
import numpy as np

from . import config


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(config.EMBEDDING_MODEL)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts. Returns one vector per input text."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vectors).tolist()


def embed_query(query: str) -> List[float]:
    return embed_texts([query])[0]
