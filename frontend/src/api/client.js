import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request Interceptor: Attach JWT Bearer Token from localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('lifeline_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Graceful 401 handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if expired or invalid
      console.warn('Session expired or unauthorized. Clearing stored credentials.');
      localStorage.removeItem('lifeline_token');
      localStorage.removeItem('lifeline_user');
    }
    return Promise.reject(error);
  }
);

export default api;
