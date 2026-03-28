// Performance profiling service for application performance monitoring and analytics
// Provides real-time performance metrics, profiling capabilities, and optimization insights

export type PerformanceMetricType = 'timing' | 'resource' | 'render' | 'network' | 'memory';

export interface PerformanceMetric {
  id: string;
  type: PerformanceMetricType;
  name: string;
  value: number;
  unit: string;
  timestamp: string;
  context?: Record<string, unknown>;
  baseline?: number; // Baseline value for comparison
  threshold?: number; // Performance threshold/alert level
}

export interface ProfilingSession {
  id: string;
  name: string;
  started_at: string;
  ended_at?: string;
  status: 'active' | 'completed' | 'cancelled';
  metrics: PerformanceMetric[];
  snapshots: PerformanceSnapshot[];
  summary: {
    duration_ms: number;
    total_metrics: number;
    avg_cpu_usage?: number;
    avg_memory_usage?: number;
    network_requests?: number;
    render_count?: number;
  };
}

export interface PerformanceSnapshot {
  timestamp: string;
  metrics: Record<string, number>;
  stack_trace?: string;
  component_tree?: ComponentTreeNode[];
}

export interface ComponentTreeNode {
  name: string;
  render_time: number;
  children: ComponentTreeNode[];
  props_size?: number;
  state_size?: number;
}

export interface PerformanceReport {
  period: {
    start: string;
    end: string;
  };
  overall_score: number; // 0-100
  metrics_summary: Record<PerformanceMetricType, {
    count: number;
    avg: number;
    min: number;
    max: number;
    trend: 'improving' | 'degrading' | 'stable';
  }>;
  bottlenecks: PerformanceBottleneck[];
  recommendations: PerformanceRecommendation[];
  comparison?: {
    previous_period_score: number;
    improvement_percentage: number;
  };
}

export interface PerformanceBottleneck {
  id: string;
  type: 'component' | 'network' | 'database' | 'render' | 'memory';
  location: string;
  impact_score: number; // 0-100
  duration_ms: number;
  frequency: number; // How often it occurs
  suggestion: string;
}

export interface PerformanceRecommendation {
  id: string;
  category: 'optimization' | 'refactoring' | 'architecture' | 'configuration';
  priority: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  implementation_effort: 'low' | 'medium' | 'high';
  estimated_improvement: number; // Percentage improvement expected
  code_example?: string;
}

class PerformanceProfilingService {
  private baseUrl: string;
  private activeSessions: Map<string, ProfilingSession> = new Map();
  private metricsBuffer: PerformanceMetric[] = [];
  private bufferSize: number = 1000;
  private samplingInterval: number = 1000; // ms
  private isCollecting: boolean = false;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  // Start a new profiling session
  public async startProfilingSession(name: string): Promise<ProfilingSession> {
    const sessionId = `prof_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const session: ProfilingSession = {
      id: sessionId,
      name,
      started_at: new Date().toISOString(),
      status: 'active',
      metrics: [],
      snapshots: [],
      summary: {
        duration_ms: 0,
        total_metrics: 0
      }
    };

    this.activeSessions.set(sessionId, session);
    this.startMetricCollection(sessionId);
    
    return session;
  }

  // Stop profiling session
  public async stopProfilingSession(sessionId: string): Promise<ProfilingSession> {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    session.status = 'completed';
    session.ended_at = new Date().toISOString();
    session.summary.duration_ms = new Date(session.ended_at).getTime() - new Date(session.started_at).getTime();
    session.summary.total_metrics = session.metrics.length;

    this.stopMetricCollection(sessionId);
    this.activeSessions.delete(sessionId);

    return session;
  }

  // Record a performance metric
  public recordMetric(
    type: PerformanceMetricType,
    name: string,
    value: number,
    unit: string,
    context?: Record<string, unknown>
  ): void {
    const metric: PerformanceMetric = {
      id: `metric_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      name,
      value,
      unit,
      timestamp: new Date().toISOString(),
      context
    };

    this.metricsBuffer.push(metric);
    
    // Trim buffer if it exceeds size limit
    if (this.metricsBuffer.length > this.bufferSize) {
      this.metricsBuffer.shift();
    }

    // Add to active sessions
    this.activeSessions.forEach(session => {
      if (session.status === 'active') {
        session.metrics.push(metric);
      }
    });
  }

  // Take a performance snapshot
  public takeSnapshot(sessionId: string, additionalMetrics?: Record<string, number>): void {
    const session = this.activeSessions.get(sessionId);
    if (!session || session.status !== 'active') return;

    const snapshot: PerformanceSnapshot = {
      timestamp: new Date().toISOString(),
      metrics: {
        ...this.getCurrentMetrics(),
        ...additionalMetrics
      }
    };

    session.snapshots.push(snapshot);
  }

  // Get performance report
  public async getPerformanceReport(
    startDate: string,
    endDate: string,
    compareWithPrevious?: boolean
  ): Promise<PerformanceReport> {
    try {
      // Mock implementation - in real scenario would fetch from backend
      const mockReport: PerformanceReport = {
        period: {
          start: startDate,
          end: endDate
        },
        overall_score: 87,
        metrics_summary: {
          timing: { count: 1250, avg: 45.2, min: 2.1, max: 234.5, trend: 'improving' },
          resource: { count: 890, avg: 128.4, min: 45.0, max: 512.3, trend: 'stable' },
          render: { count: 2100, avg: 12.3, min: 1.2, max: 89.7, trend: 'improving' },
          network: { count: 340, avg: 156.7, min: 23.4, max: 890.1, trend: 'degrading' },
          memory: { count: 780, avg: 234.5, min: 156.7, max: 456.8, trend: 'stable' }
        },
        bottlenecks: [
          {
            id: 'bottleneck_1',
            type: 'network',
            location: 'API /api/projects/list',
            impact_score: 85,
            duration_ms: 1250,
            frequency: 45,
            suggestion: 'Implement pagination and caching for project list endpoint'
          },
          {
            id: 'bottleneck_2',
            type: 'render',
            location: 'ProjectList component',
            impact_score: 72,
            duration_ms: 89,
            frequency: 120,
            suggestion: 'Virtualize the list and optimize re-renders with React.memo'
          }
        ],
        recommendations: [
          {
            id: 'rec_1',
            category: 'optimization',
            priority: 'high',
            title: 'Implement Code Splitting',
            description: 'Split large bundles to reduce initial load time',
            implementation_effort: 'medium',
            estimated_improvement: 25,
            code_example: 'const ProjectModule = lazy(() => import("./ProjectModule"));'
          },
          {
            id: 'rec_2',
            category: 'refactoring',
            priority: 'medium',
            title: 'Optimize Database Queries',
            description: 'Add proper indexing and query optimization for slow endpoints',
            implementation_effort: 'high',
            estimated_improvement: 40
          }
        ]
      };

      if (compareWithPrevious) {
        mockReport.comparison = {
          previous_period_score: 78,
          improvement_percentage: 11.5
        };
      }

      return mockReport;
    } catch (error) {
      console.error('Failed to generate performance report:', error);
      throw error;
    }
  }

  // Get real-time performance metrics
  public getCurrentMetrics(): Record<string, number> {
    const latestMetrics = this.metricsBuffer.slice(-10);
    const metrics: Record<string, number> = {};

    latestMetrics.forEach(metric => {
      metrics[`${metric.type}_${metric.name}`] = metric.value;
    });

    // Add browser performance metrics
    if (typeof window !== 'undefined' && window.performance) {
      const perf = window.performance;
      metrics['navigation_domContentLoaded'] = perf.timing.domContentLoadedEventEnd - perf.timing.navigationStart;
      metrics['navigation_load'] = perf.timing.loadEventEnd - perf.timing.navigationStart;
      metrics['memory_used'] = (perf as any).memory ? (perf as any).memory.usedJSHeapSize : 0;
    }

    return metrics;
  }

  // Get component performance data
  public async getComponentPerformance(componentName: string): Promise<{
    render_times: number[];
    average_render_time: number;
    render_frequency: number;
    props_changes: number;
  }> {
    // Mock implementation
    return {
      render_times: [12.3, 15.6, 8.9, 22.1, 11.4],
      average_render_time: 14.1,
      render_frequency: 25,
      props_changes: 8
    };
  }

  // Identify performance bottlenecks
  public async identifyBottlenecks(thresholdMs: number = 100): Promise<PerformanceBottleneck[]> {
    const bottlenecks: PerformanceBottleneck[] = [];
    
    // Analyze buffered metrics for slow operations
    const slowOperations = this.metricsBuffer.filter(
      metric => metric.type === 'timing' && metric.value > thresholdMs
    );

    slowOperations.forEach((metric, index) => {
      bottlenecks.push({
        id: `bottleneck_${index}`,
        type: 'render',
        location: metric.name,
        impact_score: Math.min(100, metric.value / 10),
        duration_ms: metric.value,
        frequency: 1,
        suggestion: `Optimize ${metric.name} - current time: ${metric.value}${metric.unit}`
      });
    });

    return bottlenecks;
  }

  // Private methods
  private startMetricCollection(sessionId: string): void {
    if (this.isCollecting) return;
    
    this.isCollecting = true;
    
    // Collect browser performance metrics
    const collectInterval = setInterval(() => {
      if (typeof window !== 'undefined' && window.performance) {
        const perf = window.performance;
        
        // Navigation timing
        if (perf.timing) {
          this.recordMetric('timing', 'dom_content_loaded', 
            perf.timing.domContentLoadedEventEnd - perf.timing.navigationStart, 'ms');
          this.recordMetric('timing', 'page_load', 
            perf.timing.loadEventEnd - perf.timing.navigationStart, 'ms');
        }
        
        // Memory usage
        if ((perf as any).memory) {
          this.recordMetric('memory', 'js_heap_used', 
            (perf as any).memory.usedJSHeapSize / 1024 / 1024, 'MB');
          this.recordMetric('memory', 'js_heap_total', 
            (perf as any).memory.totalJSHeapSize / 1024 / 1024, 'MB');
        }
        
        // Resource timing
        if (perf.getEntriesByType) {
          const resources = perf.getEntriesByType('resource') as PerformanceResourceTiming[];
          resources.forEach(resource => {
            this.recordMetric('network', `${resource.name}_duration`, 
              resource.duration, 'ms', { entryType: resource.entryType });
          });
        }
      }
    }, this.samplingInterval);
  }

  private stopMetricCollection(sessionId: string): void {
    this.isCollecting = false;
  }

  // Export session data
  public exportSessionData(sessionId: string): string {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }
    
    return JSON.stringify(session, null, 2);
  }

  // Import session data
  public importSessionData(data: string): ProfilingSession {
    const session = JSON.parse(data) as ProfilingSession;
    this.activeSessions.set(session.id, session);
    return session;
  }
}

// Singleton instance
export const performanceProfilingService = new PerformanceProfilingService();