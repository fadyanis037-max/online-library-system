import React, { useState } from 'react';
import { createBooking } from '../api/api';

function BookingForm({ bookId, onBooked }) {
  const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
  const [userId, setUserId] = useState(storedUser?.id || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!userId) {
      setError('Please provide a user id or login.');
      return;
    }
    try {
      setLoading(true);
      const { data } = await createBooking({ user_id: Number(userId), book_id: Number(bookId) });
      setSuccess('Booked successfully.');
      onBooked?.(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Booking failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <h4>Book this title</h4>
      <label>
        User ID
        <input
          type="number"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter your user ID"
        />
      </label>
      <button className="btn" type="submit" disabled={loading}>
        {loading ? 'Booking...' : 'Confirm Booking'}
      </button>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
    </form>
  );
}

export default BookingForm;

