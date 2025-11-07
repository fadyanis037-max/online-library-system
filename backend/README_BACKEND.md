Backend: AI-Powered Online Library Booking System

Overview
- Flask REST API with SQLite (dev) and PostgreSQL (prod via DATABASE_URL)
- SQLAlchemy models: User, Book, Booking
- Endpoints: /api/books, /api/users, /api/bookings
- AI endpoints: /api/books/summarize (BART), /api/books/recommend (Sentence-Transformers)

Setup
1) Create and activate a virtualenv
   - Windows (PowerShell):
     - cd backend
     - python -m venv .venv
     - .venv\\Scripts\\Activate.ps1
   - macOS/Linux:
     - cd backend
     - python -m venv .venv
     - source .venv/bin/activate

2) Install dependencies
   - pip install -r requirements.txt
   - Note: transformers and sentence-transformers will download models on first use.

3) Configure environment
   - Optional: set DATABASE_URL for Postgres (e.g., postgresql+psycopg://user:pass@host:5432/db)
   - Optional: set SECRET_KEY

4) Initialize database (Flask-Migrate)
   - Set FLASK_APP
     - Windows PowerShell: $env:FLASK_APP = "app.py"
     - macOS/Linux: export FLASK_APP=app.py
   - flask db init
   - flask db migrate -m "init"
   - flask db upgrade

5) Seed data (optional)
   - flask seed-books

6) Run
   - flask run

Key Files
- app.py: Flask app factory, health endpoint, seed CLI
- config.py: Config with SQLite default and DATABASE_URL override
- models.py: SQLAlchemy models
- routes/
  - books.py: List/get/create books, summarize, recommend
  - users.py: Basic user CRUD (create/list)
  - bookings.py: Create bookings and list bookings
- ai_engine/
  - summarizer.py: BART summarization
  - recommender.py: MiniLM similarity-based recommendation
- data/seed_books.csv: Initial dataset

API Examples
- GET http://127.0.0.1:5000/api/books/
- POST http://127.0.0.1:5000/api/books/summarize
  Body: {"text": "Long description to summarize..."}
- POST http://127.0.0.1:5000/api/books/recommend
  Body: {"query": "post-apocalyptic surveillance state"}

Notes
- For production, use Postgres and a proper WSGI server (e.g., gunicorn) and enable model caching/warmup.
- Passwords are not hashed here to keep the example minimal; do not use as-is in production.

