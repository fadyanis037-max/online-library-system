from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    """Application user."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }


class Book(db.Model):
    """Book entity with optional AI summary."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(120))
    summary = db.Column(db.Text)
    ai_summary = db.Column(db.Text)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    total_copies = db.Column(db.Integer, nullable=False, default=1)

    bookings = db.relationship("Booking", back_populates="book", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "summary": self.summary,
            "ai_summary": self.ai_summary,
            "available_copies": self.available_copies,
            "total_copies": self.total_copies,
        }


class Booking(db.Model):
    """A booking made by a user for a book."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default="active", nullable=False)

    user = db.relationship("User", back_populates="bookings")
    book = db.relationship("Book", back_populates="bookings")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "booking_date": self.booking_date.isoformat(),
            "status": self.status,
        }

