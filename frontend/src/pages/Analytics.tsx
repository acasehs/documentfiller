import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart3,
  TrendingUp,
  FileText,
  Zap,
  Award,
  Download,
  Calendar,
  Activity
} from 'lucide-react';

interface UserStats {
  period_days: number;
  documents: {
    total: number;
    recent: number;
  };
  generations: {
    total: number;
    recent: number;
    avg_time_seconds: number;
  };
  tokens: {
    total: number;
    recent: number;
    avg_per_generation: number;
  };
  reviews: {
    total: number;
    recent: number;
    avg_quality_score: number;
  };
  model_usage: Array<{
    model: string;
    count: number;
  }>;
}

interface TimelineEntry {
  period: string;
  generations: number;
  tokens: number;
}

interface DocumentBreakdown {
  total_documents: number;
  status_breakdown: { [key: string]: number };
  section_distribution: { [key: string]: number };
  avg_sections_per_document: number;
}

interface QualityTrends {
  period_days: number;
  sample_size: number;
  overall_quality: {
    min: number;
    max: number;
    avg: number;
  };
  metric_averages: {
    tense_consistency: number;
    readability: number;
    coherence: number;
  };
  distribution: {
    excellent: number;
    good: number;
    needs_improvement: number;
  };
}

export default function Analytics() {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [breakdown, setBreakdown] = useState<DocumentBreakdown | null>(null);
  const [quality, setQuality] = useState<QualityTrends | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [activeTab, setActiveTab] = useState<'overview' | 'activity' | 'quality' | 'documents'>('overview');

  useEffect(() => {
    fetchAnalytics();
  }, [selectedPeriod]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [statsRes, timelineRes, breakdownRes, qualityRes] = await Promise.all([
        axios.get(`/api/analytics/user/stats?days=${selectedPeriod}`),
        axios.get(`/api/analytics/user/timeline?days=${selectedPeriod}`),
        axios.get('/api/analytics/user/documents'),
        axios.get(`/api/analytics/quality?days=${selectedPeriod}`)
      ]);

      setStats(statsRes.data);
      setTimeline(timelineRes.data.timeline);
      setBreakdown(breakdownRes.data);
      setQuality(qualityRes.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportAnalytics = async () => {
    try {
      const response = await axios.get('/api/analytics/export');
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-${new Date().toISOString()}.json`;
      a.click();
    } catch (error) {
      console.error('Failed to export analytics:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Analytics Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Track your document generation activity and performance</p>
        </div>
        <div className="flex gap-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
          <button
            onClick={exportAnalytics}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Download className="w-4 h-4" />
            Export Data
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'overview', label: 'Overview', icon: BarChart3 },
          { id: 'activity', label: 'Activity', icon: Activity },
          { id: 'quality', label: 'Quality', icon: Award },
          { id: 'documents', label: 'Documents', icon: FileText }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-500'
                : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && stats && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Documents */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <FileText className="w-8 h-8 text-blue-600" />
                <span className="text-sm text-gray-500 dark:text-gray-400">Documents</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{stats.documents.recent}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {stats.documents.total} total
              </div>
            </div>

            {/* Generations */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <Zap className="w-8 h-8 text-yellow-600" />
                <span className="text-sm text-gray-500 dark:text-gray-400">Generations</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{stats.generations.recent}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Avg: {stats.generations.avg_time_seconds.toFixed(1)}s
              </div>
            </div>

            {/* Tokens */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8 text-green-600" />
                <span className="text-sm text-gray-500 dark:text-gray-400">Tokens</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                {(stats.tokens.recent / 1000).toFixed(1)}K
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {stats.tokens.avg_per_generation} avg/gen
              </div>
            </div>

            {/* Quality Score */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <Award className="w-8 h-8 text-purple-600" />
                <span className="text-sm text-gray-500 dark:text-gray-400">Quality</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                {stats.reviews.avg_quality_score.toFixed(1)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {stats.reviews.recent} reviews
              </div>
            </div>
          </div>

          {/* Model Usage */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Model Usage</h3>
            <div className="space-y-3">
              {stats.model_usage.map((model) => {
                const total = stats.model_usage.reduce((sum, m) => sum + m.count, 0);
                const percentage = (model.count / total) * 100;
                return (
                  <div key={model.model}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700 dark:text-gray-300">{model.model}</span>
                      <span className="text-gray-600 dark:text-gray-400">{model.count} ({percentage.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Activity Tab */}
      {activeTab === 'activity' && (
        <div className="space-y-6">
          {/* Activity Timeline */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Activity Timeline</h3>
            <div className="space-y-2">
              {timeline.map((entry, index) => {
                const maxGenerations = Math.max(...timeline.map(e => e.generations));
                const barWidth = (entry.generations / maxGenerations) * 100;
                return (
                  <div key={index} className="flex items-center gap-3">
                    <span className="text-sm text-gray-600 dark:text-gray-400 w-24">
                      {new Date(entry.period).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                    <div className="flex-1 flex items-center gap-2">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-6 relative">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-blue-600 h-6 rounded-full flex items-center justify-end pr-2 transition-all"
                          style={{ width: `${barWidth}%` }}
                        >
                          {entry.generations > 0 && (
                            <span className="text-white text-xs font-medium">{entry.generations}</span>
                          )}
                        </div>
                      </div>
                      <span className="text-sm text-gray-500 dark:text-gray-400 w-20">
                        {(entry.tokens / 1000).toFixed(1)}K tokens
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Quality Tab */}
      {activeTab === 'quality' && quality && (
        <div className="space-y-6">
          {/* Quality Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Average Quality</h4>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">{quality.overall_quality.avg.toFixed(1)}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Range: {quality.overall_quality.min.toFixed(1)} - {quality.overall_quality.max.toFixed(1)}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Reviews</h4>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">{quality.sample_size}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Last {quality.period_days} days
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Excellence Rate</h4>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">
                {quality.sample_size > 0
                  ? ((quality.distribution.excellent / quality.sample_size) * 100).toFixed(0)
                  : 0}%
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {quality.distribution.excellent} excellent documents
              </div>
            </div>
          </div>

          {/* Quality Metrics */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quality Metrics</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-700 dark:text-gray-300">Tense Consistency</span>
                  <span className="text-gray-600 dark:text-gray-400">{quality.metric_averages.tense_consistency.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${(quality.metric_averages.tense_consistency / 10) * 100}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-700 dark:text-gray-300">Readability</span>
                  <span className="text-gray-600 dark:text-gray-400">{quality.metric_averages.readability.toFixed(1)}/100</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${quality.metric_averages.readability}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-700 dark:text-gray-300">Coherence</span>
                  <span className="text-gray-600 dark:text-gray-400">{quality.metric_averages.coherence.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full"
                    style={{ width: `${(quality.metric_averages.coherence / 10) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Quality Distribution */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quality Distribution</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl font-bold text-green-600 dark:text-green-500">{quality.distribution.excellent}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Excellent (8-10)</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-500">{quality.distribution.good}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Good (6-8)</div>
              </div>
              <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div className="text-2xl font-bold text-red-600 dark:text-red-500">{quality.distribution.needs_improvement}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Needs Work (&lt;6)</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Documents Tab */}
      {activeTab === 'documents' && breakdown && (
        <div className="space-y-6">
          {/* Document Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Total Documents</h3>
              <div className="text-4xl font-bold text-blue-600">{breakdown.total_documents}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Avg {breakdown.avg_sections_per_document} sections per document
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Status Breakdown</h3>
              <div className="space-y-2">
                {Object.entries(breakdown.status_breakdown).map(([status, count]) => (
                  <div key={status} className="flex justify-between items-center">
                    <span className="text-gray-700 dark:text-gray-300 capitalize">{status}</span>
                    <span className="text-gray-600 dark:text-gray-400 font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section Distribution */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Section Count Distribution</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(breakdown.section_distribution).map(([range, count]) => (
                <div key={range} className="text-center p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">{count}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{range} sections</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
