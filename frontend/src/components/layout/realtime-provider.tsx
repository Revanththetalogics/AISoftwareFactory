'use client';

import { createContext, useContext, useCallback, useState } from 'react';
import { useWebSocket, type WebSocketMessage } from '@/lib/websocket';
import { toast } from 'sonner';

interface RealtimeContextType {
  isConnected: boolean;
  isConnecting: boolean;
  lastMessage: WebSocketMessage | null;
  agentUpdates: Map<string, WebSocketMessage['data']>;
  workflowUpdates: Map<string, WebSocketMessage['data']>;
  logEntries: WebSocketMessage['data'][];
  systemMetrics: WebSocketMessage['data'] | null;
}

const RealtimeContext = createContext<RealtimeContextType>({
  isConnected: false,
  isConnecting: false,
  lastMessage: null,
  agentUpdates: new Map(),
  workflowUpdates: new Map(),
  logEntries: [],
  systemMetrics: null,
});

export function useRealtime() {
  return useContext(RealtimeContext);
}

interface RealtimeProviderProps {
  children: React.ReactNode;
}

export function RealtimeProvider({ children }: RealtimeProviderProps) {
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [agentUpdates, setAgentUpdates] = useState<Map<string, WebSocketMessage['data']>>(new Map());
  const [workflowUpdates, setWorkflowUpdates] = useState<Map<string, WebSocketMessage['data']>>(new Map());
  const [logEntries, setLogEntries] = useState<WebSocketMessage['data'][]>([]);
  const [systemMetrics, setSystemMetrics] = useState<WebSocketMessage['data'] | null>(null);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    setLastMessage(message);

    switch (message.type) {
      case 'agent_status':
        setAgentUpdates((prev) => {
          const next = new Map(prev);
          next.set(message.data.agentId, message.data);
          return next;
        });
        break;

      case 'workflow_progress':
        setWorkflowUpdates((prev) => {
          const next = new Map(prev);
          next.set(message.data.workflowId, message.data);
          return next;
        });
        break;

      case 'log_entry':
        setLogEntries((prev) => {
          const next = [message.data, ...prev].slice(0, 100); // Keep last 100 logs
          return next;
        });
        break;

      case 'system_metrics':
        setSystemMetrics(message.data);
        break;

      case 'notification':
        toast(message.data.title, {
          description: message.data.message,
          icon: message.data.type === 'error' ? '❌' : message.data.type === 'warning' ? '⚠️' : message.data.type === 'success' ? '✅' : 'ℹ️',
        });
        break;
    }
  }, []);

  const { isConnected, isConnecting } = useWebSocket({
    enableMock: true,
    onMessage: handleMessage,
    onConnect: () => {
      toast.success('Real-time connection established', {
        description: 'Live updates are now active',
      });
    },
    onDisconnect: () => {
      toast.error('Real-time connection lost', {
        description: 'Attempting to reconnect...',
      });
    },
  });

  const value: RealtimeContextType = {
    isConnected,
    isConnecting,
    lastMessage,
    agentUpdates,
    workflowUpdates,
    logEntries,
    systemMetrics,
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
}
