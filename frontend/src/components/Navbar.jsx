import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  const active = (path) => (location.pathname === path ? 'active' : '');

  return (
    <header className="navbar">
      <div className="navbar-brand">AI Online Library</div>
      <nav className="navbar-nav">
        <Link className={`nav-link ${active('/')}`} to="/">Home</Link>
        <Link className={`nav-link ${active('/books')}`} to="/books">Books</Link>
        <Link className={`nav-link ${active('/bookings')}`} to="/bookings">My Bookings</Link>
        <Link className={`nav-link ${active('/login')}`} to="/login">Login</Link>
      </nav>
    </header>
  );
}

export default Navbar;

