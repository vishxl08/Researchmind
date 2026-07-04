import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Activity } from 'lucide-react';
import Navbar from '../components/Navbar';
import useResearchStore from '../store/researchStore';
import useWebSocket from '../hooks/useWebSocket';
import ReactMarkdown from 'react-markdown';

const LiveResearch = () => {
  const { jobId } = useParams();
  const { currentJob, currentSteps, currentReport, fetchJobDetails } = useResearchStore();

  useEffect(() => {
    fetchJobDetails(jobId);
  }, [jobId]);

  const isConnected = useWebSocket(jobId);
  const markdown = currentReport?.full_report_markdown || '';

  if (!currentJob) {
    return (
      <div className="min-h-screen bg-slate-900 text-white">
        <Navbar />
        <div className="flex items-center justify-center h-96">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">{currentJob.query}</h1>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-2">
              {isConnected ? (
                <>
                  <Activity className="w-5 h-5 text-green-500 animate-pulse" />
                  <span className="text-green-400">Live</span>
                </>
              ) : (
                <span className="text-slate-400">Connecting...</span>
              )}
            </span>
            <span className="text-slate-400">Steps: {currentSteps.length}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Steps Timeline */}
          <div className="lg:col-span-1 bg-slate-800 rounded-lg border border-slate-700 p-4 h-96 overflow-y-auto">
            <h2 className="font-semibold mb-4">Research Steps</h2>
            <div className="space-y-3">
              {currentSteps.map((step, idx) => (
                <div key={idx} className="p-3 bg-slate-700 rounded-lg text-sm">
                  <p className="font-semibold text-blue-300">Step {step.step_number}</p>
                  <p className="text-slate-300">{step.step_type}</p>
                  {step.thought && <p className="text-slate-400 text-xs mt-1">{step.thought.substring(0, 50)}...</p>}
                </div>
              ))}
            </div>
          </div>

          {/* Live Markdown Preview */}
          <div className="lg:col-span-2 bg-slate-800 rounded-lg border border-slate-700 p-6 h-96 overflow-y-auto">
            <h2 className="font-semibold mb-4">Report Preview</h2>
            <div className="prose prose-invert max-w-none text-sm">
              <ReactMarkdown>{markdown || 'Waiting for research to begin...'}</ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveResearch;
