'use client';

import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  GitBranch, 
  Play, 
  CheckCircle2, 
  XCircle, 
  MinusCircle,
  AlertTriangle,
  Clock,
  Zap,
} from 'lucide-react';
import { useState } from 'react';

export type WorkflowNodeType = 'condition' | 'action' | 'parallel' | 'terminal';
export type WorkflowNodeState = 'pending' | 'active' | 'completed' | 'failed' | 'skipped';

export interface WorkflowNodeProps {
  nodeId: string;
  nodeType: WorkflowNodeType;
  state: WorkflowNodeState;
  label: string;
  description?: string;
  executionTime?: string;
  error?: string;
  metadata?: Record<string, string>;
  onSelect?: (nodeId: string) => void;
  compact?: boolean;
}

const nodeTypeIcons: Record<WorkflowNodeType, React.ElementType> = {
  condition: GitBranch,
  action: Play,
  parallel: Zap,
  terminal: CheckCircle2,
};

const nodeStateStyles: Record<WorkflowNodeState, {
  border: string;
  bg: string;
  text: string;
  icon: string;
}> = {
  pending: {
    border: 'border-border-subtle',
    bg: 'bg-bg-panel',
    text: 'text-text-tertiary',
    icon: 'text-text-tertiary',
  },
  active: {
    border: 'border-state-running glow-running',
    bg: 'bg-state-running-dim',
    text: 'text-state-running',
    icon: 'text-state-running animate-pulse',
  },
  completed: {
    border: 'border-state-success/30',
    bg: 'bg-state-success-dim',
    text: 'text-state-success',
    icon: 'text-state-success',
  },
  failed: {
    border: 'border-state-error/30',
    bg: 'bg-state-error-dim',
    text: 'text-state-error',
    icon: 'text-state-error',
  },
  skipped: {
    border: 'border-border-subtle',
    bg: 'bg-bg-panel opacity-50',
    text: 'text-text-tertiary line-through',
    icon: 'text-text-tertiary',
  },
};

const stateIcons: Record<WorkflowNodeState, React.ElementType> = {
  pending: Clock,
  active: Zap,
  completed: CheckCircle2,
  failed: XCircle,
  skipped: MinusCircle,
};

/**
 * WorkflowNode - Visual representation of a workflow step
 * State-driven styling with animated transitions
 */
export function WorkflowNode({
  nodeId,
  nodeType,
  state,
  label,
  description,
  executionTime,
  error,
  metadata,
  onSelect,
  compact = false,
}: WorkflowNodeProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  
  const NodeTypeIcon = nodeTypeIcons[nodeType];
  const StateIcon = stateIcons[state];
  const styles = nodeStateStyles[state];

  const handleClick = () => {
    if (onSelect) {
      onSelect(nodeId);
    } else {
      setShowDetails(!showDetails);
    }
  };

  // Shape varies by node type
  const shapeClasses = {
    condition: 'rounded-lg',
    action: 'rounded-md',
    parallel: 'rounded-xl',
    terminal: 'rounded-full',
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'relative cursor-pointer transition-all duration-200',
        'hover:scale-[1.02] hover:shadow-lg',
        compact ? 'w-48' : 'w-64'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      {/* Connection points */}
      <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-bg-elevated border-2 border-border-default z-10" />
      <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-bg-elevated border-2 border-border-default z-10" />
      
      {/* Active edge indicators */}
      {state === 'active' && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-state-running"
          />
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-state-running"
          />
        </>
      )}

      {/* Main node card */}
      <div
        className={cn(
          'relative overflow-hidden border-2 transition-all',
          shapeClasses[nodeType],
          styles.border,
          styles.bg,
          compact ? 'p-3' : 'p-4'
        )}
      >
        {/* Node header */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {/* Type icon */}
            <div className={cn('shrink-0', styles.icon)}>
              <NodeTypeIcon className={compact ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
            </div>
            
            {/* Label */}
            <div className="flex-1 min-w-0">
              <h4 className={cn(
                'font-semibold truncate',
                compact ? 'text-xs' : 'text-sm',
                styles.text
              )}>
                {label}
              </h4>
              
              {!compact && description && (
                <p className="text-xs text-text-secondary mt-0.5 truncate">
                  {description}
                </p>
              )}
            </div>
          </div>

          {/* State indicator */}
          <motion.div
            animate={state === 'active' ? { rotate: 360 } : {}}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className={cn('shrink-0', styles.icon)}
          >
            <StateIcon className={compact ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
          </motion.div>
        </div>

        {/* Execution time badge */}
        {executionTime && state !== 'pending' && (
          <div className={cn(
            'mt-2 inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-mono',
            'bg-bg-base/50 border border-border-subtle',
            styles.text
          )}>
            <Clock className="w-3 h-3" />
            <span>{executionTime}</span>
          </div>
        )}

        {/* Metadata tags */}
        {metadata && !compact && Object.entries(metadata).length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {Object.entries(metadata).map(([key, value]) => (
              <span
                key={key}
                className={cn(
                  'inline-flex items-center px-1.5 py-0.5 rounded text-xs',
                  'bg-bg-base border border-border-subtle',
                  'text-text-tertiary'
                )}
              >
                {key}: {value}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Error details popover */}
      <AnimatePresence>
        {(showDetails || isHovered) && error && state === 'failed' && (
          <motion.div
            initial={{ opacity: 0, y: 10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: 10, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-2 overflow-hidden"
          >
            <div className="p-3 rounded-md bg-state-error-dim border border-state-error/20">
              <div className="flex items-center gap-2 mb-1.5">
                <AlertTriangle className="w-4 h-4 text-state-error" />
                <span className="text-sm font-semibold text-state-error">Error</span>
              </div>
              <p className="text-xs text-state-error/80 font-system">
                {error}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/**
 * WorkflowEdge - Connection line between nodes
 */
export interface WorkflowEdgeProps {
  active?: boolean;
  completed?: boolean;
  failed?: boolean;
  animated?: boolean;
}

export function WorkflowEdge({ 
  active = false, 
  completed = false,
  failed = false,
  animated = true 
}: WorkflowEdgeProps) {
  return (
    <svg className="w-full h-8 shrink-0" preserveAspectRatio="none">
      <defs>
        <linearGradient id={`gradient-${active}-${completed}-${failed}`} x1="0%" y1="0%" x2="100%" y2="0%">
          {active && (
            <>
              <stop offset="0%" stopColor="var(--state-running)" stopOpacity="0.8" />
              <stop offset="100%" stopColor="var(--state-running)" stopOpacity="0.2" />
            </>
          )}
          {completed && (
            <>
              <stop offset="0%" stopColor="var(--state-success)" stopOpacity="0.8" />
              <stop offset="100%" stopColor="var(--state-success)" stopOpacity="0.2" />
            </>
          )}
          {failed && (
            <>
              <stop offset="0%" stopColor="var(--state-error)" stopOpacity="0.8" />
              <stop offset="100%" stopColor="var(--state-error)" stopOpacity="0.2" />
            </>
          )}
          {!active && !completed && !failed && (
            <>
              <stop offset="0%" stopColor="var(--border-default)" stopOpacity="1" />
              <stop offset="100%" stopColor="var(--border-default)" stopOpacity="0.5" />
            </>
          )}
        </linearGradient>
      </defs>
      
      {/* Edge line */}
      <line
        x1="0"
        y1="50%"
        x2="100%"
        y2="50%"
        stroke={`url(#gradient-${active}-${completed}-${failed})`}
        strokeWidth="2"
        strokeDasharray={animated && active ? "5,5" : "none"}
      >
        {animated && active && (
          <animate
            attributeName="stroke-dashoffset"
            from="10"
            to="0"
            dur="1s"
            repeatCount="indefinite"
          />
        )}
      </line>
      
      {/* Arrow head */}
      <polygon
        points="100%,50% 95%,47% 95%,53%"
        fill={`var(${active ? '--state-running' : completed ? '--state-success' : failed ? '--state-error' : '--border-default'})`}
      />
    </svg>
  );
}

/**
 * WorkflowCanvas - Container for workflow visualization
 */
export interface WorkflowCanvasProps {
  children: React.ReactNode;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

export function WorkflowCanvas({
  children,
  className,
  orientation = 'horizontal',
}: WorkflowCanvasProps) {
  return (
    <div
      className={cn(
        'relative p-8 overflow-auto',
        'bg-bg-base border border-border-default rounded-lg',
        orientation === 'horizontal' ? 'flex-row' : 'flex-col',
        className
      )}
    >
      <div className={cn(
        'flex gap-8',
        orientation === 'horizontal' ? 'flex-row items-center' : 'flex-col items-stretch'
      )}>
        {children}
      </div>
    </div>
  );
}
