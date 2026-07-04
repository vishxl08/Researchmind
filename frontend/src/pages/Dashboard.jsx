import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, TrendingUp, BookOpen, Clock, BarChart3 } from 'lucide-react';
import Navbar from '../components/Navbar';
import useResearchStore from '../store/researchStore';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const navigate = useNavigate();
  const { jobs, fetchJobs, getStats } = useResearchStore();
  const [stats, setStats] = useState({
    total_jobs: 0,
    completed_jobs: 0,
    total_memories: 0,
    avg_confidence: 0
  });

  useEffect(() => {
    fetchJobs();
    loadStats();
  }, []);

  const loadStats = async () => {
    const data = await getStats();
    if (data) setStats(data);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'done':
        return 'bg-green-900 text-green-200';
      case 'running':
        return 'bg-blue-900 text-blue-200';
      case 'failed':
        return 'bg-red-900 text-red-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />
      <div className="max-w-7xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">Dashboard</h1>
          <button
            onClick={() => navigate('/research/new')}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition"
          >
            <Plus className="w-5 h-5" />
            New Research
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 mb-1">Total Jobs</p>
                <p className="text-3xl font-bold">{stats.total_jobs}</p>
              </div>
              <BarChart3 className="w-10 h-10 text-blue-500" />
            </div>
          </div>
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 mb-1">Completed</p>
                <p className="text-3xl font-bold">{stats.completed_jobs}</p>
              </div>
              <TrendingUp className="w-10 h-10 text-green-500" />
            </div>
          </div>
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 mb-1">Memories</p>
                <p className="text-3xl font-bold">{stats.total_memories}</p>
              </div>
              <BookOpen className="w-10 h-10 text-purple-500" />
            </div>
          </div>
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 mb-1">Avg Confidence</p>
                <p className="text-3xl font-bold">{(stats.avg_confidence * 100).toFixed(0)}%</p>
              </div>
              <Clock className="w-10 h-10 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Recent Jobs */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Recent Research Jobs</h2>
          <div className="space-y-3">
            {jobs.length === 0 ? (
              <p className="text-slate-400 text-center py-8">No research jobs yet</p>
            ) : (
              jobs.slice(0, 10).map((job) => (
                <div
                  key={job.id}
                  onClick={() => navigate(`/research/${job.id}`)}
                  className="flex items-center justify-between p-4 bg-slate-700 hover:bg-slate-600 rounded-lg cursor-pointer transition"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{job.query.substring(0, 50)}</h3>
                    <p className="text-slate-400 text-sm">
                      Created {new Date(job.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`px-4 py-1 rounded-full text-sm font-semibold ${getStatusColor(job.status)}`}>
                    {job.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
