'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Cpu, 
  Database, 
  HardDrive, 
  Wifi, 
  WifiOff,
  AlertTriangle,
  CheckCircle,
  Activity
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Progress, ProgressTrack, ProgressIndicator } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

export interface SystemMetric {
  name: string;
  value: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
  icon: React.ElementType;
  thresholds: {
    warning: number;
    critical: number;
  };
}

interface SystemHealthMonitorProps {
  metrics: SystemMetric[];
  className?: string;
  refreshInterval?: number;
  onMetricAlert?: (metric: SystemMetric) => void;
  isConnected?: boolean;
}

const getStatusConfig = (status: SystemMetric['status']) => {
  switch (status) {
    case 'healthy':
      return {
        color: 'text-success',
        bgColor: 'bg-success/10',
        borderColor: 'border-success/20',
        icon: CheckCircle,
      };
    case 'warning':
      return {
        color: 'text-warning',
        bgColor: 'bg-warning/10',
        borderColor: 'border-warning/20',
        icon: AlertTriangle,
      };
    case 'critical':
      return {
        color: 'text-error',
        bgColor: 'bg-error/10',
        borderColor: 'border-error/20',
        icon: AlertTriangle,
      };
  }
};

const getMetricStatus = (value: number, thresholds: SystemMetric['thresholds']): SystemMetric['status'] => {
  if (value >= thresholds.critical) return 'critical';
  if (value >= thresholds.warning) return 'warning';
  return 'healthy';
};

export function SystemHealthMonitor({ 
  metrics, 
  className,
  refreshInterval = 5000,
  onMetricAlert,
  isConnected: externalIsConnected = true
}: SystemHealthMonitorProps) {
  const [localMetrics, setLocalMetrics] = useState<SystemMetric[]>(metrics);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [latency, setLatency] = useState<number | null>(null);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLocalMetrics(prevMetrics => 
        prevMetrics.map(metric => {
          // Simulate realistic metric fluctuations
          const fluctuation = (Math.random() - 0.5) * 10;
          const newValue = Math.max(0, Math.min(100, metric.value + fluctuation));
          const newStatus = getMetricStatus(newValue, metric.thresholds);
          
          // Trigger alert if status changed to warning/critical
          if (newStatus !== 'healthy' && metric.status === 'healthy') {
            onMetricAlert?.({
              ...metric,
              value: newValue,
              status: newStatus
            });
          }
          
          return {
            ...metric,
            value: newValue,
            status: newStatus
          };
        })
      );
      setLastUpdated(new Date());
      
      // Update latency when connected
      if (externalIsConnected) {
        setLatency(Math.floor(Math.random() * 50) + 10);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval, onMetricAlert, externalIsConnected]);

  const getConnectionStatus = () => {
    return {
      connected: externalIsConnected,
      latency: externalIsConnected ? latency : null
    };
  };

  const connection = getConnectionStatus();

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-text-primary">System Health</h3>
        </div>
        <div className="flex items-center gap-2">
          <Badge 
            variant={connection.connected ? 'default' : 'destructive'} 
            className="text-xs"
          >
            {connection.connected ? (
              <>
                <Wifi className="w-3 h-3 mr-1" />
                Online
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3 mr-1" />
                Offline
              </>
            )}
          </Badge>
          {connection.latency && (
            <span className="text-xs text-text-secondary">
              {connection.latency}ms
            </span>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-3">
        {localMetrics.map((metric, index) => {
          const config = getStatusConfig(metric.status);
          const Icon = metric.icon;
          const StatusIcon = config.icon;
          
          return (
            <motion.div
              key={metric.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                'p-3 rounded-lg border',
                config.bgColor,
                config.borderColor
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Icon className={cn('w-4 h-4', config.color)} />
                  <span className="font-medium text-text-primary">
                    {metric.name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn('text-sm font-mono', config.color)}>
                    {metric.value.toFixed(1)}{metric.unit}
                  </span>
                  <StatusIcon className={cn('w-4 h-4', config.color)} />
                </div>
              </div>
              
              <Progress value={metric.value} className="h-2 mb-2">
                <ProgressTrack>
                  <ProgressIndicator className={config.color.replace('text-', 'bg-')} />
                </ProgressTrack>
              </Progress>
              
              <div className="flex justify-between text-xs text-text-secondary">
                <span>Healthy: &lt;{metric.thresholds.warning}{metric.unit}</span>
                <span>Critical: ≥{metric.thresholds.critical}{metric.unit}</span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Resource Overview */}
      <div className="p-3 rounded-lg border border-border bg-bg-surface">
        <h4 className="font-medium text-text-primary mb-2">Resource Overview</h4>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-2xl font-bold text-primary">
              {localMetrics.find(m => m.name === 'CPU')?.value.toFixed(0) || '0'}%
            </div>
            <div className="text-xs text-text-secondary">CPU Load</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-secondary">
              {localMetrics.find(m => m.name === 'Memory')?.value.toFixed(0) || '0'}%
            </div>
            <div className="text-xs text-text-secondary">Memory</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-success">
              {localMetrics.find(m => m.name === 'Storage')?.value.toFixed(0) || '0'}%
            </div>
            <div className="text-xs text-text-secondary">Storage</div>
          </div>
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-center text-xs text-text-tertiary">
        Last updated: {lastUpdated.toLocaleTimeString()}
      </div>
    </div>
  );
}

// Predefined system metrics configuration
export const DEFAULT_SYSTEM_METRICS: SystemMetric[] = [
  {
    name: 'CPU',
    value: 45,
    unit: '%',
    status: 'healthy',
    icon: Cpu,
    thresholds: {
      warning: 70,
      critical: 90
    }
  },
  {
    name: 'Memory',
    value: 62,
    unit: '%',
    status: 'healthy',
    icon: Database,
    thresholds: {
      warning: 80,
      critical: 95
    }
  },
  {
    name: 'Storage',
    value: 38,
    unit: '%',
    status: 'healthy',
    icon: HardDrive,
    thresholds: {
      warning: 85,
      critical: 95
    }
  }
];