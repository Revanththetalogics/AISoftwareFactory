'use client';

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { AgentNode, AgentStatus } from './AgentVisualization';

export interface AgentGraphNode extends AgentNode {
  x: number;
  y: number;
  connections: string[]; // IDs of connected agents
}

export interface AgentGraphEdge {
  source: string;
  target: string;
  strength: number; // 0-1 representing connection strength
}

interface AgentGraphProps {
  agents: AgentGraphNode[];
  edges: AgentGraphEdge[];
  className?: string;
  onAgentClick?: (agent: AgentGraphNode) => void;
  onAgentDrag?: (agentId: string, x: number, y: number) => void;
}

const getStatusConfig = (status: AgentStatus) => {
  switch (status) {
    case 'idle':
      return {
        bgColor: 'bg-bg-surface',
        borderColor: 'border-border',
        statusColor: 'bg-gray-500',
        statusText: 'Idle',
      };
    case 'running':
      return {
        bgColor: 'bg-primary/20',
        borderColor: 'border-primary',
        statusColor: 'bg-primary',
        statusText: 'Active',
        glowClass: 'glow-primary',
        animate: true,
      };
    case 'error':
      return {
        bgColor: 'bg-error/20',
        borderColor: 'border-error',
        statusColor: 'bg-error',
        statusText: 'Error',
      };
    case 'success':
      return {
        bgColor: 'bg-success/20',
        borderColor: 'border-success',
        statusColor: 'bg-success',
        statusText: 'Success',
      };
  }
};

export function AgentGraph({ 
  agents, 
  edges, 
  className,
  onAgentClick,
  onAgentDrag
}: AgentGraphProps) {
  const [draggedAgent, setDraggedAgent] = useState<string | null>(null);
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  
  // Initialize positions from agents prop using lazy initialization
  const initialPositions = useMemo(() => 
    agents.reduce((acc, agent) => ({
      ...acc,
      [agent.id]: { x: agent.x, y: agent.y }
    }), {}),
    [agents]
  );
  const containerRef = useRef<HTMLDivElement>(null);

  // Update positions when agents prop changes
  useEffect(() => {
    setPositions(initialPositions);
  }, [initialPositions]);

  const handleMouseDown = (agentId: string, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggedAgent(agentId);
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!draggedAgent || !containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const x = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    const y = ((e.clientY - containerRect.top) / containerRect.height) * 100;

    setPositions(prev => ({
      ...prev,
      [draggedAgent]: { 
        x: Math.max(0, Math.min(100, x)), 
        y: Math.max(0, Math.min(100, y)) 
      }
    }));

    onAgentDrag?.(draggedAgent, x, y);
  }, [draggedAgent, containerRef, setPositions, onAgentDrag]);

  const handleMouseUp = () => {
    setDraggedAgent(null);
  };

  useEffect(() => {
    if (draggedAgent) {
      const handleMouseMoveWrapped = (e: MouseEvent) => handleMouseMove(e);
      document.addEventListener('mousemove', handleMouseMoveWrapped);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMoveWrapped);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [draggedAgent, handleMouseMove]);

  const getConnectionStrength = (sourceId: string, targetId: string) => {
    const edge = edges.find(e => 
      (e.source === sourceId && e.target === targetId) ||
      (e.source === targetId && e.target === sourceId)
    );
    return edge ? edge.strength : 0;
  };

  return (
    <div 
      ref={containerRef}
      className={cn('relative w-full h-80 bg-bg-surface rounded-lg border border-border overflow-hidden', className)}
    >
      {/* Connection Lines */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {edges.map((edge, index) => {
          const sourcePos = positions[edge.source];
          const targetPos = positions[edge.target];
          
          if (!sourcePos || !targetPos) return null;

          const sourceAgent = agents.find(a => a.id === edge.source);
          const targetAgent = agents.find(a => a.id === edge.target);
          
          if (!sourceAgent || !targetAgent) return null;

          const isActive = sourceAgent.status === 'running' || targetAgent.status === 'running';
          
          return (
            <motion.line
              key={`${edge.source}-${edge.target}`}
              x1={`${sourcePos.x}%`}
              y1={`${sourcePos.y}%`}
              x2={`${targetPos.x}%`}
              y2={`${targetPos.y}%`}
              stroke={isActive ? 'var(--color-primary)' : 'var(--color-border)'}
              strokeWidth={Math.max(1, edge.strength * 3)}
              strokeOpacity={isActive ? 0.8 : 0.4}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              {isActive && (
                <animate
                  attributeName="stroke-dashoffset"
                  values="100;0"
                  dur="2s"
                  repeatCount="indefinite"
                />
              )}
            </motion.line>
          );
        })}
      </svg>

      {/* Agent Nodes */}
      {agents.map((agent) => {
        const position = positions[agent.id];
        const config = getStatusConfig(agent.status);
        const isDragging = draggedAgent === agent.id;
        const isClickable = onAgentClick !== undefined;

        return (
          <motion.div
            key={agent.id}
            className={cn(
              'absolute w-40 h-20 rounded-xl border-2 p-3 cursor-move select-none',
              'flex flex-col justify-center items-center text-center',
              config.bgColor,
              config.borderColor,
              config.glowClass,
              isDragging && 'z-50 shadow-xl scale-105',
              isClickable && 'hover:scale-105'
            )}
            style={{
              left: `${position.x}%`,
              top: `${position.y}%`,
              transform: 'translate(-50%, -50%)',
            }}
            onMouseDown={(e) => handleMouseDown(agent.id, e)}
            whileHover={isClickable && !isDragging ? { scale: 1.05 } : {}}
            whileTap={isClickable && !isDragging ? { scale: 0.95 } : {}}
            onClick={() => !isDragging && onAgentClick?.(agent)}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ 
              scale: isDragging ? 1.1 : 1, 
              opacity: 1,
              x: 0,
              y: 0
            }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            {/* Status Indicator */}
            <div className={cn(
              'absolute -top-1 -right-1 w-3 h-3 rounded-full',
              config.statusColor,
              config.animate && 'animate-pulse'
            )} />

            {/* Agent Info */}
            <div className="text-center">
              <h3 className="font-semibold text-text-primary text-sm truncate">
                {agent.name}
              </h3>
              <p className="text-xs text-text-secondary truncate">
                {agent.role}
              </p>
              {agent.currentTask && (
                <p className="text-xs text-text-tertiary mt-1 truncate">
                  {agent.currentTask}
                </p>
              )}
            </div>

            {/* Connection Strength Indicators */}
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 flex gap-1">
              {agent.connections.map(connectionId => {
                const strength = getConnectionStrength(agent.id, connectionId);
                return (
                  <div
                    key={connectionId}
                    className={cn(
                      'w-1.5 h-1.5 rounded-full',
                      strength > 0.7 ? 'bg-success' :
                      strength > 0.4 ? 'bg-warning' : 'bg-gray-500'
                    )}
                    title={`Connection strength: ${(strength * 100).toFixed(0)}%`}
                  />
                );
              })}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}