'use client';

import { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';

export type WebSocketMessage =
  | { type: 'agent_status'; data: AgentStatusUpdate }
  | { type: 'workflow_progress'; data: WorkflowProgressUpdate }
  | { type: 'log_entry'; data: LogEntryUpdate }
  | { type: 'deployment_status'; data: DeploymentStatusUpdate }
  | { type: 'system_metrics'; data: SystemMetricsUpdate }
  | { type: 'notification'; data: NotificationUpdate };

export interface AgentStatusUpdate {
  agentId: string;
  status: 'idle' | 'running' | 'success' | 'error' | 'queued';
  currentTask?: string;
  progress: number;
  timestamp: string;
}

export interface WorkflowProgressUpdate {
  workflowId: string;
  projectId: string;
  phase: string;
  progress: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  timestamp: string;
}

export interface LogEntryUpdate {
  id: string;
  level: 'info' | 'warn' | 'error' | 'debug' | 'success';
  source: string;
  message: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface DeploymentStatusUpdate {
  deploymentId: string;
  environment: string;
  status: string;
  version: string;
  healthChecks: Array<{
    name: string;
    status: 'passing' | 'failing' | 'unknown';
    responseTime?: number;
  }>;
  metrics: {
    cpu: number;
    memory: number;
    requests: number;
    latency: number;
  };
  timestamp: string;
}

export interface SystemMetricsUpdate {
  cpu: number;
  memory: number;
  network: number;
  disk: number;
  timestamp: string;
}

export interface NotificationUpdate {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
}

export interface UseWebSocketOptions {
  url?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  enableMock?: boolean;
}

// Helper function to generate mock messages
function generateMockMessage(onMessage?: (message: WebSocketMessage) => void): void {
  const messageTypes: WebSocketMessage['type'][] = [
    'agent_status',
    'workflow_progress',
    'log_entry',
    'system_metrics',
  ];

  const randomType = messageTypes[Math.floor(Math.random() * messageTypes.length)];
  let message: WebSocketMessage;

  switch (randomType) {
    case 'agent_status':
      message = {
        type: 'agent_status',
        data: {
          agentId: `agent-${String(Math.floor(Math.random() * 10)).padStart(3, '0')}`,
          status: Math.random() > 0.7 ? 'running' : Math.random() > 0.5 ? 'success' : 'idle',
          currentTask: Math.random() > 0.5 ? 'Processing task...' : undefined,
          progress: Math.floor(Math.random() * 100),
          timestamp: new Date().toISOString(),
        },
      };
      break;

    case 'workflow_progress':
      message = {
        type: 'workflow_progress',
        data: {
          workflowId: 'wf-001',
          projectId: 'proj-001',
          phase: ['Idea', 'Requirements', 'Architecture', 'Implementation', 'Testing', 'Deployment'][
            Math.floor(Math.random() * 6)
          ],
          progress: Math.floor(Math.random() * 100),
          status: Math.random() > 0.8 ? 'completed' : 'running',
          timestamp: new Date().toISOString(),
        },
      };
      break;

    case 'log_entry':
      message = {
        type: 'log_entry',
        data: {
          id: `log-${Date.now()}`,
          level: Math.random() > 0.8 ? 'warn' : Math.random() > 0.9 ? 'error' : 'info',
          source: ['Backend Agent', 'Frontend Agent', 'CEO Agent', 'System'][Math.floor(Math.random() * 4)],
          message: [
            'Processing request...',
            'Task completed successfully',
            'Warning: High memory usage',
            'Error: Connection timeout',
            'Initializing component...',
          ][Math.floor(Math.random() * 5)],
          timestamp: new Date().toISOString(),
        },
      };
      break;

    case 'system_metrics':
      message = {
        type: 'system_metrics',
        data: {
          cpu: Math.floor(Math.random() * 80) + 10,
          memory: Math.floor(Math.random() * 70) + 20,
          network: Math.floor(Math.random() * 200),
          disk: Math.floor(Math.random() * 60) + 10,
          timestamp: new Date().toISOString(),
        },
      };
      break;

    default:
      return;
  }

  onMessage?.(message);
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    url = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    enableMock = true,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const mockIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Store callbacks in refs to avoid dependency issues
  const onMessageRef = useRef(onMessage);
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);
  const onErrorRef = useRef(onError);

  // Update refs when callbacks change
  useEffect(() => {
    onMessageRef.current = onMessage;
    onConnectRef.current = onConnect;
    onDisconnectRef.current = onDisconnect;
    onErrorRef.current = onError;
  }, [onMessage, onConnect, onDisconnect, onError]);

  // Initialize connection on mount
  useEffect(() => {
    // Skip if already connected
    if (isConnected || isConnecting) {
      return;
    }

    // Use timeout to avoid setState during render
    const initTimeout = setTimeout(() => {
      setIsConnecting(true);

      // For demo purposes, use mock WebSocket if enableMock is true
      if (enableMock) {
        setIsConnected(true);
        setIsConnecting(false);
        onConnectRef.current?.();

        // Simulate incoming messages
        mockIntervalRef.current = setInterval(() => {
          generateMockMessage(onMessageRef.current);
        }, 3000 + Math.random() * 2000);

        return;
      }

      // Real WebSocket connection
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          setIsConnecting(false);
          reconnectAttemptsRef.current = 0;
          onConnectRef.current?.();
          toast.success('Connected to real-time updates');
        };

        ws.onclose = () => {
          setIsConnected(false);
          setIsConnecting(false);
          onDisconnectRef.current?.();
        };

        ws.onerror = (error) => {
          setIsConnecting(false);
          onErrorRef.current?.(error);
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            onMessageRef.current?.(message);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
          }
        };
      } catch (error) {
        setIsConnecting(false);
        console.error('WebSocket connection error:', error);
      }
    }, 0);

    return () => {
      clearTimeout(initTimeout);

      if (mockIntervalRef.current) {
        clearInterval(mockIntervalRef.current);
        mockIntervalRef.current = null;
      }

      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  const sendMessage = (message: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return {
    isConnected,
    isConnecting,
    sendMessage,
  };
}

// Hook for real-time agent updates
export function useAgentRealtime(agentId?: string) {
  const [agentStatus, setAgentStatus] = useState<AgentStatusUpdate | null>(null);

  const { isConnected } = useWebSocket({
    enableMock: true,
    onMessage: (message) => {
      if (message.type === 'agent_status') {
        if (!agentId || message.data.agentId === agentId) {
          setAgentStatus(message.data);
        }
      }
    },
  });

  return { agentStatus, isConnected };
}

// Hook for real-time workflow updates
export function useWorkflowRealtime(workflowId?: string) {
  const [workflowProgress, setWorkflowProgress] = useState<WorkflowProgressUpdate | null>(null);

  const { isConnected } = useWebSocket({
    enableMock: true,
    onMessage: (message) => {
      if (message.type === 'workflow_progress') {
        if (!workflowId || message.data.workflowId === workflowId) {
          setWorkflowProgress(message.data);
        }
      }
    },
  });

  return { workflowProgress, isConnected };
}

// Hook for real-time logs
export function useLogsRealtime() {
  const [latestLog, setLatestLog] = useState<LogEntryUpdate | null>(null);

  const { isConnected } = useWebSocket({
    enableMock: true,
    onMessage: (message) => {
      if (message.type === 'log_entry') {
        setLatestLog(message.data);
      }
    },
  });

  return { latestLog, isConnected };
}

// Hook for real-time system metrics
export function useSystemMetricsRealtime() {
  const [metrics, setMetrics] = useState<SystemMetricsUpdate | null>(null);

  const { isConnected } = useWebSocket({
    enableMock: true,
    onMessage: (message) => {
      if (message.type === 'system_metrics') {
        setMetrics(message.data);
      }
    },
  });

  return { metrics, isConnected };
}
