'use client';

import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, 
  Brain, 
  Cog, 
  Rocket, 
  CheckCircle2, 
  AlertCircle, 
  Clock,
  Zap,
  TrendingUp,
  Target,
  Activity,
} from 'lucide-react';
import { useState } from 'react';
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip';
import { Progress } from '@/components/ui/progress';

export type AgentRole = 'orchestrator' | 'executor' | 'validator' | 'deployer';
export type AgentStatus = 'idle' | 'running' | 'success' | 'error' | 'queued';

export interface AgentMetrics {
  tasksCompleted: number;
  avgExecutionTime: string;
  successRate: number;
  totalTokens?: number;
  activeDuration?: string;
}

export interface AgentCardProps {
  agentId: string;
  name?: string;
  role: AgentRole;
  status: AgentStatus;
  currentTask?: string;
  progress?: number; // 0-100
  metrics?: AgentMetrics;
  compact?: boolean;
  className?: string;
  onClick?: () => void;
}

const roleIcons: Record<AgentRole, React.ElementType> = {
  orchestrator: Brain,
  executor: Cog,
  validator: CheckCircle2,
  deployer: Rocket,
};

const roleColors: Record<AgentRole, string> = {
  orchestrator: 'text-violet-400 bg-violet-500/10 border-violet-500/20',
  executor: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  validator: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  deployer: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
};

const statusColors: Record<AgentStatus, string> = {
  idle: 'bg-state-idle',
  running: 'bg-state-running animate-pulse-dot',
  success: 'bg-state-success',
  error: 'bg-state-error',
  queued: 'bg-state-queued',
};

/**
 * AgentCard - Displays real-time agent status and metrics
 * Dense information layout with state visibility
 */
export function AgentCard({
  agentId,
  name,
  role,
  status,
  currentTask,
  progress = 0,
  metrics,
  compact = false,
  className,
  onClick,
}: AgentCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const RoleIcon = roleIcons[role];

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      setShowDetails(!showDetails);
    }
  };

  return (
    <TooltipProvider delayDuration={200}>
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
          compact ? 'p-3' : 'p-4',
          className
        )}
        onClick={handleClick}
      >
        {/* Status indicator bar at top */}
        <div 
          className={cn(
            'absolute top-0 left-0 right-0 h-0.5',
            status === 'running' && 'bg-state-running',
            status === 'success' && 'bg-state-success',
            status === 'error' && 'bg-state-error',
            status === 'idle' && 'bg-state-idle',
            status === 'queued' && 'bg-state-queued'
          )}
        />

        {/* Header section */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            {/* Role icon badge */}
            <div 
              className={cn(
                'flex items-center justify-center w-10 h-10 rounded-lg border shrink-0',
                roleColors[role]
              )}
            >
              <RoleIcon className="w-5 h-5" />
            </div>

            {/* Agent info */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-text-primary truncate">
                  {name || agentId}
                </h3>
                {/* Live status dot */}
                <span 
                  className={cn('w-2 h-2 rounded-full', statusColors[status])}
                  title={`Status: ${status}`}
                />
              </div>
              
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-xs text-text-tertiary font-medium uppercase tracking-wide">
                  {role}
                </span>
                <span className="text-xs text-text-tertiary">•</span>
                <span className="text-xs text-text-tertiary font-mono">
                  {agentId.slice(0, 8)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Current task */}
        {currentTask && (
          <div className="mt-3">
            <div className="flex items-center gap-2 text-xs text-text-secondary mb-1.5">
              <Activity className="w-3 h-3" />
              <span className="font-medium">Current Task</span>
            </div>
            <p className="text-sm text-text-code font-system line-clamp-2">
              {currentTask}
            </p>
          </div>
        )}

        {/* Progress bar for running agents */}
        {status === 'running' && progress > 0 && (
          <div className="mt-3 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-secondary">Progress</span>
              <span className="text-text-code font-mono">{progress}%</span>
            </div>
            <Progress value={progress} className="h-1.5" showAnimation />
          </div>
        )}

        {/* Metrics grid (compact mode) */}
        {metrics && !compact && (
          <div className="mt-4 grid grid-cols-3 gap-2 pt-3 border-t border-border-subtle">
            <MetricItem
              icon={Target}
              label="Completed"
              value={metrics.tasksCompleted.toString()}
            />
            <MetricItem
              icon={Clock}
              label="Avg Time"
              value={metrics.avgExecutionTime}
            />
            <MetricItem
              icon={TrendingUp}
              label="Success Rate"
              value={`${metrics.successRate.toFixed(0)}%`}
              color={metrics.successRate >= 90 ? 'text-state-success' : metrics.successRate >= 70 ? 'text-state-warning' : 'text-state-error'}
            />
          </div>
        )}

        {/* Expanded details */}
        <AnimatePresence>
          {showDetails && metrics && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="mt-4 pt-4 border-t border-border-default overflow-hidden"
            >
              <div className="space-y-3">
                {metrics.totalTokens && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary flex items-center gap-2">
                      <Zap className="w-4 h-4" />
                      Total Tokens
                    </span>
                    <span className="text-text-code font-mono">
                      {metrics.totalTokens.toLocaleString()}
                    </span>
                  </div>
                )}
                
                {metrics.activeDuration && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Active Duration
                    </span>
                    <span className="text-text-code font-mono">
                      {metrics.activeDuration}
                    </span>
                  </div>
                )}

                {/* Success rate visualization */}
                <div className="pt-2">
                  <div className="flex items-center justify-between text-sm mb-1.5">
                    <span className="text-text-secondary">Success Rate</span>
                    <span className={cn(
                      'font-mono font-medium',
                      metrics.successRate >= 90 ? 'text-state-success' : 
                      metrics.successRate >= 70 ? 'text-state-warning' : 'text-state-error'
                    )}>
                      {metrics.successRate.toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-bg-base overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${metrics.successRate}%` }}
                      transition={{ duration: 0.5, delay: 0.2 }}
                      className={cn(
                        'h-full rounded-full',
                        metrics.successRate >= 90 ? 'bg-state-success' : 
                        metrics.successRate >= 70 ? 'bg-state-warning' : 'bg-state-error'
                      )}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error state indicator */}
        {status === 'error' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 p-2 rounded-md bg-state-error-dim border border-state-error/20 flex items-center gap-2"
          >
            <AlertCircle className="w-4 h-4 text-state-error shrink-0" />
            <span className="text-sm text-state-error">Agent encountered an error</span>
          </motion.div>
        )}
      </motion.div>
    </TooltipProvider>
  );
}

/**
 * MetricItem - Small metric display component
 */
function MetricItem({ 
  icon: Icon, 
  label, 
  value, 
  color = 'text-text-primary' 
}: { 
  icon: React.ElementType;
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1.5 mb-0.5">
            <Icon className="w-3.5 h-3.5 text-text-tertiary" />
          </div>
          <div className={cn('text-sm font-semibold font-mono', color)}>
            {value}
          </div>
          <div className="text-xs text-text-tertiary">{label}</div>
        </div>
      </TooltipTrigger>
      <TooltipContent>
        <p>{label}: {value}</p>
      </TooltipContent>
    </Tooltip>
  );
}

/**
 * AgentGrid - Grid layout for multiple agent cards
 */
export interface AgentGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4 | 'auto';
  className?: string;
}

export function AgentGrid({ 
  children, 
  columns = 'auto',
  className 
}: AgentGridProps) {
  return (
    <div 
      className={cn(
        'grid gap-4',
        columns === 'auto' && 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
        typeof columns === 'number' && `grid-cols-${columns}`,
        className
      )}
    >
      {children}
    </div>
  );
}
