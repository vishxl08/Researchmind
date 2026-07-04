import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Cpu, FileText, BookOpen, ArrowRight } from 'lucide-react';
import useAuthStore from '../store/authStore';

const Landing = () => {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-hidden relative">
      {/* Navbar */}
      <header className="flex justify-between items-center px-6 py-5 max-w-7xl mx-auto relative z-10">
        <div className="flex items-center gap-2 text-xl font-bold">
          <Brain className="w-7 h-7 text-violet-400" />
          <span>ResearchMind</span>
        </div>
        <div>
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-500/20 hover:shadow-violet-500/30 transition-all duration-300"
            >
              Go to Dashboard
            </Link>
          ) : (
            <div className="flex gap-4 items-center">
              <Link to="/login" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
                Log in
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-xl text-sm font-semibold bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-6 py-20 text-center flex flex-col items-center gap-8 z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-violet-500/20 text-xs font-semibold text-violet-300 tracking-wide uppercase">
          <Cpu className="w-3.5 h-3.5" />
          Autonomous AI Agent with Memory
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-[1.15] bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
          Give it a topic.<br />Wake up to a research report.
        </h1>
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl leading-relaxed">
          ResearchMind is an autonomous research agent. It plans, queries online sources, reads academic papers, resolves contradictions, and curates cited markdown reports — all with zero human supervision.
        </p>

        <div className="mt-4 flex flex-col sm:flex-row gap-4">
          <Link
            to={isAuthenticated ? "/research/new" : "/register"}
            className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-xl shadow-violet-500/20 hover:shadow-violet-500/35 transition-all duration-300 transform hover:scale-[1.02]"
          >
            <span>Start Researching Now</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* 3-Step visual workflow card system */}
        <div className="mt-24 w-full grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass p-8 rounded-2xl flex flex-col items-center text-center gap-4 hover:border-violet-500/30 transition-colors duration-300">
            <div className="p-4 rounded-xl bg-violet-500/10 border border-violet-500/25 text-violet-400">
              <Brain className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold">1. Input Query</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Describe your topic or question. Set depth parameters and iterations to guide the autonomous agent.
            </p>
          </div>

          <div className="glass p-8 rounded-2xl flex flex-col items-center text-center gap-4 hover:border-violet-500/30 transition-colors duration-300">
            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/25 text-indigo-400">
              <Cpu className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold">2. Agentic ReAct Loop</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              The agent creates sub-questions, executes searches, scores sources, runs self-critiques, and builds knowledge.
            </p>
          </div>

          <div className="glass p-8 rounded-2xl flex flex-col items-center text-center gap-4 hover:border-violet-500/30 transition-colors duration-300">
            <div className="p-4 rounded-xl bg-teal-500/10 border border-teal-500/25 text-teal-400">
              <FileText className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold">3. Cited Report</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Read the generated report in markdown. Check references, verify confidence scores, and export to PDF/Word.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-800 z-10">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <BookOpen className="w-4 h-4" />
            <span>&copy; {new Date().getFullYear()} ResearchMind. All rights reserved.</span>
          </div>
          <div className="flex gap-6 text-sm text-slate-500">
            <a href="https://console.groq.com" target="_blank" rel="noreferrer" className="hover:text-slate-300 transition-colors">Groq API</a>
            <a href="https://serper.dev" target="_blank" rel="noreferrer" className="hover:text-slate-300 transition-colors">Serper Dev</a>
            <a href="https://github.com" className="hover:text-slate-300 transition-colors font-semibold">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
