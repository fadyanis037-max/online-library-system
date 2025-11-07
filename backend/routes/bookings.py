from flask import Blueprint, jsonify, request

from models import db, Booking, Book, User


bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bp.get("/")
def list_bookings():
    items = [b.to_dict() for b in Booking.query.order_by(Booking.id.desc()).all()]
    return jsonify({"items": items, "count": len(items)})


@bp.get("/user/<int:user_id>")
def user_bookings(user_id: int):
    items = [b.to_dict() for b in Booking.query.filter_by(user_id=user_id).all()]
    return jsonify({"items": items, "count": len(items)})


@bp.post("/")
def create_booking():
    """Create a booking if copies are available."""
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    if not user_id or not book_id:
        return jsonify({"error": "Missing user_id or book_id"}), 400

    # Ensure user and book exist
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    if not user or not book:
        return jsonify({"error": "Invalid user_id or book_id"}), 404

    if book.available_copies <= 0:
        return jsonify({"error": "No copies available"}), 409

    booking = Booking(user_id=user_id, book_id=book_id, status="active")
    book.available_copies -= 1
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201

