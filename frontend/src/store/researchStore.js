import { create } from 'zustand';
import client from '../api/client';

const useResearchStore = create((set, get) => ({
  jobs: [],
  currentJob: null,
  currentSteps: [],
  currentReport: null,
  scheduledResearches: [],
  memories: [],
  loading: false,
  error: null,

  fetchJobs: async () => {
    set({ loading: true });
    try {
      const res = await client.get('/api/research/jobs/');
      set({ jobs: res.data.results || res.data, loading: false });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  getStats: async () => {
    try {
      const res = await client.get('/api/dashboard/stats/');
      return {
        total_jobs: res.data.total_jobs,
        completed_jobs: res.data.completed_jobs,
        total_memories: res.data.total_memories,
        avg_confidence: res.data.avg_confidence_score
      };
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  fetchJobDetails: async (id) => {
    set({ loading: true });
    try {
      const res = await client.get(`/api/research/jobs/${id}/`);
      set({ currentJob: res.data, currentReport: res.data.report || null, loading: false });

      const stepsRes = await client.get(`/api/research/steps/${id}/`);
      set({ currentSteps: stepsRes.data.results || stepsRes.data });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  createJob: async (query, depth, maxIterations) => {
    set({ loading: true });
    try {
      const res = await client.post('/api/research/jobs/', {
        query,
        depth,
        max_iterations: maxIterations
      });
      set({ loading: false });
      return res.data;
    } catch (err) {
      set({ error: err.response?.data || err.message, loading: false });
      throw err;
    }
  },

  addStep: (step) => {
    set((state) => {
      // Avoid duplicate steps by step_number
      const exists = state.currentSteps.some(s => s.step_number === step.step_number && s.step_type === step.step_type);
      if (exists) return state;
      return {
        currentSteps: [...state.currentSteps, step]
      };
    });
  },

  setReport: (report) => {
    set({ currentReport: report });
  },

  clearCurrentJob: () => {
    set({ currentJob: null, currentSteps: [], currentReport: null });
  },

  fetchReport: async (reportId) => {
    try {
      const res = await client.get(`/api/research/reports/${reportId}/`);
      return res.data;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  exportReport: async (reportId, format) => {
    try {
      const res = await client.get(`/api/research/reports/${reportId}/export/${format}/`, {
        responseType: 'blob'
      });
      return res.data;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  fetchScheduledResearches: async () => {
    try {
      const res = await client.get('/api/scheduler/jobs/');
      set({ scheduledResearches: res.data.results || res.data });
    } catch (err) {
      set({ error: err.message });
    }
  },

  createScheduledResearch: async (data) => {
    try {
      const res = await client.post('/api/scheduler/jobs/', data);
      set((state) => ({ scheduledResearches: [res.data, ...state.scheduledResearches] }));
      return true;
    } catch (err) {
      set({ error: err.response?.data || err.message });
      return false;
    }
  },

  updateScheduledResearch: async (id, data) => {
    try {
      const res = await client.patch(`/api/scheduler/jobs/${id}/`, data);
      set((state) => ({
        scheduledResearches: state.scheduledResearches.map((s) => (s.id === id ? res.data : s))
      }));
      return true;
    } catch (err) {
      set({ error: err.response?.data || err.message });
      return false;
    }
  },

  deleteScheduledResearch: async (id) => {
    try {
      await client.delete(`/api/scheduler/jobs/${id}/`);
      set((state) => ({
        scheduledResearches: state.scheduledResearches.filter((s) => s.id !== id)
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  fetchMemories: async () => {
    try {
      const res = await client.get('/api/memory/entries/');
      set({ memories: res.data.results || res.data });
    } catch (err) {
      set({ error: err.message });
    }
  },

  searchMemories: async (query) => {
    try {
      const res = await client.get('/api/memory/entries/', { params: { query } });
      set({ memories: res.data.results || res.data });
    } catch (err) {
      set({ error: err.message });
    }
  }
}));

export default useResearchStore;
