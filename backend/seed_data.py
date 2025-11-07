import csv
import os

from backend.app import create_app
from backend.models import db, Book


def seed_books_from_csv(csv_path: str):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    for row in rows:
        # Skip if book with same title + author exists
        exists = Book.query.filter_by(title=row['title'], author=row['author']).first()
        if exists:
            continue
        book = Book(
            title=row.get('title') or 'Untitled',
            author=row.get('author') or 'Unknown',
            genre=row.get('genre') or None,
            description=row.get('description') or None,
            content=row.get('content') or None,
        )
        db.session.add(book)
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'seed_books.csv')
        seed_books_from_csv(data_path)
        print('Seeded database from', data_path)


