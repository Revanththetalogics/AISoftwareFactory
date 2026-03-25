'use client';

import { useEffect, useRef } from 'react';
import { 
  factoryWebSocket,
  type PipelineUpdatePayload,
  type AgentStatusPayload,
  type WorkflowStepPayload,
  type SystemMetricPayload,
  type LogEntryPayload
} from '@/services/websocket.service';
import { type FactoryAction } from '@/hooks/useFactoryState';
import { type PipelinePhaseStatus } from '@/components/factory/PipelineStepper';
import { type AgentStatus } from '@/components/factory/AgentVisualization';
import { type EnhancedWorkflowStepStatus } from '@/components/factory/EnhancedWorkflowPanel';

interface UseFactoryWebSocketOptions {
  enabled?: boolean;
  autoConnect?: boolean;
}

export function useFactoryWebSocket(
  dispatch: (action: FactoryAction) => void,
  options: UseFactoryWebSocketOptions = {}
) {
  const { enabled = true, autoConnect = true } = options;
  const isConnectedRef = useRef(false);

  useEffect(() => {
    if (!enabled) return;

    // Connect WebSocket
    if (autoConnect) {
      factoryWebSocket.connect();
    }

    // Subscribe to pipeline updates
    const unsubscribePipeline = factoryWebSocket.subscribe<PipelineUpdatePayload>(
      'PIPELINE_UPDATE',
      (payload) => {
        dispatch({
          type: 'UPDATE_PIPELINE_PHASE',
          payload: {
            phaseId: payload.phaseId,
            status: payload.status as PipelinePhaseStatus
          }
        });
      }
    );

    // Subscribe to agent status updates
    const unsubscribeAgents = factoryWebSocket.subscribe<AgentStatusPayload>(
      'AGENT_STATUS',
      (payload) => {
        dispatch({
          type: 'UPDATE_AGENT_STATUS',
          payload: {
            agentId: payload.agentId,
            status: payload.status as AgentStatus,
            currentTask: payload.taskId
          }
        });
      }
    );

    // Subscribe to workflow step updates
    const unsubscribeWorkflow = factoryWebSocket.subscribe<WorkflowStepPayload>(
      'WORKFLOW_STEP',
      (payload) => {
        dispatch({
          type: 'UPDATE_WORKFLOW_STEP_STATUS',
          payload: {
            stepId: payload.stepId,
            status: payload.status as EnhancedWorkflowStepStatus
          }
        });
      }
    );

    // Subscribe to system metrics
    const unsubscribeMetrics = factoryWebSocket.subscribe<SystemMetricPayload>(
      'SYSTEM_METRIC',
      (payload) => {
        // We need to collect all metrics before dispatching
        // This is a simplified approach - in practice, you'd want to batch these
        const metricUpdates: Partial<{ cpu: number; memory: number; storage: number }> = {};
        
        if (payload.metric === 'cpu') {
          metricUpdates.cpu = payload.value;
        } else if (payload.metric === 'memory') {
          metricUpdates.memory = payload.value;
        } else if (payload.metric === 'storage') {
          metricUpdates.storage = payload.value;
        }
        
        // For now, we'll just update what we have
        // In a real implementation, you'd want to collect metrics over time
        dispatch({
          type: 'UPDATE_SYSTEM_METRICS',
          payload: {
            cpu: metricUpdates.cpu ?? 45,
            memory: metricUpdates.memory ?? 62,
            storage: metricUpdates.storage ?? 38
          }
        });
      }
    );

    // Subscribe to log entries
    const unsubscribeLogs = factoryWebSocket.subscribe<LogEntryPayload>(
      'LOG_ENTRY',
      (payload) => {
        // This would typically be handled by a separate log management system
        console.log(`[${payload.level.toUpperCase()}] [${payload.source}] ${payload.message}`, payload.details);
      }
    );

    // Subscribe to connection status
    const unsubscribeConnection = factoryWebSocket.subscribeConnection((connected) => {
      isConnectedRef.current = connected;
      // Connection status is handled internally, no dispatch needed
    });

    // Cleanup subscriptions
    return () => {
      unsubscribePipeline();
      unsubscribeAgents();
      unsubscribeWorkflow();
      unsubscribeMetrics();
      unsubscribeLogs();
      unsubscribeConnection();
      
      if (autoConnect) {
        factoryWebSocket.disconnect();
      }
    };
  }, [dispatch, enabled, autoConnect]);

  // Helper methods for sending messages
  const sendPipelineUpdate = (update: Omit<PipelineUpdatePayload, 'timestamp'>) => {
    if (isConnectedRef.current) {
      factoryWebSocket.sendPipelineUpdate(update);
    }
  };

  const sendAgentStatus = (status: Omit<AgentStatusPayload, 'timestamp'>) => {
    if (isConnectedRef.current) {
      factoryWebSocket.sendAgentStatus(status);
    }
  };

  const sendWorkflowStep = (step: Omit<WorkflowStepPayload, 'timestamp'>) => {
    if (isConnectedRef.current) {
      factoryWebSocket.sendWorkflowStep(step);
    }
  };

  const sendSystemMetric = (metric: Omit<SystemMetricPayload, 'timestamp'>) => {
    if (isConnectedRef.current) {
      factoryWebSocket.sendSystemMetric(metric);
    }
  };

  const sendLogEntry = (log: Omit<LogEntryPayload, 'timestamp'>) => {
    if (isConnectedRef.current) {
      factoryWebSocket.sendLogEntry(log);
    }
  };

  const sendFactoryReset = () => {
    if (isConnectedRef.current) {
      factoryWebSocket.sendFactoryReset();
    }
  };

  const isConnected = () => factoryWebSocket.isConnected();

  return {
    isConnected,
    sendPipelineUpdate,
    sendAgentStatus,
    sendWorkflowStep,
    sendSystemMetric,
    sendLogEntry,
    sendFactoryReset
  };
}

// Mock WebSocket service for development/testing
export class MockWebSocketService {
  private subscribers: Map<string, Set<(payload: unknown) => void>> = new Map();
  private connectionSubscribers: Set<(connected: boolean) => void> = new Set();
  private isConnectedState = false;
  private mockInterval: NodeJS.Timeout | null = null;

  public connect(): void {
    console.log('Mock WebSocket connecting...');
    setTimeout(() => {
      this.isConnectedState = true;
      this.connectionSubscribers.forEach(cb => cb(true));
      this.startMockUpdates();
    }, 1000);
  }

  public disconnect(): void {
    if (this.mockInterval) {
      clearInterval(this.mockInterval);
      this.mockInterval = null;
    }
    this.isConnectedState = false;
    this.connectionSubscribers.forEach(cb => cb(false));
  }

  public subscribe<T>(type: string, callback: (payload: T) => void): () => void {
    if (!this.subscribers.has(type)) {
      this.subscribers.set(type, new Set());
    }
    const listeners = this.subscribers.get(type)!;
    listeners.add(callback as (payload: unknown) => void);
    return () => {
      listeners.delete(callback as (payload: unknown) => void);
    };
  }

  public subscribeConnection(callback: (connected: boolean) => void): () => void {
    this.connectionSubscribers.add(callback);
    return () => {
      this.connectionSubscribers.delete(callback);
    };
  }

  public isConnected(): boolean {
    return this.isConnectedState;
  }

  private startMockUpdates(): void {
    this.mockInterval = setInterval(() => {
      // Simulate pipeline progress
      this.publish('PIPELINE_UPDATE', {
        phaseId: '3',
        phaseIndex: 2,
        progress: Math.min(100, Math.random() * 100),
        status: 'running'
      });

      // Simulate agent status
      this.publish('AGENT_STATUS', {
        agentId: '2',
        status: Math.random() > 0.3 ? 'running' : 'idle',
        taskId: 'design-task-1',
        progress: Math.random() * 100
      });

      // Simulate system metrics
      this.publish('SYSTEM_METRIC', {
        metric: 'cpu',
        value: 30 + Math.random() * 40
      });

      this.publish('SYSTEM_METRIC', {
        metric: 'memory',
        value: 40 + Math.random() * 30
      });

      // Simulate log entries occasionally
      if (Math.random() > 0.7) {
        this.publish('LOG_ENTRY', {
          level: 'info',
          source: 'Mock Service',
          message: 'Simulated log entry',
          details: { timestamp: new Date().toISOString() }
        });
      }
    }, 3000);
  }

  private publish(type: string, payload: unknown): void {
    const listeners = this.subscribers.get(type);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(payload);
        } catch (error) {
          console.error(`Error in mock listener for ${type}:`, error);
        }
      });
    }
  }
}