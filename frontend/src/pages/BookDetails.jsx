import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getBook, summarize } from '../api/api';
import BookingForm from '../components/BookingForm';

function BookDetails() {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [aiSummary, setAiSummary] = useState('');
  const [summarizing, setSummarizing] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      const { data } = await getBook(id);
      setBook(data);
      setAiSummary(data.ai_summary || '');
    } catch (err) {
      setError('Failed to load book');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!book?.summary) return;
    try {
      setSummarizing(true);
      const { data } = await summarize({ book_id: Number(id) });
      setAiSummary(data.summary);
    } catch (err) {
      setError(err.response?.data?.error || 'Summarization failed');
    } finally {
      setSummarizing(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (loading) return <section className="container">Loading…</section>;
  if (error) return <section className="container error">{error}</section>;
  if (!book) return null;

  return (
    <section className="container">
      <h2>{book.title}</h2>
      <p className="muted">by {book.author}</p>
      <p><strong>Genre:</strong> {book.genre || '—'}</p>
      <p><strong>Available:</strong> {book.available_copies}/{book.total_copies}</p>
      <div className="panel">
        <h4>Original Summary</h4>
        <p>{book.summary || 'No summary available.'}</p>
      </div>
      <div className="panel">
        <div className="row-between">
          <h4>AI Summary</h4>
          <button className="btn" onClick={handleSummarize} disabled={!book.summary || summarizing}>
            {summarizing ? 'Summarizing…' : 'Generate AI Summary'}
          </button>
        </div>
        <p>{aiSummary || 'No AI summary yet.'}</p>
      </div>
      <BookingForm bookId={id} onBooked={() => load()} />
    </section>
  );
}

export default BookDetails;

