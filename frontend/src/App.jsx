import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import useAuthStore from './store/authStore';

// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import NewResearch from './pages/NewResearch';
import LiveResearch from './pages/LiveResearch';
import ReportView from './pages/ReportView';
import MemoryBrowser from './pages/MemoryBrowser';
import Scheduler from './pages/Scheduler';
import History from './pages/History';

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const App = () => {
  const fetchProfile = useAuthStore((state) => state.fetchProfile);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return (
    <Router>
      <Toaster position="top-right" toastOptions={{
        style: {
          background: '#1e293b',
          color: '#f8fafc',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }
      }} />
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/research/new" element={<ProtectedRoute><NewResearch /></ProtectedRoute>} />
        <Route path="/research/:jobId" element={<ProtectedRoute><LiveResearch /></ProtectedRoute>} />
        <Route path="/reports/:reportId" element={<ProtectedRoute><ReportView /></ProtectedRoute>} />
        <Route path="/memory" element={<ProtectedRoute><MemoryBrowser /></ProtectedRoute>} />
        <Route path="/scheduler" element={<ProtectedRoute><Scheduler /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
