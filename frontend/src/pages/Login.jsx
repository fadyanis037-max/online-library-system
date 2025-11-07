import React, { useState } from 'react';
import { createUser } from '../api/api';

function Login() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      setLoading(true);
      const { data } = await createUser({ name, email, password });
      localStorage.setItem('user', JSON.stringify(data));
      setSuccess('Account created and logged in.');
      setName(''); setEmail(''); setPassword('');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setSuccess('Logged out.');
  };

  const user = JSON.parse(localStorage.getItem('user') || 'null');

  return (
    <section className="container">
      <h2>Login (Demo)</h2>
      {user ? (
        <div className="panel">
          <p>You are logged in as <strong>{user.name}</strong> (ID {user.id}).</p>
          <button className="btn" onClick={handleLogout}>Log out</button>
        </div>
      ) : (
        <form className="panel" onSubmit={handleSubmit}>
          <label>Name<input value={name} onChange={(e) => setName(e.target.value)} required /></label>
          <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
          <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
          <button className="btn" type="submit" disabled={loading}>{loading ? 'Creating…' : 'Create Account'}</button>
          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}
        </form>
      )}
    </section>
  );
}

export default Login;

