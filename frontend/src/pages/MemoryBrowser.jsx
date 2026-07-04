import React, { useEffect, useState } from 'react';
import { Search, Filter, TrendingUp, Tag, Clock } from 'lucide-react';
import Navbar from '../components/Navbar';
import useResearchStore from '../store/researchStore';

const MemoryBrowser = () => {
  const { memories, fetchMemories, searchMemories } = useResearchStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({ source_tool: '', min_reliability: 0 });
  const [activeFilters, setActiveFilters] = useState(false);

  useEffect(() => {
    fetchMemories();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      await searchMemories(searchQuery);
    } else {
      fetchMemories(filters);
    }
  };

  const filteredMemories = memories.filter((m) => {
    if (filters.source_tool && m.source_tool !== filters.source_tool) return false;
    if (m.reliability_score < filters.min_reliability) return false;
    return true;
  });

  const sourceTools = [...new Set(memories.map((m) => m.source_tool))];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-4xl font-bold mb-2">Memory Browser</h1>
        <p className="text-slate-400 mb-6">Explore and search your accumulated knowledge</p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-3 w-5 h-5 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search memories..."
              className="w-full pl-12 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              className="absolute right-2 top-2 bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded transition"
            >
              Search
            </button>
          </div>
        </form>

        {/* Filters */}
        <div className="mb-6">
          <button
            onClick={() => setActiveFilters(!activeFilters)}
            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition"
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
          {activeFilters && (
            <div className="mt-3 p-4 bg-slate-800 rounded-lg border border-slate-700 space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Source Tool</label>
                <select
                  value={filters.source_tool}
                  onChange={(e) => setFilters({ ...filters, source_tool: e.target.value })}
                  className="w-full p-2 bg-slate-700 border border-slate-600 rounded text-white"
                >
                  <option value="">All Sources</option>
                  {sourceTools.map((tool) => (
                    <option key={tool} value={tool}>
                      {tool}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">
                  Min Reliability: {filters.min_reliability.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={filters.min_reliability}
                  onChange={(e) => setFilters({ ...filters, min_reliability: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>
            </div>
          )}
        </div>

        {/* Memory Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredMemories.length === 0 ? (
            <div className="col-span-full text-center py-12 text-slate-400">
              <p>No memories found. Start a research to build your knowledge base.</p>
            </div>
          ) : (
            filteredMemories.map((memory) => (
              <div key={memory.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <p className="text-slate-400 text-xs mb-1">{memory.source_tool}</p>
                    <p className="text-sm line-clamp-2">{memory.content}</p>
                  </div>
                  <div className="ml-2">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
                      {(memory.reliability_score * 100).toFixed(0)}
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-3">
                  {memory.topic_tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="inline-flex items-center gap-1 px-2 py-1 bg-slate-700 rounded text-xs">
                      <Tag className="w-3 h-3" />
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex justify-between items-center text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {memory.access_count} accesses
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(memory.created_at).toLocaleDateString()}
                  </span>
                </div>

                {memory.source_url && (
                  <a
                    href={memory.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 block text-blue-400 hover:text-blue-300 text-xs truncate"
                  >
                    {memory.source_url}
                  </a>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default MemoryBrowser;
