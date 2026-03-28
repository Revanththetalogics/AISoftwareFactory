'use client';

import { useState, useEffect } from 'react';
import { 
  analyticsService,
  AnalyticsQuery,
  AnalyticsReport,
  PredictionRequest,
  PredictionResult,
  ReportGenerateRequest,
  ReportType,
} from '@/services/analytics.service';

export default function AdvancedAnalyticsDashboard() {
  const [queries, setQueries] = useState<AnalyticsQuery[]>([]);
  const [reports, setReports] = useState<AnalyticsReport[]>([]);
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'queries' | 'reports' | 'predictions'>('overview');
  const [selectedMetric, setSelectedMetric] = useState('projects_created');
  const [timeRange, setTimeRange] = useState('last_30_days');
  const [isLoading, setIsLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    loadData();
    loadDashboardSummary();
  }, []);

  const loadData = async () => {
    try {
      const [queryList, reportList, predictionList] = await Promise.all([
        analyticsService.listQueries(),
        analyticsService.listReports(),
        analyticsService.listPredictions()
      ]);
      
      setQueries(queryList);
      setReports(reportList);
      setPredictions(predictionList);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    }
  };

  const loadDashboardSummary = async () => {
    setIsLoading(true);
    try {
      const summary = await analyticsService.getDashboardSummary();
      setDashboardData(summary);
    } catch (error) {
      console.error('Failed to load dashboard summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createQuery = async () => {
    try {
      const newQuery = await analyticsService.createQuery({
        name: `Query for ${selectedMetric}`,
        metrics: [selectedMetric],
        dimensions: ['date'],
        filters: {},
        time_range: getTimeRangeConfig(timeRange),
        granularity: 'day'
      });
      
      setQueries(prev => [...prev, newQuery]);
      console.log('Query created successfully');
    } catch (error) {
      console.error('Failed to create query:', error);
    }
  };

  const executeQuery = async (queryId: string) => {
    try {
      const results = await analyticsService.executeQuery(queryId);
      console.log('Query executed:', results);
      return results;
    } catch (error) {
      console.error('Failed to execute query:', error);
      throw error;
    }
  };

  const generateReport = async (queryId: string, reportType: ReportType = ReportType.SUMMARY) => {
    try {
      const request: ReportGenerateRequest = {
        query_id: queryId,
        report_type: reportType
      };
      const report = await analyticsService.generateReport(request);
      setReports(prev => [report, ...prev]);
      console.log('Report generated successfully');
      return report;
    } catch (error) {
      console.error('Failed to generate report:', error);
      throw error;
    }
  };

  const predictFutureValues = async (metric: string, periods: number = 30) => {
    try {
      const request: PredictionRequest = {
        metric: metric,
        periods: periods
      };
      const prediction = await analyticsService.predictFutureValues(request);
      setPredictions(prev => [prediction, ...prev]);
      console.log('Prediction generated successfully');
      return prediction;
    } catch (error) {
      console.error('Failed to generate prediction:', error);
      throw error;
    }
  };

  const getTimeRangeConfig = (range: string) => {
    const now = new Date();
    const endDate = now.toISOString().split('T')[0];
    
    let startDate: string;
    switch (range) {
      case 'last_7_days':
        startDate = new Date(now.setDate(now.getDate() - 7)).toISOString().split('T')[0];
        break;
      case 'last_30_days':
        startDate = new Date(now.setDate(now.getDate() - 30)).toISOString().split('T')[0];
        break;
      case 'last_90_days':
        startDate = new Date(now.setDate(now.getDate() - 90)).toISOString().split('T')[0];
        break;
      default:
        startDate = new Date(now.setDate(now.getDate() - 30)).toISOString().split('T')[0];
    }
    
    return { start_date: startDate, end_date: endDate };
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getMetricIcon = (metric: string) => {
    const icons: Record<string, string> = {
      'projects_created': '📊',
      'active_users': '👥',
      'conversion_rate': '📈',
      'revenue': '💰',
      'session_duration': '⏱️'
    };
    return icons[metric] || '📊';
  };



  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Advanced Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Business intelligence and predictive analytics</p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'overview'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('queries')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'queries'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Queries ({queries.length})
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'reports'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Reports ({reports.length})
            </button>
            <button
              onClick={() => setActiveTab('predictions')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'predictions'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Predictions ({predictions.length})
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 p-4">
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={createQuery}
                  className="w-full px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create Query
                </button>
                <button
                  onClick={() => predictFutureValues(selectedMetric)}
                  className="w-full px-3 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Generate Prediction
                </button>
                <button
                  onClick={loadDashboardSummary}
                  disabled={isLoading}
                  className="w-full px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
                >
                  Refresh Dashboard
                </button>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Configuration</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Metric</label>
                  <select
                    value={selectedMetric}
                    onChange={(e) => setSelectedMetric(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="projects_created">Projects Created</option>
                    <option value="active_users">Active Users</option>
                    <option value="conversion_rate">Conversion Rate</option>
                    <option value="revenue">Revenue</option>
                    <option value="session_duration">Session Duration</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Time Range</label>
                  <select
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="last_7_days">Last 7 Days</option>
                    <option value="last_30_days">Last 30 Days</option>
                    <option value="last_90_days">Last 90 Days</option>
                  </select>
                </div>
              </div>
            </div>

            {dashboardData && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Queries:</span>
                    <span className="font-medium">{String(dashboardData.total_queries)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Reports:</span>
                    <span className="font-medium">{String(dashboardData.total_reports)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Predictions:</span>
                    <span className="font-medium">{String(dashboardData.total_predictions)}</span>
                  </div>
                  <div className="pt-2 border-t border-gray-200">
                    <div className="text-xs text-gray-500">
                      Last updated: {new Date().toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-6 overflow-auto">
          {activeTab === 'overview' && (
            <div className="max-w-6xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {/* KPI Cards */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <span className="text-2xl">📊</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm text-gray-600">Total Queries</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {String(dashboardData?.total_queries || 0)}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <span className="text-2xl">📋</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm text-gray-600">Reports Generated</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {String(dashboardData?.total_reports || 0)}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <span className="text-2xl">🔮</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm text-gray-600">Predictions Made</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {String(dashboardData?.total_predictions || 0)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
                </div>
                <div className="p-6">
                  {reports.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No recent reports</p>
                  ) : (
                    <div className="space-y-4">
                      {reports.slice(0, 5).map(report => (
                        <div key={report.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div>
                            <h3 className="font-medium text-gray-900">{report.name}</h3>
                            <p className="text-sm text-gray-600 mt-1">
                              Generated {formatDate(report.generated_at)}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full capitalize">
                              {report.type}
                            </span>
                            <button className="text-blue-600 hover:text-blue-800 text-sm">
                              View Details
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'queries' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Analytics Queries</h2>
                  <p className="text-gray-600 mt-1">Manage and execute analytics queries</p>
                </div>
                
                <div className="p-6">
                  {queries.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🔍</span>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Queries Yet</h3>
                      <p className="text-gray-500 mb-6">Create your first analytics query to get started</p>
                      <button
                        onClick={createQuery}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        Create Query
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {queries.map(query => (
                        <div key={query.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="font-medium text-gray-900">{query.name}</h3>
                              <div className="mt-2 flex flex-wrap gap-2">
                                {query.metrics.map((metric: string) => (
                                  <span key={metric} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                    {getMetricIcon(metric)} {metric}
                                  </span>
                                ))}
                              </div>
                              <div className="mt-2 text-sm text-gray-600">
                                Time range: {query.time_range.start_date} to {query.time_range.end_date}
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => executeQuery(query.id)}
                                className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                              >
                                Execute
                              </button>
                              <button
                                onClick={() => generateReport(query.id)}
                                className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                              >
                                Generate Report
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Analytics Reports</h2>
                  <p className="text-gray-600 mt-1">View and manage generated reports</p>
                </div>
                
                <div className="p-6">
                  {reports.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">📋</span>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Reports Generated</h3>
                      <p className="text-gray-500">Execute queries to generate reports</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {reports.map(report => (
                        <div key={report.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="font-medium text-gray-900">{report.name}</h3>
                              <div className="mt-1 flex items-center space-x-2">
                                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded capitalize">
                                  {report.type}
                                </span>
                                <span className="text-sm text-gray-500">
                                  Generated {formatDate(report.generated_at)}
                                </span>
                              </div>
                              <div className="mt-2 text-sm text-gray-600">
                                Based on query: {report.query?.name || 'Unknown'}
                              </div>
                            </div>
                            <button className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700">
                              View Report
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'predictions' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Predictions</h2>
                  <p className="text-gray-600 mt-1">View predictive analytics results</p>
                </div>
                
                <div className="p-6">
                  {predictions.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🔮</span>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Predictions Generated</h3>
                      <p className="text-gray-500 mb-6">Generate predictions to see forecasting results</p>
                      <button
                        onClick={() => predictFutureValues(selectedMetric)}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                      >
                        Generate Prediction
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {predictions.map(prediction => (
                        <div key={prediction.metric} className="border border-gray-200 rounded-lg p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <h3 className="text-lg font-medium text-gray-900">
                                {getMetricIcon(prediction.metric)} {prediction.metric.replace('_', ' ')}
                              </h3>
                              <div className="mt-1 flex items-center space-x-4">
                                <span className="text-sm text-gray-600">
                                  Model: {prediction.model_type}
                                </span>
                                <span className="text-sm text-gray-600">
                                  Accuracy: {(prediction.accuracy_score * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold text-purple-600">
                                {prediction.predicted_values.length > 0 
                                  ? formatNumber(Math.round(prediction.predicted_values[0].value))
                                  : 'N/A'
                                }
                              </div>
                              <div className="text-sm text-gray-500">Next period prediction</div>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2">Confidence Interval</h4>
                              <div className="text-sm text-gray-600">
                                {prediction.confidence_interval[0].toFixed(2)} - {prediction.confidence_interval[1].toFixed(2)}
                              </div>
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2">Prediction Points</h4>
                              <div className="text-sm text-gray-600">
                                {prediction.predicted_values.length} future periods
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}