import React from 'react';
import { Link } from 'react-router-dom';

function BookCard({ book }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3>{book.title}</h3>
        <p className="muted">by {book.author}</p>
      </div>
      <div className="card-body">
        <p><strong>Genre:</strong> {book.genre || '—'}</p>
        <p className="summary">{book.summary || 'No summary available.'}</p>
      </div>
      <div className="card-footer">
        <span>Available: {book.available_copies}/{book.total_copies}</span>
        <Link className="btn" to={`/books/${book.id}`}>Details</Link>
      </div>
    </div>
  );
}

export default BookCard;

