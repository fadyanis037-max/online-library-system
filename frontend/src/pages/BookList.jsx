import React, { useEffect, useState } from 'react';
import { getBooks } from '../api/api';
import BookCard from '../components/BookCard';

function BookList() {
  const [books, setBooks] = useState([]);
  const [q, setQ] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async (query) => {
    try {
      setLoading(true);
      const { data } = await getBooks(query);
      setBooks(data.items || []);
    } catch (err) {
      setError('Failed to load books');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="container">
      <h2>Books</h2>
      <div className="controls">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by title, author, genre" />
        <button className="btn" onClick={() => load(q || undefined)}>Search</button>
      </div>
      {loading && <div>Loading…</div>}
      {error && <div className="error">{error}</div>}
      <div className="grid">
        {books.map((b) => (
          <BookCard key={b.id} book={b} />
        ))}
      </div>
    </section>
  );
}

export default BookList;

