'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  performanceProfilingService, 
  ProfilingSession, 
  PerformanceReport,
  PerformanceBottleneck,
  PerformanceRecommendation
} from '@/services/performance-profiling.service';

export default function PerformanceDashboard() {
  const [sessions, setSessions] = useState<ProfilingSession[]>([]);
  const [activeSession, setActiveSession] = useState<ProfilingSession | null>(null);
  const [isProfiling, setIsProfiling] = useState(false);
  const [report, setReport] = useState<PerformanceReport | null>(null);
  const [bottlenecks, setBottlenecks] = useState<PerformanceBottleneck[]>([]);
  const [recommendations, setRecommendations] = useState<PerformanceRecommendation[]>([]);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d');
  const [activeTab, setActiveTab] = useState<'realtime' | 'history' | 'analysis'>('realtime');
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const loadInitialData = async () => {
    try {
      // Load existing sessions
      // In a real implementation, this would fetch from backend
      console.log('Loading performance data...');
    } catch (error) {
      console.error('Failed to load performance data:', error);
    }
  };

  const updateRealtimeMetrics = useCallback(() => {
    // Update metrics display
    const currentMetrics = performanceProfilingService.getCurrentMetrics();
    console.log('Current metrics:', currentMetrics);
  }, []);

  useEffect(() => {
    loadInitialData();
    
    // Set up real-time updates
    intervalRef.current = setInterval(() => {
      if (isProfiling && activeSession) {
        updateRealtimeMetrics();
      }
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isProfiling, activeSession, updateRealtimeMetrics]);

  const startProfiling = async () => {
    try {
      setIsProfiling(true);
      const session = await performanceProfilingService.startProfilingSession(`Session ${sessions.length + 1}`);
      setActiveSession(session);
      setSessions(prev => [...prev, session]);
    } catch (error) {
      console.error('Failed to start profiling:', error);
      setIsProfiling(false);
    }
  };

  const stopProfiling = async () => {
    if (!activeSession) return;
    
    try {
      const completedSession = await performanceProfilingService.stopProfilingSession(activeSession.id);
      setActiveSession(null);
      setIsProfiling(false);
      setSessions(prev => prev.map(s => s.id === completedSession.id ? completedSession : s));
      
      // Generate report
      const newReport = await performanceProfilingService.getPerformanceReport(
        completedSession.started_at,
        completedSession.ended_at || new Date().toISOString()
      );
      setReport(newReport);
      setBottlenecks(newReport.bottlenecks);
      setRecommendations(newReport.recommendations);
    } catch (error) {
      console.error('Failed to stop profiling:', error);
    }
  };

  const generateReport = async () => {
    try {
      const endDate = new Date().toISOString();
      const startDate = new Date(Date.now() - 
        (timeRange === '24h' ? 24 * 60 * 60 * 1000 :
         timeRange === '7d' ? 7 * 24 * 60 * 60 * 1000 :
         30 * 24 * 60 * 60 * 1000)).toISOString();
      
      const newReport = await performanceProfilingService.getPerformanceReport(startDate, endDate, true);
      setReport(newReport);
      setBottlenecks(newReport.bottlenecks);
      setRecommendations(newReport.recommendations);
    } catch (error) {
      console.error('Failed to generate report:', error);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getEffortColor = (effort: string) => {
    switch (effort) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Performance Profiling</h1>
            <p className="text-gray-600 mt-1">Monitor, analyze, and optimize application performance</p>
          </div>
          
          <div className="flex flex-wrap gap-3">
            {!isProfiling ? (
              <button
                onClick={startProfiling}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Start Profiling
              </button>
            ) : (
              <button
                onClick={stopProfiling}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
                Stop Profiling
              </button>
            )}
            
            <button
              onClick={generateReport}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Generate Report
            </button>
          </div>
        </div>
        
        {isProfiling && activeSession && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-800">
                  Active Session: {activeSession.name}
                </p>
                <p className="text-xs text-blue-700">
                  Started: {new Date(activeSession.started_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Performance Score */}
      {report && (
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Overview</h2>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`px-4 py-2 rounded-full font-bold text-lg ${getScoreColor(report.overall_score)}`}>
                {report.overall_score}/100
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Overall Performance Score</h3>
                <p className="text-sm text-gray-600">
                  {report.comparison 
                    ? `${report.comparison.improvement_percentage > 0 ? '+' : ''}${report.comparison.improvement_percentage}% from previous period`
                    : 'Baseline measurement'}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Reporting Period</p>
              <p className="font-medium text-gray-900">
                {new Date(report.period.start).toLocaleDateString()} - {new Date(report.period.end).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            <button
              onClick={() => setActiveTab('realtime')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'realtime'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Real-time Metrics
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Session History
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'analysis'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Analysis & Recommendations
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'realtime' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Current Performance Metrics</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">DOM Content Loaded</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {performanceProfilingService.getCurrentMetrics()['timing_dom_content_loaded']?.toFixed(0) || '0'}ms
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Page Load Time</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {performanceProfilingService.getCurrentMetrics()['timing_page_load']?.toFixed(0) || '0'}ms
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Memory Usage</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {performanceProfilingService.getCurrentMetrics()['memory_js_heap_used']?.toFixed(1) || '0'}MB
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Network Requests</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {Object.keys(performanceProfilingService.getCurrentMetrics()).filter(k => k.startsWith('network_')).length}
                  </p>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-blue-800">
                    Real-time metrics are being collected. Start a profiling session to capture detailed performance data.
                  </span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Profiling Sessions</h3>
              
              {sessions.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-gray-500">No profiling sessions recorded yet</p>
                  <p className="text-sm text-gray-400 mt-1">Start a profiling session to begin capturing performance data</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.map((session) => (
                    <div key={session.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">{session.name}</h4>
                          <p className="text-sm text-gray-600">
                            {new Date(session.started_at).toLocaleString()}
                            {session.ended_at && ` - ${new Date(session.ended_at).toLocaleString()}`}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {session.metrics.length} metrics collected
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            session.status === 'active' ? 'bg-green-100 text-green-800' :
                            session.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {session.status}
                          </span>
                          {session.status === 'completed' && (
                            <button className="text-xs text-blue-600 hover:text-blue-800">
                              View Details
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="space-y-6">
              {bottlenecks.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Bottlenecks</h3>
                  <div className="space-y-3">
                    {bottlenecks.map((bottleneck) => (
                      <div key={bottleneck.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="font-medium capitalize">{bottleneck.type}</span>
                              <div className="w-24 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-red-600 h-2 rounded-full" 
                                  style={{ width: `${bottleneck.impact_score}%` }}
                                ></div>
                              </div>
                              <span className="text-sm text-gray-600">{bottleneck.impact_score}/100</span>
                            </div>
                            <h4 className="font-medium text-gray-900">{bottleneck.location}</h4>
                            <p className="text-sm text-gray-600 mt-1">{bottleneck.suggestion}</p>
                            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                              <span>{bottleneck.duration_ms}ms duration</span>
                              <span>{bottleneck.frequency} occurrences</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {recommendations.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Optimization Recommendations</h3>
                  <div className="space-y-3">
                    {recommendations.map((rec) => (
                      <div key={rec.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(rec.priority)}`}>
                                {rec.priority}
                              </span>
                              <span className={`px-2 py-1 text-xs rounded-full ${getEffortColor(rec.implementation_effort)}`}>
                                {rec.implementation_effort} effort
                              </span>
                              <span className="text-xs text-green-600">
                                ↓{rec.estimated_improvement}% expected
                              </span>
                            </div>
                            <h4 className="font-medium text-gray-900">{rec.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                            {rec.code_example && (
                              <pre className="bg-gray-100 p-2 rounded mt-2 text-xs overflow-x-auto">
                                <code>{rec.code_example}</code>
                              </pre>
                            )}
                          </div>
                          <button className="text-sm text-blue-600 hover:text-blue-800 whitespace-nowrap">
                            Implement
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {bottlenecks.length === 0 && recommendations.length === 0 && (
                <div className="text-center py-12">
                  <svg className="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-gray-500">No performance issues detected</p>
                  <p className="text-sm text-gray-400 mt-1">Run a profiling session to identify optimization opportunities</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}