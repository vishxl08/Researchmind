import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Brain, LogOut, Menu, X, Home, Zap, BookOpen, Clock, Settings } from 'lucide-react';
import useAuthStore from '../store/authStore';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'New Research', path: '/research/new', icon: Zap },
    { label: 'Memory', path: '/memory', icon: BookOpen },
    { label: 'Scheduler', path: '/scheduler', icon: Clock },
    { label: 'History', path: '/history', icon: Settings }
  ];

  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div onClick={() => navigate('/dashboard')} className="flex items-center gap-2 cursor-pointer">
            <Brain className="w-6 h-6 text-blue-400" />
            <span className="font-bold text-lg">ResearchMind</span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-6">
            {navItems.map(({ label, path, icon: Icon }) => (
              <button
                key={path}
                onClick={() => navigate(path)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
                  isActive(path)
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{label}</span>
              </button>
            ))}
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-300">{user?.username}</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-red-400 hover:text-red-300 transition"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden md:inline text-sm">Logout</span>
            </button>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden text-slate-300"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 space-y-2">
            {navItems.map(({ label, path, icon: Icon }) => (
              <button
                key={path}
                onClick={() => {
                  navigate(path);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition text-left ${
                  isActive(path)
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm">{label}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
