# AI-Powered Online Library System

An end-to-end Python project featuring a Flask backend with SQLite, AI features (BART summarization and Sentence-Transformer recommendations), and a Streamlit frontend.

## Features
- Flask REST API with CRUD for books
- SQLite via SQLAlchemy; auto-creates `library.db`
- AI Summarization using BART (`facebook/bart-large-cnn`)
- AI Recommendations using Sentence Transformers (`all-MiniLM-L6-v2`)
- Streamlit UI to browse, create, edit, summarize, and get recommendations

## Project Structure

```
online-library-system/
├── backend/
│   ├── app.py                 # Flask entry
│   ├── config.py              # SQLite config
│   ├── models.py              # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── books.py           # /api/books endpoints + AI
│   ├── ai_engine/
│   │   ├── summarizer.py      # BART
│   │   └── recommender.py     # Sentence Transformer
│   ├── data/
│   │   └── seed_books.csv
│   ├── seed_data.py           # Populate DB
│   └── requirements.txt       # Dependencies
├── app_ui.py                  # Streamlit app
├── README.md
└── library.db                 # Auto-created
```

## Setup

### 1) Create and activate a virtual environment (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
python -m pip install -U pip setuptools wheel
pip install -r backend/requirements.txt
```

If PyTorch fails to install automatically (CPU-only fallback):

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Note: First run will download large models for Transformers and Sentence-Transformers.

### 3) Run the backend (as a module)

```powershell
python -m backend.app
```

- API base: `http://localhost:5000`
- Health check: `GET /health`

Seed the database (optional, recommended; run in a new shell if backend is running):

```powershell
python -m backend.seed_data
```

### 4) Run the Streamlit UI

```powershell
streamlit run app_ui.py
```

- If backend is not on `http://localhost:5000`, set `BACKEND_URL`:

```powershell
$env:BACKEND_URL = "http://localhost:5000"
streamlit run app_ui.py
```

### Freeing occupied ports (optional)
- Check and kill processes on ports 5000/8501 if needed:

```powershell
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

## API Overview

- `GET /api/books/` — list books, optional `?q=search`
- `GET /api/books/<id>` — get a book
- `POST /api/books/` — create a book `{title, author, genre?, description?, content?}`
- `PUT /api/books/<id>` — update fields
- `DELETE /api/books/<id>` — delete
- `POST /api/books/<id>/summarize` — body `{max_length?, min_length?}` -> `{summary}`
- `GET /api/books/<id>/recommendations?top_k=5` -> similar books

## Notes
- For recommendations, book text comes from `description` + `content`.
- Summarization prefers `content`, falls back to `description`.
- On first run, model weights are downloaded; this may take a few minutes.

## License
MIT


