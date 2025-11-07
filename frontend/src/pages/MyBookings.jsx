import React, { useEffect, useState } from 'react';
import { getUserBookings } from '../api/api';

function MyBookings() {
  const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
  const [userId, setUserId] = useState(storedUser?.id || '');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    if (!userId) return;
    try {
      setLoading(true);
      const { data } = await getUserBookings(Number(userId));
      setItems(data.items || []);
    } catch (err) {
      setError('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="container">
      <h2>My Bookings</h2>
      <div className="controls">
        <input type="number" value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="Enter your user ID" />
        <button className="btn" onClick={load} disabled={!userId}>Load</button>
      </div>
      {loading && <div>Loading…</div>}
      {error && <div className="error">{error}</div>}
      <ul className="list">
        {items.map((b) => (
          <li key={b.id} className="list-item">
            <span>Booking #{b.id}</span>
            <span>Book ID: {b.book_id}</span>
            <span>Status: {b.status}</span>
            <span>Date: {new Date(b.booking_date).toLocaleString()}</span>
          </li>
        ))}
        {!items.length && !loading && <li className="muted">No bookings</li>}
      </ul>
    </section>
  );
}

export default MyBookings;

