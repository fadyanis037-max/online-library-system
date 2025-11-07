# Project: AI-Powered Online Library Booking System

You are to implement a full-stack application according to the following specification:

## 📦 Folder Structure

📁 online-library-system/
│
├── 📁 backend/
│ ├── app.py # Flask main entry point
│ ├── config.py # Configuration (SQLite / PostgreSQL)
│ ├── models.py # SQLAlchemy models (User, Book, Booking)
│ ├── routes/
│ │ ├── init.py
│ │ ├── books.py # /api/books endpoints
│ │ ├── users.py # /api/users endpoints
│ │ └── bookings.py # /api/bookings endpoints
│ ├── ai_engine/
│ │ ├── recommender.py # Uses sentence-transformers
│ │ └── summarizer.py # Uses BART summarization
│ ├── data/
│ │ └── seed_books.csv # Book dataset (title, author, genre, summary)
│ ├── requirements.txt
│ └── README_BACKEND.md
│
├── 📁 frontend/
│ ├── package.json
│ ├── public/
│ │ └── index.html
│ └── src/
│ ├── App.jsx
│ ├── index.jsx
│ ├── api/api.js
│ ├── components/
│ │ ├── Navbar.jsx
│ │ ├── BookCard.jsx
│ │ ├── BookingForm.jsx
│ │ └── AIPromptBox.jsx
│ ├── pages/
│ │ ├── Home.jsx
│ │ ├── BookList.jsx
│ │ ├── BookDetails.jsx
│ │ ├── MyBookings.jsx
│ │ └── Login.jsx
│ └── styles/app.css
│
├── 📁 migrations/
│
├── .gitignore
├── requirements.txt
├── README.md

markdown
Copy code

---

## 🎯 Project Goal

Build an **AI-enhanced online library booking system** using:

- **Frontend:** React (user interface)
- **Backend:** Flask (REST API)
- **Database:** SQLite (development) → PostgreSQL (production)
- **AI Layer:**  
  - `facebook/bart-large-cnn` for summarization  
  - `all-MiniLM-L6-v2` (Sentence-Transformers) for book recommendations

---

## 🧩 Requirements for Backend (Flask)

1. Set up Flask with:
   - `Flask`, `Flask-CORS`, `Flask-SQLAlchemy`, `Flask-Migrate`
2. Connect SQLite by default (in `config.py`), with option to switch to PostgreSQL.
3. Define models:
   - **User:** id, name, email, password  
   - **Book:** id, title, author, genre, summary, ai_summary, available_copies, total_copies  
   - **Booking:** id, user_id, book_id, booking_date, status  
4. Create `/api/books`, `/api/users`, `/api/bookings` routes.
5. Add AI endpoints:
   - `/api/books/summarize` → summarizes book text using BART.
   - `/api/books/recommend` → suggests books using Sentence-Transformers.
6. Load initial data from `data/seed_books.csv` into the database.

---

## 🧠 Requirements for AI Engine

- `summarizer.py`:  
  ```python
  from transformers import pipeline
  summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
  def summarize_text(text):
      result = summarizer(text, max_length=120, min_length=30, do_sample=False)
      return result[0]['summary_text']
recommender.py:

python
Copy code
from sentence_transformers import SentenceTransformer, util
import torch
from models import Book

model = SentenceTransformer('all-MiniLM-L6-v2')
def recommend_books(query):
    books = Book.query.all()
    summaries = [b.summary for b in books if b.summary]
    corpus_embeddings = model.encode(summaries, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    best_match = torch.argmax(scores).item()
    return {"recommended_book": books[best_match].title}
⚛️ Requirements for Frontend (React)
Use create-react-app or vite for setup.

Add axios for API calls.

Implement pages:

Home.jsx – welcome page

BookList.jsx – show all books

BookDetails.jsx – show AI summary

MyBookings.jsx – show user bookings

Login.jsx – basic auth UI (optional)

Add components:

Navbar.jsx

BookCard.jsx

AIPromptBox.jsx (takes user input for recommendations)

Create src/api/api.js:

js
Copy code
import axios from "axios";
const API = axios.create({ baseURL: "http://127.0.0.1:5000/api" });
export const getBooks = () => API.get("/books/");
export const summarize = (text) => API.post("/books/summarize", { text });
export const recommend = (query) => API.post("/books/recommend", { query });
✅ Expected Features
Users can view, search, and book books.

The system generates AI summaries using BART.

Users can get AI recommendations using Sentence-Transformers.

Database stores users, books, and bookings.

Code is modular, easy to modify, and deployable.

⚙️ Tech Stack Summary
Layer	Tech	Description
Frontend	React	User interface
Backend	Flask	REST API
Database	SQLite / PostgreSQL	Data storage
AI Engine	Transformers + Sentence-Transformers	Summaries & recommendations
Deployment (optional)	Render / Netlify	Free hosting options

Now, generate the files, code, and boilerplate for this project following this structure.
Focus on clear, modular code with docstrings and comments.