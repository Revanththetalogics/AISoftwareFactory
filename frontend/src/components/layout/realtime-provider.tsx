'use client';

import { createContext, useContext, useCallback, useState, useEffect } from 'react';
import { useEventStream, type EventSourceMessage } from '@/lib/hooks';
import { toast } from 'sonner';

interface RealtimeContextType {
  isConnected: boolean;
  isConnecting: boolean;
  lastMessage: EventSourceMessage | null;
  agentUpdates: Map<string, unknown>;
  workflowUpdates: Map<string, unknown>;
  logEntries: unknown[];
  systemMetrics: unknown | null;
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
  const [agentUpdates, setAgentUpdates] = useState<Map<string, unknown>>(new Map());
  const [workflowUpdates, setWorkflowUpdates] = useState<Map<string, unknown>>(new Map());
  const [logEntries, setLogEntries] = useState<unknown[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<unknown | null>(null);
  const [hasConnected, setHasConnected] = useState(false);

  const handleMessage = useCallback((message: EventSourceMessage) => {
    switch (message.type) {
      case 'agent_status':
        setAgentUpdates((prev) => {
          const next = new Map(prev);
          const data = message.data as { agent_id: string };
          next.set(data.agent_id, message.data);
          return next;
        });
        break;

      case 'workflow_progress':
        setWorkflowUpdates((prev) => {
          const next = new Map(prev);
          const data = message.data as { workflow_id: string };
          next.set(data.workflow_id, message.data);
          return next;
        });
        break;

      case 'log_entry':
        setLogEntries((prev) => {
          const next = [message.data, ...prev].slice(0, 100);
          return next;
        });
        break;

      case 'system_metrics':
        setSystemMetrics(message.data);
        break;

      case 'notification':
        const notif = message.data as { title: string; message: string; type: string };
        toast(notif.title, {
          description: notif.message,
          icon: notif.type === 'error' ? '❌' : notif.type === 'warning' ? '⚠️' : notif.type === 'success' ? '✅' : 'ℹ️',
        });
        break;

      case 'connected':
        if (!hasConnected) {
          toast.success('Real-time connection established', {
            description: 'Live updates are now active',
          });
          setHasConnected(true);
        }
        break;
    }
  }, [hasConnected]);

  const { isConnected, lastMessage } = useEventStream();

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (lastMessage) {
      handleMessage(lastMessage);
    }
  }, [lastMessage, handleMessage]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const value: RealtimeContextType = {
    isConnected,
    isConnecting: !isConnected && hasConnected,
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
