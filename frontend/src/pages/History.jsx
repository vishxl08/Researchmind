import React, { useEffect, useState } from 'react';
import { History, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import useResearchStore from '../store/researchStore';

const HistoryPage = () => {
  const navigate = useNavigate();
  const { jobs, fetchJobs } = useResearchStore();
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchJobs();
  }, []);

  const filteredJobs = filter === 'all' ? jobs : jobs.filter((j) => j.status === filter);

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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'done':
        return '✓';
      case 'running':
        return '⟳';
      case 'failed':
        return '✗';
      default:
        return '○';
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />
      <div className="max-w-5xl mx-auto p-6">
        <div className="flex items-center gap-3 mb-6">
          <History className="w-8 h-8" />
          <h1 className="text-4xl font-bold">Research History</h1>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6 pb-4 border-b border-slate-700">
          {['all', 'done', 'running', 'pending', 'failed'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg transition ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Jobs List */}
        <div className="space-y-3">
          {filteredJobs.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <p>No research jobs in this category</p>
            </div>
          ) : (
            filteredJobs.map((job) => (
              <div
                key={job.id}
                onClick={() => navigate(`/research/${job.id}`)}
                className="flex items-center justify-between p-4 bg-slate-800 hover:bg-slate-700 rounded-lg cursor-pointer transition border border-slate-700"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${getStatusColor(job.status)}`}
                  >
                    {getStatusIcon(job.status)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{job.query.substring(0, 60)}</h3>
                    <p className="text-sm text-slate-400">
                      Created {new Date(job.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right text-sm">
                    <p className="text-slate-400">Depth: {job.depth}</p>
                    <p className="text-slate-500">Iterations: {job.max_iterations}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-slate-500" />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;
