"""Flask app entry point for the Online Library backend.

Run locally:
  cd backend
  python -m venv .venv && .venv/Scripts/activate  # or source .venv/bin/activate (Unix)
  pip install -r requirements.txt
  set FLASK_APP=app.py  # on Windows PowerShell: $env:FLASK_APP = "app.py"
  flask db init && flask db migrate -m "init" && flask db upgrade
  flask seed-books  # optional: load initial dataset
  flask run
"""

import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from config import get_config
from models import db, Book
from routes import register_blueprints


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Extensions
    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    # Routes
    register_blueprints(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # CLI command to seed initial books
    @app.cli.command("seed-books")
    def seed_books_cmd():
        """Load books from data/seed_books.csv into the database."""
        with app.app_context():
            data_path = Path(__file__).parent / "data" / "seed_books.csv"
            if not data_path.exists():
                print(f"Seed file not found: {data_path}")
                return
            added = 0
            with open(data_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row.get("title") or not row.get("author"):
                        continue
                    # Avoid duplicates by title+author
                    exists = Book.query.filter_by(title=row["title"], author=row["author"]).first()
                    if exists:
                        continue
                    book = Book(
                        title=row["title"],
                        author=row["author"],
                        genre=row.get("genre"),
                        summary=row.get("summary"),
                        total_copies=int(row.get("total_copies", 1) or 1),
                        available_copies=int(row.get("available_copies", 1) or 1),
                    )
                    db.session.add(book)
                    added += 1
                db.session.commit()
            print(f"Seeded {added} books.")

    return app


app = create_app()

