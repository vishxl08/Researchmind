import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Zap } from 'lucide-react';
import Navbar from '../components/Navbar';
import useResearchStore from '../store/researchStore';
import toast from 'react-hot-toast';

const NewResearch = () => {
  const navigate = useNavigate();
  const createJob = useResearchStore((state) => state.createJob);
  const [formData, setFormData] = useState({
    query: '',
    depth: 'deep',
    max_iterations: 10
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'max_iterations' ? parseInt(value) : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.query.trim()) {
      toast.error('Please enter a research query');
      return;
    }

    setLoading(true);
    const job = await createJob(formData.query, formData.depth, formData.max_iterations);
    setLoading(false);

    if (job) {
      toast.success('Research job created!');
      navigate(`/research/${job.id}`);
    } else {
      toast.error('Failed to create research job');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />
      <div className="max-w-2xl mx-auto p-6 mt-8">
        <h1 className="text-4xl font-bold mb-2">Start New Research</h1>
        <p className="text-slate-400 mb-8">Configure your research parameters</p>

        <form onSubmit={handleSubmit} className="space-y-6 bg-slate-800 p-8 rounded-lg border border-slate-700">
          {/* Query Input */}
          <div>
            <label className="block text-lg font-semibold mb-3">Research Query</label>
            <textarea
              name="query"
              value={formData.query}
              onChange={handleChange}
              placeholder="What would you like to research? Ask a detailed question..."
              className="w-full p-4 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 h-32"
              required
            />
          </div>

          {/* Research Depth */}
          <div>
            <label className="block text-lg font-semibold mb-3">Research Depth</label>
            <select
              name="depth"
              value={formData.depth}
              onChange={handleChange}
              className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="quick">Quick (Surface level)</option>
              <option value="deep">Deep (Comprehensive)</option>
              <option value="expert">Expert (In-depth analysis)</option>
            </select>
            <p className="text-slate-400 text-sm mt-2">
              {formData.depth === 'quick' && 'Fast research with limited sources'}
              {formData.depth === 'deep' && 'Balanced research with multiple perspectives'}
              {formData.depth === 'expert' && 'Thorough research with deep analysis and comparisons'}
            </p>
          </div>

          {/* Max Iterations */}
          <div>
            <label className="block text-lg font-semibold mb-3">Max Iterations</label>
            <input
              type="number"
              name="max_iterations"
              value={formData.max_iterations}
              onChange={handleChange}
              min="1"
              max="50"
              className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
            <p className="text-slate-400 text-sm mt-2">Maximum steps the agent will take (higher = more thorough)</p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-6 py-3 rounded-lg font-semibold transition"
          >
            <Zap className="w-5 h-5" />
            {loading ? 'Starting Research...' : 'Start Research'}
          </button>
        </form>

        {/* Tips */}
        <div className="mt-8 bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            Tips for Better Research
          </h3>
          <ul className="space-y-2 text-slate-300 text-sm">
            <li>• Be specific with your research query</li>
            <li>• Include context about what you're looking for</li>
            <li>• Choose appropriate research depth based on your needs</li>
            <li>• Higher iterations take more time but are more thorough</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default NewResearch;
