import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock } from 'lucide-react';
import useAuthStore from '../store/authStore';
import toast from 'react-hot-toast';

const Login = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await login(formData.username, formData.password);
    setLoading(false);
    if (success) {
      toast.success('Login successful!');
      navigate('/dashboard');
    } else {
      toast.error('Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-2xl p-8">
          <h2 className="text-3xl font-bold text-white mb-6 text-center">Welcome Back</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-slate-300 mb-2">Username</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  placeholder="Enter your username"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-slate-300 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
          <p className="text-center text-slate-400 mt-4">
            Don't have an account?{' '}
            <a href="/register" className="text-blue-400 hover:text-blue-300">
              Register
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
