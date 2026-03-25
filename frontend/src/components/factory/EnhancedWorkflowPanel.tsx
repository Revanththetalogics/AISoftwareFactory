'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  ChevronRight,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  MoreHorizontal,
  Copy
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

export type EnhancedWorkflowStepStatus = 'completed' | 'running' | 'pending' | 'failed' | 'skipped' | 'queued';

export interface EnhancedWorkflowStep {
  id: string;
  title: string;
  description: string;
  status: EnhancedWorkflowStepStatus;
  duration?: string;
  estimatedDuration?: string;
  startTime?: Date;
  endTime?: Date;
  logs?: LogEntry[];
  retryCount?: number;
  dependencies?: string[]; // IDs of steps this depends on
  output?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'debug' | 'info' | 'warn' | 'error' | 'success';
  message: string;
  source?: string;
  details?: Record<string, unknown>;
}

interface EnhancedWorkflowPanelProps {
  steps: EnhancedWorkflowStep[];
  className?: string;
  expandedStepId?: string;
  isPlaying?: boolean;
  onStepToggle?: (stepId: string) => void;
  onStepAction?: (stepId: string, action: 'play' | 'pause' | 'reset' | 'retry' | 'skip') => void;
  onStepSelect?: (stepId: string) => void;
  onViewLogs?: (stepId: string) => void;
}

const getStatusConfig = (status: EnhancedWorkflowStepStatus) => {
  switch (status) {
    case 'completed':
      return {
        bgColor: 'bg-success/10',
        borderColor: 'border-success',
        statusColor: 'bg-success',
        textColor: 'text-success',
        icon: CheckCircle,
      };
    case 'running':
      return {
        bgColor: 'bg-primary/10',
        borderColor: 'border-primary',
        statusColor: 'bg-primary',
        textColor: 'text-primary',
        icon: Play,
        glowClass: 'glow-primary',
        animate: true,
      };
    case 'pending':
      return {
        bgColor: 'bg-bg-surface',
        borderColor: 'border-border',
        statusColor: 'bg-gray-500',
        textColor: 'text-text-secondary',
        icon: Clock,
      };
    case 'failed':
      return {
        bgColor: 'bg-error/10',
        borderColor: 'border-error',
        statusColor: 'bg-error',
        textColor: 'text-error',
        icon: XCircle,
      };
    case 'skipped':
      return {
        bgColor: 'bg-warning/10',
        borderColor: 'border-warning',
        statusColor: 'bg-warning',
        textColor: 'text-warning',
        icon: AlertCircle,
      };
    case 'queued':
      return {
        bgColor: 'bg-secondary/10',
        borderColor: 'border-secondary',
        statusColor: 'bg-secondary',
        textColor: 'text-secondary',
        icon: Clock,
      };
  }
};

const getLogLevelColor = (level: LogEntry['level']) => {
  switch (level) {
    case 'error': return 'text-error';
    case 'warn': return 'text-warning';
    case 'success': return 'text-success';
    case 'info': return 'text-text-primary';
    case 'debug': return 'text-text-secondary';
  }
};

export function EnhancedWorkflowPanel({ 
  steps, 
  className,
  expandedStepId,
  onStepToggle,
  onStepAction,
  onStepSelect,
  onViewLogs
}: EnhancedWorkflowPanelProps) {
  const [localExpandedId, setLocalExpandedId] = useState<string | null>(
    expandedStepId ?? null
  );
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);

  const handleStepToggle = (stepId: string) => {
    const newExpandedId = localExpandedId === stepId ? null : stepId;
    setLocalExpandedId(newExpandedId);
    onStepToggle?.(stepId);
  };

  const handleStepAction = (stepId: string, action: Parameters<NonNullable<typeof onStepAction>>[1]) => {
    onStepAction?.(stepId, action);
  };

  const handleStepSelect = (stepId: string) => {
    setSelectedStepId(stepId);
    onStepSelect?.(stepId);
  };

  const handleViewLogs = (stepId: string) => {
    onViewLogs?.(stepId);
  };

  const getActionButtons = (step: EnhancedWorkflowStep) => {
    const buttons = [];
    
    if (step.status === 'pending' || step.status === 'queued') {
      buttons.push(
        <Button
          key="play"
          variant="ghost"
          size="sm"
          className="h-6 px-2 text-xs"
          onClick={(e) => {
            e.stopPropagation();
            handleStepAction(step.id, 'play');
          }}
        >
          <Play className="w-3 h-3 mr-1" />
          Run
        </Button>
      );
    }
    
    if (step.status === 'running') {
      buttons.push(
        <Button
          key="pause"
          variant="ghost"
          size="sm"
          className="h-6 px-2 text-xs"
          onClick={(e) => {
            e.stopPropagation();
            handleStepAction(step.id, 'pause');
          }}
        >
          <Pause className="w-3 h-3 mr-1" />
          Pause
        </Button>
      );
    }
    
    if (step.status === 'failed' && (step.retryCount || 0) < 3) {
      buttons.push(
        <Button
          key="retry"
          variant="ghost"
          size="sm"
          className="h-6 px-2 text-xs"
          onClick={(e) => {
            e.stopPropagation();
            handleStepAction(step.id, 'retry');
          }}
        >
          <RotateCcw className="w-3 h-3 mr-1" />
          Retry
        </Button>
      );
    }
    
    if (step.status === 'pending' || step.status === 'queued') {
      buttons.push(
        <Button
          key="skip"
          variant="ghost"
          size="sm"
          className="h-6 px-2 text-xs"
          onClick={(e) => {
            e.stopPropagation();
            handleStepAction(step.id, 'skip');
          }}
        >
          <Square className="w-3 h-3 mr-1" />
          Skip
        </Button>
      );
    }

    return buttons;
  };

  return (
    <div className={cn('space-y-2', className)}>
      <AnimatePresence>
        {steps.map((step, index) => {
          const config = getStatusConfig(step.status);
          const isExpanded = localExpandedId === step.id;
          const isSelected = selectedStepId === step.id;
          
          return (
            <motion.div
              key={step.id}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={cn(
                'rounded-lg border transition-all duration-300 overflow-hidden',
                config.bgColor,
                config.borderColor,
                config.glowClass,
                isSelected && 'ring-2 ring-primary/50',
                'hover:shadow-md'
              )}
            >
              {/* Step Header */}
              <div 
                className="p-4 cursor-pointer"
                onClick={() => handleStepToggle(step.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className={cn(
                      'flex-shrink-0 mt-0.5',
                      config.animate && 'animate-pulse'
                    )}>
                      <config.icon className={cn('w-5 h-5', config.textColor)} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-text-primary truncate">
                          {step.title}
                        </h3>
                        <Badge 
                          variant="outline" 
                          className={cn(
                            'text-xs',
                            config.textColor,
                            config.borderColor
                          )}
                        >
                          {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                        </Badge>
                        {step.retryCount && step.retryCount > 0 && (
                          <Badge variant="secondary" className="text-xs">
                            Retry #{step.retryCount}
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-sm text-text-secondary mb-2">
                        {step.description}
                      </p>
                      
                      <div className="flex items-center gap-4 text-xs text-text-tertiary">
                        {step.duration && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {step.duration}
                          </span>
                        )}
                        {step.estimatedDuration && (
                          <span>Est: {step.estimatedDuration}</span>
                        )}
                        {step.startTime && (
                          <span>
                            Started: {step.startTime.toLocaleTimeString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    {getActionButtons(step)}
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStepSelect(step.id);
                      }}
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewLogs(step.id);
                      }}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                    
                    <motion.div
                      animate={{ rotate: isExpanded ? 90 : 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <ChevronRight className="w-5 h-5 text-text-secondary" />
                    </motion.div>
                  </div>
                </div>
              </div>
              
              {/* Expanded Content */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="border-t border-border"
                  >
                    <div className="p-4 bg-bg-surface/50">
                      {/* Dependencies */}
                      {step.dependencies && step.dependencies.length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-sm font-medium text-text-primary mb-2">
                            Dependencies
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {step.dependencies.map(depId => {
                              const depStep = steps.find(s => s.id === depId);
                              return (
                                <Badge 
                                  key={depId} 
                                  variant="outline" 
                                  className="text-xs"
                                >
                                  {depStep?.title || depId}
                                </Badge>
                              );
                            })}
                          </div>
                        </div>
                      )}
                      
                      {/* Logs Preview */}
                      {step.logs && step.logs.length > 0 && (
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-sm font-medium text-text-primary">
                              Recent Logs ({step.logs.length})
                            </h4>
                            <Button
                              variant="link"
                              size="sm"
                              className="h-auto p-0 text-xs"
                              onClick={() => handleViewLogs(step.id)}
                            >
                              View All
                            </Button>
                          </div>
                          
                          <ScrollArea className="h-32 rounded border border-border bg-bg-base p-2">
                            <div className="space-y-1 font-mono-system text-xs">
                              {step.logs.slice(-5).map(log => (
                                <div 
                                  key={log.id}
                                  className={cn(
                                    'whitespace-pre-wrap',
                                    getLogLevelColor(log.level)
                                  )}
                                >
                                  [{log.timestamp.toLocaleTimeString()}] {log.level.toUpperCase()}: {log.message}
                                </div>
                              ))}
                            </div>
                          </ScrollArea>
                        </div>
                      )}
                      
                      {/* Output/Data Preview */}
                      {step.output && (
                        <div className="mt-4">
                          <h4 className="text-sm font-medium text-text-primary mb-2">
                            Output Preview
                          </h4>
                          <pre className="text-xs bg-bg-base p-3 rounded border border-border overflow-x-auto">
                            {JSON.stringify(step.output, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}