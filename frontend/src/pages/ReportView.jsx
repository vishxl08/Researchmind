import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Download, FileText, Share2 } from 'lucide-react';
import Navbar from '../components/Navbar';
import useResearchStore from '../store/researchStore';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

const ReportView = () => {
  const { reportId } = useParams();
  const { fetchReport, exportReport } = useResearchStore();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadReport();
  }, [reportId]);

  const loadReport = async () => {
    setLoading(true);
    const data = await fetchReport(reportId);
    if (data) setReport(data);
    setLoading(false);
  };

  const handleExport = async (format) => {
    const blob = await exportReport(reportId, format);
    if (blob) {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report.${format}`;
      a.click();
      toast.success(`Report exported as ${format.toUpperCase()}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white">
        <Navbar />
        <div className="flex items-center justify-center h-96">Loading report...</div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-slate-900 text-white">
        <Navbar />
        <div className="flex items-center justify-center h-96">Report not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />
      <div className="max-w-5xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-4xl font-bold mb-2">{report.title}</h1>
          <div className="flex justify-between items-center">
            <div className="text-slate-400">
              <p>Confidence Score: {(report.confidence_score * 100).toFixed(1)}%</p>
              <p>Word Count: {report.word_count}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition"
              >
                <Download className="w-4 h-4" />
                PDF
              </button>
              <button
                onClick={() => handleExport('docx')}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition"
              >
                <FileText className="w-4 h-4" />
                DOCX
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-slate-700">
          {['overview', 'report', 'sources', 'analysis'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-semibold transition ${
                activeTab === tab
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-3">Executive Summary</h2>
                <p className="text-slate-300">{report.executive_summary}</p>
              </div>
              {report.sub_questions && report.sub_questions.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Research Sub-Questions</h3>
                  <ul className="list-disc list-inside space-y-1 text-slate-300">
                    {report.sub_questions.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {activeTab === 'report' && (
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown>{report.full_report_markdown}</ReactMarkdown>
            </div>
          )}

          {activeTab === 'sources' && (
            <div className="space-y-3">
              <h2 className="font-semibold">Sources</h2>
              {report.sources && report.sources.map((source, i) => (
                <a
                  key={i}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition"
                >
                  <p className="font-semibold text-blue-400">{source.title}</p>
                  <p className="text-slate-400 text-sm">{source.url}</p>
                  <p className="text-slate-500 text-xs">Reliability: {(source.reliability * 100).toFixed(0)}%</p>
                </a>
              ))}
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="space-y-4">
              {report.key_findings && (
                <div>
                  <h3 className="font-semibold mb-2">Key Findings</h3>
                  <ul className="space-y-2">
                    {report.key_findings.map((f, i) => (
                      <li key={i} className="p-2 bg-slate-700 rounded text-slate-300">• {f}</li>
                    ))}
                  </ul>
                </div>
              )}
              {report.contradictions_found && (
                <div>
                  <h3 className="font-semibold mb-2">Contradictions Found</h3>
                  <ul className="space-y-2">
                    {report.contradictions_found.map((c, i) => (
                      <li key={i} className="p-2 bg-red-900 rounded text-red-200">⚠️ {c}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportView;
