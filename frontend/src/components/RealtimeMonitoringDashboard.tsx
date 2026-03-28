'use client';

import { useState, useEffect } from 'react';
import { monitoringService, SystemMetrics, ApplicationMetrics, BusinessMetrics, ClusterStatus, AlertInfo } from '@/services/monitoring.service';

export default function RealtimeMonitoringDashboard() {
  const [isConnected, setIsConnected] = useState(false);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [applicationMetrics, setApplicationMetrics] = useState<ApplicationMetrics | null>(null);
  const [businessMetrics, setBusinessMetrics] = useState<BusinessMetrics | null>(null);
  const [clusterStatus, setClusterStatus] = useState<ClusterStatus | null>(null);
  const [activeAlerts, setActiveAlerts] = useState<AlertInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const setMetrics = (metrics: {
    system?: SystemMetrics | null;
    application?: ApplicationMetrics | null;
    business?: BusinessMetrics | null;
    cluster?: ClusterStatus | null;
  }) => {
    if (metrics.system) setSystemMetrics(metrics.system);
    if (metrics.application) setApplicationMetrics(metrics.application);
    if (metrics.business) setBusinessMetrics(metrics.business);
    if (metrics.cluster) setClusterStatus(metrics.cluster);
    if (isLoading) setIsLoading(false);
  };

  useEffect(() => {
    // Connect to monitoring service
    const unsubscribeConnection = monitoringService.subscribeConnection(setIsConnected);
    const unsubscribeMetrics = monitoringService.subscribeToMetrics(setMetrics);
    const unsubscribeAlerts = monitoringService.subscribeToAlerts(setActiveAlerts);

    monitoringService.connect();

    // Cleanup on unmount
    return () => {
      unsubscribeConnection();
      unsubscribeMetrics();
      unsubscribeAlerts();
      monitoringService.disconnect();
    };
  }, [setMetrics]);

  const acknowledgeAlert = (alertName: string) => {
    monitoringService.acknowledgeAlert(alertName);
    // Remove from active alerts
    setActiveAlerts(prev => prev.filter(alert => alert.name !== alertName));
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-50 border-red-200';
      case 'error': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getHealthStatus = (value: number) => {
    if (value > 90) return { status: 'critical', color: 'text-red-500' };
    if (value > 75) return { status: 'warning', color: 'text-yellow-500' };
    return { status: 'healthy', color: 'text-green-500' };
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Connecting to monitoring service...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className={`p-4 rounded-lg border ${isConnected ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-3 ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className={isConnected ? 'text-green-700' : 'text-red-700'}>
            {isConnected ? 'Connected to monitoring service' : 'Disconnected from monitoring service'}
          </span>
        </div>
      </div>

      {/* System Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* CPU Usage */}
        {systemMetrics && (
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500 mb-2">CPU Usage</h3>
            <div className="flex items-baseline">
              <span className={`text-3xl font-bold ${getHealthStatus(systemMetrics.cpu_percent).color}`}>
                {systemMetrics.cpu_percent.toFixed(1)}%
              </span>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`bg-blue-600 h-2 rounded-full transition-all duration-300`}
                style={{ width: `${systemMetrics.cpu_percent}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Updated: {new Date(systemMetrics.timestamp).toLocaleTimeString()}
            </p>
          </div>
        )}

        {/* Memory Usage */}
        {systemMetrics && (
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Memory Usage</h3>
            <div className="flex items-baseline">
              <span className={`text-3xl font-bold ${getHealthStatus(systemMetrics.memory_percent).color}`}>
                {systemMetrics.memory_percent.toFixed(1)}%
              </span>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`bg-purple-600 h-2 rounded-full transition-all duration-300`}
                style={{ width: `${systemMetrics.memory_percent}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Updated: {new Date(systemMetrics.timestamp).toLocaleTimeString()}
            </p>
          </div>
        )}

        {/* Disk Usage */}
        {systemMetrics && (
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Disk Usage</h3>
            <div className="flex items-baseline">
              <span className={`text-3xl font-bold ${getHealthStatus(systemMetrics.disk_percent).color}`}>
                {systemMetrics.disk_percent.toFixed(1)}%
              </span>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`bg-green-600 h-2 rounded-full transition-all duration-300`}
                style={{ width: `${systemMetrics.disk_percent}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Updated: {new Date(systemMetrics.timestamp).toLocaleTimeString()}
            </p>
          </div>
        )}

        {/* Application Performance */}
        {applicationMetrics && (
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Requests/Sec</h3>
            <div className="flex items-baseline">
              <span className="text-3xl font-bold text-indigo-600">
                {applicationMetrics.requests_per_second.toFixed(1)}
              </span>
            </div>
            <div className="mt-2">
              <p className="text-sm text-gray-600">
                Avg Response: {applicationMetrics.average_response_time_ms.toFixed(0)}ms
              </p>
              <p className="text-sm text-gray-600">
                Error Rate: {(applicationMetrics.error_rate * 100).toFixed(2)}%
              </p>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Updated: {new Date(applicationMetrics.timestamp).toLocaleTimeString()}
            </p>
          </div>
        )}
      </div>

      {/* Business Metrics */}
      {businessMetrics && (
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Business Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{businessMetrics.projects_count}</p>
              <p className="text-sm text-gray-600">Active Projects</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{businessMetrics.code_generations_today}</p>
              <p className="text-sm text-gray-600">Code Generations</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">{businessMetrics.simulations_run_today}</p>
              <p className="text-sm text-gray-600">Simulations Run</p>
            </div>
            <div className="text-center p-4 bg-indigo-50 rounded-lg">
              <p className="text-2xl font-bold text-indigo-600">{businessMetrics.deployments_successful}</p>
              <p className="text-sm text-gray-600">Successful Deploys</p>
            </div>
          </div>
        </div>
      )}

      {/* Cluster Status */}
      {clusterStatus && (
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cluster Status</h3>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-4 h-4 rounded-full ${
                clusterStatus.cluster_health === 'healthy' ? 'bg-green-500' :
                clusterStatus.cluster_health === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></div>
              <span className="font-medium capitalize">{clusterStatus.cluster_health} Cluster</span>
              <span className="text-gray-600">
                {clusterStatus.nodes_active}/{clusterStatus.nodes_total} Nodes Active
              </span>
              <span className="text-gray-600">Leader: {clusterStatus.leader_node}</span>
            </div>
            <span className="text-sm text-gray-500">
              Updated: {new Date(clusterStatus.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      )}

      {/* Active Alerts */}
      {activeAlerts.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Alerts</h3>
          <div className="space-y-3">
            {activeAlerts.slice(0, 5).map((alert, index) => (
              <div key={index} className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-medium capitalize">{alert.severity}</span>
                      <span className="text-sm text-gray-500">{alert.name}</span>
                    </div>
                    <p className="mt-1 text-gray-700">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      Triggered: {new Date(alert.triggered_at).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => acknowledgeAlert(alert.name)}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Acknowledge
                  </button>
                </div>
              </div>
            ))}
            {activeAlerts.length > 5 && (
              <p className="text-center text-sm text-gray-500">
                +{activeAlerts.length - 5} more alerts
              </p>
            )}
          </div>
        </div>
      )}

      {/* Reconnect Button */}
      {!isConnected && (
        <div className="text-center">
          <button
            onClick={() => monitoringService.connect()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Reconnect to Monitoring Service
          </button>
        </div>
      )}
    </div>
  );
}