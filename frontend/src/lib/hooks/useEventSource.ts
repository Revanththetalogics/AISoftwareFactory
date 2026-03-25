'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export interface EventSourceMessage {
  type: string;
  data: unknown;
  timestamp: string;
}

interface UseEventSourceOptions {
  onMessage?: (message: EventSourceMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectDelay?: number;
}

export function useEventSource(
  url: string | null,
  options: UseEventSourceOptions = {}
) {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectDelay = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<EventSourceMessage | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();
  const connectRef = useRef<(() => void) | null>(null);

  const connect = useCallback(() => {
    if (!url || eventSourceRef.current) return;

    try {
      const eventSource = new EventSource(url, {
        withCredentials: true,
      });

      eventSource.onopen = () => {
        setIsConnected(true);
        onConnect?.();
      };

      eventSource.onmessage = (event) => {
        try {
          const message: EventSourceMessage = JSON.parse(event.data);
          setLastMessage(message);
          
          // Auto-update React Query cache based on event type
          switch (message.type) {
            case 'agent_status':
              queryClient.invalidateQueries({ queryKey: ['agents'] });
              break;
            case 'workflow_progress':
              queryClient.invalidateQueries({ queryKey: ['workflows'] });
              break;
            case 'system_metrics':
              queryClient.setQueryData(['metrics'], message.data);
              break;
            case 'deployment_status':
              queryClient.invalidateQueries({ queryKey: ['deployments'] });
              break;
          }
          
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      };

      eventSource.onerror = (error) => {
        setIsConnected(false);
        onError?.(error);
        
        // Close and reconnect
        eventSource.close();
        eventSourceRef.current = null;
        
        if (autoReconnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connectRef.current?.();
          }, reconnectDelay);
        }
      };

      eventSourceRef.current = eventSource;
    } catch (error) {
      console.error('Failed to create EventSource:', error);
      onError?.(error as Event);
    }
  }, [url, onMessage, onConnect, onError, autoReconnect, reconnectDelay, queryClient]);

  // Store connect function in ref to avoid circular dependency
  // eslint-disable-next-line
  connectRef.current = connect;

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      onDisconnect?.();
    }
  }, [onDisconnect]);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
  };
}

// Hook for system metrics stream
export function useMetricsStream() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  
  return useEventSource(`${API_URL}/events/metrics`, {
    autoReconnect: true,
  });
}

// Hook for full event stream
export function useEventStream() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  
  return useEventSource(`${API_URL}/events/stream`, {
    autoReconnect: true,
  });
}
