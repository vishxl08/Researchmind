import { create } from 'zustand';
import client from '../api/client';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null,

  login: async (username, password) => {
    set({ loading: true, error: null });
    try {
      const res = await client.post('/api/auth/login/', { username, password });
      localStorage.setItem('access_token', res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      
      const profileRes = await client.get('/api/auth/profile/');
      set({ user: profileRes.data, isAuthenticated: true, loading: false });
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Invalid username or password', loading: false });
      return false;
    }
  },

  register: async (userData) => {
    set({ loading: true, error: null });
    try {
      const res = await client.post('/api/auth/register/', userData);
      localStorage.setItem('access_token', res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      set({ user: res.data.user, isAuthenticated: true, loading: false });
      return true;
    } catch (err) {
      set({ error: err.response?.data || 'Registration failed', loading: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  fetchProfile: async () => {
    if (!localStorage.getItem('access_token')) return;
    set({ loading: true });
    try {
      const res = await client.get('/api/auth/profile/');
      set({ user: res.data, isAuthenticated: true, loading: false });
    } catch (err) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, loading: false });
    }
  }
}));

export default useAuthStore;
