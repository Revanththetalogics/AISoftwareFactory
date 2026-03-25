'use client';

import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

export type PipelinePhaseStatus = 'completed' | 'running' | 'pending' | 'failed';

export interface PipelinePhase {
  id: string;
  name: string;
  status: PipelinePhaseStatus;
}

interface PipelineStepperProps {
  phases: PipelinePhase[];
  currentPhaseIndex: number;
  className?: string;
  onPhaseClick?: (phase: PipelinePhase, index: number) => void;
}

interface StatusConfig {
  bgColor: string;
  borderColor: string;
  textColor: string;
  icon?: typeof Check;
  glowClass?: string;
}

const getStatusConfig = (status: PipelinePhaseStatus): StatusConfig => {
  switch (status) {
    case 'completed':
      return {
        bgColor: 'bg-success',
        borderColor: 'border-success',
        textColor: 'text-white',
        icon: Check,
      };
    case 'running':
      return {
        bgColor: 'bg-primary',
        borderColor: 'border-primary',
        textColor: 'text-white',
        glowClass: 'glow-primary',
      };
    case 'pending':
      return {
        bgColor: 'bg-bg-surface',
        borderColor: 'border-border',
        textColor: 'text-text-secondary',
      };
    case 'failed':
      return {
        bgColor: 'bg-error',
        borderColor: 'border-error',
        textColor: 'text-white',
      };
  }
};

export function PipelineStepper({ 
  phases, 
  currentPhaseIndex, 
  className,
  onPhaseClick 
}: PipelineStepperProps) {
  const handlePhaseClick = (phase: PipelinePhase, index: number) => {
    onPhaseClick?.(phase, index);
  };

  return (
    <div className={cn('w-full', className)}>
      <div className="flex items-center justify-between mb-6">
        {phases.map((phase, index) => {
          const config = getStatusConfig(phase.status);
          const isClickable = onPhaseClick && phase.status !== 'pending';
          
          return (
            <div key={phase.id} className="flex items-center">
              {/* Phase Node */}
              <motion.div
                className={cn(
                  'flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300',
                  config.bgColor,
                  config.borderColor,
                  config.glowClass,
                  isClickable && 'cursor-pointer hover:scale-110'
                )}
                animate={phase.status === 'running' ? { scale: [1, 1.1, 1] } : {}}
                transition={phase.status === 'running' ? { duration: 2, repeat: Infinity } : {}}
                onClick={() => handlePhaseClick(phase, index)}
                whileHover={isClickable ? { scale: 1.05 } : {}}
                whileTap={isClickable ? { scale: 0.95 } : {}}
              >
                {config.icon ? (
                  <config.icon className={cn('w-5 h-5', config.textColor)} />
                ) : (
                  <span className={cn('text-xs font-medium', config.textColor)}>
                    {index + 1}
                  </span>
                )}
              </motion.div>
              
              {/* Connection Line */}
              {index < phases.length - 1 && (
                <div 
                  className={cn(
                    'h-0.5 w-12 mx-2 transition-colors duration-300',
                    index < currentPhaseIndex 
                      ? 'bg-success' 
                      : index === currentPhaseIndex 
                        ? 'bg-gradient-to-r from-primary to-secondary' 
                        : 'bg-border'
                  )}
                />
              )}
            </div>
          );
        })}
      </div>
      
      {/* Phase Labels */}
      <div className="flex justify-between mb-4">
        {phases.map((phase) => {
          return (
            <div key={phase.id} className="text-center min-w-0">
              <span className={cn(
                'text-xs font-medium truncate block',
                phase.status === 'completed' ? 'text-success' : '',
                phase.status === 'running' ? 'text-primary' : '',
                phase.status === 'pending' ? 'text-text-secondary' : '',
                phase.status === 'failed' ? 'text-error' : ''
              )}>
                {phase.name}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}