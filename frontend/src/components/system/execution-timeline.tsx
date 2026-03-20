'use client';

import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2, 
  Clock, 
  Play, 
  XCircle,
  ChevronRight,
} from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';

export interface TimelinePhase {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  duration?: string;
  steps?: Array<{
    name: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    timestamp: Date;
    details?: string;
  }>;
}

export interface ExecutionTimelineProps {
  phases: TimelinePhase[];
  collapsed?: boolean;
  autoScroll?: boolean;
  compact?: boolean;
  className?: string;
}

const statusIcons: Record<string, React.ElementType> = {
  pending: Clock,
  running: Play,
  completed: CheckCircle2,
  failed: XCircle,
};

const statusColors: Record<string, string> = {
  pending: 'text-text-tertiary',
  running: 'text-state-running',
  completed: 'text-state-success',
  failed: 'text-state-error',
};

const statusBg: Record<string, string> = {
  pending: 'bg-bg-panel border-border-subtle',
  running: 'bg-state-running-dim border-state-running/30',
  completed: 'bg-state-success-dim border-state-success/30',
  failed: 'bg-state-error-dim border-state-error/30',
};

/**
 * ExecutionTimeline - Visual timeline of execution phases
 * Shows phase progression with expandable step details
 */
export function ExecutionTimeline({
  phases,
  collapsed = false,
  autoScroll = true,
  compact = false,
  className,
}: ExecutionTimelineProps) {
  const [expandedPhases, setExpandedPhases] = useState<Set<string>>(new Set());
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to running phase
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      const runningPhase = phases.findIndex(p => p.status === 'running');
      if (runningPhase >= 0) {
        const element = scrollRef.current.children[runningPhase];
        element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [phases, autoScroll]);

  const togglePhase = (phaseId: string) => {
    const newExpanded = new Set(expandedPhases);
    if (newExpanded.has(phaseId)) {
      newExpanded.delete(phaseId);
    } else {
      newExpanded.add(phaseId);
    }
    setExpandedPhases(newExpanded);
  };

  if (collapsed) {
    return (
      <div className={cn('flex items-center gap-1', className)}>
        {phases.map((phase, index) => (
          <div key={phase.id} className="flex items-center">
            <div className={`w-2 h-2 rounded-full ${
              phase.status === 'completed' ? 'bg-state-success' :
              phase.status === 'running' ? 'bg-state-running animate-pulse' :
              'bg-border-default'
            }`} />
            {index < phases.length - 1 && (
              <div className="w-4 h-px bg-border-default" />
            )}
          </div>
        ))}
      </div>
    );
  }

  return (
    <ScrollArea ref={scrollRef} className={cn('max-h-[600px]', className)}>
      <div className="space-y-2 p-4">
        {phases.map((phase, index) => (
          <TimelinePhaseItem
            key={phase.id}
            phase={phase}
            isExpanded={expandedPhases.has(phase.id)}
            onToggle={() => togglePhase(phase.id)}
            compact={compact}
            showConnector={index < phases.length - 1}
          />
        ))}
      </div>
    </ScrollArea>
  );
}

interface PhaseItemProps {
  phase: TimelinePhase;
  isExpanded: boolean;
  onToggle: () => void;
  compact: boolean;
  showConnector: boolean;
}

function TimelinePhaseItem({
  phase,
  isExpanded,
  onToggle,
  compact,
  showConnector,
}: PhaseItemProps) {
  const Icon = statusIcons[phase.status];
  const hasSteps = phase.steps && phase.steps.length > 0;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2 }}
      className="relative"
    >
      {/* Phase card */}
      <div
        className={cn(
          'rounded-lg border transition-all cursor-pointer',
          'hover:border-emphasis',
          statusBg[phase.status],
          compact ? 'p-2' : 'p-3'
        )}
        onClick={onToggle}
      >
        <div className="flex items-center gap-3">
          {/* Expand/collapse chevron */}
          {hasSteps && (
            <motion.div
              animate={{ rotate: isExpanded ? 90 : 0 }}
              transition={{ duration: 0.2 }}
              className="text-text-tertiary"
            >
              <ChevronRight className="w-4 h-4" />
            </motion.div>
          )}

          {/* Status icon */}
          <motion.div
            animate={phase.status === 'running' ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity }}
            className={cn('shrink-0', statusColors[phase.status])}
          >
            <Icon className={compact ? 'w-4 h-4' : 'w-5 h-5'} />
          </motion.div>

          {/* Phase info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h4 className={cn(
                'font-semibold',
                compact ? 'text-sm' : 'text-base',
                statusColors[phase.status]
              )}>
                {phase.name}
              </h4>
              
              {/* Duration badge */}
              {phase.duration && (
                <span className={cn(
                  'inline-flex items-center px-2 py-0.5 rounded text-xs font-mono',
                  'bg-bg-base/50 border border-border-subtle',
                  'text-text-secondary'
                )}>
                  <Clock className="w-3 h-3 mr-1" />
                  {phase.duration}
                </span>
              )}
            </div>

            {!compact && phase.startTime && (
              <p className="text-xs text-text-tertiary mt-0.5 font-mono">
                Started: {phase.startTime.toLocaleTimeString()}
              </p>
            )}
          </div>

          {/* Step count */}
          {hasSteps && !compact && (
            <div className="text-xs text-text-tertiary">
              {phase.steps!.filter(s => s.status === 'completed').length} / {phase.steps!.length} steps
            </div>
          )}
        </div>
      </div>

      {/* Expanded steps */}
      <AnimatePresence>
        {isExpanded && hasSteps && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden ml-8 mt-2"
          >
            <div className="border-l-2 border-border-subtle pl-4 space-y-1">
              {phase.steps!.map((step, index) => (
                <StepItem key={index} step={step} compact={compact} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Connector line to next phase */}
      {showConnector && (
        <div className="absolute left-6 top-full w-px h-4 bg-border-subtle" />
      )}
    </motion.div>
  );
}

interface StepItemProps {
  step: {
    name: string;
    status: string;
    timestamp: Date;
    details?: string;
  };
  compact: boolean;
}

function StepItem({ step, compact }: StepItemProps) {
  const Icon = statusIcons[step.status];
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={cn(
        'flex items-start gap-2 py-1.5',
        'hover:bg-bg-hover rounded px-2 -mx-2 transition-colors'
      )}
    >
      <Icon className={cn(
        'w-3.5 h-3.5 shrink-0 mt-0.5',
        statusColors[step.status]
      )} />
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className={cn(
            'text-sm font-medium',
            compact ? 'text-text-code' : 'text-text-primary'
          )}>
            {step.name}
          </span>
          <span className="text-xs text-text-tertiary font-mono whitespace-nowrap">
            {step.timestamp.toLocaleTimeString()}
          </span>
        </div>
        
        {step.details && (
          <p className="text-xs text-text-secondary mt-0.5">
            {step.details}
          </p>
        )}
      </div>
    </motion.div>
  );
}

/**
 * MiniTimeline - Compact timeline view for cards/dashboards
 */
export function MiniTimeline({
  phases,
  className,
}: {
  phases: TimelinePhase[];
  className?: string;
}) {
  return (
    <div className={cn('flex items-center gap-1.5', className)}>
      {phases.map((phase, index) => (
        <div key={phase.id} className="flex items-center">
          <div
            className={cn(
              'w-2.5 h-2.5 rounded-full',
              phase.status === 'running' && 'bg-state-running animate-pulse',
              phase.status === 'completed' && 'bg-state-success',
              phase.status === 'failed' && 'bg-state-error',
              phase.status === 'pending' && 'bg-state-idle'
            )}
            title={`${phase.name}: ${phase.status}`}
          />
          {index < phases.length - 1 && (
            <div className="w-3 h-px bg-border-default" />
          )}
        </div>
      ))}
    </div>
  );
}
