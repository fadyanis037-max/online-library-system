from flask import Blueprint, jsonify, request

from backend.models import db, Book
from backend.ai_engine.summarizer import summarize_text
from backend.ai_engine.recommender import top_k_similar


books_bp = Blueprint('books', __name__)


def serialize_book(book: Book, include_content: bool = False):
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "description": book.description,
        **({"content": book.content} if include_content else {}),
        "created_at": book.created_at.isoformat() if book.created_at else None,
    }


@books_bp.get('/')
def list_books():
    query = Book.query
    search = request.args.get('q')
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Book.title.ilike(like),
                Book.author.ilike(like),
                Book.genre.ilike(like),
                Book.description.ilike(like),
            )
        )
    books = query.order_by(Book.created_at.desc()).all()
    return jsonify([serialize_book(b) for b in books])


@books_bp.get('/<int:book_id>')
def get_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    return jsonify(serialize_book(book, include_content=True))


@books_bp.post('/')
def create_book():
    data = request.get_json(force=True)
    title = data.get('title')
    author = data.get('author')
    if not title or not author:
        return jsonify({"error": "'title' and 'author' are required"}), 400
    book = Book(
        title=title,
        author=author,
        genre=data.get('genre'),
        description=data.get('description'),
        content=data.get('content'),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(serialize_book(book, include_content=True)), 201


@books_bp.put('/<int:book_id>')
def update_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    data = request.get_json(force=True)
    for field in ['title', 'author', 'genre', 'description', 'content']:
        if field in data:
            setattr(book, field, data[field])
    db.session.commit()
    return jsonify(serialize_book(book, include_content=True))


@books_bp.delete('/<int:book_id>')
def delete_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"status": "deleted", "id": book_id})


@books_bp.post('/<int:book_id>/summarize')
def summarize_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    source = (book.content or '').strip()
    if not source:
        return jsonify({"error": "No content available to summarize"}), 400
    params = request.get_json(silent=True) or {}
    max_length = int(params.get('max_length', 130))
    min_length = int(params.get('min_length', 30))
    summary = summarize_text(source, max_length=max_length, min_length=min_length)
    if not summary:
        return jsonify({"error": "Summarization failed"}), 500

    # Persist the summary so future views load quickly
    book.description = summary
    db.session.commit()

    return jsonify({"book_id": book_id, "summary": summary})


@books_bp.get('/<int:book_id>/recommendations')
def recommend_books(book_id: int):
    book = Book.query.get_or_404(book_id)
    target_text = (book.description or '') + '\n' + (book.content or '')
    if not target_text.strip():
        return jsonify({"error": "No text available for recommendations"}), 400

    other_books = Book.query.filter(Book.id != book_id).all()
    corpus = [((b.description or '') + '\n' + (b.content or '')).strip() for b in other_books]
    top_k = int(request.args.get('top_k', 5))

    ranking = top_k_similar(target_text, corpus, top_k=top_k)

    # Map indices back to book ids
    results = []
    for idx, score in ranking:
        b = other_books[idx]
        payload = serialize_book(b)
        payload["score"] = score
        results.append(payload)

    return jsonify({"book_id": book_id, "recommendations": results})


@books_bp.post('/search-by-description')
def search_by_description():
    """Find the most relevant books based on user description using AI."""
    data = request.get_json(force=True)
    user_description = data.get('description', '').strip()
    if not user_description:
        return jsonify({"error": "'description' is required"}), 400

    top_k = int(data.get('top_k', 5))
    
    all_books = Book.query.all()
    if not all_books:
        return jsonify({"results": []})

    # Build corpus from all books
    corpus = [((b.description or '') + '\n' + (b.content or '')).strip() for b in all_books]
    
    # Find most similar books
    ranking = top_k_similar(user_description, corpus, top_k=top_k)

    # Map indices back to book ids
    results = []
    for idx, score in ranking:
        b = all_books[idx]
        payload = serialize_book(b)
        payload["score"] = score
        results.append(payload)

    return jsonify({"query": user_description, "results": results})


