'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export type WorkflowStepStatus = 'completed' | 'running' | 'pending' | 'failed';

export interface WorkflowStep {
  id: string;
  title: string;
  status: WorkflowStepStatus;
  duration: string;
  description?: string;
  logs?: string[];
}

interface WorkflowPanelProps {
  steps: WorkflowStep[];
  className?: string;
  expandedStepId?: string;
  onStepToggle?: (stepId: string) => void;
  onStepClick?: (step: WorkflowStep) => void;
}

const getStatusConfig = (status: WorkflowStepStatus) => {
  switch (status) {
    case 'completed':
      return {
        bgColor: 'bg-success/10',
        borderColor: 'border-success',
        statusColor: 'bg-success',
        textColor: 'text-success',
      };
    case 'running':
      return {
        bgColor: 'bg-primary/10',
        borderColor: 'border-primary',
        statusColor: 'bg-primary',
        textColor: 'text-primary',
        glowClass: 'glow-primary',
        animate: true,
      };
    case 'pending':
      return {
        bgColor: 'bg-bg-surface',
        borderColor: 'border-border',
        statusColor: 'bg-gray-500',
        textColor: 'text-text-secondary',
      };
    case 'failed':
      return {
        bgColor: 'bg-error/10',
        borderColor: 'border-error',
        statusColor: 'bg-error',
        textColor: 'text-error',
      };
  }
};

export function WorkflowPanel({ 
  steps, 
  className,
  expandedStepId,
  onStepToggle,
  onStepClick 
}: WorkflowPanelProps) {
  const handleStepClick = (step: WorkflowStep) => {
    onStepClick?.(step);
    onStepToggle?.(step.id);
  };

  const isExpandable = onStepToggle !== undefined;

  return (
    <div className={cn('space-y-3', className)}>
      {steps.map((step, index) => {
        const config = getStatusConfig(step.status);
        const isExpanded = expandedStepId === step.id;
        const isClickable = onStepClick !== undefined;
        
        return (
          <motion.div
            key={step.id}
            className={cn(
              'rounded-lg border transition-all duration-300 overflow-hidden',
              config.bgColor,
              config.borderColor,
              config.glowClass,
              isClickable && 'cursor-pointer'
            )}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={isClickable ? { scale: 1.01 } : {}}
            whileTap={isClickable ? { scale: 0.99 } : {}}
          >
            <div 
              className="p-3"
              onClick={() => handleStepClick(step)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'w-2 h-2 rounded-full',
                    config.statusColor,
                    config.animate && 'animate-pulse'
                  )} />
                  <span className="text-sm font-medium text-text-primary truncate">
                    {step.title}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn(
                    'text-xs',
                    config.textColor
                  )}>
                    {step.duration}
                  </span>
                  {isExpandable && (
                    <svg 
                      className={cn(
                        'w-4 h-4 transition-transform duration-200',
                        isExpanded && 'rotate-180'
                      )}
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                </div>
              </div>
              
              {step.description && (
                <p className="text-xs text-text-secondary mt-1 ml-5">
                  {step.description}
                </p>
              )}
            </div>
            
            {isExpanded && step.logs && step.logs.length > 0 && (
              <div className="border-t border-border bg-bg-surface/50 p-3">
                <div className="font-mono-system text-xs space-y-1">
                  {step.logs.map((log, logIndex) => (
                    <div 
                      key={logIndex}
                      className={cn(
                        'whitespace-pre-wrap',
                        log.includes('ERROR') && 'text-error',
                        log.includes('WARN') && 'text-warning',
                        log.includes('SUCCESS') && 'text-success'
                      )}
                    >
                      {log}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}