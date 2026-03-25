'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export type AgentStatus = 'idle' | 'running' | 'error' | 'success';

export interface AgentNode {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  currentTask?: string;
}

interface AgentVisualizationProps {
  agents: AgentNode[];
  className?: string;
  onAgentClick?: (agent: AgentNode) => void;
}

const getStatusConfig = (status: AgentStatus) => {
  switch (status) {
    case 'idle':
      return {
        bgColor: 'bg-bg-surface',
        borderColor: 'border-border',
        statusColor: 'bg-gray-500',
        statusText: 'Ready',
      };
    case 'running':
      return {
        bgColor: 'bg-primary/10',
        borderColor: 'border-primary',
        statusColor: 'bg-primary',
        statusText: 'Processing...',
        glowClass: 'glow-primary',
        animate: true,
      };
    case 'error':
      return {
        bgColor: 'bg-error/10',
        borderColor: 'border-error',
        statusColor: 'bg-error',
        statusText: 'Error',
      };
    case 'success':
      return {
        bgColor: 'bg-success/10',
        borderColor: 'border-success',
        statusColor: 'bg-success',
        statusText: 'Complete',
      };
  }
};

export function AgentVisualization({ 
  agents, 
  className,
  onAgentClick 
}: AgentVisualizationProps) {
  const handleAgentClick = (agent: AgentNode) => {
    onAgentClick?.(agent);
  };

  // Group agents into rows for grid layout
  const groupedAgents = [];
  const agentsPerRow = 2;
  
  for (let i = 0; i < agents.length; i += agentsPerRow) {
    groupedAgents.push(agents.slice(i, i + agentsPerRow));
  }

  return (
    <div className={cn('relative', className)}>
      <div className="grid grid-cols-2 gap-4">
        {groupedAgents.map((row, rowIndex) => (
          <div key={rowIndex} className="flex gap-4">
            {row.map((agent) => {
              const config = getStatusConfig(agent.status);
              const isClickable = onAgentClick !== undefined;
              
              return (
                <motion.div
                  key={agent.id}
                  className={cn(
                    'p-4 rounded-lg border transition-all duration-300 w-full',
                    config.bgColor,
                    config.borderColor,
                    config.glowClass,
                    isClickable && 'cursor-pointer hover:scale-105'
                  )}
                  whileHover={isClickable ? { scale: 1.02 } : {}}
                  whileTap={isClickable ? { scale: 0.98 } : {}}
                  onClick={() => handleAgentClick(agent)}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className={cn(
                      'w-3 h-3 rounded-full',
                      config.statusColor,
                      config.animate && 'animate-pulse'
                    )} />
                    <h3 className="font-medium text-text-primary truncate">
                      {agent.name}
                    </h3>
                  </div>
                  <p className="text-xs text-text-secondary mb-2 truncate">
                    {agent.role}
                  </p>
                  <div className="text-xs text-text-tertiary">
                    {agent.currentTask || config.statusText}
                  </div>
                </motion.div>
              );
            })}
          </div>
        ))}
      </div>
      
      {/* Connection Lines */}
      {groupedAgents.length > 1 && (
        <div className="absolute inset-0 pointer-events-none">
          {groupedAgents.slice(0, -1).map((_, i) => (
            <div 
              key={i}
              className="absolute h-px bg-border"
              style={{
                top: `${((i + 1) * 100) / groupedAgents.length}%`,
                left: '25%',
                width: '50%',
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}