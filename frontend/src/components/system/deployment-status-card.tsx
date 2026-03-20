'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { 
  Server, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  Clock,
  GitCommit,
  ExternalLink,
  Activity,
  Cpu,
  HardDrive,
  Network,
  Timer,
} from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip';

export type DeploymentEnvironment = 'development' | 'staging' | 'production';
export type DeploymentStatus = 'building' | 'deploying' | 'running' | 'failed' | 'rollback';

export interface HealthCheck {
  name: string;
  status: 'passing' | 'failing' | 'unknown';
  lastCheck: Date;
  responseTime?: number;
}

export interface DeploymentMetrics {
  cpu: number;
  memory: number;
  requests: number;
  latency: number;
  errorRate?: number;
}

export interface DeploymentStatusCardProps {
  environment: DeploymentEnvironment;
  status: DeploymentStatus;
  version: string;
  commitHash: string;
  deployedAt?: Date;
  healthChecks?: HealthCheck[];
  metrics?: DeploymentMetrics;
  buildDuration?: string;
  buildLogs?: string;
  className?: string;
  onClick?: () => void;
}

const envColors: Record<DeploymentEnvironment, string> = {
  development: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  staging: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  production: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
};

const statusIcons: Record<DeploymentStatus, React.ElementType> = {
  building: Clock,
  deploying: Activity,
  running: CheckCircle2,
  failed: XCircle,
  rollback: AlertCircle,
};

const statusColors: Record<DeploymentStatus, string> = {
  building: 'text-state-running',
  deploying: 'text-state-running',
  running: 'text-state-success',
  failed: 'text-state-error',
  rollback: 'text-state-warning',
};

/**
 * DeploymentStatusCard - Real-time deployment monitoring
 * Shows environment status, health checks, and resource metrics
 */
export function DeploymentStatusCard({
  environment,
  status,
  version,
  commitHash,
  deployedAt,
  healthChecks = [],
  metrics,
  buildDuration,
  buildLogs,
  className,
  onClick,
}: DeploymentStatusCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const StatusIcon = statusIcons[status];

  const envLabel = {
    development: 'DEV',
    staging: 'STAGING',
    production: 'PROD',
  };

  return (
    <TooltipProvider>
      <motion.div
        layout
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        className={cn(
          'relative overflow-hidden rounded-lg border transition-all cursor-pointer',
          'bg-bg-panel hover:bg-bg-elevated',
          'border-border-default hover:border-emphasis',
          className
        )}
        onClick={() => {
          setShowDetails(!showDetails);
          onClick?.();
        }}
      >
        {/* Status bar at top */}
        <div className={cn(
          'absolute top-0 left-0 right-0 h-1',
          status === 'running' && 'bg-state-success',
          status === 'building' && 'bg-state-running animate-pulse',
          status === 'deploying' && 'bg-state-running animate-pulse',
          status === 'failed' && 'bg-state-error',
          status === 'rollback' && 'bg-state-warning'
        )} />

        <div className="p-4">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              {/* Environment badge */}
              <div className={cn(
                'px-2 py-1 rounded text-xs font-bold border',
                envColors[environment]
              )}>
                {envLabel[environment]}
              </div>

              {/* Version info */}
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-text-primary">
                    v{version}
                  </h3>
                  <Badge variant="outline" className="font-mono text-xs">
                    <GitCommit className="w-3 h-3 mr-1" />
                    {commitHash.slice(0, 7)}
                  </Badge>
                </div>
                
                {deployedAt && (
                  <p className="text-xs text-text-tertiary mt-0.5">
                    Deployed: {deployedAt.toLocaleString()}
                  </p>
                )}
              </div>
            </div>

            {/* Status indicator */}
            <div className="flex items-center gap-2">
              <motion.div
                animate={status === 'building' || status === 'deploying' 
                  ? { rotate: 360 } 
                  : {}
                }
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className={cn('shrink-0', statusColors[status])}
              >
                <StatusIcon className="w-5 h-5" />
              </motion.div>
              
              <span className={cn(
                'text-sm font-semibold capitalize',
                statusColors[status]
              )}>
                {status}
              </span>
            </div>
          </div>

          {/* Health checks grid */}
          {healthChecks.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-text-secondary">
                  Health Checks
                </span>
                <span className="text-xs text-text-tertiary">
                  {healthChecks.filter(h => h.status === 'passing').length} / {healthChecks.length} passing
                </span>
              </div>
              
              <div className="grid grid-cols-3 gap-2">
                {healthChecks.map((check, index) => (
                  <Tooltip key={index}>
                    <TooltipTrigger>
                      <div
                        className={cn(
                          'flex items-center gap-1.5 px-2 py-1.5 rounded border text-xs',
                          check.status === 'passing' && 'bg-state-success-dim border-state-success/30 text-state-success',
                          check.status === 'failing' && 'bg-state-error-dim border-state-error/30 text-state-error',
                          check.status === 'unknown' && 'bg-bg-base border-border-subtle text-text-tertiary'
                        )}
                      >
                        <div
                          className={cn(
                            'w-1.5 h-1.5 rounded-full',
                            check.status === 'passing' && 'bg-state-success',
                            check.status === 'failing' && 'bg-state-error',
                            check.status === 'unknown' && 'bg-state-idle'
                          )}
                        />
                        <span className="truncate">{check.name}</span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <div className="space-y-1">
                        <p className="font-medium">{check.name}</p>
                        <p className="text-xs text-text-tertiary">
                          Status: {check.status}
                        </p>
                        <p className="text-xs text-text-tertiary">
                          Last check: {check.lastCheck.toLocaleString()}
                        </p>
                        {check.responseTime && (
                          <p className="text-xs text-text-tertiary">
                            Response time: {check.responseTime}ms
                          </p>
                        )}
                      </div>
                    </TooltipContent>
                  </Tooltip>
                ))}
              </div>
            </div>
          )}

          {/* Resource metrics */}
          {metrics && (
            <div className="grid grid-cols-2 gap-3">
              <ResourceMetric
                icon={Cpu}
                label="CPU"
                value={metrics.cpu}
                unit="%"
                status={metrics.cpu > 90 ? 'critical' : metrics.cpu > 70 ? 'warning' : 'normal'}
              />
              <ResourceMetric
                icon={HardDrive}
                label="Memory"
                value={metrics.memory}
                unit="%"
                status={metrics.memory > 90 ? 'critical' : metrics.memory > 70 ? 'warning' : 'normal'}
              />
              <ResourceMetric
                icon={Network}
                label="Requests"
                value={metrics.requests}
                unit="/s"
              />
              <ResourceMetric
                icon={Timer}
                label="Latency"
                value={metrics.latency}
                unit="ms"
                status={metrics.latency > 500 ? 'critical' : metrics.latency > 200 ? 'warning' : 'normal'}
              />
            </div>
          )}

          {/* Build duration */}
          {buildDuration && (
            <div className="mt-4 pt-4 border-t border-border-subtle">
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-secondary flex items-center gap-1.5">
                  <Clock className="w-3 h-3" />
                  Build Time
                </span>
                <span className="font-mono text-text-code">{buildDuration}</span>
              </div>
            </div>
          )}

          {/* Expanded details */}
          {showDetails && buildLogs && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-4 pt-4 border-t border-border-default"
            >
              <div className="text-xs font-system bg-bg-code rounded p-3 max-h-32 overflow-auto">
                <pre className="whitespace-pre-wrap text-text-code">
                  {buildLogs}
                </pre>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </TooltipProvider>
  );
}

interface ResourceMetricProps {
  icon: React.ElementType;
  label: string;
  value: number;
  unit: string;
  status?: 'normal' | 'warning' | 'critical';
}

function ResourceMetric({ icon: Icon, label, value, unit, status = 'normal' }: ResourceMetricProps) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1.5 text-xs text-text-secondary">
        <Icon className="w-3 h-3" />
        <span>{label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span className={cn(
          'text-lg font-bold font-mono',
          status === 'normal' && 'text-text-primary',
          status === 'warning' && 'text-state-warning',
          status === 'critical' && 'text-state-error'
        )}>
          {value.toFixed(0)}
        </span>
        <span className="text-xs text-text-tertiary">{unit}</span>
      </div>
    </div>
  );
}

/**
 * DeploymentGrid - Grid layout for multiple deployment cards
 */
export function DeploymentGrid({
  children,
  columns = 3,
  className,
}: {
  children: React.ReactNode;
  columns?: 1 | 2 | 3;
  className?: string;
}) {
  return (
    <div className={cn(
      'grid gap-4',
      columns === 1 && 'grid-cols-1',
      columns === 2 && 'grid-cols-1 md:grid-cols-2',
      columns === 3 && 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
      className
    )}>
      {children}
    </div>
  );
}
