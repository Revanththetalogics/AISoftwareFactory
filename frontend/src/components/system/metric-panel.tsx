'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Activity,
  Zap,
  Cpu,
  HardDrive,
  Network,
  Clock,
} from 'lucide-react';
import { useState } from 'react';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';

export interface MetricData {
  id: string;
  label: string;
  value: string | number;
  delta?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  sparkline?: number[];
  unit?: string;
  status?: 'normal' | 'warning' | 'critical';
  icon?: React.ElementType;
}

export interface MetricPanelProps {
  metrics: MetricData[];
  variant?: 'compact' | 'expanded' | 'graph';
  timeRange?: '1h' | '24h' | '7d' | '30d';
  className?: string;
  onMetricClick?: (metricId: string) => void;
}

const statusColors = {
  normal: 'text-state-success',
  warning: 'text-state-warning',
  critical: 'text-state-error',
};

const statusBg = {
  normal: 'bg-state-success-dim',
  warning: 'bg-state-warning-dim',
  critical: 'bg-state-error-dim',
};

/**
 * MetricPanel - Dashboard KPI display with charts and trends
 * Supports multiple visualization modes
 */
export function MetricPanel({
  metrics,
  variant = 'expanded',
  timeRange = '24h',
  className,
  onMetricClick,
}: MetricPanelProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className={cn(
      'grid gap-4',
      variant === 'compact' && 'grid-cols-2 lg:grid-cols-4',
      variant === 'expanded' && 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
      variant === 'graph' && 'grid-cols-1 lg:grid-cols-2',
      className
    )}>
      {metrics.map((metric) => (
        <MetricCard
          key={metric.id}
          metric={metric}
          variant={variant}
          onClick={() => onMetricClick?.(metric.id)}
        />
      ))}
    </div>
  );
}

interface MetricCardProps {
  metric: MetricData;
  variant: string;
  onClick?: () => void;
}

function MetricCard({ metric, variant, onClick }: MetricCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const Icon = metric.icon || Activity;

  // Prepare sparkline data
  const chartData = metric.sparkline?.map((value, index) => ({
    index,
    value,
  }));

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      className={cn(
        'relative overflow-hidden rounded-lg border transition-all cursor-pointer',
        'bg-bg-panel hover:bg-bg-elevated',
        'border-border-default hover:border-emphasis',
        variant === 'compact' && 'p-3',
        variant !== 'compact' && 'p-4'
      )}
    >
      {/* Status indicator */}
      {metric.status && (
        <div className={cn(
          'absolute top-0 right-0 w-2 h-2 m-3 rounded-full',
          statusColors[metric.status]
        )} />
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-bg-base border border-border-subtle">
            <Icon className="w-4 h-4 text-text-secondary" />
          </div>
          <span className="text-sm font-medium text-text-secondary">
            {metric.label}
          </span>
        </div>

        {/* Delta indicator */}
        {metric.delta && (
          <div className={cn(
            'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium',
            metric.delta.direction === 'up' && 'text-state-success bg-state-success-dim',
            metric.delta.direction === 'down' && 'text-state-error bg-state-error-dim',
            metric.delta.direction === 'neutral' && 'text-text-tertiary bg-bg-base'
          )}>
            {metric.delta.direction === 'up' && <TrendingUp className="w-3 h-3" />}
            {metric.delta.direction === 'down' && <TrendingDown className="w-3 h-3" />}
            {metric.delta.direction === 'neutral' && <Minus className="w-3 h-3" />}
            {Math.abs(metric.delta.value).toFixed(1)}%
          </div>
        )}
      </div>

      {/* Value */}
      <div className="mb-3">
        <div className="flex items-baseline gap-1">
          <span className="text-2xl font-bold text-text-primary font-mono">
            {typeof metric.value === 'number' 
              ? metric.value.toLocaleString() 
              : metric.value}
          </span>
          {metric.unit && (
            <span className="text-sm text-text-tertiary">
              {metric.unit}
            </span>
          )}
        </div>
      </div>

      {/* Sparkline chart */}
      {(variant === 'expanded' || variant === 'graph') && chartData && chartData.length > 0 && (
        <div className="h-16 -mx-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id={`gradient-${metric.id}`} x1="0" y1="0" x2="0" y2="1">
                  <stop 
                    offset="0%" 
                    stopColor="var(--state-running)" 
                    stopOpacity={0.3} 
                  />
                  <stop 
                    offset="100%" 
                    stopColor="var(--state-running)" 
                    stopOpacity={0} 
                  />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke="var(--state-running)"
                strokeWidth={2}
                fill={`url(#gradient-${metric.id})`}
                isAnimationActive={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="rounded bg-bg-elevated border border-border-default px-2 py-1 text-xs font-mono">
                        {payload[0].value}
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Compact sparkline dots */}
      {variant === 'compact' && chartData && chartData.length > 0 && (
        <div className="flex items-end gap-0.5 h-8 mt-2">
          {chartData.slice(-20).map((point, i) => (
            <div
              key={i}
              className="flex-1 bg-state-running/50 rounded-t-sm"
              style={{
                height: `${(point.value / Math.max(...chartData.map(d => d.value))) * 100}%`,
              }}
            />
          ))}
        </div>
      )}

      {/* Time range badge */}
      {variant !== 'compact' && (
        <div className="mt-3 pt-3 border-t border-border-subtle flex items-center justify-between text-xs text-text-tertiary">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Last {timeRange}
          </span>
          {isHovered && (
            <span className="text-text-secondary hover:text-text-primary transition-colors">
              View details →
            </span>
          )}
        </div>
      )}
    </motion.div>
  );
}

/**
 * ResourceGauge - Visual resource utilization gauge
 */
export function ResourceGauge({
  label,
  value,
  max = 100,
  unit = '%',
  status = 'normal',
  icon,
}: {
  label: string;
  value: number;
  max?: number;
  unit?: string;
  status?: 'normal' | 'warning' | 'critical';
  icon?: React.ElementType;
}) {
  const percentage = (value / max) * 100;
  const Icon = icon || Activity;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-text-secondary" />
          <span className="text-sm font-medium text-text-secondary">{label}</span>
        </div>
        <span className={cn('text-sm font-mono font-semibold', statusColors[status])}>
          {value.toFixed(1)}{unit}
        </span>
      </div>
      
      {/* Progress bar */}
      <div className="h-2 rounded-full bg-bg-base overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5 }}
          className={cn(
            'h-full rounded-full',
            status === 'normal' && 'bg-state-success',
            status === 'warning' && 'bg-state-warning',
            status === 'critical' && 'bg-state-error'
          )}
        />
      </div>
    </div>
  );
}

/**
 * SystemMetrics - Pre-configured system metrics panel
 */
export function SystemMetrics({
  cpu,
  memory,
  network,
  disk,
  className,
}: {
  cpu?: number;
  memory?: number;
  network?: number;
  disk?: number;
  className?: string;
}) {
  const generateSparkline = () => Array.from({ length: 24 }, () => Math.random() * 100);
  
  const metrics: MetricData[] = [
    {
      id: 'cpu',
      label: 'CPU Usage',
      value: cpu || 0,
      unit: '%',
      icon: Cpu,
      status: cpu! > 90 ? 'critical' : cpu! > 70 ? 'warning' : 'normal',
      sparkline: generateSparkline(),
    },
    {
      id: 'memory',
      label: 'Memory',
      value: memory || 0,
      unit: '%',
      icon: HardDrive,
      status: memory! > 90 ? 'critical' : memory! > 70 ? 'warning' : 'normal',
      sparkline: generateSparkline(),
    },
    {
      id: 'network',
      label: 'Network I/O',
      value: network || 0,
      unit: 'MB/s',
      icon: Network,
      sparkline: generateSparkline(),
    },
    {
      id: 'disk',
      label: 'Disk Usage',
      value: disk || 0,
      unit: '%',
      icon: HardDrive,
      status: disk! > 90 ? 'critical' : disk! > 70 ? 'warning' : 'normal',
      sparkline: generateSparkline(),
    },
  ];

  return (
    <MetricPanel
      metrics={metrics}
      variant="expanded"
      className={className}
    />
  );
}
