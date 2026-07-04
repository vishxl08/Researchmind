import React, { useEffect, useState } from 'react';
import { Plus, Calendar, Clock, Trash2, ToggleLeft, ToggleRight } from 'lucide-react';
import Navbar from '../components/Navbar';
import useResearchStore from '../store/researchStore';
import toast from 'react-hot-toast';

const Scheduler = () => {
  const {
    scheduledResearches,
    fetchScheduledResearches,
    createScheduledResearch,
    updateScheduledResearch,
    deleteScheduledResearch
  } = useResearchStore();

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    query_template: '',
    frequency: 'weekly',
    deliver_via_email: true
  });

  useEffect(() => {
    fetchScheduledResearches();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await createScheduledResearch(formData);
    if (success) {
      setFormData({ query_template: '', frequency: 'weekly', deliver_via_email: true });
      setShowForm(false);
      toast.success('Scheduled research created!');
    }
  };

  const handleToggle = async (id, isActive) => {
    await updateScheduledResearch(id, { is_active: !isActive });
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this scheduled research?')) {
      await deleteScheduledResearch(id);
      toast.success('Deleted!');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />
      <div className="max-w-5xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-4xl font-bold">Research Scheduler</h1>
            <p className="text-slate-400">Set up automatic research jobs</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition"
          >
            <Plus className="w-5 h-5" />
            New Schedule
          </button>
        </div>

        {/* Form */}
        {showForm && (
          <form onSubmit={handleSubmit} className="mb-6 bg-slate-800 p-6 rounded-lg border border-slate-700 space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Research Query Template</label>
              <textarea
                value={formData.query_template}
                onChange={(e) => setFormData({ ...formData, query_template: e.target.value })}
                placeholder="e.g., Latest developments in {topic}"
                className="w-full p-3 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 h-20"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Frequency</label>
              <select
                value={formData.frequency}
                onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.deliver_via_email}
                onChange={(e) => setFormData({ ...formData, deliver_via_email: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-sm">Deliver via email</span>
            </label>
            <div className="flex gap-2">
              <button
                type="submit"
                className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition"
              >
                Schedule
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg transition"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* List */}
        <div className="space-y-3">
          {scheduledResearches.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <p>No scheduled research yet. Create one to get started!</p>
            </div>
          ) : (
            scheduledResearches.map((scheduled) => (
              <div key={scheduled.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-semibold text-lg">{scheduled.query_template}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm text-slate-400">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {scheduled.frequency}
                      </span>
                      {scheduled.last_run && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          Last run: {new Date(scheduled.last_run).toLocaleDateString()}
                        </span>
                      )}
                      {scheduled.deliver_via_email && (
                        <span className="px-2 py-1 bg-slate-700 rounded text-xs">Email delivery</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleToggle(scheduled.id, scheduled.is_active)}
                      className={`p-2 rounded transition ${
                        scheduled.is_active
                          ? 'bg-green-900 text-green-200'
                          : 'bg-slate-700 text-slate-300'
                      }`}
                    >
                      {scheduled.is_active ? (
                        <ToggleRight className="w-5 h-5" />
                      ) : (
                        <ToggleLeft className="w-5 h-5" />
                      )}
                    </button>
                    <button
                      onClick={() => handleDelete(scheduled.id)}
                      className="p-2 bg-red-900 text-red-200 hover:bg-red-800 rounded transition"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Scheduler;
