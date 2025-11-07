from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from models import db, Book


bp = Blueprint("books", __name__, url_prefix="/api/books")


@bp.get("/")
def list_books():
    """Return all books. Optional search via ?q=term."""
    q = request.args.get("q")
    query = Book.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like), Book.genre.ilike(like)))
    books = [b.to_dict() for b in query.order_by(Book.title.asc()).all()]
    return jsonify({"items": books, "count": len(books)})


@bp.get("/<int:book_id>")
def get_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@bp.post("/")
def create_book():
    """Create a new book entry."""
    data = request.get_json(force=True) or {}
    required = ["title", "author"]
    if not all(k in data and data[k] for k in required):
        return jsonify({"error": "Missing required fields: title, author"}), 400

    book = Book(
        title=data["title"],
        author=data["author"],
        genre=data.get("genre"),
        summary=data.get("summary"),
        ai_summary=data.get("ai_summary"),
        available_copies=int(data.get("available_copies", 1)),
        total_copies=int(data.get("total_copies", 1)),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@bp.post("/summarize")
def summarize_endpoint():
    """Summarize provided text or a book's summary.

    Body: {"text": "..."} OR {"book_id": 1}
    """
    payload = request.get_json(force=True) or {}
    text = payload.get("text")
    book_id = payload.get("book_id")

    if not text and not book_id:
        return jsonify({"error": "Provide 'text' or 'book_id'"}), 400

    if not text and book_id:
        book = Book.query.get_or_404(book_id)
        if not book.summary:
            return jsonify({"error": "Book has no summary to summarize"}), 400
        text = book.summary

    try:
        # Lazy import to avoid hard dependency at app startup
        from ai_engine.summarizer import summarize_text  # type: ignore

        result = summarize_text(text)
    except ImportError:
        return (
            jsonify({
                "error": "Summarization unavailable: install transformers/sentence-transformers/torch.",
            }),
            501,
        )
    except Exception as exc:  # model may need download on first run
        return jsonify({"error": f"Summarization failed: {exc}"}), 500

    # Optionally persist if book_id provided
    if book_id:
        book = Book.query.get(book_id)
        if book:
            book.ai_summary = result
            db.session.commit()

    return jsonify({"summary": result})


@bp.post("/recommend")
def recommend_endpoint():
    """Recommend a book based on a user query.

    Body: {"query": "mystery detective"}
    """
    payload = request.get_json(force=True) or {}
    query = payload.get("query")
    if not query:
        return jsonify({"error": "Missing 'query'"}), 400
    try:
        # Lazy import to avoid hard dependency at app startup
        from ai_engine.recommender import recommend_books  # type: ignore

        rec = recommend_books(query)
    except ImportError:
        return (
            jsonify({
                "error": "Recommendation unavailable: install sentence-transformers/torch.",
            }),
            501,
        )
    except Exception as exc:
        return jsonify({"error": f"Recommendation failed: {exc}"}), 500
    return jsonify(rec)

