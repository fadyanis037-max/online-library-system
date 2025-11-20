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

### 4) Run the Streamlit UI in another terminal(with activatied venv)

```powershell
-activate the env again if not activated 
.\.venv\Scripts\Activate.ps1

streamlit run app_ui.py
```

- If backend is not on `http://localhost:5000`, set `BACKEND_URL`:

```powershell
$env:BACKEND_URL = "http://localhost:5000"
streamlit run app_ui.py
```

### Freeing occupied ports (optional)
- Check and kill processes on ports 5000/8501 if needed:

## Open New shell
```powershell 
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
## Credentials (Quick Start)
- Admin
  - Username: `admin`
  - Password: value of `ADMIN_PASSWORD` (default: `1234`)
- User
  - Username: `user`
  - Password: value of `USER_PASSWORD` (default: `1234`)

## API Overview(optional, try the UI is better)

- `GET /api/books/` — list books, optional `?q=search`
- `GET /api/books/<id>` — get a book
- `POST /api/books/` — create a book `{title, author, genre?, description?, content?}`
- `PUT /api/books/<id>` — update fields
- `DELETE /api/books/<id>` — delete
- `POST /api/books/<id>/summarize` — body `{max_length?, min_length?}` -> `{summary}`
- `GET /api/books/<id>/recommendations?top_k=5` -> similar books
- `POST /api/books/search-by-description` — body `{description, top_k?}` -> AI-powered search results

## Features

### AI-Powered Search
- Users can describe what they're looking for in natural language(scroll up after press Find relevant books)
- The system uses Sentence Transformers to find the most relevant books based on semantic similarity
- Results are ranked by relevance score

### Summarization
- summarizing feature may take 3 mins to see the result of the book as it's a large model
- When a user selects a book, the system automatically generates a summary using BART
- Summaries are cached to avoid regeneration on subsequent views
- Provides a quick overview of the book's content

## Notes
- For recommendations, book text comes from `description` + `content`.
- On first run, model weights are downloaded during backend startup, so expect a longer boot time rather than a slow first request.
- Models download on first use. The summarizer preloads in the background after startup; the recommender is initialized at startup for snappy recommendations.

## License
MIT
