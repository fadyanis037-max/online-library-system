import axios from 'axios';

const API = axios.create({ baseURL: 'http://127.0.0.1:5000/api' });

// Books
export const getBooks = (q) => API.get('/books/', { params: q ? { q } : {} });
export const getBook = (id) => API.get(`/books/${id}`);
export const createBook = (payload) => API.post('/books/', payload);

// AI endpoints
export const summarize = (textOrBook) => API.post('/books/summarize', textOrBook);
export const recommend = (query) => API.post('/books/recommend', { query });

// Users
export const createUser = (payload) => API.post('/users/', payload);
export const getUsers = () => API.get('/users/');

// Bookings
export const createBooking = (payload) => API.post('/bookings/', payload);
export const getUserBookings = (userId) => API.get(`/bookings/user/${userId}`);

export default API;

