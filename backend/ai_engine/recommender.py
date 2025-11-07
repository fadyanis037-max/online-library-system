"""Book recommendation using Sentence-Transformers similarity.

Embeds available book summaries and returns the best match for a query.
"""

from typing import Dict

from sentence_transformers import SentenceTransformer, util

from models import Book

_model = None  # lazy singleton


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def recommend_books(query: str) -> Dict:
    if not query or not query.strip():
        raise ValueError("Empty query provided for recommendation")

    books = Book.query.all()
    candidates = [(b, b.summary) for b in books if b.summary]
    if not candidates:
        return {"recommended_book": None, "reason": "No summaries available"}

    # Embed corpus and query
    model = _get_model()
    summaries = [summary for _, summary in candidates]
    corpus_embeddings = model.encode(summaries, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    best_idx = int(scores.argmax().item())
    best_book = candidates[best_idx][0]
    return {"recommended_book": best_book.title, "book_id": best_book.id}

