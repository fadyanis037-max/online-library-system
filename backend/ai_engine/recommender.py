from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_embedding_model()
    return np.array(model.encode(texts, normalize_embeddings=True))


def cosine_similarities(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    return np.dot(matrix, query_vec)


def top_k_similar(query_text: str, corpus_texts: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
    if not corpus_texts:
        return []
    model = get_embedding_model()
    query_vec = model.encode([query_text], normalize_embeddings=True)[0]
    corpus_vecs = embed_texts(corpus_texts)
    scores = cosine_similarities(query_vec, corpus_vecs)
    top_idx = np.argsort(-scores)[:top_k]
    return [(int(i), float(scores[i])) for i in top_idx]


