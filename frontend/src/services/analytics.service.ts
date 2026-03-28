/**
 * Analytics Service
 * 
 * Provides frontend interface for advanced analytics and reporting operations
 * including queries, reports, predictions, and dashboard data.
 */

// @ts-ignore - These will be imported in component files
import { useState, useEffect, useCallback } from 'react';

// Enums matching backend
export enum ReportType {
  SUMMARY = 'summary',
  DETAILED = 'detailed',
  TREND = 'trend',
  COMPARISON = 'comparison',
  PREDICTIVE = 'predictive'
}

export enum TimeGranularity {
  MINUTE = 'minute',
  HOUR = 'hour',
  DAY = 'day',
  WEEK = 'week',
  MONTH = 'month',
  QUARTER = 'quarter',
  YEAR = 'year'
}

// Types matching backend models
export interface AnalyticsQuery {
  id: string;
  name: string;
  metrics: string[];
  dimensions: string[];
  filters: Record<string, any>;
  time_range: {
    start_date: string;
    end_date: string;
  };
  granularity: string;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsReport {
  id: string;
  name: string;
  type: string;
  query: AnalyticsQuery;
  data: Record<string, any>;
  created_at: string;
  generated_at: string;
  description?: string;
  visualization_type: string;
}

export interface PredictionResult {
  metric: string;
  predicted_values: Array<{
    timestamp: string;
    value: number;
    metadata?: Record<string, any>;
  }>;
  confidence_interval: [number, number];
  model_type: string;
  accuracy_score: number;
  created_at: string;
}

export interface TrendAnalysis {
  metric: string;
  trend_direction: 'increasing' | 'decreasing' | 'stable';
  trend_strength: number;
  trend_classification: 'strong' | 'moderate' | 'weak';
  slope: number;
  volatility: number;
  data_points: number;
  period_start: string;
  period_end: string;
}

export interface CorrelationAnalysis {
  correlations: Record<string, number>;
  data_points: number;
  metrics_analyzed: string[];
}

export interface QueryCreateRequest {
  name: string;
  metrics: string[];
  dimensions: string[];
  filters: Record<string, any>;
  time_range: {
    start_date: string;
    end_date: string;
  };
  granularity: string;
}

export interface ReportGenerateRequest {
  query_id: string;
  report_type: string;
  visualization_type?: string;
}

export interface PredictionRequest {
  metric: string;
  periods: number;
  model_type?: string;
}

export interface TrendAnalysisRequest {
  metric: string;
  time_range: {
    start_date: string;
    end_date: string;
  };
}

export interface CorrelationAnalysisRequest {
  metrics: string[];
  time_range: {
    start_date: string;
    end_date: string;
  };
}

class AnalyticsService {
  private baseUrl = '/api/v1/analytics';

  /**
   * Create a new analytics query
   */
  async createQuery(request: QueryCreateRequest): Promise<AnalyticsQuery> {
    const response = await fetch(`${this.baseUrl}/queries`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to create query: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * List all analytics queries
   */
  async listQueries(): Promise<AnalyticsQuery[]> {
    const response = await fetch(`${this.baseUrl}/queries`);
    
    if (!response.ok) {
      throw new Error(`Failed to list queries: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Execute an analytics query
   */
  async executeQuery(queryId: string): Promise<Record<string, any>> {
    const response = await fetch(`${this.baseUrl}/queries/${queryId}/execute`);
    
    if (!response.ok) {
      throw new Error(`Failed to execute query: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Generate a report from a query
   */
  async generateReport(request: ReportGenerateRequest): Promise<AnalyticsReport> {
    const response = await fetch(`${this.baseUrl}/reports`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate report: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * List all analytics reports
   */
  async listReports(): Promise<AnalyticsReport[]> {
    const response = await fetch(`${this.baseUrl}/reports`);
    
    if (!response.ok) {
      throw new Error(`Failed to list reports: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Get a specific report
   */
  async getReport(reportId: string): Promise<AnalyticsReport> {
    const response = await fetch(`${this.baseUrl}/reports/${reportId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get report: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Generate predictions for a metric
   */
  async predictFutureValues(request: PredictionRequest): Promise<PredictionResult> {
    const response = await fetch(`${this.baseUrl}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate predictions: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * List prediction results
   */
  async listPredictions(): Promise<PredictionResult[]> {
    const response = await fetch(`${this.baseUrl}/predictions`);
    
    if (!response.ok) {
      throw new Error(`Failed to list predictions: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Perform trend analysis on a metric
   */
  async getTrendAnalysis(request: TrendAnalysisRequest): Promise<TrendAnalysis> {
    const response = await fetch(`${this.baseUrl}/trend-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to perform trend analysis: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Perform correlation analysis between metrics
   */
  async getCorrelationAnalysis(request: CorrelationAnalysisRequest): Promise<CorrelationAnalysis> {
    const response = await fetch(`${this.baseUrl}/correlation-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to perform correlation analysis: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Get available metrics
   */
  async getAvailableMetrics(): Promise<Array<{ name: string; description: string; type: string }>> {
    const response = await fetch(`${this.baseUrl}/metrics/available`);
    
    if (!response.ok) {
      throw new Error(`Failed to get available metrics: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Get dashboard summary
   */
  async getDashboardSummary(): Promise<Record<string, any>> {
    const response = await fetch(`${this.baseUrl}/dashboard-summary`);
    
    if (!response.ok) {
      throw new Error(`Failed to get dashboard summary: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }
}

// Global service instance
export const analyticsService = new AnalyticsService();

// React hooks for easy integration
export const useAnalytics = () => {
  const [queries, setQueries] = useState<AnalyticsQuery[]>([]);
  const [reports, setReports] = useState<AnalyticsReport[]>([]);
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadQueries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const queryList = await analyticsService.listQueries();
      setQueries(queryList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load queries');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadReports = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const reportList = await analyticsService.listReports();
      setReports(reportList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadPredictions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const predictionList = await analyticsService.listPredictions();
      setPredictions(predictionList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load predictions');
    } finally {
      setLoading(false);
    }
  }, []);

  const createQuery = useCallback(async (request: QueryCreateRequest) => {
    setLoading(true);
    setError(null);
    try {
      const newQuery = await analyticsService.createQuery(request);
      setQueries(prev => [...prev, newQuery]);
      return newQuery;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create query');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateReport = useCallback(async (request: ReportGenerateRequest) => {
    setLoading(true);
    setError(null);
    try {
      const newReport = await analyticsService.generateReport(request);
      setReports(prev => [newReport, ...prev]);
      return newReport;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate report');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadQueries();
    loadReports();
    loadPredictions();
  }, [loadQueries, loadReports, loadPredictions]);

  return {
    queries,
    reports,
    predictions,
    loading,
    error,
    loadQueries,
    loadReports,
    loadPredictions,
    createQuery,
    executeQuery: analyticsService.executeQuery,
    generateReport,
    getReport: analyticsService.getReport,
    predictFutureValues: analyticsService.predictFutureValues,
    getTrendAnalysis: analyticsService.getTrendAnalysis,
    getCorrelationAnalysis: analyticsService.getCorrelationAnalysis,
    getAvailableMetrics: analyticsService.getAvailableMetrics,
    getDashboardSummary: analyticsService.getDashboardSummary,
  };
};